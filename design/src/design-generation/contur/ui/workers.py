# workers.py
# Фоновые потоки приложения.
#
# Вынесены из main_window.py: там они соседствовали с виджетами, главным окном
# и логикой экспорта в одном файле на 2487 строк.
#
# Каждый поток делает один этап конвейера и сообщает о ходе сигналами
# progress / finished / error.
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.core import config

import json
import os
import shutil
import tempfile
import time
from typing import List

import fitz
import svgwrite
from PySide6.QtCore import QThread, Signal

from contur.core import errors
from contur.pdf import markup_cache
from contur.pdf.contour_detector import find_all_contour_names_by_proximity, find_contours, gen_xml
from contur.matching.device_matcher import (extract_lua_names, find_pdf_device_texts, find_sheet_object,
                            load_lua_data, load_pdf_geometry, match_devices)
from contur.pdf.extract_geometry import extract_line_segments, extract_text_elements
from contur.lua.parse_lua import lua_table_to_python, merge_lua_data, read_file_with_encoding
from contur.lua.parse_lua_objects import extract_all_data, parse_objects_file
from contur.pdf.pdf_processor import (MAX_FAILED_SHARE, DeviceDetector, DeviceLabeler,
                           _median_device_size, iter_markup_elements, point_in_device)
from contur.core.data_models import SegmentData


class GeometryExtractionThread(QThread):
    # Поток для извлечения геометрии из PDF
    progress = Signal(str)
    finished = Signal(bool, str, list, list)  # success, xml_path, contours, texts
    error = Signal(str)

    def __init__(self, pdf_path: str, page_number: int = 0):
        super().__init__()
        self.pdf_path = pdf_path
        self.page_number = page_number

    def run(self):
        try:
            self.progress.emit("Извлечение линий из PDF...")

            # Берём только выбранную страницу: раньше геометрия собиралась
            # со всех страниц, а размечалась всегда первая
            raw_segments = extract_line_segments(self.pdf_path, self.page_number)
            texts = extract_text_elements(self.pdf_path, self.page_number)

            # Скан открывается без ошибки и даёт ноль сегментов. Дальше
            # конвейер молча доходил до пустой схемы, и понять почему
            # было нельзя
            if not raw_segments:
                self.error.emit(errors.NO_VECTOR_GRAPHICS)
                return

            self.progress.emit(f"Извлечено {len(raw_segments)} сегментов, {len(texts)} текстовых элементов")

            # Конвертируем в SegmentData
            segments = [SegmentData(**s) for s in raw_segments]

            # Находим контуры
            self.progress.emit("Поиск замкнутых контуров...")
            contours = find_contours(segments)

            self.progress.emit(f"Найдено {len(contours)} контуров")

            # Загружаем Lua данные для именования контуров
            lua_data = None
            lua_names = {}
            if os.path.exists(config.PARSED_LUA_OBJECTS_JSON):
                lua_data = load_lua_data(str(config.PARSED_LUA_OBJECTS_JSON))
                lua_names = extract_lua_names(lua_data) if lua_data else {}
                self.progress.emit("Lua данные загружены для именования контуров")

            # Находим имена контуров
            self.progress.emit("Сопоставление имен контуров...")
            find_all_contour_names_by_proximity(contours, segments, texts, lua_names, max_distance=200)

            # Создаем временный XML файл.
            # Открытый файл нужен только ради имени: путь отдаётся дальше
            # по конвейеру, а пишет в него gen_xml
            temp_xml = tempfile.NamedTemporaryFile(  # noqa: SIM115
                mode='w', suffix='.xml', delete=False)
            temp_xml.close()

            gen_xml(segments, contours).write(temp_xml.name, encoding="utf-8", xml_declaration=True)

            self.progress.emit(f"Геометрия сохранена в {temp_xml.name}")

            # Конвертируем контуры в формат для визуализатора
            contour_list = []
            for c in contours:
                if c.name:
                    contour_list.append({
                        'name': c.name,
                        'tech_object': c.name,
                        'bounds': c.bounds,
                        'center': c.center,
                        'segments': c.segments
                    })

            self.finished.emit(True, temp_xml.name, contour_list, texts)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(errors.describe(e, self.pdf_path))


