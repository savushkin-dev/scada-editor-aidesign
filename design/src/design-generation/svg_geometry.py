# svg_geometry.py
# Общая работа с геометрией размеченного SVG.
#
# Модуль собран из одинакового кода, который раньше дублировался в
# xml_export.py и postgreSQL_export.py: определение системы координат,
# извлечение сегментов, поиск точек сопряжения и сборка трубопроводов.
#
# Точки сопряжения и подключённые устройства ищутся через пространственную
# сетку, а не полным перебором пар «красная линия × синяя линия».
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from itertools import pairwise
from dataclasses import dataclass, field, replace
from typing import Dict, Iterator, List, Optional, Tuple

import config

SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}

# Стандартные размеры страниц в пунктах (портретная ориентация)
PDF_SIZES = [
    (595, 842),    # A4
    (842, 1191),   # A3
    (1191, 1684),  # A2
    (1684, 2384),  # A1
    (2384, 3370),  # A0
    (612, 792),    # Letter
    (792, 1224),   # Legal
]

# Допуск сопряжения красной и синей линии, пункты
JUNCTION_TOLERANCE = 10.0
# Допуск «точка лежит на сегменте», пункты
ON_SEGMENT_TOLERANCE = 3.0
# Сегменты короче отбрасываются при сборке труб, пункты
MIN_PIPELINE_SEGMENT_LENGTH = 5.0
# Поля рамки чертежа, доля холста
FRAME_MARGIN_PERCENT = 3.0
# Какая доля длины линии должна лежать внутри рамки, чтобы линия
# считалась частью устройства, а не проходящей мимо трубой
DEVICE_OVERLAP_SHARE = 0.5

# Размер устройства, под который подобраны допуски выше (лист A0), пункты.
# Все допуски заданы в пунктах, поэтому на листе меньшего формата они
# относительно крупнее: на A3 медианная деталь устройства — 8.5 пт,
# а допуск связки 10 пт, то есть больше самой детали. Отсюда масштабирование.
REFERENCE_DEVICE_SIZE = 32.0


@dataclass
class LineSegment:
    id: int
    x1: float
    y1: float
    x2: float
    y2: float
    color: str  # 'red' — устройство, 'blue' — трубопровод
    stroke_width: float = 1.0
    device_name: str = ""
    # Класс и уверенность приходят от модели через атрибуты SVG
    device_class: str = ""
    device_confidence: float = 0.0
    # Заполняются только у набора для чертежа (см. extract_line_segments):
    # frame — отрезок лежит в полосе поля листа, source_id — номер сегмента
    # анализа, от которого он произошёл (0 — анализ его не видел)
    frame: bool = False
    source_id: int = 0
    # Ломаная кривой, если примитив изогнут. Анализ строится на хордах,
    # но обводка устройства в окне должна повторять сам рисунок: у круга
    # четыре хорды дают ромб, а не круг
    curve: Optional[List[Tuple[float, float]]] = None

    def get_endpoints(self) -> List[Tuple[float, float]]:
        return [(self.x1, self.y1), (self.x2, self.y2)]

    def length(self) -> float:
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)


@dataclass
class JunctionPoint:
    x: float
    y: float
    red_line_id: int
    blue_line_id: int
    red_device_name: str = ""
    confidence: float = 1.0


@dataclass
class Pipeline:
    id: int
    name: str
    segments: List[LineSegment] = field(default_factory=list)
    connected_devices: List[str] = field(default_factory=list)
    total_length: float = 0.0

    @property
    def segment_count(self) -> int:
        return len(self.segments)


class SpatialGrid:
    # Равномерная сетка для поиска объектов рядом с точкой.
    # Заменяет вложенные циклы: вместо сравнения всех пар проверяются
    # только объекты в соседних ячейках.

    def __init__(self, cell_size: float):
        self.cell_size = max(cell_size, 1e-6)
        self._cells: Dict[Tuple[int, int], list] = defaultdict(list)

    def _cell(self, x: float, y: float) -> Tuple[int, int]:
        return math.floor(x / self.cell_size), math.floor(y / self.cell_size)

    def add(self, x: float, y: float, item) -> None:
        self._cells[self._cell(x, y)].append(item)

    def near_point(self, x: float, y: float) -> Iterator:
        # Объекты из ячейки точки и восьми соседних
        cx, cy = self._cell(x, y)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield from self._cells.get((cx + dx, cy + dy), ())

    def near_box(self, min_x: float, min_y: float, max_x: float, max_y: float) -> Iterator:
        # Объекты во всех ячейках, пересекающих прямоугольник
        cx0, cy0 = self._cell(min_x, min_y)
        cx1, cy1 = self._cell(max_x, max_y)
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                yield from self._cells.get((cx, cy), ())


_PATH_TOKEN = re.compile(r'([MLCmlc])|(-?\d*\.?\d+)')

Point = Tuple[float, float]

# Разбиение кривой на ломаную: докуда дробить и сколькими точками мерить
# отклонение. Предел жёсткий — дробление удваивается, и без него крутая
# кривая с малым допуском съела бы сколько угодно элементов. На контрольном
# листе при допуске 1 пт ни одна кривая не потребовала больше четырёх делений
MAX_CURVE_STEPS = 32
CURVE_PROBES = 8

# Насколько ломаная вправе отступать от кривой, пункты PDF. Один пункт
# при символе устройства в 31 пт неразличим, а элементов добавляет вдвое
# меньше, чем полпункта
CURVE_TOLERANCE = 1.0

# С каким допуском концы отрезков считаются одной точкой при склейке
COLLINEAR_TOLERANCE = 0.05


