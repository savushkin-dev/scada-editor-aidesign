# tests/test_geometry.py
# Тесты на места, которые уже были сломаны. Каждый закрывает конкретную
# ошибку из истории — чтобы она не вернулась незамеченной.
#
# Запуск из папки CONTUR:
#     python -m pytest tests -q
#     python tests/test_geometry.py      (без pytest, простым прогоном)
import contextlib
import io
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from contour_detector import (find_all_contour_names_by_proximity, find_contours,
                              point_over_contour)
from data_models import DeviceBox
from pdf_processor import DeviceDetector, DeviceLabeler
from segment_data import SegmentData
from svg_geometry import (_flatten_cubic, _path_points, detect_coordinate_system,
                          get_svg_dimensions,
                          parse_absolute_length, segment_box_overlap, tolerance_scale)


# ------------------------------------------------ разбор path и кривые

def test_path_returns_curve_controls():
    # Опорные точки кривой нужны, чтобы показать дугу дугой: анализ
    # довольствуется хордой, а редактор рисует пришедшее в файле
    points, controls = _path_points(
        "M 10,20 C 30,40 50,60 70,80", with_controls=True)

    assert points == [(10.0, 20.0), (70.0, 80.0)]
    assert controls == [None, ((30.0, 40.0), (50.0, 60.0))]


def test_flattened_curve_keeps_within_tolerance():
    # Хорда на контрольном листе отступает от кривой на 3.27 пт в медиане
    # и до 6.3 — при символе устройства в 31 пт срезанный угол видно
    p0, c1, c2, p3 = (0.0, 0.0), (0.0, 100.0), (100.0, 100.0), (100.0, 0.0)

    for tolerance in (5.0, 1.0, 0.2):
        points = _flatten_cubic(p0, c1, c2, p3, tolerance)
        assert points[0] == p0 and points[-1] == p3, "концы кривой должны совпасть"
        assert len(points) >= 2

        worst = _curve_gap(p0, c1, c2, p3, points)
        assert worst <= tolerance + 1e-6,             f"допуск {tolerance}: отклонение {worst:.3f}"


def test_finer_tolerance_gives_more_pieces():
    p0, c1, c2, p3 = (0.0, 0.0), (0.0, 100.0), (100.0, 100.0), (100.0, 0.0)

    rough = _flatten_cubic(p0, c1, c2, p3, 5.0)
    fine = _flatten_cubic(p0, c1, c2, p3, 0.2)
    assert len(fine) > len(rough)


def test_straight_curve_stays_one_piece():
    # Кривая, вырожденная в прямую, дробиться не должна: лишние элементы
    # на холсте редактора не бесплатны
    points = _flatten_cubic((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0), 1.0)

    assert len(points) == 2


def _curve_gap(p0, c1, c2, p3, points) -> float:
    # Наибольшее расстояние от кривой до ломаной
    import math

    from svg_geometry import _cubic_point

    worst = 0.0
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        lo, hi = i / (len(points) - 1), (i + 1) / (len(points) - 1)
        for j in range(1, 16):
            x, y = _cubic_point(p0, c1, c2, p3, lo + (hi - lo) * j / 16)
            worst = max(worst, abs((b[1] - a[1]) * x - (b[0] - a[0]) * y
                                   + b[0] * a[1] - b[1] * a[0]) / length)
    return worst



def test_path_curve_with_commas():
    # Была регулярка, требовавшая пробел между координатами, а генератор
    # пишет их через запятую. Из-за этого не разбиралась ни одна кривая:
    # 784 участка труб со скруглениями исчезали, разрывая цепочки.
    points = _path_points("M 10.00,20.00 C 30.00,40.00 50.00,60.00 70.00,80.00")
    assert points == [(10.0, 20.0), (70.0, 80.0)]


def test_path_lines_and_spaces():
    assert _path_points("M 1,2 L 3,4 L 5,6") == [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]
    assert _path_points("M 0 0 L 10 10") == [(0.0, 0.0), (10.0, 10.0)]


def test_path_empty():
    assert _path_points("") == []
    assert _path_points(None) == []


# ---------------------------------------------- принадлежность линии рамке

def test_segment_inside_box():
    assert segment_box_overlap(12, 12, 18, 18, 10, 10, 20, 20) == 1.0


def test_segment_outside_box():
    assert segment_box_overlap(0, 0, 5, 5, 10, 10, 20, 20) == 0.0


def test_segment_half_inside():
    assert abs(segment_box_overlap(15, 15, 25, 15, 10, 10, 20, 20) - 0.5) < 1e-9


