# hmi_validate.py
# Самопроверка файла для редактора мнемосхем — по их же списку
# (IMPORT_SCHEME_SPEC, §10).
#
# Зачем отдельно от экспорта. Экспорт знает, что он собирался сделать;
# проверка знает, чего ждут от файла при импорте. Это разные знания,
# и держать их в одном месте — значит проверять себя своими же словами.
# Файл читается с диска, как его прочитает редактор.
#
# Строгость разная у двух групп, и это не поблажка проверки, а разделение
# (§3.1). Объекты — всё, что человек двигает, выделяет и выравнивает:
# группы, рамки, кружки устройств, тексты. Они обязаны стоять в узлах сетки,
# иначе схема разъезжается по мере работы с ней и починить это в редакторе
# нельзя. Чертёж — перерисованный PDF: требовать кратности от каждого
# отрезка нельзя, диагонали и разложенные кривые заметно деформируются.
#
# Запуск:
#     python hmi_validate.py выгрузка.json
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
import json
import math
from typing import Any, Dict, List, Tuple

# Сетка холста — из спецификации импорта, §0. Размер сцены ничем не
# ограничен (§7a): клампа позиций нет, камера не ограничена, холст Konva
# аллоцируется по видимой области. Лист остаётся в отчёте числом — он важен
# сам по себе, но замечанием быть перестал
GRID = 20.0
MIN_FONT_SIZE = 12.0
MIN_STROKE_WIDTH = 0.5

# Типы, к которым сетка не относится: чертёж и элемент с данными
DRAWING_TYPES = ("line",)
DATA_TYPES = ("meta",)


def _on_grid(value: Any) -> bool:
    return isinstance(value, (int, float)) and abs(value / GRID - round(value / GRID)) < 1e-6


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(elements: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, int]]:
    """Замечания к файлу и сводка по чертежу.

    Возвращает (замечания, показатели). Замечания — то, что редактор
    считает поломкой. Показатели — то, что поломкой не считается,
    но полезно знать: сколько отрезков чертежа короче клетки и сколько
    ортогональных не село на сетку.
    """
    problems: List[str] = []
    stats = {"короткие_отрезки": 0, "ортогональные_вне_сетки": 0, "диагонали": 0,
             "внутри_символов": 0, "холст_ширина": 0, "холст_высота": 0}

    if not isinstance(elements, list):
        return ["файл не массив элементов"], stats
    if not elements:
        return ["массив пуст"], stats

    by_key = {e.get("key"): e for e in elements if isinstance(e, dict)}
    if len(by_key) != len(elements):
        problems.append(f"ключи повторяются: {len(by_key)} на {len(elements)}")

    def say(element: Dict[str, Any], message: str):
        name = element.get("label") or element.get("lua_name") or element.get("key")
        problems.append(f"{element.get('type', '?')} {name}: {message}")

    for element in elements:
        kind = str(element.get("type", ""))

        if element.get("id") is not None:
            say(element, "id должен быть null или отсутствовать")
        for field in ("x", "y", "w", "h"):
            if field in element and not _number(element[field]):
                say(element, f"{field} не число: {element[field]!r}")

        _check_links(element, by_key, say)

        if kind in DATA_TYPES:
            continue

        # Внутренности готовой фигуры — третий уровень строгости, рядом
        # с чертежом. Фигуру рисовали на сетке 20 в её собственном размере,
        # а на схему она встаёт в размере устройства: половинный размер
        # делит клетку пополам, и требовать узлов от круга радиусом 10
        # значит требовать перерисовать саму фигуру. Что обязано стоять
        # в узлах — это её рамка, то есть группа устройства
        if element.get("contur_symbol_part"):
            stats["внутри_символов"] += 1
            if kind in DRAWING_TYPES:
                _check_line(element, {"короткие_отрезки": 0,
                                      "ортогональные_вне_сетки": 0,
                                      "диагонали": 0}, say)
            continue

        if kind == "group":
            _check_group(element, by_key, say)
        elif kind == "circle":
            _check_circle(element, say)
        elif kind in DRAWING_TYPES:
            _check_line(element, stats, say)
        else:
            _check_object(element, say)

    _check_canvas(elements, by_key, problems, stats)
    return problems, stats


def _check_links(element: Dict[str, Any], by_key: Dict[Any, Dict[str, Any]], say):
    # Связь родитель-ребёнок обязана быть двусторонней: холст обходит детей
    # по массиву children, и ребёнок с одной ссылкой вверх не отрисуется
    parent_key = element.get("parentKey")
    if parent_key and parent_key not in ("undefined", "null"):
        parent = by_key.get(parent_key)
        if parent is None:
            say(element, f"parentKey {parent_key} не найден")
        elif element.get("key") not in (parent.get("children") or []):
            say(element, "нет обратной ссылки в children родителя")

    for child_key in element.get("children") or []:
        child = by_key.get(child_key)
        if child is None:
            say(element, f"children: {child_key} не найден")
        elif child.get("parentKey") != element.get("key"):
            say(element, f"children: у {child_key} другой parentKey")


def _check_group(element: Dict[str, Any], by_key: Dict[Any, Dict[str, Any]], say):
    if not (_on_grid(element.get("x")) and _on_grid(element.get("y"))):
        say(element, "начало группы не на сетке — вся внутренность уедет")
    if not (_on_grid(element.get("w")) and _on_grid(element.get("h"))):
        say(element, "размер группы не кратен клетке")

    children = element.get("children") or []
    first = by_key.get(children[0]) if children else None
    if first is None or first.get("type") != "rectangle":
        say(element, "первым ребёнком нет рамки-rectangle")