def _path_points(path_data: str, with_controls: bool = False):
    # Опорные точки пути: начало и конец каждого участка.
    #
    # Кубическая кривая заменяется хордой (начало -> конец), как это делает
    # генератор SVG. Раньше здесь была регулярка вида '([ML])\\s*(x)\\s+(y)',
    # которая требовала пробел между координатами, а генератор пишет их через
    # запятую ('M 10.00,20.00 C ...') — из-за этого ни одна кривая не
    # разбиралась, и участки труб со скруглениями терялись вместе со связками.
    numbers: List[float] = []
    commands: List[Tuple[str, int]] = []  # (команда, индекс первого числа)

    for match in _PATH_TOKEN.finditer(path_data or ""):
        command, number = match.group(1), match.group(2)
        if command:
            commands.append((command.upper(), len(numbers)))
        else:
            numbers.append(float(number))

    points: List[Tuple[float, float]] = []
    controls: List[Optional[Tuple[Point, Point]]] = []
    for index, (command, start) in enumerate(commands):
        end = commands[index + 1][1] if index + 1 < len(commands) else len(numbers)
        args = numbers[start:end]

        if command in ("M", "L"):
            for i in range(0, len(args) - 1, 2):
                points.append((args[i], args[i + 1]))
                controls.append(None)
        elif command == "C":
            # Каждая кривая описывается шестью числами: две опорные точки
            # и конец. Опорные нужны, чтобы показать дугу дугой (_flatten_cubic)
            for i in range(0, len(args) - 5, 6):
                points.append((args[i + 4], args[i + 5]))
                controls.append(((args[i], args[i + 1]), (args[i + 2], args[i + 3])))

    return (points, controls) if with_controls else points


def _cubic_point(p0: Point, c1: Point, c2: Point, p3: Point, t: float) -> Point:
    u = 1.0 - t
    return (u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p3[1])


def _flatten_cubic(p0: Point, c1: Point, c2: Point, p3: Point,
                   tolerance: float) -> List[Point]:
    """Кубическая кривая ломаной, отклоняющейся от неё не больше допуска.

    Генератор разметки пишет скругления труб кривыми, а разбор до сих пор
    заменял каждую хордой «начало -> конец». Для анализа этого хватает,
    но редактор рисует ровно то, что пришло в файле: на контрольном
    листе 784 кривые, и хорда врёт на 3.27 пт в медиане и до 6.3 пт —
    при символе устройства в 31 пт срезанный угол видно.
    """
    steps = 1
    while steps < MAX_CURVE_STEPS:
        points = [_cubic_point(p0, c1, c2, p3, i / steps) for i in range(steps + 1)]
        worst = 0.0
        for i in range(steps):
            a, b = points[i], points[i + 1]
            length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            for j in range(1, CURVE_PROBES):
                x, y = _cubic_point(p0, c1, c2, p3, (i + j / CURVE_PROBES) / steps)
                worst = max(worst, abs((b[1] - a[1]) * x - (b[0] - a[0]) * y
                                       + b[0] * a[1] - b[1] * a[0]) / length)
        if worst <= tolerance:
            return points
        steps *= 2

    return [_cubic_point(p0, c1, c2, p3, i / steps) for i in range(steps + 1)]


def segment_box_overlap(x1: float, y1: float, x2: float, y2: float,
                        box_x1: float, box_y1: float, box_x2: float, box_y2: float,
                        tolerance: float = 0.0) -> float:
    # Доля длины отрезка, попавшая внутрь прямоугольника (отсечение Лианга-Барски).
    #
    # Нужна вместо проверки «середина отрезка внутри рамки»: длинная труба,
    # пересекающая устройство, серединой попасть внутрь может, а принадлежит
    # трубопроводу; и наоборот, линия устройства длиннее рамки серединой
    # выпадает наружу.
    min_x, max_x = min(box_x1, box_x2) - tolerance, max(box_x1, box_x2) + tolerance
    min_y, max_y = min(box_y1, box_y2) - tolerance, max(box_y1, box_y2) + tolerance

    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return 1.0 if (min_x <= x1 <= max_x and min_y <= y1 <= max_y) else 0.0

    t0, t1 = 0.0, 1.0
    for direction, start, low, high in ((dx, x1, min_x, max_x), (dy, y1, min_y, max_y)):
        if direction == 0:
            if start < low or start > high:
                return 0.0
            continue
        near = (low - start) / direction
        far = (high - start) / direction
        if near > far:
            near, far = far, near
        t0 = max(t0, near)
        t1 = min(t1, far)
        if t0 > t1:
            return 0.0

    return max(0.0, t1 - t0)


def parse_absolute_length(value: str) -> Optional[float]:
    # Разбирает длину SVG в абсолютное число.
    # Относительные величины ('100%') размером холста не являются — возвращаем None,
    # иначе '100.000%' превращается в размер 100 и проценты становятся сырыми пунктами.
    if not value:
        return None
    if '%' in value:
        return None
    match = re.search(r'-?[\d.]+', value)
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def _device_marks(elem: ET.Element) -> Tuple[str, str, float]:
    # Имя, класс и уверенность устройства из атрибутов элемента SVG
    try:
        confidence = float(elem.get('data-device-conf', 0) or 0)
    except (TypeError, ValueError):
        confidence = 0.0
    return (elem.get('data-device-name', ''),
            elem.get('data-device-class', ''),
            confidence)


def _canvas_size(svg_root: ET.Element) -> Tuple[Optional[float], Optional[float]]:
    # Размеры холста в собственных единицах SVG: viewBox важнее width/height
    viewBox = svg_root.get('viewBox', '')
    if viewBox:
        parts = viewBox.strip().split()
        if len(parts) == 4:
            try:
                return float(parts[2]), float(parts[3])
            except ValueError:
                pass

    return (parse_absolute_length(svg_root.get('width', '')),
            parse_absolute_length(svg_root.get('height', '')))


def detect_coordinate_system(svg_root: ET.Element,
                             pdf_size: Optional[Tuple[float, float]] = None) -> Tuple[str, float]:
    # Определяет систему координат SVG и масштаб относительно PDF пунктов.
    # pdf_size — размер страницы исходного PDF; если он известен, масштаб
    # вычисляется точно. Без него приходится подбирать: у всех ISO-форматов
    # одинаковое соотношение сторон, поэтому подходит несколько вариантов
    # и выбирается тот, чей масштаб ближе к 1.
    vb_width, vb_height = _canvas_size(svg_root)
    if not vb_width or not vb_height:
        return 'unknown', 1.0

    if pdf_size and pdf_size[0] and pdf_size[1]:
        scale = ((vb_width / pdf_size[0]) + (vb_height / pdf_size[1])) / 2
        if abs(scale - 1.0) < 0.02:
            return 'pdf_pts', 1.0
        return f'scaled_{scale:.4g}', scale

    best = None
    for pdf_w, pdf_h in PDF_SIZES:
        for page_w, page_h in ((pdf_w, pdf_h), (pdf_h, pdf_w)):  # портрет и альбом
            scale_w = vb_width / page_w
            scale_h = vb_height / page_h
            if abs(scale_w - scale_h) > 0.02 * max(scale_w, scale_h):
                continue
            scale = (scale_w + scale_h) / 2
            if not 0.1 <= scale <= 20:
                continue
            if best is None or abs(scale - 1.0) < abs(best - 1.0):
                best = scale

    if best is None:
        return 'unknown', 1.0
    if abs(best - 1.0) < 0.02:
        return 'pdf_pts', 1.0
    return f'scaled_{best:.4g}', best


