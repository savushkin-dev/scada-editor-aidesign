# tools/extract_symbols.py
# Каталог готовых символов из сцены редактора мнемосхем.
#
# Зачем. Раньше устройство уезжало отрисовкой конвейера: кружок или скопление
# красных отрезков с чертежа. Но у редактора уже нарисованы свои фигуры —
# клапан, ёмкость, датчик, — и рисовать их заново значит отдавать схему,
# которая на его мнемосхемы не похожа. Правильнее взять готовые фигуры
# и подставлять их на места устройств.
#
# Откуда берётся форма. Из выгрузки редактора (`SCADA_EDITOR_SCENE` или
# плоский массив элементов): повторяющаяся группа — это и есть готовый
# символ. В присланной сцене MOZARELLA_01 таких три: клапан (24 экземпляра),
# ёмкость (2) и разлиновка (13); плюс фигуры без группы — кружок датчика
# с тегом внутри и «бабочка» ручного клапана из двух треугольников.
#
# Что считается одним символом. Дети группы переводятся в её систему
# координат, нормируются к габариту 1x1 и округляются — получается подпись
# формы. Одинаковые подписи — один символ, разные — разные. Так символ
# узнаётся независимо от того, где на схеме он стоит и какого размера.
#
# Имена. В сцене MOZARELLA_01 их приходилось задавать вручную: все группы
# там называются «Group (8)», а элементы «Element», и понять из файла, что
# клапан, а что ёмкость, нельзя. В присланной позже библиотеке
# (`elements/MCA_1_components.json`) у групп стоят настоящие подписи —
# «Насос центробежный», «Клапан, НЗ», — и тогда работает `--from-labels`:
# подпись переводится в имя каталога по таблице LIBRARY_NAMES, а сама
# подпись остаётся в символе полем `title`.
#
# Запуск из папки CONTUR:
#     python tools/extract_symbols.py --scene сцена.json --list
#     python tools/extract_symbols.py --scene сцена.json --name 1=valve --name 2=tank
#     python tools/extract_symbols.py --scene библиотека.json --from-labels --keep
#
# Второй вызов записывает `hmi_symbols.json` рядом с кодом — его читает
# `hmi_symbols.py` при выгрузке. Файл лежит в репозитории: пересобирать его
# нужно только когда библиотека редактора пополнится.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (настройка кодировки вывода)

import argparse
import itertools
import json
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import hmi_symbols

# Сетка холста редактора: к ней прижимаются размеры символа (спецификация импорта, §0)
GRID = 20.0

# С какой точностью сравниваются формы. Координаты нормируются к габариту
# символа, поэтому это доли стороны: 1/1000 стороны — заведомо меньше того,
# что человек различает на схеме
SHAPE_ROUND = 3

# Одиночные фигуры (не группы) тоже бывают готовым символом: кружок датчика
# с тегом внутри — как раз такой. Но одиночных фигур на схеме сотни, и класть
# в каталог каждую нельзя: символом считается та, что повторяется не реже
MIN_SINGLE_INSTANCES = 3

# Какие поля фигуры описывают её вид. Всё остальное (ключи, ссылки, состояния,
# подписи) относится к месту на схеме, а не к форме
SHAPE_FIELDS = ("strokeColor", "strokeWidth", "strokeDasharray", "bg",
                "arrowStart", "arrowEnd", "sides", "fontSize")