class PageTitlesThread(QThread):
    """Названия листов из штампа чертежа.

    В рабочем файле 265 страниц, и вычитывать текст со всех сразу нельзя —
    окно замерло бы на несколько секунд. Названия приходят порциями, список
    при этом уже открыт и им можно пользоваться.
    """
    titles = Signal(int, str)  # номер страницы, название
    finished_reading = Signal()

    # Штамп Eplan занимает правый нижний угол листа. Границы подобраны
    # замером: уже — и в область не попадает название, шире — в неё лезут
    # примечания с самого чертежа
    TITLE_AREA = (0.55, 0.80, 1.0, 1.0)

    # Подписи самого штампа, а не названия листа: попадаются на сотнях
    # страниц и ничего не говорят о содержимом
    GENERIC_LABELS = ("примечания к чертежу",)

    def __init__(self, pdf_path: str, total_pages: int):
        super().__init__()
        self.pdf_path = pdf_path
        self.total_pages = total_pages

    def run(self):
        try:
            document = fitz.open(self.pdf_path)
        except Exception:
            self.finished_reading.emit()
            return

        try:
            for number in range(min(self.total_pages, document.page_count)):
                if self.isInterruptionRequested():
                    break
                self.titles.emit(number, self._page_title(document[number]))
        finally:
            document.close()
            self.finished_reading.emit()

    def _page_title(self, page) -> str:
        # Берём самую длинную осмысленную строку из штампа: там название
        # участка, а вокруг него — обозначения и номера.
        #
        # Отбор строк подобран замером на файле в 265 листов. Без него
        # в названия попадали обрывки примечаний с чертежа — «и, запитанных
        # от внешнего источника», «ойства операции мойка». Названия листов
        # начинаются с прописной буквы или цифры, обрывки — со строчной.
        left, top, right, bottom = self.TITLE_AREA
        rect = page.rect
        area = fitz.Rect(rect.x0 + rect.width * left, rect.y0 + rect.height * top,
                         rect.x0 + rect.width * right, rect.y0 + rect.height * bottom)

        best = ""
        for block in page.get_text("dict", clip=area).get("blocks", []):
            for line in block.get("lines", []):
                text = " ".join(span["text"] for span in line.get("spans", [])).strip()
                if len(text) <= 4 or text.isdigit() or text[0].islower():
                    continue
                if text.lower() in self.GENERIC_LABELS:
                    continue
                if len(text) > len(best):
                    best = text
        return best