def _check_circle(element: Dict[str, Any], say):
    # Центр круга тоже обязан попадать в узел: перетаскивание привязывает
    # к сетке именно центр, и круг, пришедший мимо узла, останется смещённым
    # на свои +7.3 навсегда
    if not (_on_grid(element.get("x")) and _on_grid(element.get("y"))):
        say(element, "центр круга не на сетке")

    radius = element.get("radius")
    if not _number(radius) or radius < GRID or not _on_grid(radius):
        say(element, f"radius {radius}: нужен кратный клетке и не меньше неё")
    elif element.get("w") != 2 * radius or element.get("h") != 2 * radius:
        say(element, "габарит должен равняться двум радиусам")


def _check_object(element: Dict[str, Any], say):
    if not (_on_grid(element.get("x")) and _on_grid(element.get("y"))):
        say(element, "позиция не на сетке")
    if not _number(element.get("w")) or element["w"] < GRID:
        say(element, "ширина меньше клетки")
    if not _number(element.get("h")) or element["h"] < GRID:
        say(element, "высота меньше клетки")

    size = element.get("font_size", element.get("fontSize"))
    if element.get("type") == "text" and _number(size) and size < MIN_FONT_SIZE:
        say(element, f"кегль {size} не читается на экране")


def _check_line(element: Dict[str, Any], stats: Dict[str, int], say):
    ends = [element.get(f) for f in ("x1", "y1", "x2", "y2")]
    if not all(_number(v) for v in ends):
        say(element, "у отрезка нет концов")
        return

    width = element.get("stroke_width", element.get("strokeWidth"))
    if _number(width) and width < MIN_STROKE_WIDTH:
        say(element, f"толщина {width} тоньше половины пикселя")

    x1, y1, x2, y2 = ends
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        say(element, "отрезок схлопнулся в точку")
        return

    # Дальше — не поломки, а показатели чертежа: спецификация импорта (§3.1)
    # разрешает точные координаты у диагоналей и разложенных кривых
    if length < GRID:
        stats["короткие_отрезки"] += 1
    if abs(x2 - x1) >= 1.0 and abs(y2 - y1) >= 1.0:
        stats["диагонали"] += 1
    elif not all(_on_grid(v) for v in ends):
        stats["ортогональные_вне_сетки"] += 1


def _check_canvas(elements: List[Dict[str, Any]], by_key: Dict[Any, Dict[str, Any]],
                  problems: List[str], stats: Dict[str, int]):
    # Габарит схемы: у отрезка x, y — середина, поэтому край берётся
    # по концам, а не по габариту
    def size(element: Dict[str, Any], *fields: str) -> float:
        # Нечисловые координаты уже названы поломкой выше — здесь они просто
        # не участвуют в замере, иначе замер падает вместо отчёта
        values = [element.get(f) for f in fields]
        return sum(v for v in values if _number(v)) if all(
            _number(v) for v in values) else 0.0

    far_x = far_y = 0.0
    for element in elements:
        if element.get("parentKey") in by_key:
            continue
        if element.get("type") in DRAWING_TYPES:
            far_x = max(far_x, size(element, "x1"), size(element, "x2"))
            far_y = max(far_y, size(element, "y1"), size(element, "y2"))
        elif element.get("type") not in DATA_TYPES:
            far_x = max(far_x, size(element, "x", "w"))
            far_y = max(far_y, size(element, "y", "h"))

    stats["холст_ширина"], stats["холст_высота"] = int(far_x), int(far_y)

    # Размер листа кратен сетке (§7a): по нему редактор рисует рамку сцены
    # и считает координаты, заданные процентом. Крайним элементом обычно
    # оказывается рамка чертежа или надпись, а они на сетку сажаются, —
    # но стоит дальше всех оказаться диагонали, чьи координаты по §3.1
    # остаются точными, и кратность теряется. Проверяется объявленный
    # размер, а не замер: спецификация требует кратности именно от него
    canvas = next((e.get("canvas") for e in elements
                   if isinstance(e, dict) and e.get("type") in DATA_TYPES
                   and isinstance(e.get("canvas"), dict)), None)
    for name in ("width", "height"):
        value = (canvas or {}).get(name)
        if _number(value) and not _on_grid(value):
            problems.append(f"meta.canvas.{name} {value} "
                            f"не кратен сетке {GRID:.0f}")


def format_report(problems: List[str], stats: Dict[str, int], limit: int = 10) -> str:
    lines = []
    if problems:
        lines.append(f"замечаний: {len(problems)}")
        lines += [f"  {p}" for p in problems[:limit]]
        if len(problems) > limit:
            lines.append(f"  … и ещё {len(problems) - limit}")
    else:
        lines.append("замечаний нет")

    lines.append(f"чертёж: короче клетки {stats['короткие_отрезки']}, "
                 f"ортогональных вне сетки {stats['ортогональные_вне_сетки']}, "
                 f"диагоналей и звеньев кривых {stats['диагонали']}")
    if stats.get("внутри_символов"):
        lines.append(f"внутри готовых фигур: {stats['внутри_символов']} "
                     f"примитивов, сетка к ним не применяется")
    if stats.get("холст_ширина"):
        lines.append(f"лист {stats['холст_ширина']}x{stats['холст_высота']} — "
                     f"рамка сцены, координаты за ней не запрещены; "
                     f"размер задаётся CONTUR_HMI_SYMBOL_CELLS")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Укажите файл: python hmi_validate.py выгрузка.json")
        raise SystemExit(2)

    with open(sys.argv[1], encoding="utf-8") as f:
        document = json.load(f)

    found, measured = validate(document)
    print(f"Элементов: {len(document)}")
    print(format_report(found, measured, limit=20))
    raise SystemExit(1 if found else 0)
