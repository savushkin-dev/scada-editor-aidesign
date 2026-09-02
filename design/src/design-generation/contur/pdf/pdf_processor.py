from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.core import config
import fitz
import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import tempfile
import re
from collections import Counter
from dataclasses import dataclass



from contur.pdf import markup_cache
from contur.core.data_models import DeviceBox
from contur.pdf.svg_geometry import (DEVICE_OVERLAP_SHARE, JunctionPoint, LineSegment,
                          find_junction_points,
                          segment_box_overlap)


# Доля неотрисованных элементов, при которой разметку нельзя отдавать:
# лучше остановиться с ошибкой, чем выдать заведомо испорченную схему.
# Оба генератора разметки — консольный и оконный — держат один порог.
MAX_FAILED_SHARE = 5


@dataclass
class MarkupElement:
    """Один примитив чертежа, уже разобранный и отнесённый к устройству или трубе.

    Общий промежуточный вид для обоих генераторов разметки. До этого каждый
    из них обходил примитивы сам: окно через svgwrite, консоль сборкой строк.
    Логика была одинаковой по смыслу и разной по написанию — включая две
    копии проверок принадлежности с разными именами, — и одну и ту же ошибку
    в них дважды исправляли порознь.
    """
    kind: str                       # "line" | "rect" | "curve"
    points: tuple                   # линия (x1,y1,x2,y2); прямоугольник (x,y,w,h);
                                    # кривая ((x,y) x 4)
    color: str                      # "red" — устройство, "blue" — труба
    is_device: bool
    marks: Dict[str, str]           # атрибуты data-* от DeviceLabeler
    device_name: str
    stroke_width: float


def point_in_device(x: float, y: float, rects, tolerance: float = 5) -> bool:
    for x1, y1, x2, y2 in rects:
        if x1 - tolerance <= x <= x2 + tolerance and y1 - tolerance <= y <= y2 + tolerance:
            return True
    return False


def line_in_device(x1: float, y1: float, x2: float, y2: float, rects,
                   tolerance: float = 3) -> bool:
    # Линия принадлежит устройству, если внутри его рамки лежит больше
    # половины её длины. Проверка по середине красила трубу, пересекающую
    # устройство, красной, а линию устройства длиннее рамки оставляла синей.
    return any(
        segment_box_overlap(x1, y1, x2, y2, rx1, ry1, rx2, ry2, tolerance)
        >= DEVICE_OVERLAP_SHARE
        for rx1, ry1, rx2, ry2 in rects)


def _stroke_width(path: dict) -> float:
    try:
        return float(path.get("width"))
    except (TypeError, ValueError):
        return 1.0


def iter_markup_elements(page, device_rects, labeler):
    """Разбирает примитивы страницы и относит каждый к устройству или трубе.

    Отдаёт MarkupElement в порядке отрисовки. Ошибку на отдельном примитиве
    не глушит — пусть решает вызывающий: раньше молчаливый пропуск стоил
    59 потерянных элементов из 1108, и заметить это было нечем.
    """
    for path in page.get_drawings():
        width = _stroke_width(path)

        for item in path.get("items", []):
            kind = item[0]
            if kind == "l":
                _, p1, p2 = item
                (x1, y1), (x2, y2) = p1, p2
                is_device = line_in_device(x1, y1, x2, y2, device_rects)
                centre = ((x1 + x2) / 2, (y1 + y2) / 2)
                points = (x1, y1, x2, y2)
                name = "line"
            elif kind == "re":
                _, rect = item
                x, y, w, h = rect
                centre = (x + w / 2, y + h / 2)
                is_device = point_in_device(centre[0], centre[1], device_rects)
                points = (x, y, w, h)
                name = "rect"
            elif kind == "c":
                _, p1, p2, p3, p4 = item
                is_device = any(point_in_device(px, py, device_rects)
                                for px, py in (p1, p2, p3, p4))
                centre = ((p1[0] + p4[0]) / 2, (p1[1] + p4[1]) / 2)
                points = (p1, p2, p3, p4)
                name = "curve"
            else:
                continue

            # Метки берём только для устройств, но переменную заводим всегда:
            # иначе на первых элементах листа её ещё нет, а дальше труба
            # получает метки последнего встреченного устройства
            marks = labeler.marks_at(*centre) if is_device else {}

            yield MarkupElement(
                kind=name, points=points,
                color="red" if is_device else "blue",
                is_device=is_device, marks=marks,
                device_name=marks.get("data-device-name", ""),
                stroke_width=width)