def get_svg_dimensions(svg_root: ET.Element, scale: float = 1.0
                       ) -> Tuple[Optional[float], Optional[float]]:
    # Размеры холста, приведённые к PDF пунктам.
    # Возвращает (None, None), если определить их нельзя — тогда вызывающий код
    # обязан отказаться от процентных координат.
    width, height = _canvas_size(svg_root)
    if not width or not height:
        return None, None
    if scale and scale > 0:
        return width / scale, height / scale
    return width, height


def extract_line_segments(svg_root: ET.Element, scale: float = 1.0,
                          dimensions: Tuple[Optional[float], Optional[float]] = (None, None),
                          verbose: bool = True,
                          drawing: Optional[List[LineSegment]] = None,
                          curve_tolerance: float = CURVE_TOLERANCE) -> List[LineSegment]:
    """Сегменты листа в пунктах PDF: для анализа и, по просьбе, для чертежа.

    Возвращаемый набор — для анализа: из него выброшены отрезки, задевающие
    полосу поля листа. Отсев нужен геометрии: рамка чертежа и разлиновка
    штампа иначе лезут в точки сопряжения и в граф труб.

    У выгрузки задача другая — показать лист как есть. Прежний отсев
    выбрасывал отрезок, если **любой** его конец попал в поле, и вместе
    с рамкой уносил живую геометрию: на контрольном листе 73 отрезка
    из 252 отсеянных, 27 из них — красные контуры устройств. Отсюда
    и «линии местами обрываются» в редакторе.

    Если передать список `drawing`, он заполняется полным набором: ничего
    не выброшено, у отрезков полосы поля стоит `frame=True`, а `source_id`
    указывает на сегмент анализа. Один проход на оба набора — чтобы `line_id`
    в чертеже и в анализе означали одно и то же.

    Кривые в набор для чертежа уходят ломаной с допуском `curve_tolerance`,
    а в анализ по-прежнему хордой: трубы и точки сопряжения построены
    на хордах, а рисовать надо дугу.
    """
    svg_width, svg_height = dimensions
    segments: List[LineSegment] = []
    next_id = 1
    total = filtered = 0

    def normalize(value: float) -> float:
        return value / scale if scale and scale > 0 else value

    if svg_width and svg_height:
        min_x = svg_width * FRAME_MARGIN_PERCENT / 100.0
        max_x = svg_width * (100.0 - FRAME_MARGIN_PERCENT) / 100.0
        min_y = svg_height * FRAME_MARGIN_PERCENT / 100.0
        max_y = svg_height * (100.0 - FRAME_MARGIN_PERCENT) / 100.0
    else:
        min_x = min_y = float('-inf')
        max_x = max_y = float('inf')
        if verbose:
            print("📏 Размеры SVG неизвестны — фильтрация рамки отключена")

    def is_frame(x1: float, y1: float, x2: float, y2: float) -> bool:
        # Мера для анализа: достаточно, чтобы конец задел полосу поля.
        # Строго, зато рамка гарантированно не попадёт в трубы
        return (x1 < min_x or x1 > max_x or x2 < min_x or x2 > max_x or
                y1 < min_y or y1 > max_y or y2 < min_y or y2 > max_y)

    def in_frame_band(x1: float, y1: float, x2: float, y2: float) -> bool:
        # Мера для чертежа: отрезок должен лежать в полосе поля целиком.
        # Отрезок, начатый внутри листа, — это чертёж, каким бы длинным он
        # ни был: на контрольном листе таких 73 из 252 отсеянных анализом
        return (max(x1, x2) < min_x or min(x1, x2) > max_x or
                max(y1, y2) < min_y or min(y1, y2) > max_y)

    def emit(x1: float, y1: float, x2: float, y2: float, color: str,
             stroke_width: float, name: str = "", cls_name: str = "",
             conf: float = 0.0, curve: Optional[List[Point]] = None):
        # Отсев рамки касается только набора для анализа; в чертёж отрезок
        # уходит всегда, помеченным. Кривая уходит в анализ хордой, а в чертёж
        # ломаной: анализ на хордах и построен, а рисовать надо дугу
        nonlocal next_id, filtered
        source_id = 0
        if is_frame(x1, y1, x2, y2):
            filtered += 1
        else:
            source_id = next_id
            next_id += 1
            segments.append(LineSegment(
                id=source_id, x1=x1, y1=y1, x2=x2, y2=y2, color=color,
                stroke_width=stroke_width, device_name=name,
                device_class=cls_name, device_confidence=conf, curve=curve))

        if drawing is None:
            return

        pieces = ([(curve[i], curve[i + 1]) for i in range(len(curve) - 1)]
                  if curve else [((x1, y1), (x2, y2))])
        for (ax, ay), (bx, by) in pieces:
            # Вырожденный примитив есть и в самом PDF: для анализа он
            # безобиден, а на холсте это элемент-точка, который нельзя
            # ни увидеть, ни взять
            if ax == bx and ay == by:
                continue
            drawing.append(LineSegment(
                id=len(drawing) + 1, x1=ax, y1=ay, x2=bx, y2=by, color=color,
                stroke_width=stroke_width, device_name=name,
                device_class=cls_name, device_confidence=conf,
                frame=in_frame_band(ax, ay, bx, by), source_id=source_id))

    for elem in svg_root.findall('.//svg:line', namespaces=SVG_NS):
        total += 1
        try:
            x1 = normalize(float(elem.get('x1', 0)))
            y1 = normalize(float(elem.get('y1', 0)))
            x2 = normalize(float(elem.get('x2', 0)))
            y2 = normalize(float(elem.get('y2', 0)))
        except (ValueError, TypeError):
            continue

        stroke = elem.get('stroke', 'blue')
        try:
            stroke_width = float(elem.get('stroke-width', 1.0))
        except (ValueError, TypeError):
            stroke_width = 1.0

        name, cls_name, conf = _device_marks(elem)
        emit(x1, y1, x2, y2, 'red' if stroke.lower() == 'red' else 'blue',
             stroke_width, name, cls_name, conf)

    # Прямоугольники: генератор пишет их как <rect>, а внутри они те же
    # четыре линии. Без разбора терялись контуры устройств, нарисованных
    # прямоугольником — вместе с их связками и геометрией.
    for elem in svg_root.findall('.//svg:rect', namespaces=SVG_NS):
        total += 1
        try:
            x = normalize(float(elem.get('x', 0)))
            y = normalize(float(elem.get('y', 0)))
            width = normalize(float(elem.get('width', 0)))
            height = normalize(float(elem.get('height', 0)))
        except (ValueError, TypeError):
            continue

        # Белая подложка на весь холст — не геометрия
        if width <= 0 or height <= 0:
            continue

        stroke = elem.get('stroke')
        if not stroke or stroke.lower() == 'none':
            continue

        try:
            stroke_width = float(elem.get('stroke-width', 1.0))
        except (ValueError, TypeError):
            stroke_width = 1.0

        color = 'red' if stroke.lower() == 'red' else 'blue'
        name, cls_name, conf = _device_marks(elem)

        for x1, y1, x2, y2 in ((x, y, x + width, y),
                               (x, y + height, x + width, y + height),
                               (x, y, x, y + height),
                               (x + width, y, x + width, y + height)):
            emit(x1, y1, x2, y2, color, stroke_width, name, cls_name, conf)

    for elem in svg_root.findall('.//svg:path', namespaces=SVG_NS):
        total += 1
        try:
            stroke = elem.get('stroke', 'blue')
            color = 'red' if stroke.lower() == 'red' else 'blue'
            try:
                stroke_width = float(elem.get('stroke-width', 1.0))
            except (ValueError, TypeError):
                stroke_width = 1.0

            points, controls = _path_points(elem.get('d', ''), with_controls=True)
            # Имя устройства генератор пишет и на кривых, а разбор его здесь
            # не читал: круг сенсора нарисован четырьмя кривыми Безье, и все
            # четыре уходили безымянными. Для устройства с круглым символом
            # это значило «геометрии нет вовсе» — на листе 13 моцареллы так
            # теряли всё у LS1, LS2, LT1, PT1, QT1, TE1 и NY1, а у FQT1, M1,
            # M2, M3 и PC1 оставались одни прямые отводы
            name, cls_name, conf = _device_marks(elem)

            for i in range(len(points) - 1):
                x1 = normalize(points[i][0])
                y1 = normalize(points[i][1])
                x2 = normalize(points[i + 1][0])
                y2 = normalize(points[i + 1][1])

                curve = None
                bend = controls[i + 1] if i + 1 < len(controls) else None
                if bend and curve_tolerance > 0:
                    c1 = (normalize(bend[0][0]), normalize(bend[0][1]))
                    c2 = (normalize(bend[1][0]), normalize(bend[1][1]))
                    curve = _flatten_cubic((x1, y1), c1, c2, (x2, y2),
                                           curve_tolerance)

                emit(x1, y1, x2, y2, color, stroke_width, name, cls_name, conf,
                     curve=curve)
        except (ValueError, TypeError, AttributeError):
            continue

    if verbose:
        red = sum(1 for s in segments if s.color == 'red')
        print(f"   Линий в SVG: {total}, отфильтровано рамки: {filtered}, "
              f"оставлено: {len(segments)} (красных: {red}, синих: {len(segments) - red})")
        if drawing is not None:
            print(f"   Для чертежа отрезков: {len(drawing)}, "
                  f"из них в полосе поля: {sum(1 for s in drawing if s.frame)}")

    return segments