def test_pipe_crossing_device():
    # Труба насквозь: середина внутри рамки, но принадлежит трубопроводу.
    # Прежняя проверка «середина внутри» красила её как устройство.
    share = segment_box_overlap(0, 15, 100, 15, 10, 10, 20, 20)
    assert share == 0.1


# ------------------------------------------------------- система координат

def _svg(**attrs) -> ET.Element:
    element = ET.Element("svg")
    for key, value in attrs.items():
        element.set(key.replace("_", "-"), str(value))
    return element


def test_percent_size_is_not_canvas_size():
    # '100.000%' превращалось в размер 100, и проценты становились равны
    # сырым PDF пунктам — в экспорте появлялись значения вида 1178%.
    assert parse_absolute_length("100.000%") is None
    assert parse_absolute_length("4210.00pt") == 4210.0


def test_scale_from_pdf_size_is_exact():
    root = _svg(viewBox="0 0 4210 2980")
    name, scale = detect_coordinate_system(root, (3368.0, 2384.0))
    assert abs(scale - 1.25) < 0.01
    assert name.startswith("scaled_")


def test_dimensions_normalized_to_pdf_points():
    root = _svg(viewBox="0 0 4210 2980")
    _, scale = detect_coordinate_system(root, (3368.0, 2384.0))
    width, height = get_svg_dimensions(root, scale)
    assert abs(width - 3368) < 2 and abs(height - 2384) < 2


def test_dimensions_unknown_when_relative():
    # Без viewBox и с относительными размерами определить холст нельзя:
    # экспорт обязан честно перейти на абсолютные координаты
    assert get_svg_dimensions(_svg(width="100%", height="100%")) == (None, None)


def test_tolerance_scale_from_device_size():
    assert tolerance_scale(_svg(data_device_size="32")) == 1.0
    assert abs(tolerance_scale(_svg(data_device_size="16")) - 0.5) < 1e-9
    assert tolerance_scale(_svg()) == 1.0          # атрибута нет
    assert tolerance_scale(_svg(data_device_size="0")) == 1.0


# ------------------------------------------------------- объединение рамок

def test_nested_box_is_duplicate():
    # Рамка 89x89 внутри 200x200 даёт IoU 0.198 — ниже порога 0.5,
    # и вложенный дубликат оставался жить рядом с содержащей его рамкой
    big = DeviceBox(0, 0, 200, 200, "valve", 0.9)
    small = DeviceBox(50, 50, 139, 139, "valve", 0.8)

    iou, iomin = DeviceDetector._overlap(small, big)
    assert iou < DeviceDetector.MERGE_IOU
    assert iomin >= DeviceDetector.MERGE_IOMIN

    kept = DeviceDetector._merge_overlapping([big, small])
    assert len(kept) == 1


def test_most_confident_box_wins():
    # Раньше сортировка шла по площади — оставалась самая крупная рамка,
    # а не самая уверенная
    weak_big = DeviceBox(0, 0, 100, 100, "valve", 0.4)
    strong_small = DeviceBox(10, 10, 90, 90, "valve", 0.95)
    kept = DeviceDetector._merge_overlapping([weak_big, strong_small])
    assert len(kept) == 1 and kept[0].confidence == 0.95


def test_separate_boxes_survive():
    kept = DeviceDetector._merge_overlapping([
        DeviceBox(0, 0, 50, 50, "valve", 0.9),
        DeviceBox(500, 500, 550, 550, "valve", 0.9),
    ])
    assert len(kept) == 2


# ------------------------------------------------------------- имена контуров

def _box(x1, y1, x2, y2):
    # Прямоугольник четырьмя отрезками. Штриховые — контуры собираются
    # только из них: Eplan обводит функциональный блок штрихпунктиром
    return [SegmentData((x1, y1), (x2, y1), True), SegmentData((x2, y1), (x2, y2), True),
            SegmentData((x2, y2), (x1, y2), True), SegmentData((x1, y2), (x1, y1), True)]


def _name_contours(segments, texts, lua_names):
    contours = find_contours(segments)
    with contextlib.redirect_stdout(io.StringIO()):
        find_all_contour_names_by_proximity(contours, segments, texts, lua_names,
                                            config.CONTOUR_NAME_MAX_DISTANCE)
    return {tuple(round(v, 1) for v in c.bounds): c.name for c in contours}


def test_label_over_contour_but_diagonal_to_box():
    assert point_over_contour((100, 50), (90, 100, 200, 300)) is True    # сверху
    assert point_over_contour((50, 150), (90, 100, 200, 300)) is True    # слева
    assert point_over_contour((150, 200), (90, 100, 200, 300)) is True   # внутри
    assert point_over_contour((50, 50), (90, 100, 200, 300)) is False    # по диагонали


