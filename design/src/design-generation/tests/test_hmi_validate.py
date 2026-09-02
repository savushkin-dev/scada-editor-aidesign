# tests/test_hmi_validate.py
# Самопроверка файла для редактора мнемосхем.
#
# Проверяется сама проверка: она должна ловить то, на чём спотыкается
# редактор, и не ловить того, что спецификация импорта разрешает.
# Иначе приёмка в конвейере превращается в зелёную галочку ни о чём.
#
# Запуск из папки CONTUR:
#     python tests/test_hmi_validate.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.export.hmi_validate import GRID, format_report, validate


def _element(kind, key, **fields):
    element = {"id": None, "key": key, "type": kind, "x": 0.0, "y": 0.0,
               "w": GRID, "h": GRID, "parentId": None, "parentKey": "undefined",
               "children": []}
    element.update(fields)
    return element


def _circle(key="dev", **fields):
    return _element("circle", key, **{"x": 100.0, "y": 100.0, "w": 40.0,
                                      "h": 40.0, "radius": 20.0, **fields})


def _line(key="pipe", **fields):
    return _element("line", key, **{"x": 50.0, "y": 0.0, "w": 100.0, "h": 0.0,
                                    "x1": 0.0, "y1": 0.0, "x2": 100.0,
                                    "y2": 0.0, **fields})


def _text(key="lbl", **fields):
    return _element("text", key, **{"x": 20.0, "y": 20.0, "w": 60.0, "h": 20.0,
                                    "text": "V1", "font_size": 12.0, **fields})


def _group(key="grp"):
    frame = _element("rectangle", "frm", x=0.0, y=0.0, w=100.0, h=100.0,
                     parentKey=key)
    group = _element("group", key, x=40.0, y=40.0, w=100.0, h=100.0,
                     children=["frm"])
    return [group, frame]


def _problems(elements):
    return validate(elements)[0]


# ---------------------------------------------------------------- годный файл

def test_good_file_has_no_remarks():
    assert _problems([_circle(), _line(), _text(), *_group()]) == []


def test_not_an_array_is_refused():
    assert _problems({"type": "circle"})
    assert _problems([])


# ---------------------------------------------------------------- сетка

def test_object_off_the_grid_is_caught():
    # Схема, пришедшая не по узлам, разъезжается по мере работы с ней,
    # и починить это в редакторе нельзя
    assert _problems([_text(x=27.0)])
    assert _problems([_circle(x=101.0)])


def test_group_off_the_grid_is_caught():
    group, frame = _group()
    group["x"] = 53.0
    assert _problems([group, frame])


def test_group_without_a_frame_is_caught():
    group, frame = _group()
    frame["type"] = "circle"
    frame["radius"] = 20.0
    frame["w"] = frame["h"] = 40.0
    assert any("рамки" in p for p in _problems([group, frame]))


# ---------------------------------------------------------------- круг

def test_small_radius_is_caught():
    assert _problems([_circle(radius=14.0, w=28.0, h=28.0)])


def test_radius_off_the_grid_is_caught():
    assert _problems([_circle(radius=30.0, w=60.0, h=60.0)])


def test_box_must_equal_two_radii():
    assert _problems([_circle(radius=20.0, w=41.0, h=40.0)])


# ---------------------------------------------------------------- ссылки

def test_one_sided_link_is_caught():
    group, frame = _group()
    group["children"] = []
    assert any("обратной ссылки" in p for p in _problems([group, frame]))


def test_unknown_parent_is_caught():
    assert any("не найден" in p for p in _problems([_circle(parentKey="нет")]))


def test_duplicate_keys_are_caught():
    assert any("повторяются" in p for p in _problems([_circle(), _circle()]))


def test_server_id_is_caught():
    # С непустым id элемент притворяется уже существующим на их бэкенде
    assert _problems([_circle(id="42")])


# ---------------------------------------------------------------- чертёж

def test_drawing_line_off_the_grid_is_not_a_problem():
    # Требовать кратности от каждого отрезка нельзя: диагонали
    # и разложенные кривые заметно деформируются
    problems, stats = validate([_line(x1=3.0, y1=7.0, x2=93.0, y2=7.0)])

    assert problems == []
    assert stats["ортогональные_вне_сетки"] == 1