@dataclass
class SheetText:
    # Надпись самого чертежа: обозначение Eplan, номер позиции, штамп листа.
    #
    # Разметка их рисует (`<text>` в SVG), а разбор до сих пор брал из неё
    # только линии — до потребителя надписи не доезжали вовсе, хотя без них
    # схема безымянная.
    x: float
    y: float
    text: str
    color: str = "blue"       # 'red' — надпись внутри рамки устройства
    font_size: float = 0.0


def extract_texts(svg_root: ET.Element, scale: float = 1.0,
                  verbose: bool = True) -> List[SheetText]:
    # Извлекает надписи из <text>, приводя координаты к пунктам PDF.
    #
    # Рамку чертежа здесь не отсекаем, в отличие от линий: в её полосе стоит
    # штамп листа, а он — содержательная надпись, а не разлиновка.
    texts: List[SheetText] = []

    def normalize(value: float) -> float:
        return value / scale if scale and scale > 0 else value

    for elem in svg_root.findall('.//svg:text', namespaces=SVG_NS):
        content = (elem.text or "").strip()
        if not content:
            continue
        try:
            x = normalize(float(elem.get('x', 0)))
            y = normalize(float(elem.get('y', 0)))
        except (ValueError, TypeError):
            continue

        try:
            size = normalize(float(elem.get('font-size', 0)))
        except (ValueError, TypeError):
            size = 0.0

        texts.append(SheetText(x=x, y=y, text=content,
                               color=elem.get('fill', 'blue'), font_size=size))

    if verbose:
        print(f"   Надписей в SVG: {len(texts)}")

    return texts