class PDFToPNGConverter:
    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def convert(self, pdf_path: str, output_dir: str | None = None,
                page_number: int = 0) -> List[str]:
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)

        print("📄 Конвертируем PDF в PNG...")
        print(f"   Файл: {pdf_path}")

        png_paths = []

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            print(f"📊 Всего страниц: {total_pages}")

            if not total_pages:
                raise IndexError("В файле нет ни одной страницы — он повреждён "
                                 "или выгрузился не полностью.")
            if not 0 <= page_number < total_pages:
                raise IndexError(f"В PDF нет страницы {page_number + 1} — "
                                 f"в файле их {total_pages}.")

            for page_num in (page_number,):
                page = doc[page_num]

                zoom = self.dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                output_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
                pix.save(output_path)
                png_paths.append(output_path)
                print(f"✅ Сохранено: {output_path}")

            doc.close()
            return png_paths

        except Exception as e:
            print(f"❌ Ошибка конвертации: {e}")
            return []


class DeviceDetector:
    # Порог «плитка пустая»: доля небелых пикселей, ниже которой на плитке
    # заведомо ничего нет и запускать модель не нужно
    BLANK_INK_RATIO = 1e-5
    # Порог IoU, при котором две рамки считаются одним устройством
    MERGE_IOU = 0.5
    # Порог «пересечение к меньшей площади». Нужен для вложенных рамок:
    # рамка 89x89 внутри рамки 200x200 даёт IoU всего 0.198 — ниже MERGE_IOU,
    # и дубликат оставался жить рядом с той, что его целиком содержит.
    MERGE_IOMIN = 0.8

    def __init__(self, model_path: str, tile_size: int = config.YOLO_TILE_SIZE,
                 conf_threshold: float = config.YOLO_CONF_THRESHOLD, step: int = config.YOLO_STEP,
                 batch_size: int = 4, imgsz: int = config.YOLO_IMGSZ):
        self.model_path = model_path
        self.tile_size = tile_size
        # Плитка масштабируется до imgsz перед подачей в сеть: так можно менять
        # относительный размер символа, не трогая DPI рендера
        self.imgsz = imgsz
        self.conf_threshold = conf_threshold
        self.step = step
        self.batch_size = max(1, batch_size)
        self.model = None
        # Устройство для OpenVINO. У PyTorch остаётся None: ему довод device
        # не нужен, и передавать его незачем
        self.device = None

    def _load_model(self):
        # ultralytics тянет за собой torch — это 1.9 секунды импорта. В шапке
        # модуля он удлинял запуск приложения втрое даже тогда, когда разметку
        # не запускали ни разу, поэтому импорт живёт здесь.
        if self.model is not None:
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Модель YOLO не найдена: {self.model_path}")

        # Выгруженная модель считает на треть быстрее при том же результате
        # (замер и оговорки — в config). Путь к весам при этом не подменяется:
        # на нём держится ключ кэша разметки, и подмена обесценила бы весь кэш
        exported = config.find_openvino_model(self.model_path)
        source = str(exported) if exported else self.model_path
        self.device = config.OPENVINO_DEVICE if exported else None

        print(f"📦 Загрузка модели YOLO: {source}")
        from ultralytics import YOLO
        self.model = YOLO(source)

    @staticmethod
    def _tile_positions(total: int, tile: int, step: int) -> List[int]:
        # Координаты плиток с обязательным покрытием правого/нижнего края.
        # Прежний range(0, total - tile, step) до края не доходил, и устройства
        # у правой и нижней границы листа не обнаруживались вовсе.
        if total <= tile:
            return [0]
        positions = list(range(0, total - tile + 1, step))
        if positions[-1] != total - tile:
            positions.append(total - tile)
        return positions

    def _is_blank(self, tile: np.ndarray) -> bool:
        # Чертёж — тёмные линии на белом фоне. Если тёмных пикселей почти нет,
        # запускать модель бессмысленно: проверка занимает миллисекунды
        # против секунды инференса.
        gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY) if tile.ndim == 3 else tile
        ink = int(np.count_nonzero(gray < 250))
        return ink <= max(1, int(gray.size * self.BLANK_INK_RATIO))

    @staticmethod
    def _overlap(a: DeviceBox, b: DeviceBox) -> Tuple[float, float]:
        # Возвращает (IoU, IoMin) — отношение пересечения к объединению
        # и к меньшей из площадей
        inter_w = min(a.x2, b.x2) - max(a.x1, b.x1)
        inter_h = min(a.y2, b.y2) - max(a.y1, b.y1)
        if inter_w <= 0 or inter_h <= 0:
            return 0.0, 0.0

        inter = inter_w * inter_h
        union = a.area + b.area - inter
        smaller = min(a.area, b.area)
        return (inter / union if union > 0 else 0.0,
                inter / smaller if smaller > 0 else 0.0)

    @classmethod
    def _merge_overlapping(cls, boxes: List[DeviceBox]) -> List[DeviceBox]:
        # Плитки идут внахлёст, поэтому одно устройство попадает в несколько
        # плиток и даёт слегка разные рамки.
        #
        # Рамки перебираются от самой уверенной к наименее уверенной, как
        # в обычном NMS. Раньше сортировка шла по площади — произвольный
        # критерий, смещённый в сторону раздутых рамок, потому что класс
        # и уверенность модели вообще не читались.
        if not boxes:
            return []

        ordered = sorted(boxes, key=lambda b: (b.confidence, b.area), reverse=True)
        kept: List[DeviceBox] = []

        for box in ordered:
            duplicate = False
            for other in kept:
                iou, iomin = cls._overlap(box, other)
                if iou >= cls.MERGE_IOU or iomin >= cls.MERGE_IOMIN:
                    duplicate = True
                    break
            if not duplicate:
                kept.append(box)

        return kept

    def detect_devices(self, png_path: str, on_progress=None,
                       should_stop=None) -> List[DeviceBox]:
        # on_progress(готово, всего) — для полосы прогресса в окне;
        # should_stop() -> bool — чтобы разметку можно было прервать.
        # Детекция занимает почти всё время разметки, поэтому и то и другое
        # имеет смысл спрашивать только здесь.
        self._load_model()

        print("🔍 Обнаружение устройств...")

        img = cv2.imread(png_path)
        if img is None:
            return []

        H, W = img.shape[:2]
        print(f"   Размер PNG: {W}x{H}")

        # Готовим плитки: пустые отбрасываем сразу
        tiles, offsets, blank = [], [], 0
        for y in self._tile_positions(H, self.tile_size, self.step):
            for x in self._tile_positions(W, self.tile_size, self.step):
                tile = img[y:y + self.tile_size, x:x + self.tile_size]
                if self._is_blank(tile):
                    blank += 1
                    continue
                tiles.append(tile)
                offsets.append((x, y))

        print(f"   Плиток: {len(tiles) + blank} (пустых пропущено: {blank})")

        raw_boxes: List[DeviceBox] = []
        class_names = self.model.names or {}

        if on_progress:
            on_progress(0, len(tiles))

        # Инференс пачками — меньше накладных расходов, чем по одной плитке
        for start in range(0, len(tiles), self.batch_size):
            # Прерывание проверяем между пачками: внутрь predict не залезть,
            # а пачка считается доли секунды
            if should_stop and should_stop():
                print("   Детекция прервана")
                return []

            batch = tiles[start:start + self.batch_size]
            extra = {"device": self.device} if self.device else {}
            results = self.model.predict(batch, conf=self.conf_threshold,
                                         imgsz=self.imgsz, verbose=False, **extra)

            if on_progress:
                on_progress(min(start + self.batch_size, len(tiles)), len(tiles))

            # strict: рассинхрон результатов и смещений сдвинул бы рамки
            # по всему листу, и заметить это можно было бы только глазами
            for result, (offset_x, offset_y) in zip(
                    results, offsets[start:start + self.batch_size], strict=True):
                if result.boxes is None:
                    continue

                coords = result.boxes.xyxy.cpu().numpy()
                # Класс и уверенность модель выдаёт вместе с координатами,
                # раньше они просто терялись
                classes = result.boxes.cls.cpu().numpy()
                scores = result.boxes.conf.cpu().numpy()

                for (x1, y1, x2, y2), cls_id, score in zip(coords, classes, scores, strict=True):
                    raw_boxes.append(DeviceBox(
                        x1=int(x1) + offset_x, y1=int(y1) + offset_y,
                        x2=int(x2) + offset_x, y2=int(y2) + offset_y,
                        cls_name=str(class_names.get(int(cls_id), int(cls_id))),
                        confidence=float(score)))

        device_boxes = self._merge_overlapping(raw_boxes)

        by_class = Counter(b.cls_name for b in device_boxes)
        print(f"   Найдено устройств: {len(device_boxes)} "
              f"(до объединения дублей: {len(raw_boxes)})")
        print(f"   По классам: {dict(by_class)}")
        if device_boxes:
            confidences = sorted(b.confidence for b in device_boxes)
            print(f"   Уверенность: медиана {confidences[len(confidences) // 2]:.2f}, "
                  f"минимум {confidences[0]:.2f}")

        return device_boxes