class PostgresExportThread(QThread):
    """Выгрузка в базу отдельным потоком.

    Раньше экспорт шёл прямо в потоке окна: разбор SVG, перевод координат
    и сама запись в базу — всё это время окно не перерисовывалось и Windows
    показывала его как переставшее отвечать. Помогали вызовы processEvents,
    но только до первого долгого запроса.
    """
    progress = Signal(str)
    finished = Signal(bool, str)  # success, сообщение

    def __init__(self, svg_path: str, matches: list, contours: list,
                 db_config: dict, pdf_size=None, mode: str = "append"):
        super().__init__()
        self.svg_path = svg_path
        self.matches = matches
        self.contours = contours
        self.db_config = db_config
        self.pdf_size = pdf_size
        self.mode = mode

    def run(self):
        try:
            from contur.export.postgres_export import PostgresExporter

            self.progress.emit("Выгрузка в PostgreSQL...")
            # Экспортёр берётся напрямую, а не через export_to_postgresql:
            # оттуда не достать итоги, а окно должно показать числа,
            # а не одно лишь «данные выгружены»
            exporter = PostgresExporter(self.db_config, pdf_size=self.pdf_size)
            success = exporter.export(self.svg_path, self.matches, self.contours,
                                      auto_create_tables=True, mode=self.mode)

            if success:
                self.finished.emit(True, self._summary(exporter.stats))
            else:
                self.finished.emit(False, "База отказала в записи. Проверьте подключение "
                                          "и права пользователя.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, f"Ошибка выгрузки: {e}")

    @staticmethod
    def _summary(stats: dict) -> str:
        if not stats:
            return "Данные выгружены в PostgreSQL"

        lines = [f"Контуров: {stats['контуров']}",
                 f"Устройств: {stats['устройств']}",
                 f"Связей: {stats['связей']}",
                 f"Точек сопряжения: {stats['точек сопряжения']}"]
        return "Выгружено в PostgreSQL.\n\n" + "\n".join(lines)


class DeviceMatchingThread(QThread):
    # Поток для сопоставления устройств
    progress = Signal(str)
    finished = Signal(bool, list)  # success, matches
    error = Signal(str)

    def __init__(self, lua_json_path: str, pdf_path: str, geometry_xml_path: str,
                 page_number: int = 0):
        super().__init__()
        self.lua_json_path = lua_json_path
        self.pdf_path = pdf_path
        self.geometry_xml_path = geometry_xml_path
        # Тексты берутся с той же страницы, что и геометрия: иначе на
        # многостраничном файле в сопоставление попадают подписи со всего документа
        self.page_number = page_number
        # Сохраняем для отчёта о расхождениях
        self.lua_data = None
        self.pdf_contours = None
        self.device_texts = None

    def run(self):
        try:
            self.progress.emit("Загрузка Lua данных...")

            # Используем импортированные функции из device_matcher
            lua_data = load_lua_data(self.lua_json_path)
            self.progress.emit(f"Загружено устройств: {len(lua_data.get('devices', []))}")

            # Загружаем геометрию из XML
            self.progress.emit("Загрузка геометрии...")
            pdf_contours, _ = load_pdf_geometry(self.geometry_xml_path)
            self.progress.emit(f"Загружено контуров: {len(pdf_contours)}")

            # Извлекаем тексты из PDF
            self.progress.emit("Извлечение текстов из PDF...")
            pdf_device_texts = find_pdf_device_texts(self.pdf_path, self.page_number)
            self.progress.emit(f"Найдено текстовых меток: {len(pdf_device_texts)}")

            # Сопоставляем устройства
            self.progress.emit("Сопоставление устройств...")
            matches = match_devices(lua_data, pdf_contours, pdf_device_texts,
                                    find_sheet_object(self.pdf_path, self.page_number))

            self.lua_data = lua_data
            self.pdf_contours = pdf_contours
            self.device_texts = pdf_device_texts

            self.progress.emit(f"Сопоставлено устройств: {len(matches)}")

            # device_matcher возвращает те же DeviceMatch из data_models —
            # переписывать поля вручную больше не нужно
            self.finished.emit(True, matches)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(errors.describe(e))


class LuaParsingThread(QThread):
    #Поток для парсинга Lua файлов
    progress = Signal(str)
    finished = Signal(bool, dict)
    error = Signal(str)

    def __init__(self, lua_files: List[str]):
        super().__init__()
        self.lua_files = lua_files

    def run(self):
        try:
            from lupa import LuaRuntime

            self.progress.emit("Парсинг Lua файлов...")

            all_data = []

            for i, lua_file in enumerate(self.lua_files):
                self.progress.emit(f"Обработка файла {i + 1}/{len(self.lua_files)}: {os.path.basename(lua_file)}")

                # Используем импортированную функцию для чтения с определением кодировки
                content = read_file_with_encoding(lua_file)

                # Выполняем Lua код
                lua = LuaRuntime(unpack_returned_tuples=True)
                lua.execute(content)

                globals_ = lua.globals()
                nodes = globals_.nodes if "nodes" in globals_ else None
                devices = globals_.devices if "devices" in globals_ else None

                if nodes is None:
                    raise ValueError(f"В файле {os.path.basename(lua_file)} не найден блок 'nodes'")
                if devices is None:
                    raise ValueError(f"В файле {os.path.basename(lua_file)} не найден блок 'devices'")

                # Используем импортированную функцию для конвертации
                parsed = {
                    "nodes": lua_table_to_python(nodes),
                    "devices": lua_table_to_python(devices)
                }

                all_data.append(parsed)

            # Используем импортированную функцию для объединения
            merged = merge_lua_data(all_data)

            # Обмен с соседними контроллерами, если рядом лежит shared.lua
            from contur.lua import parse_lua_shared

            parse_lua_shared.attach(merged, self.lua_files)

            # Сохраняем в JSON. Путь берётся из config: относительная строка
            # клала разбор в текущую папку, а собранное приложение запускают
            # ярлыком откуда угодно — файл уезжал туда, где его потом не искали
            config.ensure_output_dir()
            output_path = str(config.PARSED_LUA_JSON)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)

            self.progress.emit(f"Сохранено: {output_path}")
            self.progress.emit(f"IO узлов: {len(merged['nodes'])}, устройств: {len(merged['devices'])}")

            self.finished.emit(True, merged)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(errors.describe(e, self.lua_files[0] if self.lua_files else None))