def merge_collinear(segments: List[LineSegment],
                    tolerance: float = COLLINEAR_TOLERANCE,
                    verbose: bool = True) -> List[LineSegment]:
    """Склеивает цепочки коллинеарных отрезков в один.

    Eplan рисует чертёж короткими штрихами: на контрольном листе медиана
    длины отрезка — 10 пунктов, а клетка сетки редактора 20,
    и отрезок короче клетки там схлопывается в точку и пропадает с холста.
    Это одна из причин «линии местами обрываются».

    Склеиваются только соседи, у которых общий конец принадлежит ровно им
    двоим: на развилке вершина сохраняется, иначе схема потеряет узлы,
    за которые её потом тянут руками.
    """
    if not segments:
        return []

    def node(x: float, y: float) -> Tuple[int, int]:
        return (round(x / tolerance), round(y / tolerance))

    def style(seg: LineSegment) -> Tuple:
        return (seg.color, round(seg.stroke_width, 3), seg.device_name, seg.frame)

    at: Dict[Tuple[int, int], List[LineSegment]] = defaultdict(list)
    for seg in segments:
        at[node(seg.x1, seg.y1)].append(seg)
        at[node(seg.x2, seg.y2)].append(seg)

    def direction(seg: LineSegment) -> Tuple[float, float]:
        length = seg.length() or 1.0
        return ((seg.x2 - seg.x1) / length, (seg.y2 - seg.y1) / length)

    def next_in_chain(seg: LineSegment, x: float, y: float) -> Optional[LineSegment]:
        # Продолжение есть, если в узле сходятся ровно два отрезка одной
        # породы и второй лежит на той же прямой. Считаем только свою породу:
        # чертёж пересекается сам с собой, и трубу нельзя обрывать только
        # потому, что её задел контур устройства
        kin = [s for s in at[node(x, y)] if style(s) == style(seg)]
        if len(kin) != 2:
            return None
        other = kin[0] if kin[1] is seg else kin[1]
        if other is seg:
            return None
        dx1, dy1 = direction(seg)
        dx2, dy2 = direction(other)
        return other if abs(dx1 * dy2 - dy1 * dx2) < 1e-3 else None

    merged: List[LineSegment] = []
    seen: set = set()

    for seg in segments:
        if id(seg) in seen:
            continue

        chain = [seg]
        seen.add(id(seg))

        # Разматываем цепочку в обе стороны от исходного отрезка
        for forward in (True, False):
            current = seg
            x, y = (seg.x2, seg.y2) if forward else (seg.x1, seg.y1)
            while True:
                nxt = next_in_chain(current, x, y)
                if nxt is None or id(nxt) in seen:
                    break
                seen.add(id(nxt))
                chain.append(nxt)
                if node(nxt.x1, nxt.y1) == node(x, y):
                    x, y = nxt.x2, nxt.y2
                else:
                    x, y = nxt.x1, nxt.y1
                current = nxt

        if len(chain) == 1:
            merged.append(seg)
            continue

        # Концы цепочки — две самые далёкие друг от друга точки
        points = [(s.x1, s.y1) for s in chain] + [(s.x2, s.y2) for s in chain]
        start, end = max(((a, b) for a in points for b in points),
                         key=lambda pair: math.hypot(pair[1][0] - pair[0][0],
                                                     pair[1][1] - pair[0][1]))
        merged.append(replace(seg, x1=start[0], y1=start[1], x2=end[0], y2=end[1]))

    if verbose and len(merged) != len(segments):
        print(f"   Склеено коллинеарных: {len(segments)} -> {len(merged)}")

    return merged


def find_junction_points(segments: List[LineSegment],
                         tolerance: float = JUNCTION_TOLERANCE,
                         verbose: bool = True,
                         scale: float = 1.0) -> List[JunctionPoint]:
    # Точки сопряжения: конец красной линии рядом с концом синей.
    # На каждую пару (красная, синяя) приходится не больше одной точки.
    tolerance *= scale
    red_lines = [s for s in segments if s.color == 'red']
    blue_lines = [s for s in segments if s.color == 'blue']

    if verbose:
        print(f"   Красных линий: {len(red_lines)}, синих линий: {len(blue_lines)}")

    if not red_lines or not blue_lines:
        return []

    # Концы синих линий раскладываем по сетке с ячейкой в размер допуска —
    # тогда для конца красной линии достаточно проверить 9 ячеек
    grid = SpatialGrid(tolerance)
    for blue in blue_lines:
        for point in blue.get_endpoints():
            grid.add(point[0], point[1], blue)

    junction_points: List[JunctionPoint] = []

    for red in red_lines:
        red_endpoints = red.get_endpoints()

        # Кандидаты рядом с любым из концов красной линии
        candidates: Dict[int, LineSegment] = {}
        for rx, ry in red_endpoints:
            for blue in grid.near_point(rx, ry):
                candidates[blue.id] = blue

        # Порядок по id повторяет прежний перебор списка синих линий
        for blue_id in sorted(candidates):
            blue = candidates[blue_id]
            found = None
            for rx, ry in red_endpoints:
                for bx, by in blue.get_endpoints():
                    if math.hypot(rx - bx, ry - by) <= tolerance:
                        found = ((rx + bx) / 2, (ry + by) / 2)
                        break
                if found:
                    break

            if found:
                junction_points.append(JunctionPoint(
                    x=found[0], y=found[1],
                    red_line_id=red.id, blue_line_id=blue.id,
                    red_device_name=red.device_name))

    if verbose:
        print(f"   Найдено точек сопряжения: {len(junction_points)}")

    return junction_points


def resolve_device_names(junction_points: List[JunctionPoint],
                         devices: List[Tuple[str, str, float, float]],
                         max_distance: float = 150.0,
                         verbose: bool = True, scale: float = 1.0) -> int:
    # Заменяет короткие имена в связках на полные имена из Lua.
    #
    # В SVG подпись устройства короткая ('V1', 'LS1') и на схеме повторяется
    # у каждого техобъекта, поэтому сама по себе она связь не идентифицирует.
    # Здесь короткое имя сопоставляется с ближайшим распознанным устройством,
    # у которого такая же подпись, и подставляется его полное имя.
    #
    # devices: список (полное_имя, короткое_имя, x, y)
    max_distance *= scale
    if not junction_points or not devices:
        return 0

    by_short: Dict[str, List[Tuple[str, float, float]]] = defaultdict(list)
    for full_name, short_name, x, y in devices:
        if short_name:
            by_short[short_name.upper()].append((full_name, x, y))

    resolved = 0
    for junction in junction_points:
        short = (junction.red_device_name or "").upper()
        candidates = by_short.get(short)
        if not candidates:
            continue

        best_name, best_distance = None, max_distance
        for full_name, x, y in candidates:
            distance = math.hypot(junction.x - x, junction.y - y)
            if distance < best_distance:
                best_name, best_distance = full_name, distance

        if best_name:
            junction.red_device_name = best_name
            resolved += 1

    if verbose:
        print(f"   Связок с полным именем устройства: {resolved} из {len(junction_points)}")

    return resolved