def _median_device_size(boxes) -> float:
    # Медианный размер устройства в пунктах. Записывается в SVG, чтобы
    # допуски геометрии можно было масштабировать под формат листа.
    if not boxes:
        return 0.0
    sizes = sorted((abs(b.x2 - b.x1) + abs(b.y2 - b.y1)) / 2 for b in boxes)
    return sizes[len(sizes) // 2]


def _attrs(marks: Dict[str, str]) -> str:
    # Атрибуты устройства для SVG-элемента
    return "".join(f' {key}="{value}"' for key, value in marks.items())


class DeviceLabeler:
    """Сопоставляет рамкам устройств подписи с чертежа.

    Раньше имя искалось первым попавшимся текстом в рамке ±20 пунктов, а затем
    ближайшим — но независимо для каждой рамки, без исключительности: одну и ту
    же метку могли забрать несколько соседних устройств. Здесь пары
    (рамка, метка) назначаются жадно по возрастанию расстояния, и каждая метка
    достаётся ровно одному устройству.
    """

    # Метка устройства: буквенный тип и номер (V12, LS1, FQT3, HDOG2)
    LABEL_PATTERN = re.compile(r'\b([A-Z]{1,4}\d+)\b')
    # Максимальное расстояние от центра рамки до метки, пункты
    MAX_LABEL_DISTANCE = 60.0
    # Во сколько раз ближе считается метка, попавшая внутрь рамки
    INSIDE_BONUS = 0.1
    # Во сколько раз дальше считается метка, чей тип противоречит классу модели
    CLASS_CONFLICT_PENALTY = 3.0

    # Во сколько раз ближе считается устройство, уже сопоставленное с Lua:
    # его имя выверено техобъектом, а не просто лежит рядом на чертеже
    MATCHED_BONUS = 0.2

    def __init__(self, device_boxes: List[DeviceBox],
                 labels: List[Tuple[float, float, str]],
                 max_distance: float = MAX_LABEL_DISTANCE,
                 matched_devices: List[Tuple[str, float, float]] | None = None):
        # matched_devices — уже сопоставленные устройства (полное_имя, x, y).
        # Разметка и сопоставление работали независимо: разметка искала подпись
        # в сырых текстах и для трети рамок не находила ничего, хотя
        # сопоставление к этому моменту уже знало полные имена.
        self.device_boxes = [b if isinstance(b, DeviceBox) else DeviceBox(*b)
                             for b in device_boxes]
        self.matched_devices = list(matched_devices or [])

        # Радиус поиска подписи привязан к размеру устройства: 60 пунктов
        # подобраны под A0, а на A3 это семь размеров устройства — метка
        # находилась бы у соседа
        median_size = _median_device_size(self.device_boxes)
        scale = max(0.25, min(4.0, median_size / 32.0)) if median_size else 1.0
        self.max_distance = max_distance * scale

        # Оставляем только тексты, похожие на обозначение устройства
        self.labels = []
        for x, y, text in labels:
            match = self.LABEL_PATTERN.search(text.upper())
            if match:
                self.labels.append((x, y, match.group(1)))

        self._names: Dict[int, str] = self._assign_labels()

    @staticmethod
    def _label_type(name: str) -> str:
        # Работает и с коротким именем (V12), и с полным (LA_TANK1V12)
        match = re.search(rf'{config.device_types_pattern()}\d+$', name.upper())
        return match.group(1) if match else ""

    def _label_sources(self) -> List[Tuple[float, float, str, bool]]:
        # Источники имён: выверенные сопоставлением устройства и сырые подписи.
        # Первые дают полное имя (LA_TANK1V1) вместо короткого (V1), которое
        # повторяется у каждого техобъекта и само по себе неоднозначно.
        sources = [(x, y, name, True) for name, x, y in self.matched_devices]
        sources += [(x, y, name, False) for x, y, name in self.labels]
        return sources

    def _assign_labels(self) -> Dict[int, str]:
        # Все допустимые пары (рамка, метка) с оценкой близости
        candidates = []
        sources = self._label_sources()

        for box_index, box in enumerate(self.device_boxes):
            cx, cy = box.center
            for label_index, (lx, ly, name, matched) in enumerate(sources):
                distance = ((lx - cx) ** 2 + (ly - cy) ** 2) ** 0.5
                if distance > self.max_distance * 2:
                    continue

                score = distance
                if box.x1 <= lx <= box.x2 and box.y1 <= ly <= box.y2:
                    score *= self.INSIDE_BONUS
                if matched:
                    score *= self.MATCHED_BONUS
                # Класс модели противоречит типу подписи — метка, скорее всего,
                # относится к соседнему устройству
                if config.device_type_matches_class(self._label_type(name), box.cls_name) is False:
                    score *= self.CLASS_CONFLICT_PENALTY

                if score <= self.max_distance:
                    candidates.append((score, box_index, label_index, name))

        # Жадно раздаём: сначала самые уверенные пары
        candidates.sort(key=lambda c: c[0])
        used_boxes, used_labels = set(), set()
        assigned: Dict[int, str] = {}

        for _, box_index, label_index, name in candidates:
            if box_index in used_boxes or label_index in used_labels:
                continue
            used_boxes.add(box_index)
            used_labels.add(label_index)
            assigned[id(self.device_boxes[box_index])] = name

        return assigned

    def name_for_box(self, box: DeviceBox) -> str:
        return self._names.get(id(box), "")

    def box_at(self, x: float, y: float, tolerance: float = 5.0) -> Optional[DeviceBox]:
        # Рамка устройства, содержащая точку
        for box in self.device_boxes:
            if (box.x1 - tolerance <= x <= box.x2 + tolerance and
                    box.y1 - tolerance <= y <= box.y2 + tolerance):
                return box
        return None

    def marks_at(self, x: float, y: float, tolerance: float = 5.0) -> Dict[str, str]:
        # Атрибуты устройства для точки: имя, класс модели и её уверенность.
        # Класс и уверенность нужны, чтобы потом сверить подпись с типом
        # устройства и не доверять слабым детекциям.
        box = self.box_at(x, y, tolerance)
        if box is None:
            return {}

        marks = {}
        name = self.name_for_box(box)
        if name:
            marks["data-device-name"] = name
        if box.cls_name:
            marks["data-device-class"] = box.cls_name
        if box.confidence:
            marks["data-device-conf"] = f"{box.confidence:.3f}"
        return marks

    def name_at(self, x: float, y: float, tolerance: float = 5.0) -> str:
        box = self.box_at(x, y, tolerance)
        return self.name_for_box(box) if box is not None else ""


class PDFToSVGConverter:
    def __init__(self, model_path: str | None = None, scale_factor: float = 1,
                 page_number: int = 0,
                 matched_devices: List[Tuple[str, float, float]] | None = None):
        model_path = model_path or str(config.YOLO_MODEL_PATH)
        self.model_path = model_path
        self.scale_factor = scale_factor
        self.page_number = page_number
        # Уже сопоставленные устройства (полное_имя, x, y) — приоритетный
        # источник имён при разметке
        self.matched_devices = list(matched_devices or [])
        self.detector = DeviceDetector(model_path)
        # DPI берётся из профиля: раньше здесь было зашито 200, а в GUI 300,
        # то есть два пути разметки работали в разном масштабе
        self.converter = PDFToPNGConverter(dpi=config.YOLO_DPI)
        self.line_segments: List[LineSegment] = []
        self.junction_points: List[JunctionPoint] = []
        self._next_line_id = 1

    def _sanitize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        return text

    def _scale_coordinate(self, value: float) -> float:
        return value * self.scale_factor

    def _find_junction_points(self) -> List[JunctionPoint]:
        # Точки сопряжения ищет общий модуль svg_geometry (пространственная сетка
        # вместо перебора всех пар «красная линия × синяя линия»)
        return find_junction_points(self.line_segments, tolerance=5.0, verbose=False)

    def _create_svg_content(self, pdf_path: str, device_rectangles_pdf: List[Tuple]) -> Tuple[
        Optional[str], List[JunctionPoint]]:
        try:
            pdf_document = fitz.open(pdf_path)
            page = pdf_document[self.page_number]

            pdf_rect = page.rect
            pdf_width = pdf_rect.width
            pdf_height = pdf_rect.height

            scaled_width = self._scale_coordinate(pdf_width)
            scaled_height = self._scale_coordinate(pdf_height)

            print(f"   Размер PDF: {pdf_width:.2f} x {pdf_height:.2f}")
            print(f"   Размер SVG (масштаб {self.scale_factor}): {scaled_width:.2f} x {scaled_height:.2f}")

            self.line_segments = []
            self.junction_points = []
            self._next_line_id = 1

            def point_in_device(x, y, rects, tolerance=5):
                for x1, y1, x2, y2 in rects:
                    if (x1 - tolerance <= x <= x2 + tolerance and
                            y1 - tolerance <= y <= y2 + tolerance):
                        return True
                return False

            def line_in_device(x1, y1, x2, y2, rects, tolerance=3):
                # Линия принадлежит устройству, если внутри его рамки лежит
                # больше половины её длины. Прежняя проверка смотрела только
                # на середину: труба, пересекающая устройство, красилась красной,
                # а линия устройства длиннее рамки оставалась синей.
                return any(
                    segment_box_overlap(x1, y1, x2, y2, rx1, ry1, rx2, ry2, tolerance)
                    >= DEVICE_OVERLAP_SHARE
                    for rx1, ry1, rx2, ry2 in rects)

            # Собираем текст
            print("   Сбор текстовых меток...")
            text_data = page.get_text("dict")
            text_mapping = {}

            for block in text_data["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text and text.strip() and span["size"] > 5:
                            bbox = span["bbox"]
                            x = bbox[0]
                            y = bbox[1]
                            text_clean = self._sanitize_text(text.strip())
                            if text_clean:
                                text_mapping[(x, y, text_clean)] = bbox

            # Определитель имён: ближайшая метка к рамке устройства
            labeler = DeviceLabeler(
                device_rectangles_pdf,
                [(x, y, text) for (x, y, text) in text_mapping],
                matched_devices=self.matched_devices)

            # Сколько элементов не удалось отрисовать: раньше их молча
            # пропускали, и потеря 59 из 1108 оставалась незамеченной
            failed_elements = 0

            svg_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg"',
                f'     width="{scaled_width:.2f}pt"',
                f'     height="{scaled_height:.2f}pt"',
                f'     viewBox="0 0 {scaled_width:.2f} {scaled_height:.2f}"',
                f'     data-device-count="{len(device_rectangles_pdf)}"',
                f'     data-device-size="{_median_device_size(device_rectangles_pdf):.2f}"',
                f'     data-device-named="{sum(1 for b in device_rectangles_pdf if labeler.name_for_box(b))}">',
                '  <rect width="100%" height="100%" fill="white"/>'
            ]

            # Извлекаем графику
            device_count = 0
            pipe_count = 0
            element_count = 0

            for element in iter_markup_elements(page, device_rectangles_pdf, labeler):
                try:
                    element_count += 1
                    if element.is_device:
                        device_count += 1
                    else:
                        pipe_count += 1

                    color = element.color
                    name = element.device_name
                    stroke = self._scale_coordinate(element.stroke_width)
                    marks = _attrs(element.marks)

                    if element.kind == "line":
                        x1, y1, x2, y2 = (self._scale_coordinate(v) for v in element.points)
                        self.line_segments.append(LineSegment(
                            id=self._next_line_id, x1=x1, y1=y1, x2=x2, y2=y2,
                            color=color, device_name=name))
                        self._next_line_id += 1
                        svg_lines.append(
                            f'  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"'
                            f' stroke="{color}" stroke-width="{stroke:.2f}"'
                            f' data-line-id="{self._next_line_id - 1}"' + marks + '/>')

                    elif element.kind == "rect":
                        x, y, w, h = (self._scale_coordinate(v) for v in element.points)
                        # Четыре стороны прямоугольника — отдельными сегментами
                        for sx1, sy1, sx2, sy2 in ((x, y, x + w, y),
                                                   (x, y + h, x + w, y + h),
                                                   (x, y, x, y + h),
                                                   (x + w, y, x + w, y + h)):
                            self.line_segments.append(LineSegment(
                                self._next_line_id, sx1, sy1, sx2, sy2, color,
                                device_name=name))
                            self._next_line_id += 1
                        svg_lines.append(
                            f'  <rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"'
                            f' fill="none" stroke="{color}" stroke-width="{stroke:.2f}"'
                            + marks + '/>')

                    else:  # кривая
                        p1, p2, p3, p4 = ((self._scale_coordinate(px), self._scale_coordinate(py))
                                          for px, py in element.points)
                        self.line_segments.append(LineSegment(
                            self._next_line_id, p1[0], p1[1], p4[0], p4[1], color,
                            device_name=name))
                        self._next_line_id += 1
                        svg_lines.append(
                            f'  <path d="M {p1[0]:.2f},{p1[1]:.2f} C {p2[0]:.2f},{p2[1]:.2f}'
                            f' {p3[0]:.2f},{p3[1]:.2f} {p4[0]:.2f},{p4[1]:.2f}" fill="none"'
                            f' stroke="{color}" stroke-width="{stroke:.2f}"'
                            f' data-line-id="{self._next_line_id - 1}"' + marks + '/>')

                except Exception as e:
                    # Молчаливый пропуск уже стоил 59 потерянных элементов
                    # из 1108: ошибка гасилась, счётчик выше считал их
                    # отрисованными, и разметка выглядела целой
                    failed_elements += 1
                    if failed_elements <= 3:
                        print(f"   ⚠️ элемент не отрисован: {type(e).__name__}: {e}")
                    continue

            if failed_elements:
                share = failed_elements * 100 // max(1, self._next_line_id)
                message = (f"не отрисовано элементов: {failed_elements} "
                           f"(~{share}% от разобранных)")
                if share >= MAX_FAILED_SHARE:
                    raise RuntimeError(f"Разметка неполная — {message}")
                print(f"   ⚠️ {message}")

            # Добавляем текст
            print("   Добавление текста...")
            text_count = 0

            for (x, y, text), bbox in text_mapping.items():
                if text and text.strip():
                    x_s = self._scale_coordinate(x)
                    y_s = self._scale_coordinate(y)
                    size_s = self._scale_coordinate(bbox[3] - bbox[1]) if len(bbox) > 3 else 10

                    is_near_device = point_in_device(x, y, device_rectangles_pdf, tolerance=15)
                    color = "red" if is_near_device else "blue"

                    svg_lines.append(
                        f'  <text x="{x_s:.2f}" y="{y_s:.2f}" fill="{color}" font-size="{size_s:.2f}">{text}</text>')
                    text_count += 1

            svg_lines.append('</svg>')

            pdf_document.close()

            self.junction_points = self._find_junction_points()

            print(f"   Сгенерировано: {element_count} примитивов, {text_count} текстов")
            print(f"   Красных: {device_count}, Синих: {pipe_count}")
            print(f"   Сегментов: {len(self.line_segments)}")
            print(f"   Точек сопряжения: {len(self.junction_points)}")

            return '\n'.join(svg_lines), self.junction_points

        except Exception as e:
            print(f"❌ Ошибка создания SVG: {e}")
            import traceback
            traceback.print_exc()
            return None, []

    def convert(self, pdf_path: str, output_svg_path: str | None = None) -> Tuple[Optional[str], List[JunctionPoint]]:
        if output_svg_path is None:
            output_svg_path = os.path.join(tempfile.gettempdir(), f"marked_{Path(pdf_path).stem}.svg")

        print("\n" + "=" * 60)
        print("🚀 НАЧАЛО РАЗМЕТКИ PDF")
        print(f"   Масштаб: {self.scale_factor}")
        print("=" * 60)

        # Результат разметки при тех же исходных данных не меняется,
        # а детекция стоит ~30 секунд на лист
        cache_key = markup_cache.build_key(
            pdf_path, self.page_number, self.model_path,
            generator="pdf_processor",
            params={"tile": self.detector.tile_size, "step": self.detector.step,
                    "conf": self.detector.conf_threshold,
                    "dpi": self.converter.dpi, "scale": self.scale_factor,
                    # Имена в разметке зависят от сопоставленных устройств,
                    # иначе из кэша отдавалась бы разметка с другими подписями
                    "matched": len(self.matched_devices)})

        cached = markup_cache.lookup(cache_key)
        cached_junctions = markup_cache.load_meta(cache_key) if cached else None
        if cached and cached_junctions is not None:
            print(f"♻️  Разметка взята из кэша: {cached}")
            # Точки сопряжения берём из кэша, а не пересчитываем по SVG:
            # при генерации они считаются по исходным примитивам, и повторный
            # разбор SVG дал бы другой результат
            self.junction_points = [JunctionPoint(**item) for item in cached_junctions]
            print(f"   Точек сопряжения: {len(self.junction_points)}")
            return cached, self.junction_points

        png_dir = tempfile.mkdtemp()
        png_paths = self.converter.convert(pdf_path, png_dir, self.page_number)

        if not png_paths:
            return None, []

        png_path = png_paths[0]
        device_rectangles_png = self.detector.detect_devices(png_path)

        pdf_document = fitz.open(pdf_path)
        page = pdf_document[self.page_number]
        pdf_rect = page.rect
        pdf_width = pdf_rect.width
        pdf_height = pdf_rect.height
        # Размер растра, в котором работала детекция. Раньше ради двух чисел
        # картинка 14034x9934 читалась с диска и распаковывалась второй раз;
        # преобразование прямоугольника страницы даёт тот же размер до пикселя
        zoom = self.converter.dpi / 72
        irect = (pdf_rect * fitz.Matrix(zoom, zoom)).irect
        W, H = irect.width, irect.height
        pdf_document.close()

        scale_x = pdf_width / W
        scale_y = pdf_height / H

        # scaled() сохраняет класс и уверенность, распаковка координат
        # по-прежнему работает через DeviceBox.__iter__
        device_rectangles_pdf = [box.scaled(scale_x, scale_y)
                                 for box in device_rectangles_png]

        svg_content, junction_points = self._create_svg_content(pdf_path, device_rectangles_pdf)

        if not svg_content:
            return None, []

        with open(output_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        markup_cache.store(cache_key, output_svg_path)
        markup_cache.store_meta(cache_key, [vars(jp) for jp in junction_points])

        print(f"✅ SVG сохранен: {output_svg_path}")
        return output_svg_path, junction_points


def save_xml_with_junctions(svg_path: str, output_xml_path: str, junction_points: List[JunctionPoint]) -> bool:
    # Сохраняет SVG и точки сопряжения в XML файл
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        root = ET.Element("PlantGeometry")
        root.set("version", "1.2")

        # Добавляем точки сопряжения
        junctions_elem = ET.SubElement(root, "JunctionPoints")
        junctions_elem.set("count", str(len(junction_points)))

        for jp in junction_points:
            jp_elem = ET.SubElement(junctions_elem, "JunctionPoint")
            jp_elem.set("x", f"{jp.x:.3f}")
            jp_elem.set("y", f"{jp.y:.3f}")
            jp_elem.set("red_line_id", str(jp.red_line_id))
            jp_elem.set("blue_line_id", str(jp.blue_line_id))
            if jp.red_device_name:
                jp_elem.set("red_device", jp.red_device_name)

        # Добавляем SVG
        svg_elem = ET.SubElement(root, "SVGContent")
        svg_elem.text = f"<![CDATA[{svg_content}]]>"

        # Форматируем
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

        with open(output_xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        print(f"✅ XML сохранен: {output_xml_path}")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        output_xml = sys.argv[2] if len(sys.argv) > 2 else "output.xml"

        converter = PDFToSVGConverter(scale_factor=1.25)
        svg_path, junction_points = converter.convert(pdf_file)

        if svg_path and junction_points:
            save_xml_with_junctions(svg_path, output_xml, junction_points)
            print(f"\n✅ Готово! Найдено {len(junction_points)} точек сопряжения")
        else:
            print("❌ Ошибка конвертации")