def test_nested_box_does_not_steal_contour_name():
    # Лист 5: подпись «+CAB2» стоит в 4 пт над кромкой шкафа и в 71 пт левее
    # вложенного квадратика «-Y1». Контуры разбираются от меньшего к большему,
    # и квадратик забирал подпись себе — до его угла было 73 пт, меньше
    # порога 200. Шкаф оставался безымянным, а три его устройства
    # (DI2, SB1, G1) не сопоставлялись вовсе.
    cabinet = (34.0, 185.4, 442.2, 321.4)
    inner = (119.1, 196.7, 175.7, 230.7)
    segments = _box(*cabinet) + _box(*inner)
    texts = [{"text": "+CAB2", "center": (47.5, 181.0)}]

    names = _name_contours(segments, texts, {"CAB2": {"name_eplan": "CAB2"}})
    assert names[cabinet] == "CAB2"
    assert names[inner] is None


def test_label_above_inner_box_stays_on_it():
    # Обратный случай с контрольного листа: TANK1 подписан прямо над своей
    # рамкой, а та лежит внутри высокой колонки. Подпись должна остаться
    # у рамки, иначе колонка соберёт по одному «-V1» с каждого из 12 рядов.
    column = (408.2, 603.8, 912.8, 2230.9)
    tank = (405.4, 2117.5, 581.1, 2208.3)
    segments = _box(*column) + _box(*tank)
    texts = [{"text": "+TANK1", "center": (421.7, 2109.7)}]

    names = _name_contours(segments, texts, {"TANK1": {"name_eplan": "TANK1"}})
    assert names[tank] == "TANK1"
    assert names[column] is None


def test_nested_box_takes_no_label_from_outside_its_block():
    # Лист 14: подпись «+LINE_M4» стоит в 25 пт правее своего блока и в 43 пт
    # левее тесной рамки, вложенной в соседний блок LINE_M6. Рамку разбирают
    # раньше (она меньше), и она забирала подпись себе — семь сигналов
    # LINE_M4 не сопоставлялись вовсе. Обозначение блока Eplan ставит
    # вплотную к его кромке, но никогда не за пределами объемлющего блока.
    block = (22.7, 60.6, 589.6, 366.8)
    neighbour = (646.3, 60.6, 1133.9, 412.1)
    inner = (657.6, 72.0, 748.3, 151.3)
    segments = _box(*block) + _box(*neighbour) + _box(*inner)
    texts = [{"text": "+LINE_M4", "center": (614.5, 68.3)},
             {"text": "+LINE_M6", "center": (1158.7, 68.3)}]

    names = _name_contours(segments, texts, {})
    assert names[block] == "LINE_M4"
    assert names[neighbour] == "LINE_M6"
    assert names[inner] is None


# --------------------------------------------------------- привязка подписей

def test_label_type_from_full_and_short_name():
    # Регулярка требовала, чтобы всё имя было ТИП+номер, и для полного
    # имени LA_TANK1V12 не срабатывала
    assert DeviceLabeler._label_type("V12") == "V"
    assert DeviceLabeler._label_type("LA_TANK1V12") == "V"
    assert DeviceLabeler._label_type("TANK1FQT1") == "FQT"
    assert DeviceLabeler._label_type("CAB10") == ""


def test_label_goes_to_one_device_only():
    # Подпись назначалась независимо для каждой рамки, и одну метку
    # могли забрать несколько соседних устройств
    boxes = [DeviceBox(0, 0, 40, 40, "valve", 0.9),
             DeviceBox(50, 0, 90, 40, "valve", 0.9)]
    labeler = DeviceLabeler(boxes, [(20.0, 20.0, "V1")])
    names = [labeler.name_for_box(box) for box in boxes]
    assert names.count("V1") == 1


def test_matched_device_beats_raw_label():
    # Сопоставленное устройство знает полное имя, выверенное техобъектом,
    # и должно побеждать сырую подпись с чертежа
    box = DeviceBox(0, 0, 40, 40, "valve", 0.9)
    labeler = DeviceLabeler([box], [(25.0, 20.0, "V1")],
                            matched_devices=[("LA_TANK1V1", 30.0, 20.0)])
    assert labeler.name_for_box(box) == "LA_TANK1V1"


def test_device_types_pattern_prefers_longest():
    # FQT не должен разбираться как QT
    assert config.device_types_pattern().index("FQT") < config.device_types_pattern().index("QT")


def test_class_agreement():
    assert config.device_type_matches_class("V", "valve") is True
    assert config.device_type_matches_class("V", "pump") is False
    assert config.device_type_matches_class("V", "") is None


# ------------------------------------------------------------------ прогон

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