@dataclass
class DeviceCenter:
    # Положение устройства, собранное из красных сегментов одной подписи
    name: str
    x: float
    y: float
    cls_name: str = ""
    confidence: float = 0.0
    # Габарит кластера: нужен выгрузке, которой рисовать сам символ,
    # а не точку. Сопоставлению хватает центра, поэтому по умолчанию нули
    width: float = 0.0
    height: float = 0.0
    # Сами линии символа. Выгрузка собирает из них цельный объект: устройство
    # в редакторе должно быть одной фигурой со всеми своими
    # данными, а не россыпью отрезков, среди которых ничего не выбрать
    segments: List["LineSegment"] = field(default_factory=list)


def device_centers(segments: List[LineSegment],
                   cluster_radius: float = 60.0,
                   scale: float = 1.0) -> List[DeviceCenter]:
    # Центры самих устройств, собранные из красных сегментов с именем.
    #
    # Красные сегменты — это линии внутри рамки устройства, размеченной YOLO.
    # Сегменты с одинаковой подписью, лежащие рядом, объединяются в кластер;
    # центр его габаритного прямоугольника и есть положение устройства.
    # Одинаковая подпись повторяется у разных техобъектов, поэтому близость
    # обязательна — иначе V1 всех танков склеится в один кластер.
    cluster_radius *= scale
    named = [s for s in segments if s.color == 'red' and s.device_name]
    if not named:
        return []

    by_name: Dict[str, List[LineSegment]] = defaultdict(list)
    for segment in named:
        by_name[segment.device_name].append(segment)

    centers: List[DeviceCenter] = []

    for name, group in by_name.items():
        grid = SpatialGrid(cluster_radius)
        for segment in group:
            grid.add((segment.x1 + segment.x2) / 2, (segment.y1 + segment.y2) / 2, segment)

        unvisited = {s.id: s for s in group}
        while unvisited:
            seed = unvisited.pop(next(iter(unvisited)))
            cluster = [seed]
            queue = deque([seed])

            while queue:
                current = queue.popleft()
                cx = (current.x1 + current.x2) / 2
                cy = (current.y1 + current.y2) / 2
                for neighbour in grid.near_point(cx, cy):
                    if neighbour.id in unvisited:
                        del unvisited[neighbour.id]
                        cluster.append(neighbour)
                        queue.append(neighbour)

            xs = [v for s in cluster for v in (s.x1, s.x2)]
            ys = [v for s in cluster for v in (s.y1, s.y2)]

            # Класс и уверенность берём у самого уверенного сегмента кластера
            best = max(cluster, key=lambda s: s.device_confidence)
            centers.append(DeviceCenter(
                name=name,
                x=(min(xs) + max(xs)) / 2,
                y=(min(ys) + max(ys)) / 2,
                cls_name=best.device_class,
                confidence=best.device_confidence,
                width=max(xs) - min(xs),
                height=max(ys) - min(ys),
                segments=cluster))

    return centers


def _local_shape(center: DeviceCenter) -> List[Tuple[float, float, float, float]]:
    """Линии символа устройства относительно его центра.

    Изогнутый примитив разворачивается в свою ломаную: анализ работает
    на хордах, но обводка в окне должна повторять рисунок — у круга
    четыре хорды дали бы ромб.
    """
    shape: List[Tuple[float, float, float, float]] = []
    for segment in center.segments:
        points = segment.curve or [(segment.x1, segment.y1), (segment.x2, segment.y2)]
        for (ax, ay), (bx, by) in pairwise(points):
            shape.append((ax - center.x, ay - center.y,
                          bx - center.x, by - center.y))
    return shape


def snap_devices_to_geometry(matches, centers: List[DeviceCenter],
                             max_distance: float = 120.0, verbose: bool = True,
                             scale: float = 1.0) -> Dict[str, int]:
    # Привязывает устройство к его геометрии: сдвигает координату с центра
    # подписи на центр самого устройства и переносит на устройство класс
    # и уверенность модели.
    #
    # match.coordinates приходят от текстовой метки, которая нарисована рядом
    # с устройством, а не на нём. Для отрисовки мнемосхемы нужнее геометрия.
    max_distance *= scale
    stats = {"moved": 0, "class_agree": 0, "class_conflict": 0, "no_geometry": 0}
    if not matches or not centers:
        return stats

    by_name: Dict[str, List[DeviceCenter]] = defaultdict(list)
    for center in centers:
        by_name[center.name.upper()].append(center)

    total_shift = 0.0

    for match in matches:
        # Сначала по полному имени: разметка получает имена от сопоставления
        # и подписывает геометрию полным именем (LA_TANK1V1), а не коротким.
        # Короткое остаётся запасным вариантом для рамок, до которых
        # сопоставление не дотянулось.
        candidates = (by_name.get((match.lua_name or "").upper())
                      or by_name.get((match.pdf_name or "").upper()))
        if not candidates:
            stats["no_geometry"] += 1
            continue

        x0, y0 = match.coordinates
        best, best_distance = None, max_distance
        for center in candidates:
            distance = math.hypot(center.x - x0, center.y - y0)
            if distance < best_distance:
                best, best_distance = center, distance

        if best is None:
            stats["no_geometry"] += 1
            continue

        match.coordinates = (best.x, best.y)
        # Габарит кластера — по нему окно ловит курсор на устройстве,
        # а сами линии символа — по ним оно его обводит. И то, и другое
        # в выгрузки не уходит: это поля модели, а не extra_data
        match.view_size = (best.width, best.height)
        match.view_shape = _local_shape(best)
        stats["moved"] += 1
        total_shift += best_distance

        # Уверенность до сих пор была зашитой единицей — ставим настоящую
        if best.confidence:
            match.confidence = best.confidence
        if best.cls_name:
            match.extra_data["detected_class"] = best.cls_name
            agrees = config.device_type_matches_class(match.device_type, best.cls_name)
            if agrees is True:
                stats["class_agree"] += 1
            elif agrees is False:
                stats["class_conflict"] += 1
                match.extra_data["class_conflict"] = "true"

    if verbose and stats["moved"]:
        print(f"   Уточнено положений устройств: {stats['moved']} из {len(matches)}, "
              f"средний сдвиг {total_shift / stats['moved']:.1f} пт")
        if stats["class_agree"] or stats["class_conflict"]:
            print(f"   Класс модели согласуется с подписью: {stats['class_agree']}, "
                  f"противоречит: {stats['class_conflict']}")

    return stats


