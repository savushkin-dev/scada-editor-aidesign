# check_pipeline.py
# Проверка конвейера без GUI: прогоняет все этапы на тестовых данных
# и печатает показатели. Нужен, чтобы после изменений (или отката)
# быстро убедиться, что ничего не сломалось.
#
# Запуск из папки CONTUR:
#     python check_pipeline.py
#     python check_pipeline.py --pdf input/test1.pdf --svg путь/к/marked.svg
#
# Этап экспорта выполняется, только если передан --svg с размеченным SVG
# (его создаёт разметка YOLO).
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.core import config

import argparse
import contextlib
import io
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from contur.core import golden
from contur.export import xml_io

DEFAULT_PDF = config.INPUT_DIR / "test1" / "BN1-МОЛОКОХРАНИЛИЩЕ-2025Full-4.pdf"
DEFAULT_IO_LUA = config.INPUT_DIR / "test1" / "main.io.lua"
DEFAULT_OBJECTS_LUA = config.INPUT_DIR / "test1" / "main.objects.lua"

failures = []


def step(name, fn):
    # Выполняет этап, гасит его вывод и печатает одну строку с результатом
    buffer = io.StringIO()
    start = time.perf_counter()
    try:
        with contextlib.redirect_stdout(buffer):
            value = fn()
        elapsed = time.perf_counter() - start

        # Некоторые этапы не бросают исключение, а возвращают False —
        # это тоже сбой, иначе проверка «проходит» при сломанном экспорте
        if value is False:
            failures.append(f"{name}: этап вернул False")
            print(f"  [СБОЙ] {name:<26} {elapsed:7.2f}s  вернул False")
            print(buffer.getvalue().rstrip()[-2000:])
            return value

        print(f"  [OK]   {name:<26} {elapsed:7.2f}s  {value}")
        return value
    except Exception as e:
        elapsed = time.perf_counter() - start
        failures.append(f"{name}: {type(e).__name__}: {e}")
        print(f"  [СБОЙ] {name:<26} {elapsed:7.2f}s  {type(e).__name__}: {e}")
        return None


def measure_startup(attempts: int = 5) -> float:
    # Отдельный процесс: в этом модули конвейера уже загружены, и замер
    # показал бы ноль. Мерим ровно то, что ждёт пользователь до появления окна.
    #
    # Берём наименьшее из нескольких запусков. Одиночный замер зависит от того,
    # чем занята машина: сразу после разбора чертежа тот же запуск показывал
    # 1.11 секунды вместо 0.54. Наименьшее — ближайшее к настоящему времени,
    # всё сверх него это чужая нагрузка.
    #
    # Трёх запусков не хватало. Замер сразу после прогона всех проверок дал
    # 0.78 с при неизменном пути запуска — все три попытки попали на занятую
    # машину, и проверка объявила ложное ухудшение на 37%. На спокойной
    # машине те же запуски дают 0.63-0.78, то есть разброс шире, чем шаг,
    # который проверка должна ловить. Порог трогать нельзя — он и так с запасом
    # в четверть; надёжнее сам замер.
    import os
    import subprocess

    code = "import time; t = time.perf_counter(); from contur.ui import main_window; print(time.perf_counter() - t)"
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    results = []
    for _ in range(attempts):
        try:
            done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                                  text=True, encoding="utf-8", env=env,
                                  cwd=str(Path(__file__).resolve().parent), timeout=120)
            results.append(float(done.stdout.strip().splitlines()[-1]))
        except (OSError, ValueError, IndexError, subprocess.SubprocessError) as e:
            print(f"  не удалось замерить запуск: {e}")
            return None
    return min(results)