# Библиотечная подпись фигуры — короткое имя в каталоге. Подписи русские и говорят
# о назначении («Санитарная запорная заслонка с пневмоприводом, НЗ»), а код
# обращается к символу коротким именем; чтобы связь не терялась, сама подпись
# уезжает в каталог полем `title` и видна в панели сведений.
#
# Таблица заполняется руками ровно один раз на присланную библиотеку:
# по подписи нельзя вывести имя механически, а ошибка в имени — это чужая
# фигура на месте устройства.
LIBRARY_NAMES = {
    # приборы
    "Прибор, установленный в щите, или функция программного обоеспечения":
        "panel_instrument",
    "Датчик верхнего предельного уровня": "level_high",
    "Датчик среднего уровня": "level_mid",
    "Датчик нижнего предельного уровня": "level_low",
    # клапаны и заслонки
    "Санитарная запорная заслонка с пневмоприводом, НЗ": "butterfly_nc",
    "Санитарная запорная заслонка с пневмоприводом, НО": "butterfly_no",
    "Санитарная запорная заслонка с ручным приводом 1": "manual_butterfly",
    "Санитарная запорная заслонка с ручным приводом 2": "manual_butterfly_2",
    "Санитарный переключающий клапан 1": "mix_valve_1",
    "Санитарный переключающий клапан 2": "mix_valve_2",
    "Санитарный переключающий клапан 3": "mix_valve_3",
    "Санитарный переключающий клапан 4": "mix_valve_4",
    "Санитарный регулирующий клапан": "control_valve",
    "Клапан, НЗ": "valve_nc",
    "Клапан, НО": "valve_no",
    "Клапан шаровый с пневмоприводом, НЗ": "ball_valve_nc",
    "Клапан шаровый с пневмоприводом, НО": "ball_valve_no",
    "Клапан шаровый с ручным приводом": "manual_ball_valve",
    "Клапан с ручным приводом": "manual_valve",
    "Клапан с ручным приводом с плавной характеристикой": "manual_valve_smooth",
    "Клапан трехходовой": "three_way_valve",
    "Клапан обратный": "check_valve",
    # насосы
    "Насос центробежный": "pump_centrifugal",
    "Насос вакуумный": "pump_vacuum",
    "Насос мембранный": "pump_membrane",
    # электрические устройства — нарисованы отдельно, в библиотеке их нет
    # (tools/make_contur_symbols.py)
    "Лампа сигнальная": "lamp",
    "Кнопка": "button",
    "Сирена": "siren",
    "Сигнальная колонна": "beacon",
    # прочее оборудование
    "Теплообменник пластинчатый": "heat_exchanger_plate",
    "Теплообменник кожухотрубный": "heat_exchanger_shell",
    "Фильтр": "filter",
    "Дренажная воронка": "drain_funnel",
    "Предохранительная мембрана": "rupture_disc",
    "Местное сопротивление (диафрагма, диффузор)": "restriction",
}

# Кружок прибора в библиотеке пустой: тег в него вписывает человек, когда
# ставит фигуру на схему. В рабочей сцене (MOZARELLA_01) он уже
# с тегом внутри, и выгрузка тоже пишет туда имя устройства, поэтому
# у этих фигур кружок помечается местом под тег
TAGGED = frozenset((
    "panel_instrument", "level_high", "level_mid", "level_low",
))

# У каких фигур собрать заодно стоячий вид (имя с суффиксом `_v`). Клапан
# на чертеже стоит и вдоль трубы, и поперёк, а в библиотеке нарисован
# в одном положении: второй вид — тот же символ, повёрнутый на 90°
ROTATED = frozenset((
    "butterfly_nc", "butterfly_no", "manual_butterfly", "manual_butterfly_2",
    "valve_nc", "valve_no", "ball_valve_nc", "ball_valve_no",
    "manual_valve", "manual_valve_smooth", "manual_ball_valve",
    "control_valve", "check_valve", "three_way_valve",
))

# Подписи, которые ничего не говорят о фигуре: так редактор называет
# то, что человек не назвал сам
EMPTY_LABELS = re.compile(r"^(Group \(\d+\)|Element|Элемент|)$")


def load_scene(path: str) -> List[Dict[str, Any]]:
    """Элементы сцены: и их выгрузка объектом, и плоский массив."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("elements") or []
    return [item for item in data if isinstance(item, dict) and item.get("key")]


def _children(element: Dict[str, Any],
              by_key: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [by_key[key] for key in element.get("children") or [] if key in by_key]


def _points(element: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Точки многоугольника или кривой в системе координат родителя.

    `points` отсчитываются от `x, y` самого элемента (спецификация
    импорта, §5.6), а не от угла габарита и не от холста.
    """
    raw = element.get("points") or []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            return []
    x, y = float(element.get("x") or 0), float(element.get("y") or 0)
    return [(x + float(raw[i]), y + float(raw[i + 1]))
            for i in range(0, len(raw) - 1, 2)]