def tolerance_scale(svg_root: ET.Element) -> float:
    # Во сколько раз допуски нужно изменить для этого листа.
    #
    # Генератор записывает в корень SVG медианный размер устройства в пунктах.
    # Допуски подбирались на A0, где он около 32 пт; на A3 устройства втрое
    # мельче, и те же абсолютные пункты начинают склеивать соседние объекты.
    try:
        size = float(svg_root.get('data-device-size', ''))
    except (TypeError, ValueError):
        return 1.0

    if size <= 0:
        return 1.0
    # Ограничиваем разумными пределами, чтобы странная разметка
    # не развалила геометрию
    return max(0.25, min(4.0, size / REFERENCE_DEVICE_SIZE))


def detected_device_count(svg_root: ET.Element) -> Optional[int]:
    # Сколько устройств нашла модель — записано генератором в корень SVG
    try:
        return int(svg_root.get('data-device-count', ''))
    except (TypeError, ValueError):
        return None


def named_device_count(svg_root: ET.Element) -> Optional[int]:
    # Сколько рамок получило имя. Раньше вместо этого показывалось число
    # кластеров геометрии — оно меньше и с числом устройств не совпадает,
    # из-за чего отчёт создавал впечатление десятков «неопознанных» устройств.
    try:
        return int(svg_root.get('data-device-named', ''))
    except (TypeError, ValueError):
        return None


@dataclass
class Connection:
    # Трубопровод, соединяющий устройства.
    #
    # Точки сопряжения и трубы до сих пор жили порознь: было известно, что
    # труба чего-то касается, но не то, что она соединяет. Для мнемосхемы
    # нужна именно связность.
    pipeline_id: int
    pipeline_name: str
    devices: List[str]
    length: float
    segment_count: int


def build_connection_graph(pipelines: List[Pipeline]) -> Dict:
    # Граф связности: устройства — узлы, трубопроводы — рёбра.
    #
    # Труба с двумя устройствами — обычное соединение, с тремя и более —
    # коллектор. Пары не раскладываем: у коллектора связь общая, и разбиение
    # на пары исказило бы схему.
    connections: List[Connection] = []
    neighbours: Dict[str, set] = defaultdict(set)
    degree: Dict[str, int] = defaultdict(int)

    for pipeline in pipelines:
        devices = sorted(set(pipeline.connected_devices))
        if not devices:
            continue

        connections.append(Connection(
            pipeline_id=pipeline.id,
            pipeline_name=pipeline.name,
            devices=devices,
            length=pipeline.total_length,
            segment_count=pipeline.segment_count))

        for device in devices:
            degree[device] += 1
            neighbours[device].update(d for d in devices if d != device)

    linking = [c for c in connections if len(c.devices) >= 2]
    manifolds = [c for c in connections if len(c.devices) >= 3]

    return {
        "connections": connections,
        "linking": len(linking),
        "manifolds": len(manifolds),
        "dead_ends": len(connections) - len(linking),
        "devices": sorted(degree),
        "degree": dict(degree),
        "neighbours": {name: sorted(items) for name, items in neighbours.items()},
    }