class LuaObjectsParsingThread(QThread):
    # Поток для парсинга main.objects.lua
    progress = Signal(str)
    finished = Signal(bool, dict)
    error = Signal(str)

    def __init__(self, lua_file_path: str):
        super().__init__()
        self.lua_file_path = lua_file_path

    def run(self):
        try:
            self.progress.emit("Парсинг main.objects.lua...")

            # Используем импортированные классы и функции
            parsed_data = parse_objects_file(self.lua_file_path)

            self.progress.emit("Извлечение данных...")
            extracted_data = extract_all_data(parsed_data)

            # Сохраняем в JSON
            config.ensure_output_dir()
            output_path = str(config.PARSED_LUA_OBJECTS_JSON)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False, default=str)

            self.progress.emit(f"Сохранено: {output_path}")
            self.progress.emit(f"Объектов: {len(extracted_data.get('tech_objects', []))}, "
                               f"Операций: {len(extracted_data.get('operations', []))}, "
                               f"Состояний: {len(extracted_data.get('states', []))}, "
                               f"Шагов: {len(extracted_data.get('steps', []))}")

            self.finished.emit(True, extracted_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(errors.describe(e, self.lua_file_path))


class YOLOMarkingThread(QThread):
    #Поток для разметки PDF с помощью YOLO
    progress = Signal(str)
    # Доля выполненного: сделано плиток из скольких. Полоса прогресса была
    # бесконечной, и по ней нельзя было понять, идёт работа минуту или десять
    progress_value = Signal(int, int)
    finished = Signal(bool, str)  # success, svg_path
    error = Signal(str)
    cancelled = Signal()

    # Настройки модели берутся из config.py (переопределяются переменными окружения)
    MODEL_PATH = str(config.YOLO_MODEL_PATH)
    CONF_THRESHOLD = config.YOLO_CONF_THRESHOLD

    def __init__(self, pdf_path: str, page_number: int = 0, profile: str | None = None,
                 matched_devices=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.page_number = page_number
        # К моменту разметки сопоставление уже отработало и знает полные имена;
        # без них разметка искала подписи в сырых текстах и треть рамок
        # оставалась безымянной
        self.matched_devices = list(matched_devices or [])

        # Профиль задаёт масштаб детекции: «точнее» режет лист мельче
        # и находит меньше сомнительных устройств, но считает дольше
        self.profile = profile or config.YOLO_PROFILE
        settings = config.YOLO_PROFILES.get(self.profile, config.YOLO_PROFILES["balanced"])
        self.TILE_SIZE = settings["tile"]
        self.STEP = settings["step"]
        self.DPI = settings["dpi"]
        # Моменты старта нужны для оценки остатка; задаются здесь на случай
        # вызова детекции в обход run() — так делают проверки
        self._started_at = time.monotonic()
        self._tiles_started_at = self._started_at

    def _convert_pdf_to_png(self, pdf_path: str, png_path: str):
        # Конвертирует первую страницу PDF в PNG
        doc = fitz.open(pdf_path)
        page = doc[self.page_number]

        zoom = self.DPI / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(png_path)
        doc.close()

    def _detect_devices(self, png_path: str) -> list:
        # Детекция вынесена в pdf_processor.DeviceDetector — тот же код
        # использует и консольный сценарий разметки
        detector = DeviceDetector(self.MODEL_PATH, tile_size=self.TILE_SIZE,
                                  conf_threshold=self.CONF_THRESHOLD, step=self.STEP)
        return detector.detect_devices(png_path,
                                       on_progress=self._on_tiles_done,
                                       should_stop=self.isInterruptionRequested)

    # Сколько плиток пройти, прежде чем показывать оценку остатка: первые
    # пачки идут медленнее прочих, и по ним время завышается втрое
    ESTIMATE_AFTER_TILES = 16

    def _on_tiles_done(self, done: int, total: int):
        self.progress_value.emit(done, total)
        if not total:
            return

        # Отсчёт начинается с первой плитки, а не со старта потока: загрузка
        # модели и рендер страницы занимают около десяти секунд, и попав
        # в расчёт, они завышали оценку остатка на порядок
        if done == 0:
            self._tiles_started_at = time.monotonic()
            self.progress.emit(f"Обнаружение устройств: {total} плиток")
            return

        message = f"Обнаружение устройств: плитка {done} из {total}"
        if done >= self.ESTIMATE_AFTER_TILES:
            elapsed = time.monotonic() - self._tiles_started_at
            # Детекция идёт равномерно, поэтому линейной пропорции достаточно
            left = elapsed / done * (total - done)
            if left > 1:
                message += f", осталось ~{left:.0f} с"
        self.progress.emit(message)

    def _png_size(self, page) -> tuple:
        # Размер растра, в котором работала детекция.
        #
        # Раньше ради этих двух чисел страница рендерилась в PNG второй раз:
        # сжатие картинки 14034x9934 стоит 3.1 секунды на каждый прогон
        # разметки. Тот же размер даёт преобразование прямоугольника страницы —
        # ровно так его считает и сам get_pixmap, значения совпадают до пикселя.
        zoom = self.DPI / 72
        irect = (page.rect * fitz.Matrix(zoom, zoom)).irect
        return irect.width, irect.height

    def _create_svg_with_markup(self, pdf_path: str, device_rectangles: list) -> str:
        # Создает SVG с разметкой устройств
        # Открываем PDF для получения размеров
        doc = fitz.open(pdf_path)
        page = doc[self.page_number]
        pdf_width = page.rect.width
        pdf_height = page.rect.height
        W, H = self._png_size(page)
        doc.close()

        # Масштабируем координаты из PNG в PDF
        scale_x = pdf_width / W
        scale_y = pdf_height / H

        # scaled() сохраняет класс и уверенность, распаковка координат
        # по-прежнему работает через DeviceBox.__iter__
        scaled_rectangles = [box.scaled(scale_x, scale_y) for box in device_rectangles]

        # Создаем SVG
        # Файл нужен только ради имени: писать в него будет svgwrite
        svg_path = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False)  # noqa: SIM115
        svg_path.close()

        dwg = svgwrite.Drawing(
            svg_path.name,
            size=(f"{pdf_width}", f"{pdf_height}"),
            viewBox=f"0 0 {pdf_width} {pdf_height}",
            profile="full",
            # debug=True (по умолчанию) отвергает нестандартные атрибуты:
            # add() с data-device-name бросал ValueError, а вызов обёрнут
            # в try/except — линии устройств молча пропадали из разметки
            debug=False
        )
        # Извлекаем графику из PDF
        doc = fitz.open(pdf_path)
        page = doc[self.page_number]

        # Метки устройств нужны до отрисовки: имя пишется в data-device-name,
        # иначе связь «устройство -> трубопровод» теряется при разборе SVG.
        # И до заголовка SVG: в нём указывается число подписанных рамок.
        labels = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["text"].strip():
                        labels.append((span["bbox"][0], span["bbox"][1], span["text"].strip()))
        labeler = DeviceLabeler(scaled_rectangles, labels,
                                matched_devices=self.matched_devices)

        # Показатели разметки — отчёту о качестве, чтобы видеть разрыв
        # между найденным и подписанным
        dwg['data-device-count'] = str(len(scaled_rectangles))
        dwg['data-device-size'] = f"{_median_device_size(scaled_rectangles):.2f}"
        dwg['data-device-named'] = str(sum(1 for b in scaled_rectangles
                                           if labeler.name_for_box(b)))

        # Белый фон
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(f"{pdf_width}pt", f"{pdf_height}pt"),
            fill="white"
        ))

        failed_elements = 0
        total_elements = 0

        for element in iter_markup_elements(page, scaled_rectangles, labeler):
            total_elements += 1
            try:
                stroke = element.stroke_width
                if element.kind == "line":
                    x1, y1, x2, y2 = element.points
                    item = dwg.line(start=(x1, y1), end=(x2, y2),
                                    stroke=element.color, stroke_width=stroke)
                elif element.kind == "rect":
                    x, y, w, h = element.points
                    item = dwg.rect(insert=(x, y), size=(w, h), fill="none",
                                    stroke=element.color, stroke_width=stroke)
                else:  # кривая
                    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = element.points
                    item = dwg.path(
                        d=f"M {x1},{y1} C {x2},{y2} {x3},{y3} {x4},{y4}",
                        fill="none", stroke=element.color, stroke_width=stroke)

                for key, value in element.marks.items():
                    item[key] = value
                dwg.add(item)

            except Exception as e:
                failed_elements += 1
                if failed_elements <= 3:
                    print(f"Ошибка обработки элемента: {e}")

        # Молчаливое проглатывание ошибок уже приводило к тому, что разметка
        # теряла половину линий и почти все устройства, а внешне отличалась
        # только «пустой» схемой. Теперь неудачи видно.
        if failed_elements:
            share = failed_elements * 100 // max(1, total_elements)
            message = (f"не отрисовано элементов: {failed_elements} из {total_elements} "
                       f"({share}%)")
            print(f"⚠️ {message}")
            if share >= MAX_FAILED_SHARE:
                raise RuntimeError(
                    f"Разметка получилась неполной — {message}. "
                    f"Файл SVG не сохранён, чтобы не выдать заведомо испорченную схему.")

        # Добавляем текст
        text_data = page.get_text("dict")
        for block in text_data["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    # Пробельные строки в чертеже есть, и они попадали в SVG
                    # пустыми элементами <text>. Консольный генератор их
                    # отбрасывает — из-за этого два пути расходились на три
                    # элемента при полностью совпадающей геометрии
                    if not text.strip():
                        continue

                    size = span["size"]
                    bbox = span["bbox"]
                    x = bbox[0]
                    y = bbox[1]

                    color = "red" if point_in_device(x, y, scaled_rectangles) else "blue"
                    dwg.add(dwg.text(
                        text,
                        insert=(x, y),
                        fill=color,
                        font_size=size
                    ))

        doc.close()
        dwg.save()

        return svg_path.name

    def cache_key(self) -> str:
        # Ключ вынесен из run(), чтобы окно могло заранее узнать, готова ли
        # разметка этого листа, и показать её без запуска модели
        return markup_cache.build_key(
            self.pdf_path, self.page_number, self.MODEL_PATH,
            generator="main_window.svgwrite",
            params={"tile": self.TILE_SIZE, "step": self.STEP,
                    "conf": self.CONF_THRESHOLD, "dpi": self.DPI,
                    "profile": self.profile,
                    "matched": len(self.matched_devices)})

    def run(self):
        temp_dir = None
        self._started_at = time.monotonic()
        try:
            # Разметка одного и того же листа даёт один и тот же результат,
            # а стоит ~80 секунд — сначала смотрим в кэш
            key = self.cache_key()

            cached = markup_cache.lookup(key)
            if cached:
                self.progress.emit("Разметка взята из кэша")
                self.finished.emit(True, cached)
                return

            # Создаем временную папку для PNG
            temp_dir = tempfile.mkdtemp()
            png_path = os.path.join(temp_dir, "temp_page.png")

            # Конвертируем PDF в PNG
            self.progress.emit("Конвертация PDF в PNG...")
            self._convert_pdf_to_png(self.pdf_path, png_path)

            if self.isInterruptionRequested():
                self._finish_cancelled(temp_dir)
                return

            # Обнаружение устройств на PNG
            self.progress.emit(f"Обнаружение устройств (модель: {self.MODEL_PATH})...")
            device_rectangles = self._detect_devices(png_path)

            # Прерванная детекция возвращает пустой список — сохранять такой
            # результат в кэш нельзя, иначе лист навсегда останется пустым
            if self.isInterruptionRequested():
                self._finish_cancelled(temp_dir)
                return

            self.progress.emit(f"Найдено устройств: {len(device_rectangles)}")

            # Обработка PDF и создание SVG
            self.progress.emit("Создание размеченного SVG...")
            svg_path = self._create_svg_with_markup(self.pdf_path, device_rectangles)

            # Очищаем временные файлы
            shutil.rmtree(temp_dir, ignore_errors=True)

            svg_path = markup_cache.store(key, svg_path)

            spent = time.monotonic() - self._started_at
            self.progress.emit(f"SVG создан за {spent:.0f} с: {svg_path}")
            self.finished.emit(True, svg_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.error.emit(errors.describe(e, self.pdf_path))

    def _finish_cancelled(self, temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        self.progress.emit("Разметка отменена")
        self.cancelled.emit()