def primitives(element: Dict[str, Any], by_key: Dict[str, Dict[str, Any]],
               ox: float = 0.0, oy: float = 0.0) -> List[Dict[str, Any]]:
    """Фигура (или группа) разложенная в плоский список примитивов.

    Координаты — в системе координат самого символа, начиная от его угла.
    Группы разворачиваются: внутри каталога вложенности нет, она вернётся
    при подстановке.
    """
    kind = element.get("type")
    x, y = ox + float(element.get("x") or 0), oy + float(element.get("y") or 0)
    style = {field: element[field] for field in SHAPE_FIELDS if field in element}

    if kind == "group":
        out: List[Dict[str, Any]] = []
        for child in _children(element, by_key):
            out.extend(primitives(child, by_key, x, y))
        return out

    if kind == "line":
        return [dict(style, type="line",
                     x1=ox + float(element.get("x1") or 0),
                     y1=oy + float(element.get("y1") or 0),
                     x2=ox + float(element.get("x2") or 0),
                     y2=oy + float(element.get("y2") or 0))]

    if kind == "circle":
        radius = float(element.get("radius") or (element.get("w") or 0) / 2)
        shape = dict(style, type="circle", cx=x + radius, cy=y + radius,
                     radius=radius)
        if element.get("text"):
            # У кружка датчика внутри стоит тег. Своё содержимое подставится
            # при выгрузке, в каталоге остаётся только признак «здесь тег»
            shape["text"] = "$tag"
        return [shape]

    if kind in ("polygon", "curve"):
        pts = _points(element)
        if not pts:
            return []
        return [dict(style, type=kind,
                     points=[coord + (ox if index % 2 == 0 else oy)
                             for point in pts for index, coord in enumerate(point)])]

    if kind in ("rectangle", "rect"):
        w, h = float(element.get("w") or 0), float(element.get("h") or 0)
        return [dict(style, type="rectangle", x=x, y=y, w=w, h=h)]

    if kind == "text":
        return [dict(style, type="text", x=x, y=y,
                     text=element.get("text") or element.get("label") or "")]

    return []