def markup_quality_report(segments: List[LineSegment],
                          junction_points: List[JunctionPoint],
                          pipelines: List[Pipeline],
                          detected_devices: Optional[int] = None,
                          named_devices: Optional[int] = None) -> Dict:
    # Показатели качества разметки. Нужны, чтобы её ухудшение было видно числом:
    # регрессию, при которой из разметки пропали все символы устройств, заметил
    # только человек глазами, а все числовые проверки её пропустили.
    red = [s for s in segments if s.color == 'red']
    blue = [s for s in segments if s.color == 'blue']
    centers = device_centers(segments)

    named_centers = [c for c in centers if c.name]
    confidences = sorted(c.confidence for c in centers if c.confidence)

    classes: Dict[str, int] = defaultdict(int)
    for center in centers:
        if center.cls_name:
            classes[center.cls_name] += 1

    # Устройства, к которым не подходит ни одна труба: либо ложная детекция,
    # либо потерянная связь
    connected_names = {jp.red_device_name for jp in junction_points if jp.red_device_name}
    isolated = sorted({c.name for c in named_centers if c.name not in connected_names})

    pipelines_with_devices = [p for p in pipelines if p.connected_devices]

    return {
        "detected_devices": detected_devices,
        "named_devices": named_devices,
        "segments_total": len(segments),
        "segments_red": len(red),
        "segments_blue": len(blue),
        "devices": len(centers),
        "devices_named": len(named_centers),
        "device_classes": dict(classes),
        "confidence_median": confidences[len(confidences) // 2] if confidences else 0.0,
        "confidence_min": confidences[0] if confidences else 0.0,
        "confidence_low": sum(1 for c in confidences if c < 0.5),
        "junctions": len(junction_points),
        "junctions_named": sum(1 for jp in junction_points if jp.red_device_name),
        "pipelines": len(pipelines),
        "pipelines_with_devices": len(pipelines_with_devices),
        "isolated_devices": isolated,
    }


def format_markup_report(report: Dict, limit: int = 10) -> str:
    lines = [
        "КАЧЕСТВО РАЗМЕТКИ",
        "=" * 60,
        f"Сегментов: {report['segments_total']} "
        f"(устройства {report['segments_red']}, трубопроводы {report['segments_blue']})",
        (f"Устройств найдено моделью: {report['detected_devices']}, "
         f"из них подписано: {report['named_devices']}"
         if report.get("named_devices") is not None
         else f"Устройств найдено моделью: {report.get('detected_devices', '—')}"),
        f"Кластеров геометрии с именем: {report['devices_named']} "
        f"(кластер — сегменты одного имени, лежащие рядом; "
        f"с числом устройств не совпадает)",
        f"По классам модели: {report['device_classes'] or '—'}",
        f"Уверенность: медиана {report['confidence_median']:.2f}, "
        f"минимум {report['confidence_min']:.2f}, ниже 0.5: {report['confidence_low']}",
        f"Связок: {report['junctions']}, с именем устройства: {report['junctions_named']}",
        f"Трубопроводов: {report['pipelines']}, "
        f"с подключёнными устройствами: {report['pipelines_with_devices']}",
        "",
        f"Устройства без единой связки: {len(report['isolated_devices'])}",
        "   (либо ложная детекция, либо потерянная труба)",
    ]
    for name in report["isolated_devices"][:limit]:
        lines.append(f"   {name}")
    if len(report["isolated_devices"]) > limit:
        lines.append(f"   ... ещё {len(report['isolated_devices']) - limit}")

    return "\n".join(lines)


def _distance_point_to_segment(px: float, py: float, seg: LineSegment) -> float:
    dx = seg.x2 - seg.x1
    dy = seg.y2 - seg.y1
    if dx == 0 and dy == 0:
        return math.hypot(px - seg.x1, py - seg.y1)
    t = ((px - seg.x1) * dx + (py - seg.y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (seg.x1 + t * dx), py - (seg.y1 + t * dy))


def is_point_on_segment(x: float, y: float, seg: LineSegment,
                        tolerance: float = ON_SEGMENT_TOLERANCE) -> bool:
    return _distance_point_to_segment(x, y, seg) <= tolerance


def _devices_by_segment(segments: List[LineSegment],
                        junction_points: List[JunctionPoint],
                        tolerance: float = ON_SEGMENT_TOLERANCE) -> Dict[int, set]:
    # Для каждого сегмента — устройства, привязанные к нему точками сопряжения.
    # Раньше на каждый сегмент перебирались все точки сопряжения
    # (сегменты × точки операций); теперь точки берутся из сетки по bbox сегмента.
    result: Dict[int, set] = defaultdict(set)
    if not junction_points:
        return result

    named_points = [jp for jp in junction_points if jp.red_device_name]

    # Прямая привязка по идентификатору синей линии
    for jp in named_points:
        result[jp.blue_line_id].add(jp.red_device_name)

    if not named_points:
        return result

    grid = SpatialGrid(max(tolerance * 8, 16.0))
    for jp in named_points:
        grid.add(jp.x, jp.y, jp)

    for seg in segments:
        min_x, max_x = sorted((seg.x1, seg.x2))
        min_y, max_y = sorted((seg.y1, seg.y2))
        seen = set()
        for jp in grid.near_box(min_x - tolerance, min_y - tolerance,
                                max_x + tolerance, max_y + tolerance):
            key = id(jp)
            if key in seen:
                continue
            seen.add(key)
            if is_point_on_segment(jp.x, jp.y, seg, tolerance):
                result[seg.id].add(jp.red_device_name)

    return result


def sort_pipeline_segments(segments: List[LineSegment]) -> List[LineSegment]:
    # Выстраивает сегменты в порядке следования вдоль трубы,
    # разворачивая те, что идут против направления обхода.
    if len(segments) <= 1:
        return segments

    graph = defaultdict(list)
    for seg in segments:
        p1 = (round(seg.x1, 2), round(seg.y1, 2))
        p2 = (round(seg.x2, 2), round(seg.y2, 2))
        graph[p1].append((seg, p2))
        graph[p2].append((seg, p1))

    start_point = None
    for point, neighbors in graph.items():
        if len(neighbors) == 1:
            start_point = point
            break
    if start_point is None:
        start_point = next(iter(graph))

    sorted_segs: List[LineSegment] = []
    visited_ids = set()
    current_point = start_point

    while True:
        next_seg = None
        for seg, _point in graph.get(current_point, []):
            if seg.id not in visited_ids:
                # Точка пересчитывается ниже: сегмент мог быть развёрнут
                next_seg = seg
                break

        if next_seg is None:
            break

        p2 = (round(next_seg.x2, 2), round(next_seg.y2, 2))
        if current_point == p2:
            next_seg = LineSegment(
                id=next_seg.id,
                x1=next_seg.x2, y1=next_seg.y2,
                x2=next_seg.x1, y2=next_seg.y1,
                color=next_seg.color,
                stroke_width=next_seg.stroke_width,
                device_name=next_seg.device_name)

        sorted_segs.append(next_seg)
        visited_ids.add(next_seg.id)
        current_point = (round(next_seg.x2, 2), round(next_seg.y2, 2))

    return sorted_segs


def build_pipelines(blue_segments: List[LineSegment],
                    junction_points: List[JunctionPoint],
                    min_segment_length: float = MIN_PIPELINE_SEGMENT_LENGTH,
                    verbose: bool = True, scale: float = 1.0) -> List[Pipeline]:
    # Собирает трубопроводы из связных цепочек синих сегментов
    if not blue_segments:
        if verbose:
            print("   Нет синих сегментов для построения труб")
        return []

    min_segment_length *= scale
    original_count = len(blue_segments)
    blue_segments = [s for s in blue_segments if s.length() >= min_segment_length]
    if verbose and len(blue_segments) < original_count:
        print(f"   Отфильтровано коротких сегментов: {original_count - len(blue_segments)}")

    if not blue_segments:
        return []

    # Устройства для всех сегментов считаем один раз, а не заново для каждой трубы
    devices_by_segment = _devices_by_segment(blue_segments, junction_points,
                                             ON_SEGMENT_TOLERANCE * scale)

    point_to_segments = defaultdict(list)
    for seg in blue_segments:
        point_to_segments[(round(seg.x1, 2), round(seg.y1, 2))].append(seg)
        point_to_segments[(round(seg.x2, 2), round(seg.y2, 2))].append(seg)

    visited = set()
    pipelines: List[Pipeline] = []
    counter = 1

    for seg in blue_segments:
        if seg.id in visited:
            continue

        # Обход в ширину по общим концам сегментов
        component = []
        queue = deque([seg])
        visited.add(seg.id)
        while queue:
            current = queue.popleft()
            component.append(current)
            for point in ((current.x1, current.y1), (current.x2, current.y2)):
                for neighbor in point_to_segments.get((round(point[0], 2), round(point[1], 2)), ()):
                    if neighbor.id not in visited:
                        visited.add(neighbor.id)
                        queue.append(neighbor)

        sorted_segments = sort_pipeline_segments(component)
        total_length = sum(s.length() for s in sorted_segments)

        devices = set()
        for s in sorted_segments:
            devices |= devices_by_segment.get(s.id, set())

        pipelines.append(Pipeline(
            id=counter,
            name=f"pipeline{counter * 1000 + int(total_length)}",
            segments=sorted_segments,
            connected_devices=sorted(devices),
            total_length=total_length))
        counter += 1

    if verbose:
        print(f"   ✅ Построено труб: {len(pipelines)}")

    return pipelines
