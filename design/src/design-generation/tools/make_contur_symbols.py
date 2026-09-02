# tools/make_contur_symbols.py
# Фигуры, которых нет в библиотеке редактора: кнопка, лампа,
# сирена и сигнальная колонна.
#
# Зачем. Библиотека шаблонов (`MCA_1_components.json`) — про технологию:
# клапаны, насосы, датчики, теплообменники. Электрических устройств в ней нет
# вовсе, и на месте кнопки, лампы, сирены и колонны в объекте оставалась
# пустая рамка. Эти четыре фигуры нарисованы здесь и уезжают с каталогом.
#
# Откуда форма. Лампа и кнопка срисованы с чертежа Eplan: на листе 240
# лампа — кружок с косым крестом и выводами x1/x2, кнопка (`-SB2`) — контакт
# с толкателем и пунктирной связью «E». Сирены и колонны в чертеже нет как
# рисунка: Eplan показывает их клеммным блоком с подписями «Supply GND»,
# «Supply +» (лист 56), — из такого символа мнемосхему не сделать, поэтому
# они нарисованы по общепринятому виду: рупор со звуковыми дугами и колонна
# из двух секций под куполом.
#
# Правила те же, по которым нарисован насос: сетка 20, чёрный штрих,
# прозрачная заливка, габарит кратен клетке, вершины по возможности в узлах.
# Диагонали и дуги в узлы не ложатся — так же, как в их собственных фигурах.
#
# Запуск из папки CONTUR:
#     python tools/make_contur_symbols.py
#
# Пишет `CONTUR_extra_components.json` в формате сцены редактора: группа
# с подписью на фигуру. Такой файл читает и сборщик каталога
# (`extract_symbols.py --from-labels`), и сам редактор — то есть это
# одновременно исходник фигур и готовая к передаче сцена.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (настройка кодировки вывода)

import argparse
import json
import math
import uuid
from typing import Any, Dict, List, Tuple

GRID = 20.0
STROKE = "#000000"

# Ключи в сцене uuid, а файл нужен один и тот же при каждом запуске:
# ключ выводится из содержимого, как и в выгрузке
NAMESPACE = uuid.UUID("6f1d5f9c-6a1f-5c2a-9b1e-2c7c9a4d3e10")


def key(*parts: Any) -> str:
    return str(uuid.uuid5(NAMESPACE, "|".join(str(p) for p in parts)))


def line(x1: float, y1: float, x2: float, y2: float) -> Dict[str, Any]:
    return {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "x": (x1 + x2) / 2, "y": (y1 + y2) / 2,
            "w": abs(x2 - x1), "h": abs(y2 - y1)}


def circle(cx: float, cy: float, radius: float) -> Dict[str, Any]:
    return {"type": "circle", "x": cx - radius, "y": cy - radius,
            "w": radius * 2, "h": radius * 2, "radius": radius}