def test_short_line_is_counted_not_refused():
    problems, stats = validate([_line(x1=0.0, y1=0.0, x2=8.0, y2=0.0, w=8.0, x=4.0)])

    assert problems == []
    assert stats["короткие_отрезки"] == 1


def test_collapsed_line_is_refused():
    # Отрезок нулевой длины — элемент, который нельзя ни увидеть, ни взять
    assert _problems([_line(x1=10.0, y1=10.0, x2=10.0, y2=10.0)])


def test_hairline_is_caught():
    assert _problems([_line(stroke_width=0.1)])


def test_diagonals_are_counted_separately():
    _, stats = validate([_line(x1=0.0, y1=0.0, x2=100.0, y2=100.0)])

    assert stats["диагонали"] == 1
    assert stats["ортогональные_вне_сетки"] == 0


# ---------------------------------------------------------------- прочее

def test_small_font_is_caught():
    assert any("кегль" in p for p in _problems([_text(font_size=8.0)]))


def test_percent_coordinates_are_caught():
    # Проценты строкой импорт редактора умножает на 5000 по обеим осям,
    # а лист не квадратный
    assert _problems([_circle(x="73.1%")])


def test_big_sheet_is_measured_but_not_blamed():
    """Крупный лист — это размер, а не поломка.

    Проверка шла от «мира 5000x5000» из спецификации, и лист A0 стоял
    красным всегда. Мира этого не существует: размер сцены задаётся
    блоком canvas и служит рамкой, а не пределом (§7a), координаты за ней
    работают как обычно. Размер при этом важен сам по себе и остаётся
    в отчёте числом.
    """
    far = _circle(x=6000.0, y=100.0)

    problems, stats = validate([far])
    assert not [p for p in problems if "не влезает" in p], "размер листа — не замечание"
    assert stats["холст_ширина"] >= 6000, "размер листа потерян"
    assert "рамка сцены" in format_report(problems, stats)


def test_sheet_size_off_the_grid_is_caught():
    # По объявленному размеру редактор рисует рамку сцены, и §7a требует
    # от него кратности сетке. Меряется именно объявленный блок, а не
    # габарит содержимого: у диагоналей координаты точные и по §3.1 такими
    # и остаются
    meta = {"key": "meta", "type": "meta", "parentKey": "undefined",
            "canvas": {"width": 11900, "height": 8400, "grid": 20}}
    assert not [p for p in validate([_circle(), meta])[0] if "canvas" in p]

    meta["canvas"]["height"] = 8433.5
    assert [p for p in validate([_circle(), meta])[0] if "canvas.height" in p]


def test_symbol_parts_are_not_measured_by_the_grid():
    # Внутренности готовой фигуры — её собственный рисунок: при размере
    # меньше натурального узлы делятся, и требовать от них сетки значило бы
    # требовать перерисовать фигуру
    part = _circle(x=137.0, y=213.0, radius=10.0, w=20.0, h=20.0)
    part["contur_symbol_part"] = True

    problems, stats = validate([part])
    assert problems == [], f"внутренность фигуры сочли поломкой: {problems}"
    assert stats["внутри_символов"] == 1


def test_meta_is_not_measured_as_a_shape():
    # Элемент с данными о листе — не фигура: нулевой габарит для него
    # не поломка
    meta = _element("meta", "meta", w=0.0, h=0.0, contur_meta=True)
    assert _problems([meta, _circle()]) == []


if __name__ == "__main__":
    failures = 0
    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]

    for name, test in tests:
        try:
            test()
            print(f"  OK    {name}")
        except AssertionError as e:
            failures += 1
            print(f"  СБОЙ  {name}: {e or 'проверка не прошла'}")
        except Exception as e:
            failures += 1
            print(f"  СБОЙ  {name}: {type(e).__name__}: {e}")

    print(f"\nВсего: {len(tests)}, сбоев: {failures}")
    sys.exit(1 if failures else 0)