def bounds(shapes: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
    xs: List[float] = []
    ys: List[float] = []
    for shape in shapes:
        kind = shape["type"]
        if kind == "line":
            xs += [shape["x1"], shape["x2"]]
            ys += [shape["y1"], shape["y2"]]
        elif kind == "circle":
            xs += [shape["cx"] - shape["radius"], shape["cx"] + shape["radius"]]
            ys += [shape["cy"] - shape["radius"], shape["cy"] + shape["radius"]]
        elif kind in ("polygon", "curve"):
            pts = shape["points"]
            xs += pts[0::2]
            ys += pts[1::2]
        elif kind == "rectangle":
            xs += [shape["x"], shape["x"] + shape["w"]]
            ys += [shape["y"], shape["y"] + shape["h"]]
        else:
            xs.append(shape.get("x", 0.0))
            ys.append(shape.get("y", 0.0))
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    return (min(xs), min(ys), max(xs), max(ys))


def normalize(shapes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float, float]:
    """Символ в собственных координатах: угол в (0, 0), габарит — как есть.

    Возвращает (примитивы, ширина, высота). Габарит округляется вверх
    до клетки: символ подставляется как объект, а объект обязан быть
    кратен сетке (спецификация импорта, §3.1, уровень A).
    """
    minx, miny, maxx, maxy = bounds(shapes)
    moved: List[Dict[str, Any]] = []
    for shape in shapes:
        item = dict(shape)
        kind = item["type"]
        if kind == "line":
            item["x1"] -= minx
            item["x2"] -= minx
            item["y1"] -= miny
            item["y2"] -= miny
        elif kind == "circle":
            item["cx"] -= minx
            item["cy"] -= miny
        elif kind in ("polygon", "curve"):
            item["points"] = [coord - (minx if index % 2 == 0 else miny)
                              for index, coord in enumerate(item["points"])]
        else:
            item["x"] = item.get("x", 0.0) - minx
            item["y"] = item.get("y", 0.0) - miny
        moved.append(item)

    width = math.ceil(max(maxx - minx, GRID) / GRID) * GRID
    height = math.ceil(max(maxy - miny, GRID) / GRID) * GRID
    return moved, width, height


def _canonical_points(values: List[float], closed: bool) -> List[float]:
    """Точки в порядке, не зависящем от того, откуда их начали рисовать.

    Один и тот же прямоугольник в сцене нарисован то с левого верхнего угла,
    то с правого: без приведения к общему порядку два одинаковых клапана
    разъезжались на два разных символа (в присланной сцене — 7 и 6 штук).
    """
    points = list(zip(values[0::2], values[1::2], strict=True))
    if len(points) < 2:
        return values

    variants: List[List[Tuple[float, float]]] = []
    for order in (points, points[::-1]):
        if closed:
            # У замкнутой фигуры начать можно с любой вершины
            variants += [order[shift:] + order[:shift] for shift in range(len(order))]
        else:
            variants.append(order)
    best = min(variants)
    return [coord for point in best for coord in point]


def signature(shapes: List[Dict[str, Any]]) -> str:
    """Подпись формы: одинаковая у одинаковых фигур, где бы они ни стояли.

    Координаты нормируются к габариту, поэтому один и тот же клапан,
    нарисованный крупнее, узнаётся как тот же символ.
    """
    moved, width, height = normalize(shapes)
    side = max(width, height) or 1.0

    def rel(value: float) -> float:
        return round(value / side, SHAPE_ROUND)

    parts: List[str] = []
    for shape in moved:
        kind = shape["type"]
        if kind == "line":
            parts.append(f"l{rel(shape['x1'])},{rel(shape['y1'])},"
                         f"{rel(shape['x2'])},{rel(shape['y2'])}")
        elif kind == "circle":
            parts.append(f"c{rel(shape['cx'])},{rel(shape['cy'])},{rel(shape['radius'])}"
                         + (":tag" if shape.get("text") else ""))
        elif kind in ("polygon", "curve"):
            values = _canonical_points([rel(v) for v in shape["points"]],
                                       closed=kind == "polygon")
            parts.append(f"{kind[0]}" + ",".join(str(v) for v in values))
        elif kind == "rectangle":
            parts.append(f"r{rel(shape['x'])},{rel(shape['y'])},"
                         f"{rel(shape['w'])},{rel(shape['h'])}")
        else:
            parts.append(f"t{rel(shape.get('x', 0))},{rel(shape.get('y', 0))}")
        if shape.get("bg") not in (None, "transparent"):
            parts[-1] += f"#{shape['bg']}"
    # Порядок примитивов в подписи не значит ничего: одну и ту же фигуру
    # рисуют начиная с разных её частей. Порядок отрисовки при этом
    # сохраняется в самом символе — он важен для заливок
    return "|".join(sorted(parts))


def clusters(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Повторяющиеся фигуры сцены, от частых к редким.

    Группа — кандидат всегда: её собрал человек, значит это законченная
    фигура. Одиночная фигура — только если повторяется (MIN_SINGLE_INSTANCES):
    иначе в каталог попал бы каждый отрезок чертежа.
    """
    by_key = {element["key"]: element for element in elements}
    grouped = {key for element in elements if element.get("type") == "group"
               for key in element.get("children") or []}

    found: Dict[str, Dict[str, Any]] = {}
    for element in elements:
        if element["key"] in grouped:
            continue          # ребёнок группы — часть символа, а не символ
        if element.get("type") not in ("group", "circle", "polygon",
                                       "curve", "rectangle"):
            continue          # одиночный отрезок символом не считается
        shapes = primitives(element, by_key)
        if not shapes:
            continue

        sign = signature(shapes)
        moved, width, height = normalize(shapes)
        entry = found.setdefault(sign, {
            "signature": sign, "instances": 0, "grouped": False, "label": "",
            "sizes": Counter(), "by_size": {},
        })
        entry["instances"] += 1
        entry["grouped"] = entry["grouped"] or element.get("type") == "group"
        label = (element.get("label") or "").strip()
        if not entry["label"] and not EMPTY_LABELS.match(label):
            entry["label"] = label
        entry["sizes"][(width, height)] += 1
        entry["by_size"].setdefault((width, height), moved)

    out: List[Dict[str, Any]] = []
    for entry in found.values():
        if not (entry["grouped"] or entry["instances"] >= MIN_SINGLE_INSTANCES):
            continue
        # За образец берётся самый частый размер, а не самый крупный:
        # кружок датчика на схеме встречается радиусом 40 и 60, но там же
        # нарисованы два обода ёмкости радиусом 780 — по ним символ датчика
        # уехал бы в габарит 1560
        (width, height), _ = max(entry["sizes"].items(), key=lambda kv: (kv[1], kv[0]))
        entry["w"], entry["h"] = width, height
        entry["shapes"] = entry["by_size"][(width, height)]
        entry.pop("by_size")
        out.append(entry)

    out.sort(key=lambda e: (-e["instances"], -e["w"] * e["h"]))
    return out


# ------------------------------------------------------------------ показ

def ascii_art(shapes: List[Dict[str, Any]], cols: int = 40) -> str:
    """Форма символа знаками — чтобы называть их, глядя на фигуру."""
    minx, miny, maxx, maxy = bounds(shapes)
    sx = cols / max(1e-6, maxx - minx)
    sy = sx * 0.5                       # знак вдвое выше своей ширины
    rows = max(1, int((maxy - miny) * sy) + 1)
    grid = [[" "] * (cols + 1) for _ in range(rows + 1)]

    def dot(x: float, y: float) -> None:
        col, row = int((x - minx) * sx), int((y - miny) * sy)
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            grid[row][col] = "#"

    def segment(x1: float, y1: float, x2: float, y2: float) -> None:
        steps = int(max(abs(x2 - x1) * sx, abs(y2 - y1) * sy) * 3) + 2
        for step in range(steps + 1):
            t = step / steps
            dot(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)

    for shape in shapes:
        kind = shape["type"]
        if kind == "line":
            segment(shape["x1"], shape["y1"], shape["x2"], shape["y2"])
        elif kind == "circle":
            for degree in range(0, 360, 2):
                angle = math.radians(degree)
                dot(shape["cx"] + shape["radius"] * math.cos(angle),
                    shape["cy"] + shape["radius"] * math.sin(angle))
        elif kind in ("polygon", "curve"):
            pts = list(zip(shape["points"][0::2], shape["points"][1::2],
                           strict=True))
            if kind == "polygon" and pts:
                pts = [*pts, pts[0]]
            for first, second in itertools.pairwise(pts):
                segment(first[0], first[1], second[0], second[1])
        elif kind == "rectangle":
            x, y, w, h = shape["x"], shape["y"], shape["w"], shape["h"]
            segment(x, y, x + w, y)
            segment(x + w, y, x + w, y + h)
            segment(x + w, y + h, x, y + h)
            segment(x, y + h, x, y)
    return "\n".join("".join(row).rstrip() for row in grid)


def show(entries: List[Dict[str, Any]]) -> None:
    print(f"Найдено повторяющихся фигур: {len(entries)}\n")
    for index, entry in enumerate(entries, 1):
        kind = "группа" if entry["grouped"] else "одиночная фигура"
        title = entry.get("label") or ""
        name = LIBRARY_NAMES.get(title)
        print(f"[{index}] {kind}, экземпляров {entry['instances']}, "
              f"габарит {entry['w']:.0f}x{entry['h']:.0f}, "
              f"примитивов {len(entry['shapes'])}"
              + (f"\n     подпись: {title}" if title else "")
              + (f" → {name}" if name else ""))
        print(ascii_art(entry["shapes"]))
        print()
    print("Назвать нужные и записать каталог:")
    print("    python tools/extract_symbols.py --scene <файл> "
          "--name 1=valve --name 2=tank")


# ------------------------------------------------------------------ запись

def rotate(shapes: List[Dict[str, Any]], height: float) -> List[Dict[str, Any]]:
    """Те же примитивы, повёрнутые на 90° по часовой стрелке.

    Клапан в библиотеке нарисован в одном положении, а на чертеже он стоит
    и вдоль трубы, и поперёк. Поворот — это (x, y) → (высота − y, x):
    ширина и высота меняются местами, форма не искажается.
    """
    def point(x: float, y: float) -> Tuple[float, float]:
        return (height - y, x)

    out: List[Dict[str, Any]] = []
    for shape in shapes:
        item = dict(shape)
        kind = item["type"]
        if kind == "line":
            item["x1"], item["y1"] = point(shape["x1"], shape["y1"])
            item["x2"], item["y2"] = point(shape["x2"], shape["y2"])
        elif kind == "circle":
            item["cx"], item["cy"] = point(shape["cx"], shape["cy"])
        elif kind in ("polygon", "curve"):
            pts = list(zip(shape["points"][0::2], shape["points"][1::2], strict=True))
            item["points"] = [coord for x, y in pts for coord in point(x, y)]
        elif kind == "rectangle":
            # Угол прямоугольника после поворота — его левый нижний
            x, y = point(shape["x"], shape["y"] + shape["h"])
            item["x"], item["y"] = x, y
            item["w"], item["h"] = shape["h"], shape["w"]
        else:
            item["x"], item["y"] = point(shape.get("x", 0.0), shape.get("y", 0.0))
        out.append(item)
    return out


def tagged(shapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Кружок фигуры — место под тег устройства.

    В библиотеке кружок прибора пустой: обозначение в него вписывает
    человек. Наша выгрузка ставит туда имя устройства, и без этой пометки
    датчик приезжал бы безымянным кружком.
    """
    out: List[Dict[str, Any]] = []
    biggest = max((s for s in shapes if s["type"] == "circle"),
                  key=lambda s: s["radius"], default=None)
    for shape in shapes:
        item = dict(shape)
        if shape is biggest:
            item["text"] = "$tag"
        out.append(item)
    return out


def catalogue(entries: List[Dict[str, Any]], names: Dict[int, str],
              source: str, origin: str = "editor") -> Dict[str, Any]:
    symbols: Dict[str, Any] = {}
    for index, name in sorted(names.items()):
        if not 1 <= index <= len(entries):
            raise SystemExit(f"нет фигуры номер {index}: их {len(entries)}")
        entry = entries[index - 1]
        shapes = entry["shapes"]
        if name in TAGGED:
            shapes = tagged(shapes)
        symbols[name] = {
            "w": entry["w"],
            "h": entry["h"],
            "origin": origin,
            "instances": entry["instances"],
            "signature": entry["signature"],
            "shapes": shapes,
        }
        if entry.get("label"):
            symbols[name]["title"] = entry["label"]
        if name in ROTATED:
            # Какой это вид — лежачий или стоячий — видно по самой фигуре.
            # Клапан с приводом выше, чем шире: корпус на трубе, привод
            # над ним. Выгрузка выбирает вид по той же примете, но у своего
            # скопления красных линий на чертеже, поэтому и здесь признак
            # один — пропорции, а не то, как фигуру нарисовали в библиотеке
            turned = dict(symbols[name], w=entry["h"], h=entry["w"],
                          shapes=rotate(shapes, entry["h"]))
            upright = f"{name}{hmi_symbols.VERTICAL_SUFFIX}"
            if entry["h"] > entry["w"]:
                symbols[upright] = symbols[name]
                symbols[name] = turned
            else:
                symbols[upright] = turned
    return {
        "source": Path(source).name,
        "grid": GRID,
        "symbols": symbols,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Каталог готовых символов из сцены редактора мнемосхем")
    parser.add_argument("--scene", required=True,
                        help="выгрузка редактора (*.json)")
    parser.add_argument("--list", action="store_true",
                        help="показать найденные фигуры и выйти")
    parser.add_argument("--name", action="append", default=[], metavar="N=имя",
                        help="назвать фигуру номер N (можно несколько раз)")
    parser.add_argument("--from-labels", action="store_true",
                        help="взять имена из подписей групп (таблица LIBRARY_NAMES)")
    parser.add_argument("--origin", default="editor", choices=("editor", "contur"),
                        help="откуда фигура: из сцены редактора или нарисована здесь")
    parser.add_argument("--out", default=str(hmi_symbols.CATALOGUE_PATH),
                        help="куда записать каталог")
    parser.add_argument("--keep", action="store_true",
                        help="дописать в существующий каталог, а не заменить")
    args = parser.parse_args(argv)

    elements = load_scene(args.scene)
    entries = clusters(elements)
    print(f"Сцена {Path(args.scene).name}: элементов {len(elements)}")

    if args.list or not (args.name or args.from_labels):
        show(entries)
        return 0

    names: Dict[int, str] = {}
    if args.from_labels:
        for index, entry in enumerate(entries, 1):
            name = LIBRARY_NAMES.get(entry.get("label") or "")
            if name:
                names[index] = name
        unknown = sorted({entry["label"] for entry in entries
                          if entry.get("label")
                          and entry["label"] not in LIBRARY_NAMES})
        for label in unknown:
            print(f"   подпись без имени в таблице, пропущена: {label}")
        if not names:
            raise SystemExit("ни одна подпись не нашлась в LIBRARY_NAMES")

    for item in args.name:
        number, _, name = item.partition("=")
        if not name:
            raise SystemExit(f"нужно N=имя, а не {item!r}")
        names[int(number)] = name.strip()

    data = catalogue(entries, names, args.scene, args.origin)
    if args.keep and Path(args.out).exists():
        with open(args.out, encoding="utf-8") as handle:
            old = json.load(handle)
        merged = dict(old.get("symbols") or {})
        merged.update(data["symbols"])
        data["symbols"] = merged
        # Откуда что взято, видно по файлу: фигуры собраны из двух присылок,
        # и через полгода этого не вспомнить
        was = [part.strip() for part in str(old.get("source") or "").split(",")]
        data["source"] = ", ".join(dict.fromkeys(
            [part for part in was if part] + [data["source"]]))

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
    print(f"Каталог записан: {args.out}")
    for name, symbol in data["symbols"].items():
        print(f"   {name}: {symbol['w']:.0f}x{symbol['h']:.0f}, "
              f"примитивов {len(symbol['shapes'])}, "
              f"экземпляров в сцене {symbol.get('instances', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