def polygon(points: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Многоугольник: их `points` отсчитываются от собственных x, y фигуры."""
    ox, oy = points[0]
    flat: List[float] = []
    for x, y in points:
        flat += [x - ox, y - oy]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return {"type": "polygon", "x": ox, "y": oy,
            "w": max(xs) - min(xs), "h": max(ys) - min(ys),
            "points": flat, "sides": len(points)}


def arc(cx: float, cy: float, radius: float, start: float, end: float,
        steps: int = 8) -> Dict[str, Any]:
    """Дуга ломаной: в сцене редактора кривая — это тоже список точек."""
    points = []
    for i in range(steps + 1):
        angle = math.radians(start + (end - start) * i / steps)
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    ox, oy = points[0]
    flat: List[float] = []
    for x, y in points:
        flat += [round(x - ox, 2), round(y - oy, 2)]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return {"type": "curve", "x": round(ox, 2), "y": round(oy, 2),
            "w": round(max(xs) - min(xs), 2), "h": round(max(ys) - min(ys), 2),
            "points": flat}


# ------------------------------------------------------------------ фигуры

def lamp() -> List[Dict[str, Any]]:
    """Лампа сигнальная: кружок с косым крестом — как на листе 240.

    Концы креста лежат на самом круге (45°), поэтому в узлы сетки они
    не попадают: у круга радиуса 60 это 17.57, а не 20. Так же нарисован
    и их собственный насос — важно, что фигура целиком кратна клетке.
    """
    r, c = 60.0, 60.0
    d = round(r - r / math.sqrt(2), 2)
    return [
        circle(c, c, r),
        line(d, d, 2 * c - d, 2 * c - d),
        line(2 * c - d, d, d, 2 * c - d),
    ]


def button() -> List[Dict[str, Any]]:
    """Кнопка: контакт с толкателем — как `-SB2` на листе 240.

    Вывод слева, вывод справа, разомкнутый контакт наклонной чертой,
    от него стержень вверх и полка нажимной части.
    """
    return [
        line(0, 80, 40, 80),
        line(80, 80, 120, 80),
        line(40, 80, 80, 60),
        line(60, 70, 60, 20),
        line(20, 20, 100, 20),
    ]


def siren() -> List[Dict[str, Any]]:
    """Сирена: рупор со звуковыми дугами.

    Своего рисунка в чертеже нет — Eplan показывает сирену клеммным блоком.
    Взят общепринятый вид: корпус, раструб и две дуги.
    """
    return [
        polygon([(0, 40), (60, 40), (100, 0), (100, 120), (60, 80), (0, 80)]),
        arc(100, 60, 40, -60, 60),
        arc(100, 60, 60, -60, 60),
    ]


def beacon() -> List[Dict[str, Any]]:
    """Сигнальная колонна: две секции под куполом, на основании.

    Тоже нарисована здесь: в чертеже колонна — клеммный блок с подписями
    «Supply GND» и «Supply +», рисунка нет.
    """
    return [
        arc(60, 60, 40, 180, 360),          # купол
        line(20, 60, 20, 140),
        line(100, 60, 100, 140),
        line(20, 100, 100, 100),            # граница секций
        line(20, 140, 100, 140),
        line(0, 160, 120, 160),             # основание
        line(40, 140, 40, 160),
        line(80, 140, 80, 160),
    ]


FIGURES = [
    ("Лампа сигнальная", lamp),
    ("Кнопка", button),
    ("Сирена", siren),
    ("Сигнальная колонна", beacon),
]


def bounds(shapes: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
    xs: List[float] = []
    ys: List[float] = []
    for shape in shapes:
        kind = shape["type"]
        if kind == "line":
            xs += [shape["x1"], shape["x2"]]
            ys += [shape["y1"], shape["y2"]]
        elif kind == "circle":
            xs += [shape["x"], shape["x"] + shape["w"]]
            ys += [shape["y"], shape["y"] + shape["h"]]
        else:
            pts = shape["points"]
            xs += [shape["x"] + v for v in pts[0::2]]
            ys += [shape["y"] + v for v in pts[1::2]]
    return min(xs), min(ys), max(xs), max(ys)


def scene(gap: float = 200.0) -> Dict[str, Any]:
    """Сцена в формате редактора: по группе на фигуру, фигуры в ряд."""
    elements: List[Dict[str, Any]] = []
    left = 0.0
    for label, build in FIGURES:
        shapes = build()
        minx, miny, maxx, maxy = bounds(shapes)
        width = math.ceil((maxx - minx) / GRID) * GRID
        height = math.ceil((maxy - miny) / GRID) * GRID
        group_key = key("group", label)

        children = []
        for index, shape in enumerate(shapes):
            child = dict(shape)
            child["key"] = key(label, index)
            child["parentKey"] = group_key
            child["strokeColor"] = STROKE
            child["bg"] = "transparent"
            child["states"] = [{"id": "1", "name": "Нормальное",
                                "overrides": {}, "isDefault": True}]
            child["id"] = None
            child["parentId"] = None
            children.append(child)

        elements.append({
            "key": group_key, "type": "group",
            "x": left, "y": 0.0, "w": width, "h": height,
            "label": label, "parentKey": "undefined",
            "children": [c["key"] for c in children],
            "composition": [], "isComponent": False,
            "states": [{"id": "1", "name": "Нормальное",
                        "overrides": {}, "isDefault": True}],
            "scripts": [], "bindings": [], "events": [], "properties": [],
            "id": None, "parentId": None,
        })
        elements.extend(children)
        left += width + gap

    return {"format": "SCADA_EDITOR_SCENE", "version": 1,
            "scene": {"name": "CONTUR_extra"}, "elements": elements}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Фигуры, которых нет в библиотеке редактора")
    parser.add_argument("--out", default="CONTUR_extra_components.json",
                        help="куда записать сцену")
    args = parser.parse_args(argv)

    data = scene()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)

    print(f"Записано: {path}")
    for label, build in FIGURES:
        shapes = build()
        minx, miny, maxx, maxy = bounds(shapes)
        print(f"   {label}: габарит {maxx - minx:.0f}x{maxy - miny:.0f}, "
              f"примитивов {len(shapes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