def run_with_coverage() -> int:
    # Замер идёт по проверкам из tests/: они запускаются отдельными процессами,
    # поэтому coverage собирается в общий файл ключом parallel и потом
    # склеивается. Иначе замер показал бы только сам check_pipeline.
    import os
    import subprocess

    root = Path(__file__).resolve().parent
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")

    subprocess.run([sys.executable, "-m", "coverage", "erase"], cwd=str(root), env=env)

    tests = sorted((root / "tests").glob("test_*.py"))
    print(f"Замер покрытия: {len(tests)} файлов проверок\n")
    for tests_file in tests:
        done = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "--parallel-mode",
             "--rcfile=pyproject.toml", str(tests_file)],
            cwd=str(root), env=env, capture_output=True, text=True, encoding="utf-8")
        last = [line for line in (done.stdout or "").splitlines()
                if line.startswith("Всего:")]
        print(f"  {tests_file.name}: {last[0] if last else 'не отработали'}")

    subprocess.run([sys.executable, "-m", "coverage", "combine"],
                   cwd=str(root), env=env, capture_output=True)
    print()
    report = subprocess.run(
        [sys.executable, "-m", "coverage", "report", "--rcfile=pyproject.toml",
         "--sort=cover"],
        cwd=str(root), env=env, capture_output=True, text=True, encoding="utf-8")
    print(report.stdout)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка конвейера CONTUR")
    parser.add_argument("--pdf", default=str(DEFAULT_PDF), help="схема для разбора")
    # Файлов устройств бывает несколько (main.io.lua и main.wago.lua) —
    # окно грузит их вместе, и проверка должна видеть столько же
    parser.add_argument("--io-lua", default=[str(DEFAULT_IO_LUA)], nargs="+",
                        help="main.io.lua, можно несколько файлов подряд")
    parser.add_argument("--objects-lua", default=str(DEFAULT_OBJECTS_LUA), help="main.objects.lua")
    parser.add_argument("--page", type=int, default=0, help="страница PDF (с нуля)")
    parser.add_argument("--svg", help="размеченный SVG для проверки экспорта")
    parser.add_argument("--report", action="store_true", help="печатать отчёт о расхождениях")
    parser.add_argument("--report-limit", type=int, default=10,
                        help="сколько строк показывать в каждом разделе отчёта (0 — все)")
    parser.add_argument("--update-golden", action="store_true",
                        help="перезаписать эталонные показатели этим прогоном")
    parser.add_argument("--coverage", action="store_true",
                        help="замерить, какая доля кода исполняется проверками")
    args = parser.parse_args()

    if args.coverage:
        return run_with_coverage()

    for path in (args.pdf, args.objects_lua, *args.io_lua):
        if not Path(path).exists():
            print(f"❌ Нет файла: {path}")
            return 2

    config.ensure_output_dir()

    # Показатели этого прогона: в конце сверяются с эталоном
    metrics = {}

    # Время запуска меряется первым делом, до всякой тяжёлой работы.
    # Стояло это в конце, и замер попадал на машину, разогретую разбором
    # чертежа: 0.88 с вместо 0.66 на спокойной. С таким эталоном порог
    # ушёл бы к 1.1 с и спрятал бы настоящую регрессию.
    startup = measure_startup()
    if startup is not None:
        metrics["время_запуска_с"] = round(startup, 2)

    # Модульные тесты на разобранные места — быстрые, гоняем всегда
    import subprocess
    for tests_file in sorted((Path(__file__).resolve().parent / "tests").glob("test_*.py")):
        result = subprocess.run([sys.executable, str(tests_file)],
                                capture_output=True, text=True, encoding="utf-8")
        last = [line for line in (result.stdout or "").splitlines()
                if line.startswith("Всего:")]
        print(f"Тесты {tests_file.name}: {last[0] if last else 'не отработали'}")
        if result.returncode != 0:
            failures.append(f"тесты {tests_file.name} не прошли")
            print((result.stdout or result.stderr or "")[-1500:])
    print()

    from contur.lua.parse_lua import parse_lua_file
    from contur.lua.parse_lua_objects import parse_objects_file, extract_all_data
    from contur.pdf.extract_geometry import extract_line_segments, extract_text_elements, page_count
    from contur.core.segments import SegmentData
    from contur.pdf.contour_detector import find_contours, find_all_contour_names_by_proximity, gen_xml
    from contur.matching.device_matcher import (load_lua_data, extract_lua_names, load_pdf_geometry,
                                find_pdf_device_texts, match_devices,
                                build_match_report, format_match_report,
                                sheet_object_from_texts)

    print(f"PDF: {args.pdf} (страниц: {page_count(args.pdf)}, обрабатывается: {args.page + 1})")
    print("\nРазбор Lua:")

    def parse_io():
        # Файлов устройств может быть несколько: окно грузит main.io.lua
        # вместе с main.wago.lua и объединяет их. Проверка брала только один,
        # и на проекте mozzarella из 1298 устройств видела 730 — все COAG1*
        # с проверяемого листа лежали во втором файле.
        from contur.lua.parse_lua import merge_lua_data

        data = merge_lua_data([parse_lua_file(path) for path in args.io_lua])
        with open(config.PARSED_LUA_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        metrics["устройств_в_lua"] = len(data["devices"])
        metrics["узлов_в_lua"] = len(data["nodes"])
        return f"узлов: {len(data['nodes'])}, устройств: {len(data['devices'])}"

    def parse_objects():
        from contur.lua.objects_loader import objects_data

        data = extract_all_data(parse_objects_file(args.objects_lua))
        with open(config.PARSED_LUA_OBJECTS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        # Разобранное надо ещё и загрузить: окно так и делает, а проверка
        # до сих пор только писала файл — и весь путь «состояние устройства
        # в операции» проходил мимо неё. Теперь выгрузка видит операции,
        # и показатель «состояний_устройств» означает состояния, а не ноль
        objects_data.load_from_json(data)
        return (f"объектов: {len(data['tech_objects'])}, операций: {len(data['operations'])}, "
                f"состояний: {len(data['states'])}, шагов: {len(data['steps'])}")

    step(", ".join(Path(path).name for path in args.io_lua), parse_io)
    step("main.objects.lua", parse_objects)

    print("\nГеометрия PDF:")
    raw, texts, contours = [], [], []

    def extract_lines():
        raw.extend(extract_line_segments(args.pdf, args.page))
        metrics["сегментов"] = len(raw)
        return f"сегментов: {len(raw)}"

    def extract_texts():
        texts.extend(extract_text_elements(args.pdf, args.page))
        metrics["текстов"] = len(texts)
        return f"текстов: {len(texts)}"

    if step("извлечение линий", extract_lines) is None:
        return 1
    if step("извлечение текстов", extract_texts) is None:
        return 1

    segments = [SegmentData(**s) for s in raw]

    def detect_contours():
        contours.extend(find_contours(segments))
        metrics["контуров"] = len(contours)
        return f"контуров: {len(contours)}"

    if step("поиск контуров", detect_contours) is None:
        return 1

    lua_names = extract_lua_names(load_lua_data(str(config.PARSED_LUA_OBJECTS_JSON)))

    def name_contours():
        find_all_contour_names_by_proximity(contours, segments, texts, lua_names,
                                            config.CONTOUR_NAME_MAX_DISTANCE)
        named = sum(1 for c in contours if c.name)
        metrics["контуров_именованных"] = named
        return f"именованных: {named}"

    step("именование контуров", name_contours)

    geometry_xml = config.OUTPUT_DIR / "_check_geometry.xml"
    gen_xml(segments, contours).write(str(geometry_xml), encoding="utf-8", xml_declaration=True)

    print("\nСопоставление устройств:")
    pdf_contours, _ = load_pdf_geometry(str(geometry_xml))
    device_texts = find_pdf_device_texts(args.pdf, args.page)
    matches = []

    def run_matching():
        matches.extend(match_devices(
            load_lua_data(str(config.PARSED_LUA_JSON)), pdf_contours, device_texts,
            sheet_object_from_texts(texts)))
        metrics["меток_устройств"] = len(device_texts)
        metrics["сопоставлено"] = len(matches)
        return f"меток: {len(device_texts)}, сопоставлено: {len(matches)}"

    step("сопоставление", run_matching)

    lua_data = load_lua_data(str(config.PARSED_LUA_JSON))
    report = build_match_report(lua_data, pdf_contours, device_texts, matches)
    print(f"         нет на этом листе: {len(report['missing_on_drawing'])}, "
          f"нет в Lua: {len(report['unknown_labels'])}, "
          f"не разобрано имён: {len(report['unparsed_lua_names'])}")
    if args.report:
        print()
        print(format_match_report(report, limit=args.report_limit))

    if args.svg and matches:
        print("\nЭкспорт:")
        if not Path(args.svg).exists():
            print(f"  [СБОЙ] нет SVG: {args.svg}")
            failures.append(f"нет SVG: {args.svg}")
        else:
            from contur.core.data_models import Contour
            from contur.export.xml_export import export_current_visualization, get_pdf_page_size

            export_contours = [Contour(name=c.name, bounds=c.bounds, center=c.center,
                                       tech_object=c.name) for c in contours if c.name]
            output_xml = config.OUTPUT_DIR / "_check_export.xml"

            ok = step("экспорт в XML", lambda: export_current_visualization(
                args.svg, str(output_xml), matches, export_contours,
                pdf_size=get_pdf_page_size(args.pdf, args.page)))

            if ok:
                # Показатели качества самой разметки
                from contur.pdf.svg_geometry import (build_pipelines, detect_coordinate_system,
                                          detected_device_count, named_device_count,
                                          extract_line_segments, find_junction_points,
                                          format_markup_report, get_svg_dimensions,
                                          markup_quality_report, tolerance_scale)
                svg_root = ET.parse(args.svg).getroot()
                _, svg_scale = detect_coordinate_system(
                    svg_root, get_pdf_page_size(args.pdf, args.page))
                svg_dims = get_svg_dimensions(svg_root, svg_scale)
                svg_segments = extract_line_segments(svg_root, svg_scale, svg_dims, verbose=False)
                geometry_scale = tolerance_scale(svg_root)
                svg_junctions = find_junction_points(svg_segments, verbose=False,
                                                     scale=geometry_scale)
                svg_pipelines = build_pipelines(
                    [s for s in svg_segments if s.color == "blue"], svg_junctions,
                    verbose=False, scale=geometry_scale)
                markup = markup_quality_report(svg_segments, svg_junctions, svg_pipelines,
                                               detected_device_count(svg_root),
                                               named_device_count(svg_root))
                metrics["сегментов_в_svg"] = len(svg_segments)
                metrics["сегментов_красных"] = sum(1 for s in svg_segments if s.color == "red")
                metrics["точек_сопряжения"] = len(svg_junctions)
                metrics["трубопроводов"] = len(svg_pipelines)
                metrics["устройств_найдено"] = markup["detected_devices"]
                metrics["устройств_подписано"] = markup["named_devices"]
                metrics["разметка_sha256"] = golden.file_digest(args.svg)
                print(f"         разметка: устройств {markup['detected_devices']}, "
                      f"подписано {markup['named_devices']}, "
                      f"уверенность {markup['confidence_median']:.2f}, "
                      f"кластеров без связок {len(markup['isolated_devices'])}")
                if args.report:
                    print()
                    print(format_markup_report(markup, limit=args.report_limit))
                    print()

                root = ET.parse(output_xml).getroot()
                percents = [float(v[:-1]) for d in root.iter("Device")
                            for v in (d.get("x", ""), d.get("y", "")) if v.endswith("%")]
                out_of_range = [p for p in percents if p < 0 or p > 100]
                metrics["координат_в_экспорте"] = len(percents)
                metrics["координат_вне_диапазона"] = len(out_of_range)
                metrics["холст"] = f"{root.get('canvas-width')} x {root.get('canvas-height')}"
                metrics["связей_в_графе"] = len(list(root.iter("Connection")))
                print(f"         точек сопряжения: {root.get('junction-points-count')}, "
                      f"труб: {root.get('pipelines-count')}")
                if out_of_range:
                    failures.append(f"координат вне 0..100%: {len(out_of_range)}")
                    print(f"  [СБОЙ] координат вне диапазона 0..100%: {len(out_of_range)}")
                else:
                    print(f"  [OK]   все {len(percents)} координат в диапазоне 0..100%")

                # Обратная загрузка: экспорт должен читаться приложением.
                # Раньше здесь проверялось только наличие canvas-width — то есть
                # имя round-trip носила проверка, которая обратно ничего
                # не читала. Теперь разбор вынесен в xml_io и доступен без окна.
                devices = len(list(root.iter("Device")))
                document = xml_io.load_document(output_xml)
                metrics["устройств_при_обратном_чтении"] = len(document.matches)
                metrics["контуров_при_обратном_чтении"] = len(document.contours)

                if document.problems:
                    failures.append(f"обратное чтение потеряло записей: "
                                    f"{document.skipped}")
                    print(f"  [СБОЙ] round-trip: не разобралось {document.skipped} "
                          f"записей, первая — {document.problems[0]}")
                elif len(document.matches) != devices:
                    failures.append(f"обратное чтение дало {len(document.matches)} "
                                    f"устройств вместо {devices}")
                    print(f"  [СБОЙ] round-trip: устройств {len(document.matches)} "
                          f"вместо {devices}")
                else:
                    print(f"  [OK]   round-trip: прочитано обратно {len(document.matches)} "
                          f"устройств и {len(document.contours)} контуров, "
                          f"холст {document.canvas[0]:.0f} x {document.canvas[1]:.0f}")

                # Второй канал выдачи. Проверки на синтетическом листе есть
                # (tests/test_json_export.py), но разъехаться каналы могут
                # как раз на настоящем — здесь сверяется тот же лист
                from contur.export.json_export import export_current_visualization_json

                output_json = config.OUTPUT_DIR / "_check_export.json"
                if step("экспорт в JSON", lambda: export_current_visualization_json(
                        args.svg, str(output_json), matches, export_contours,
                        pdf_size=get_pdf_page_size(args.pdf, args.page))):
                    with open(output_json, encoding="utf-8") as f:
                        exported = json.load(f)

                    json_devices = sum(len(obj["devices"]) for obj in exported["tech_objects"])
                    same = (json_devices == devices
                            and len(exported["junction_points"]) == len(svg_junctions)
                            and len(exported["pipelines"]) == len(svg_pipelines)
                            and len(exported["connections"]) == metrics["связей_в_графе"])
                    metrics["устройств_в_json"] = json_devices

                    if same:
                        print(f"  [OK]   JSON описывает тот же лист: устройств "
                              f"{json_devices}, труб {len(exported['pipelines'])}, "
                              f"связей {len(exported['connections'])}")
                    else:
                        failures.append("JSON и XML описывают лист по-разному")
                        print(f"  [СБОЙ] JSON разошёлся с XML: устройств {json_devices} "
                              f"против {devices}, труб {len(exported['pipelines'])} "
                              f"против {len(svg_pipelines)}")

                # Формат редактора мнемосхем — то, что уходит в конечный
                # проект. Здесь важно не содержание, а что файл вообще
                # пригоден: плоский массив, числовые координаты, свой ключ
                # у каждого элемента
                from contur.export.hmi_export import export_current_visualization_hmi

                output_hmi = config.OUTPUT_DIR / "_check_export_hmi.json"
                if step("экспорт для редактора", lambda: export_current_visualization_hmi(
                        args.svg, str(output_hmi), matches, export_contours,
                        pdf_size=get_pdf_page_size(args.pdf, args.page))):
                    with open(output_hmi, encoding="utf-8") as f:
                        elements = json.load(f)

                    shapes = [e for e in elements if e.get("contur_device")]
                    frames = [e for e in elements if e["type"] == "rectangle"
                              and not e.get("contur_device_frame")]
                    # Надписи чертежа — тоже text, но это перерисованный PDF,
                    # а не подписи разметки: считаются отдельно, иначе счётчик
                    # подписей устройств перестаёт означать устройства
                    sheet_texts = [e for e in elements
                                   if e["type"] == "text" and e.get("drawing")]
                    texts = [e for e in elements
                             if e["type"] == "text" and not e.get("drawing")]
                    device_labels = [e for e in texts if not e.get("contour")]
                    meta = next((e for e in elements if e.get("contur_meta")), None)
                    keys = {e["key"] for e in elements}
                    strings = [e for e in elements
                               if isinstance(e.get("x"), str) or isinstance(e.get("x1"), str)]
                    oval = [e for e in shapes if "radius" in e
                            and (e["w"] != e["h"] or e["w"] != 2 * e["radius"])]
                    device_states = sum(len(e.get("contur_states", [])) for e in shapes)

                    metrics["элементов_для_редактора"] = len(elements)
                    metrics["элементов_рамок"] = len(frames)
                    metrics["элементов_подписей"] = len(texts)
                    metrics["элементов_надписей_чертежа"] = len(sheet_texts)
                    metrics["состояний_устройств"] = device_states

                    problems = []
                    if not isinstance(elements, list):
                        problems.append("не массив элементов")
                    if len(keys) != len(elements):
                        problems.append(f"ключи повторяются: {len(keys)} на {len(elements)}")
                    if strings:
                        problems.append(f"координаты строками: {len(strings)}")
                    if len(shapes) != devices:
                        problems.append(f"устройств {len(shapes)} вместо {devices}")
                    if oval:
                        problems.append(f"габарит круга не равен двум радиусам: {len(oval)}")
                    if device_labels and len(device_labels) != devices:
                        problems.append(f"подписей {len(device_labels)} вместо {devices}")

                    # Файл для редактора обязан описывать тот же лист, что XML:
                    # раньше он нёс только фигуры, и сверять было нечего
                    if meta is None:
                        problems.append("нет элемента meta с данными о листе")
                    else:
                        if len(meta["pipelines"]) != len(svg_pipelines):
                            problems.append(f"труб в meta {len(meta['pipelines'])} "
                                            f"вместо {len(svg_pipelines)}")
                        on_sheet = ({c.tech_object for c in export_contours}
                                    | {m.tech_object for m in matches})
                        if len(meta["tech_objects"]) != len(on_sheet):
                            problems.append(f"техобъектов в meta {len(meta['tech_objects'])} "
                                            f"вместо {len(on_sheet)}")

                    if problems:
                        failures.append("выгрузка для редактора: " + "; ".join(problems))
                        print("  [СБОЙ] выгрузка для редактора: " + "; ".join(problems))
                    else:
                        groups = [e for e in elements if e["type"] == "group"]
                        # Чертёж считается по себе, а не остатком от вычитания:
                        # у линии чертежа всегда есть contur_color, а примитивы
                        # готовых фигур лежат внутри устройств и чертежом
                        # не являются
                        drawing = [e for e in elements if "contur_color" in e
                                   and e["type"] == "line"]
                        parts = [e for e in elements if e.get("contur_symbol_part")]
                        print(f"  [OK]   формат редактора: {len(elements)} элементов "
                              f"(чертёж {len(drawing)}, надписи чертежа {len(sheet_texts)}, "
                              f"фигуры устройств {len(parts)} примитивов, "
                              f"рамки {len(frames)}, группы {len(groups)}, "
                              f"устройства {len(shapes)}, подписи {len(texts)}), "
                              f"ключи уникальны")
                        print(f"  [OK]   состояний устройств в операциях: {device_states}, "
                              f"связей в meta: {len(meta['connections'])}, "
                              f"операций: {len(meta['operations'])}")

                    # Самопроверка по спецификации импорта (§10): файл
                    # читается с диска ровно так, как его прочитает редактор
                    from contur.export import hmi_validate

                    remarks, drawing_stats = hmi_validate.validate(elements)
                    metrics["чертёж_короче_клетки"] = drawing_stats["короткие_отрезки"]
                    if remarks:
                        failures.append(f"файл не проходит приёмку: {len(remarks)}")
                        print("  [СБОЙ] приёмка по спецификации импорта:")
                        for remark in remarks[:5]:
                            print(f"           {remark}")
                    else:
                        print("  [OK]   приёмка по спецификации импорта: замечаний нет")
                    # Размер листа — величина, за которой стоит следить,
                    # но не замечание: это рамка сцены, а не предел
                    # (PROJECT.md, §6.2)
                    if drawing_stats.get("холст_ширина"):
                        print(f"         лист {drawing_stats['холст_ширина']}x"
                              f"{drawing_stats['холст_высота']} — рамка сцены, "
                              f"размер задаётся CONTUR_HMI_SYMBOL_CELLS")
                    print(f"         чертёж: короче клетки "
                          f"{drawing_stats['короткие_отрезки']}, ортогональных вне "
                          f"сетки {drawing_stats['ортогональные_вне_сетки']}, "
                          f"диагоналей {drawing_stats['диагонали']}")

    # Время запуска окна: замеряется отдельным процессом, иначе модули уже
    # загружены этим прогоном и импорт занял бы ноль. Это страховка от того,
    # чтобы ленивый импорт модели вернули обратно в шапку
    print("\nВремя:")
    if startup is not None:
        print(f"  [OK]   запуск окна {startup:.2f} с "
              f"(лучшее из 5, замерено до конвейера)")
    else:
        print("  [--]   запуск окна замерить не удалось")

    # Сверка с эталоном. Числа конвейера раньше жили только в описании
    # проекта, то есть сверялись глазами и по памяти — так и приезжали
    # тихие регрессии
    print("\nСверка с эталоном:")
    if args.update_golden:
        target = golden.save(args.pdf, args.page, metrics)
        print(f"  эталон перезаписан: {target.name} ({len(metrics)} показателей)")
        print("  правку кода и обновление эталона коммитить отдельно")
    else:
        expected = golden.load(args.pdf, args.page)
        if expected is None:
            print(f"  эталона для этого листа нет ({golden.path_for(args.pdf, args.page).name})")
            print("  создать: python check_pipeline.py --svg <svg> --update-golden")
        else:
            problems = golden.compare(expected, metrics)
            print(golden.format_report(args.pdf, args.page, problems))
            if problems:
                failures.append(f"расхождений с эталоном: {len(problems)}")

    print("\n" + "=" * 60)
    if failures:
        print(f"❌ Сбоев: {len(failures)}")
        for item in failures:
            print(f"   - {item}")
        return 1

    print("✅ Все этапы прошли")
    return 0


if __name__ == "__main__":
    sys.exit(main())
