# tests/test_hmi_export.py
# Выгрузка в формате редактора мнемосхем — то, что уходит в конечный проект.
#
# Проверки здесь не про красоту схемы, а про пригодность файла: редактор
# ждёт плоский массив элементов холста с числовыми координатами, настоящими
# null и true, и своим ключом у каждого элемента. Первая попытка передачи
# как раз и не отобразилась: отдавали дерево PlantGeometry, а среди образцов
# ходили файлы с координатами строками («73.1%») и ключами "null" строкой.
# Каждая проверка ниже закрывает одну такую мелочь.
#
# Запуск из папки CONTUR:
#     python tests/test_hmi_export.py
import contextlib
import io
import json
import math
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import hmi_export
import hmi_symbols
from hmi_export import HMIExporter, export_current_visualization_hmi
import export_scene
from dataclasses import replace

from test_json_export import (
    CONTOURS, MARKED_SVG, MATCHES, PAGE, _FakeObjectsData,
)

ROOT = Path(__file__).resolve().parent.parent

# Масштаб, который выгрузка подберёт для этого листа: устройство должно
# занять столько клеток, сколько занимает готовая фигура библиотеки
# (hmi_export._sheet_scale). У синтетического листа data-device-size нет,
# значит символ считается обычным — 32 пункта
SCALE = (hmi_symbols.DEFAULT_SYMBOL_CELLS * hmi_export.GRID
         / hmi_export.REFERENCE_DEVICE_SIZE)

# Тот же лист, но нарисованный по-старому: устройство своим символом
# с чертежа, две клетки на обычный символ листа
DRAWING_SCALE = hmi_export.MIN_OBJECT_SIZE / hmi_export.REFERENCE_DEVICE_SIZE


def _elements(**kwargs):
    """Выгружает синтетический лист и возвращает разобранный массив."""
    workdir = Path(tempfile.mkdtemp(prefix="contur_hmi_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(MARKED_SVG, encoding="utf-8")
    out_path = workdir / "hmi.json"

    exporter = HMIExporter(pdf_size=PAGE, **kwargs)
    with contextlib.redirect_stdout(io.StringIO()):
        assert exporter.export(str(svg_path), str(out_path), MATCHES, CONTOURS)

    return json.loads(out_path.read_text(encoding="utf-8"))


def _elements_with(matches, **kwargs):
    """Тот же лист, но с подменённым набором устройств."""
    workdir = Path(tempfile.mkdtemp(prefix="contur_hmi_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(MARKED_SVG, encoding="utf-8")
    out_path = workdir / "hmi.json"

    exporter = HMIExporter(pdf_size=PAGE, **kwargs)
    with contextlib.redirect_stdout(io.StringIO()):
        assert exporter.export(str(svg_path), str(out_path), matches, CONTOURS)

    return json.loads(out_path.read_text(encoding="utf-8"))


def _devices(elements):
    # Устройство — цельный объект (группа со своим символом внутри) или
    # кружок-маркер, смотря в каком виде его попросили. Признак один
    return [e for e in elements if e.get("contur_device")]


def _drawing_lines(elements):
    # Линия чертежа отличается от стороны рамки контура полем color:
    # «red» — контур устройства, «blue» — труба
    # Линия чертежа отличается от рамки полем contur_color: «red» —
    # контур устройства, «blue» — труба. Своё поле, потому что в сцене
    # редактора `color` означает заливку фигуры
    return [e for e in elements if e["type"] == "line" and "contur_color" in e]


def _frames(elements):
    # Рамка техобъекта — прямоугольник, а не четыре линии. У устройства
    # своя рамка внутри его объекта, она сюда не относится
    return [e for e in elements
            if e["type"] == "rectangle" and not e.get("contur_device_frame")
            and not e.get("contur_tank_frame")]


def _tech_groups(elements):
    # Группы техобъектов, а не устройств
    return [e for e in elements
            if e["type"] == "group" and not e.get("contur_device")
            and not e.get("contur_tank")]


def _texts(elements):
    # Наши подписи: имена контуров и обозначения устройств
    return [e for e in elements if e["type"] == "text" and not e.get("drawing")]


def _sheet_texts(elements):
    # Надписи самого чертежа, перерисованные из PDF
    return [e for e in elements if e["type"] == "text" and e.get("drawing")]


def _place(elements, x, y):
    """Где точка листа (в пунктах) окажется на холсте.

    Лист масштабируется под сетку и сдвигается в начало координат,
    поэтому сравнивать с исходными пунктами больше нельзя. Масштаб берётся
    из самой выгрузки: он зависит от того, чем показано устройство —
    готовой фигурой в шесть клеток или кружком в две.
    """
    canvas = _meta(elements)["canvas"]
    scale, origin = canvas["scale"], canvas["origin"]
    return (x * scale - origin[0], y * scale - origin[1])


def _meta(elements):
    return next((e for e in elements if e.get("contur_meta")), None)


def _with_operations(**kwargs):
    """Выгружает лист, подменив описание операций на игрушечное.

    Настоящее приходит из main.objects.lua; проверкам нужно знать, что
    состояния устройства доезжают до элемента, а не какие они бывают.
    """
    was = export_scene.objects_data
    export_scene.objects_data = _FakeObjectsData()
    try:
        return _elements(**kwargs)
    finally:
        export_scene.objects_data = was


# ---------------------------------------------------------------- форма файла

def test_file_is_flat_array():
    # Дерево PlantGeometry редактор не разбирает: файл открывается,
    # а на холсте пусто. Ради этого всё и затевалось
    elements = _elements()

    assert isinstance(elements, list), "редактор ждёт массив элементов, а не объект"
    assert elements, "массив пуст"
    assert all(isinstance(e, dict) and "type" in e and "key" in e for e in elements)


def test_coordinates_are_numbers():
    # Проценты строкой редактор координатой не считает
    elements = _elements()

    for element in elements:
        for field in ("x", "y", "w", "h", "x1", "y1", "x2", "y2"):
            if field in element:
                assert isinstance(element[field], (int, float)), \
                    f"{element['type']}.{field} = {element[field]!r}, а нужно число"


def test_nulls_and_flags_are_real():
    # В образцах ходили строки "null" и "false" — редактор ждёт настоящие
    elements = _elements()

    for element in elements:
        assert element["id"] is None, "id должен быть null, а не строкой"
        assert element["parentId"] is None
        # composition не шлётся вовсе: в редакторе это массив ключей
        # примитивов компонента, а не «контейнер ли». У группы поле его же
        assert "composition" not in element or element["type"] == "group"
        for state in element["states"]:
            assert isinstance(state["isDefault"], bool)


def test_every_element_has_its_own_key():
    # По ключам элементы ссылаются друг на друга; одинаковый «null» у всех
    # означает, что ссылаться нечем
    elements = _elements()
    keys = [e["key"] for e in elements]

    assert len(set(keys)) == len(keys), "ключи повторяются"
    for key in keys:
        uuid.UUID(key)  # бросит ValueError, если это не uuid


def test_states_are_filled():
    # Штатный список редактора: ровно одно состояние с пустым overrides.
    # Так велит спецификация импорта (§7) — иначе базовые x/y/w/h
    # элемента при отрисовке игнорируются. Состояния по операциям
    # уезжают отдельным полем contur_states
    elements = _elements()

    for element in elements:
        states = element["states"]
        assert len(states) == 1, "у элемента должно быть одно состояние"
        assert states[0]["name"] == "Нормальное"
        assert states[0]["isDefault"] is True
        assert states[0]["overrides"] == {}
        uuid.UUID(states[0]["id"])


def test_same_sheet_gives_same_file():
    # Ключи выводятся из содержимого, а не случайные: иначе каждая выгрузка
    # отличается от предыдущей целиком и сравнить их нельзя
    first, second = _elements(), _elements()

    assert [e["key"] for e in first] == [e["key"] for e in second]


# ---------------------------------------------------------------- содержание

def test_devices_and_lines_are_exported():
    elements = _elements()

    devices = _devices(elements)
    lines = [e for e in elements if e["type"] == "line"]

    assert len(devices) == len(MATCHES), "выгружены не все устройства"
    assert lines, "линии чертежа не выгружены"
    assert {d["lua_name"] for d in devices} == {"TANK1V1", "TANK1V2"}


def test_device_keeps_its_meaning():
    # Редактор лишние поля игнорирует, а по ним видно, что за устройство
    device = next(d for d in _devices(_elements()) if d["lua_name"] == "TANK1V1")

    assert device["pdf_name"] == "-V1"
    assert device["tech_object"] == "TANK1"
    assert device["device_type"] == "V"
    assert device["descr"] == "Клапан нижнего слива"
    assert device["label"] == "TANK1V1", "подпись элемента — имя устройства"


def test_device_size_comes_from_geometry():
    # Размер приходит из чертежа, а не берётся с потолка: рамка устройства
    # на синтетическом листе 30x30 пт. На холсте он округляется до клетки.
    # Это про устройство, нарисованное своим символом с чертежа: у готовой
    # фигуры размер свой, см. test_library_symbol_keeps_the_grid
    device = next(d for d in _devices(_elements(symbols="drawing"))
                  if d["lua_name"] == "TANK1V1")

    assert abs(device["w"] - 30 * DRAWING_SCALE) <= hmi_export.GRID,         f"размер {device['w']} не похож на рамку 30 пт в единицах холста"
    assert device["w"] == device["h"]

def test_symbol_size_falls_back_to_the_usual_one():
    # Без своего скопления красных линий устройству доставались жёсткие 20 пт,
    # заметно мельче обычного символа листа — в редакторе такой датчик
    # выглядел чужим среди соседей
    elements = _elements()
    usual = hmi_export.REFERENCE_DEVICE_SIZE

    for device in _devices(elements):
        assert device["w"] >= usual * hmi_export.MIN_DEVICE_RATIO,             f"{device['lua_name']}: символ мельче половины обычного"


def test_circle_box_is_exactly_two_radii():
    # Принимающая сторона проверяет равенство габарита двум радиусам,
    # а округление радиуса и габарита порознь расходилось на 0.001
    for device in _devices(_elements(scale=1.7)):
        if device["type"] != "circle":
            continue
        assert device["w"] == device["h"] == 2 * device["radius"],             f"{device['lua_name']}: {device['w']} != 2*{device['radius']}"


def test_stretched_cluster_does_not_give_a_giant_symbol():
    # Кластер красных линий прихватывает соседние отводы: на контрольном
    # листе у 105 устройств из 233 высота выходила до 482 пт вместо тридцати,
    # и такой «датчик» накрыл бы в редакторе пол-схемы
    exporter = HMIExporter(pdf_size=PAGE)
    exporter.scene = None   # обычный размер символа неизвестен — берётся 32 пт

    assert exporter._symbol_size(482.0) <= 48.0, "габарит не ограничен"
    assert exporter._symbol_size(2.0) >= 16.0, "слишком мелкий символ не виден"
    assert exporter._symbol_size(30.0) == 30.0, "нормальный размер менять незачем"


def test_device_is_a_whole_object_by_default():
    """Устройство приезжает одной фигурой, а не россыпью отрезков.

    Кружок-маркер поверх чертежа редактору не нужен: ему нужен
    объект, который выделяется и двигается целиком и несёт на себе всё,
    что об устройстве известно. Символ — те же линии с чертежа, только теперь
    они дети своей группы.
    """
    elements = _elements()

    for device in _devices(elements):
        assert device["type"] == "group", "устройство должно быть цельным объектом"
        assert device["children"], "у объекта нет ни рамки, ни символа"

        first = next(e for e in elements if e["key"] == device["children"][0])
        assert first["type"] == "rectangle", "первым ребёнком должна быть рамка"
        assert first["contur_device_frame"] is True

        for child_key in device["children"]:
            child = next(e for e in elements if e["key"] == child_key)
            assert child["parentKey"] == device["key"], "связь не двусторонняя"


def test_device_symbol_moves_inside_its_object():
    # Линии символа не должны остаться и снаружи: иначе они нарисуются
    # дважды и будут выбираться отдельно от своего устройства
    elements = _elements()
    inside = {k for d in _devices(elements) for k in d["children"]}

    top_level = [e for e in elements
                 if e["type"] == "line" and e["parentKey"] == "undefined"]
    assert not (inside & {e["key"] for e in top_level}), "символ остался и снаружи"

    with_symbol = [d for d in _devices(elements) if len(d["children"]) > 1]
    assert with_symbol, "ни у одного устройства нет своего символа"


def test_devices_can_be_circles_or_dropped():
    # Прежний вид остаётся по просьбе, и устройства можно убрать вовсе —
    # данные о них в любом случае лежат в meta
    circles = _devices(_elements(devices="circle"))
    assert circles and all(d["type"] == "circle" for d in circles)

    assert not _devices(_elements(devices="none"))

def test_circle_box_is_square():
    # Редактор строит круг по w/h, и при w != h он выходил сплющенным:
    # на листе mozzarella так рисовались 26 устройств из 35
    for device in _devices(_elements(devices="circle")):
        assert device["w"] == device["h"], f"{device['lua_name']}: круг стал овалом"

def test_no_shape_arrives_without_its_geometry():
    # Ромбы в редакторе — это polygon без списка точек:
    # редактор строит по своему `sides` правильный многоугольник в габарите
    for mode in ("object", "circle"):
        for element in _elements(devices=mode):
            if element["type"] != "polygon":
                continue
            # Многоугольник допустим только со своим списком точек:
            # из него собраны готовые фигуры библиотеки
            assert element.get("points"), "многоугольник без points даст ромб"
            assert len(element["points"]) >= 6, "многоугольнику мало точек"

    for device in _devices(_elements(devices="circle")):
        assert device["type"] == "circle" and device["radius"] > 0

def test_child_references_resolve():
    # Импортёр переводит children и parentKey по карте ключей, а ключ,
    # которого в файле нет, оставляет как есть — получается битая ссылка
    elements = _elements(groups=True)
    keys = {e["key"] for e in elements}

    for element in elements:
        for child in element["children"]:
            assert child in keys, f"ссылка на несуществующий элемент: {child}"
        parent = element["parentKey"]
        assert parent == "undefined" or parent in keys, f"битый parentKey: {parent}"


def test_line_carries_both_ends_and_centre():
    line = _drawing_lines(_elements())[0]

    assert abs(line["x"] - (line["x1"] + line["x2"]) / 2) < 0.01, \
        "x линии — середина между концами"
    assert abs(line["y"] - (line["y1"] + line["y2"]) / 2) < 0.01
    assert abs(line["w"] - abs(line["x2"] - line["x1"])) < 0.01
    assert line["contur_color"] in ("red", "blue")


# ------------------------------------------------- контуры, имена, подписи

def test_contour_has_frame_and_name():
    # Рамка техобъекта — один прямоугольник: его можно выделить и подвинуть
    # целиком, а четыре линии приходилось собирать глазами
    elements = _elements(contour_frames=True)

    frames = _frames(elements)
    assert len(frames) == len(CONTOURS), "рамка контура — один прямоугольник"

    frame = frames[0]
    minx, miny, maxx, maxy = CONTOURS[0].bounds
    left, top = _place(elements, minx, miny)
    right, bottom = _place(elements, maxx, maxy)
    assert abs(frame["x"] - left) <= 10 and abs(frame["y"] - top) <= 10,         "рамка не по границам контура"
    # Угол и габарит садятся на сетку порознь, поэтому дальний край
    # вправе разойтись с границей контура на целую клетку, а не на полклетки
    assert abs(frame["x"] + frame["w"] - right) <= hmi_export.GRID
    assert abs(frame["y"] + frame["h"] - bottom) <= hmi_export.GRID
    # borderColor их нормализатор переводит только у линии, круга и текста
    assert frame["strokeColor"] == config.tech_object_color("TANK1")
    assert frame["contour"] is True and frame["tech_object"] == "TANK1"

    name = next(t for t in _texts(elements) if t.get("contour"))
    assert name["text"] == "TANK1" and name["label"] == "TANK1"
    assert name["tech_object"] == "TANK1"
    # Сдвиг подписи задан клетками холста, а не пунктами листа: в пунктах
    # он менялся бы вместе с масштабом листа и на крупном листе уезжал
    x, y = _place(elements, *CONTOURS[0].center)
    x += hmi_export.CONTOUR_LABEL_CELLS[0] * hmi_export.GRID
    y += hmi_export.CONTOUR_LABEL_CELLS[1] * hmi_export.GRID
    assert abs(name["x"] - x) <= hmi_export.GRID
    assert abs(name["y"] - y) <= hmi_export.GRID

def test_sheet_frame_is_kept_and_marked():
    # Отсев рамки выбрасывал отрезок, если любой его конец попал в поле
    # листа, и уносил живую геометрию — отсюда «линии обрываются».
    # Теперь чертёж уезжает целиком, а полоса поля помечена
    elements = _elements()
    lines = [e for e in elements if e["type"] == "line"]
    framed = [e for e in lines if e.get("frame")]

    assert all(e.get("line_id") is None for e in framed),         "у рамки нет номера сегмента: разбор геометрии её не видел"

    without = _elements(frame=False)
    assert len([e for e in without if e["type"] == "line"]) == len(lines) - len(framed)


def test_frame_is_not_mistaken_for_a_pipe():
    # У рамки техобъекта нет поля color: по нему отличают трубу от контура
    # устройства, а рамка — ни то, ни другое
    elements = _elements()

    for frame in _frames(elements):
        assert "contur_color" not in frame, "рамка притворяется чертежом"
        assert frame["type"] == "rectangle"

    for line in _drawing_lines(elements):
        assert line["contur_color"] in ("red", "blue")


def test_every_device_has_a_label():
    elements = _elements(labels=True, devices="circle")
    labels = [t for t in _texts(elements) if not t.get("contour")]

    assert len(labels) == len(MATCHES), "подписи есть не у всех устройств"

    label = next(t for t in labels if t["lua_name"] == "TANK1V1")
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    # Подпись — pdf_name, а при неполной уверенности ещё и она в скобках
    assert label["text"] == "-V1 (0.9)"
    # Сдвиг тот же, что в окне, но целыми клетками: устройство сидит в узле
    # сетки, и сдвиг меньше клетки привязка съела бы — подпись легла бы
    # на сам кружок
    assert label["x"] == device["x"] + hmi_export.GRID, "сдвиг не как в окне"
    assert label["y"] == device["y"] - hmi_export.GRID

def test_colours_come_from_the_same_place_as_the_window():
    # Палитры лежат в config, чтобы выгрузка красила тем же, что окно
    device = next(d for d in _devices(_elements(devices="circle"))
                  if d["device_type"] == "V")
    assert device["bg"] == config.DEVICE_TYPE_COLORS["V"]
    assert device["borderColor"] == config.DEVICE_TYPE_COLORS["V"]

    frame = _frames(_elements(contour_frames=True))[0]
    assert frame["strokeColor"] == config.tech_object_color("TANK1")

def test_tech_object_colour_does_not_jump_between_runs():
    # Раньше цвет контура выбирался через hash(str), а он рандомизируется
    # при каждом запуске Python: у объекта менялся цвет от запуска к запуску
    import subprocess

    code = ("import sys; sys.path.insert(0, r'%s'); import config; "
            "print(config.tech_object_color('TANK1'))" % str(ROOT))
    runs = {subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True).stdout.strip() for _ in range(3)}

    assert len(runs) == 1, f"цвет объекта пляшет между запусками: {runs}"


def test_drawing_order_matches_the_window():
    # Порядок в массиве — это порядок отрисовки: сперва данные, потом
    # чертёж и его надписи, устройства поверх чертежа, подписи сверху
    kinds = []
    # Ёмкости просим явно: без них слоя «tank» в массиве не будет —
    # с выгруженным чертежом они не рисуются (см. _wanted_tanks)
    elements = _elements(contour_frames=True, labels=True, devices="circle",
                         tanks="1")
    tanks = {e["key"] for e in elements if e.get("contur_tank")}
    for element in elements:
        if element.get("contur_meta"):
            kinds.append("meta")
        elif (element.get("contur_tank") or element.get("contur_tank_frame")
              or (element.get("contur_symbol_part")
                  and element["parentKey"] in tanks)):
            kinds.append("tank")
        elif element.get("drawing"):
            kinds.append("sheet-text")
        elif element["type"] == "text":
            kinds.append("text")
        elif element.get("contour"):
            kinds.append("frame")
        elif element["type"] == "line":
            kinds.append("line")
        else:
            kinds.append("device")

    order = [kind for index, kind in enumerate(kinds)
             if index == 0 or kind != kinds[index - 1]]
    # Надписи чертежа лежат вместе с ним: это тот же слой, что линии,
    # а подписи устройств по-прежнему сверху всего
    assert order == ["meta", "tank", "frame", "line", "sheet-text", "device", "text"],         f"порядок слоёв: {order}"


def test_device_object_comes_after_the_drawing():
    # Устройство — цельный объект, и его символ едет внутри него, поэтому
    # линии символа стоят в массиве после самого объекта
    elements = _elements()
    order = {e["key"]: i for i, e in enumerate(elements)}

    for device in _devices(elements):
        for child in device["children"]:
            assert order[child] > order[device["key"]],                 "ребёнок объекта раньше самого объекта"

def test_contours_and_labels_can_be_switched_off():
    # По умолчанию их и нет: редактору нужен чертёж и данные,
    # а рамки и подписи — разметка поверх него
    assert not _frames(_elements()) and not _texts(_elements())

    bare = _elements(contour_frames=False, labels=False)

    assert not _frames(bare) and not _texts(bare)
    assert _devices(bare) and _drawing_lines(bare), "остальное должно остаться"
    assert _sheet_texts(bare), "надписи чертежа выключаются отдельно"


# ------------------------------------------------- состояния и остальные данные

def test_device_states_come_from_operations():
    # То, ради чего всё и делалось: у устройства есть каждое место описания
    # операций, где оно открывается или закрывается
    elements = _with_operations()
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    states = device["contur_states"]
    assert len(states) == 2, "состояния из операций не доехали"

    step = next(s for s in states if s.get("step_number") == 1)
    assert step["status"] == "opened" and step["status_text"] == "открыто"
    assert step["operation_id"] == "OP1" and step["operation"] == "Мойка"
    assert step["state"] == "Наполнение" and step["step"] == "Шаг 1"
    assert "Мойка" in step["name"] and "открыто" in step["name"]
    assert step["isDefault"] is False


def test_state_without_a_step_keeps_its_operation():
    # Устройство бывает открыто целым состоянием, а не отдельным шагом
    elements = _with_operations()
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V2")

    state = device["contur_states"][0]
    assert state["status"] == "closed"
    assert "step_number" not in state, "шага здесь нет, и поля быть не должно"
    assert state["state_id"] == "OP1_1"


def test_state_names_are_unique_within_a_device():
    # Имена операций и техобъектов в описании не уникальны, а состояние
    # выбирают по имени: в списке одного элемента они обязаны различаться
    elements = _with_operations()

    for device in _devices(elements):
        names = [s["name"] for s in device["contur_states"]]
        assert len(set(names)) == len(names), f"повтор имени состояния: {names}"


def test_state_colours_can_be_switched_off():
    coloured = _with_operations()
    plain = _with_operations(state_colors=False)

    device = next(d for d in _devices(coloured) if d["lua_name"] == "TANK1V1")
    opened = next(s for s in device["contur_states"] if s.get("status") == "opened")
    assert opened["overrides"]["bg"] == config.DEVICE_STATE_COLORS["opened"]

    device = next(d for d in _devices(plain) if d["lua_name"] == "TANK1V1")
    assert all(s["overrides"] == {} for s in device["contur_states"])


def test_states_can_be_switched_off():
    elements = _with_operations(states=False)

    for device in _devices(elements):
        assert "contur_states" not in device
        assert len(device["states"]) == 1


def test_device_carries_the_same_fields_as_xml():
    # Раньше из полей XML доезжали только описание и артикул: категория,
    # подтип и всё пришедшее из Lua оставались только в PlantGeometry
    elements = _elements()
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    assert device["descr"] == "Клапан нижнего слива"
    assert device["article"] == "SE.XB4BS8445"
    assert device["subtype_num"] == 3, "поля из Lua должны доезжать как есть"
    assert "пустое" not in device and "нет" not in device


def test_device_carries_its_tags():
    """Каналы ввода-вывода доезжают до мнемосхемы.

    Сопоставление брало из описания устройства только имя, артикул
    и подтип, а адрес в контроллере (node, offset, порт) выбрасывало —
    файл описывал, что нарисовано, но не к чему это подключено.
    """
    device = next(d for d in _devices(_elements()) if d["lua_name"] == "TANK1V1")

    tags = device["contur_tags"]
    assert tags["DI"][0]["node"] == 1
    assert tags["DI"][0]["offset"] == 1617
    assert tags["par"] == [5000, 1]


def test_device_without_tags_has_no_field():
    # Пустое поле хуже отсутствующего: по нему не отличить «нет каналов»
    # от «каналы потерялись»
    device = next(d for d in _devices(_elements()) if d["lua_name"] == "TANK1V2")

    assert "contur_tags" not in device


def test_current_operation_reaches_the_device():
    elements = _with_operations(current_operation_id="OP1")

    opened = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")
    assert opened["operation_state"] == "открыто"
    assert opened["operation_state_name"] == "Наполнение"
    assert opened["operation_step_number"] == 1

    other = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V2")
    assert other["operation_state"] == "не используется"


def test_pipe_knows_its_pipeline():
    # Трубопровод был только в XML отдельной секцией, а на холсте лежал
    # россыпью отрезков — связать их было нечем
    elements = _elements()
    pipes = [e for e in _drawing_lines(elements) if e["contur_color"] == "blue"]

    assert pipes, "синих линий нет"
    numbered = [p for p in pipes if "pipeline_id" in p]
    assert numbered, "у линий нет номера трубопровода"
    for pipe in numbered:
        assert isinstance(pipe["pipeline_id"], int)
        assert pipe["pipeline_name"]


def test_device_lists_its_neighbours():
    """Связность доезжает до самого устройства, а не только в секцию.

    Проверяется на собранном графе, а не на выгрузке: синтетический лист
    даёт трубы, но ни одной, которая касалась бы двух устройств сразу,
    а настоящий размеченный лист в репозитории не лежит (golden.py).
    """
    exporter = HMIExporter(pdf_size=PAGE)
    exporter._graph = {"neighbours": {"TANK1V1": ["M12V1", "TANK1V2"]}}

    assert exporter._connections(MATCHES[0]) == {
        "connected_devices": ["M12V1", "TANK1V2"]}
    assert exporter._connections(MATCHES[1]) == {}, "соседей нет — поля быть не должно"


def test_sheet_texts_are_exported():
    # Надписи чертежа лежали в разметке всегда, а в выгрузку не попадали
    elements = _elements()
    texts = _sheet_texts(elements)

    assert len(texts) == 2, "надписи чертежа не доехали"

    title = next(t for t in texts if t["text"] == "Схема мойки")
    assert title["label"] == title["text"], "строка дублируется в label"
    x, y = _place(elements, 200, 600)
    assert abs(title["x"] - x) <= 10
    # В SVG y — базовая линия, у элемента text привязка к верху строки
    assert title["y"] < y
    assert title["font_size"] >= hmi_export.MIN_FONT_SIZE

def test_sheet_texts_can_be_switched_off():
    assert not _sheet_texts(_elements(texts=False))


def test_meta_describes_the_sheet():
    # Секциям XML (трубы, связи, точки сопряжения, операции) на холсте
    # места нет — они уезжают одним элементом
    elements = _elements()
    meta = _meta(elements)

    assert meta is not None, "элемента meta нет"
    assert meta["type"] == "meta" and meta["contur_meta"] is True
    assert meta["sheet"]["width"] == PAGE[0], "размер листа в пунктах"
    assert meta["sheet"]["height"] == PAGE[1]
    # Размер листа меряется по содержимому и кратен сетке: по нему
    # редактор рисует рамку сцены и считает координаты в процентах (§7a)
    assert meta["canvas"]["width"] > 0 and meta["canvas"]["height"] > 0
    assert meta["canvas"]["width"] % 20 == 0
    assert meta["canvas"]["height"] % 20 == 0
    assert meta["canvas"]["grid"] == 20
    tanks = [e for e in elements if e.get("contur_tank")]
    assert meta["counts"]["group"] == len(MATCHES) + len(tanks)
    assert meta["pipelines"], "трубопроводов в meta нет"
    assert meta["junction_points"], "точек сопряжения в meta нет"

    tech_object = next(o for o in meta["tech_objects"] if o["name"] == "TANK1")
    assert tech_object["devices"] == ["TANK1V1", "TANK1V2"]
    minx, miny, maxx, maxy = CONTOURS[0].bounds
    left, top = _place(elements, minx, miny)
    right, bottom = _place(elements, maxx, maxy)
    assert tech_object["contour"]["bounds"] == [left, top, right, bottom]


def test_sheet_size_stays_on_grid_behind_a_diagonal():
    """Диагональ дальше всех не должна утаскивать размер листа с сетки.

    Ортогональные отрезки садятся на узлы, а диагонали и звенья кривых
    по §3.1 остаются с точными координатами. Стоит такой линии оказаться
    крайней — и край листа перестаёт быть кратным 20, а по нему редактор
    рисует рамку сцены.
    """
    workdir = Path(tempfile.mkdtemp(prefix="contur_hmi_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(
        MARKED_SVG.replace(
            "</svg>",
            '  <line x1="450" y1="500" x2="520.7" y2="610.3" '
            'stroke="blue" stroke-width="2"/>\n</svg>'),
        encoding="utf-8")
    out_path = workdir / "hmi.json"

    exporter = HMIExporter(pdf_size=PAGE)
    with contextlib.redirect_stdout(io.StringIO()):
        assert exporter.export(str(svg_path), str(out_path), MATCHES, CONTOURS)

    canvas = _meta(json.loads(out_path.read_text(encoding="utf-8")))["canvas"]
    assert canvas["width"] % hmi_export.GRID == 0, canvas["width"]
    assert canvas["height"] % hmi_export.GRID == 0, canvas["height"]


def test_meta_carries_operation_programs():
    # Состояние устройства ссылается на операцию по operation_id, и сама
    # операция должна быть в файле, иначе ссылка ведёт в никуда
    meta = _meta(_with_operations())

    programs = {p["id"]: p for p in meta["operations"]}
    assert "OP1" in programs, "программа операции не уехала"
    assert programs["OP1"]["states"][0]["steps"][0]["opened_devices"] == ["TANK1V1"]


def test_meta_carries_object_settings():
    """Уставки и свойства техобъекта доезжают вместе со схемой.

    Имя контура на чертеже («TANK1») и имя объекта в описании («Танк») —
    разные вещи, поэтому связь идёт через устройства: их состояния несут
    идентификатор объекта.
    """
    meta = _meta(_with_operations())

    tech_object = next(o for o in meta["tech_objects"] if o["name"] == "TANK1")
    lua_object = tech_object["lua_objects"][0]

    assert lua_object["name"] == "Танк" and lua_object["base_tech_object"] == "tank"
    assert lua_object["properties"] == {"IGNORE_LS_DOWN": "false"}
    assert lua_object["parameters"][0]["nameLua"] == "V"


def test_meta_carries_signals_and_nodes():
    # Сигналы проекта разбор до сих пор пропускал вовсе, а узлы контроллера
    # нужны, чтобы номер node в канале устройства к чему-то относился
    meta = _meta(_with_operations())

    assert meta["signals"][0]["name"] == "TANK1DI1"
    assert "nodes" not in meta or isinstance(meta["nodes"], list)


def test_meta_and_junctions_can_be_switched_off():
    assert _meta(_elements(meta=False)) is None
    assert "junction_points" not in _meta(_elements(junctions=False))


def test_meta_is_first_and_draws_nothing():
    # Холст рисует по массиву подряд; элемент с данными не должен
    # оказаться фигурой посреди схемы
    elements = _elements()

    assert elements[0].get("contur_meta") is True
    assert elements[0]["w"] == 0 and elements[0]["h"] == 0


# ------------------------------------------------------- сетка и её пределы

def _on_grid(value: float) -> bool:
    return abs(value / hmi_export.GRID - round(value / hmi_export.GRID)) < 1e-6


def test_objects_sit_on_the_grid():
    """Всё, что человек двигает, обязано стоять в узлах сетки.

    Редактор привязывает к сетке только то, что двигают, и по-разному:
    текст прыгает на узел при первом касании, а круг едет на целое число
    клеток, сохраняя своё смещение навсегда. Схема, пришедшая не по узлам,
    разъезжается по мере работы с ней, и починить это в редакторе нельзя.
    """
    for element in _elements():
        if element["type"] in ("line", "meta"):
            continue
        # Внутренности готовой фигуры — не объекты холста, а её собственный
        # рисунок: их размер задан фигурой и на клетку не делится (патрубок
        # ёмкости — три четверти клетки). В узлах обязана стоять оправа —
        # группа устройства и её рамка, а их проверяет строка ниже
        if element.get("contur_symbol_part"):
            continue
        for field in ("x", "y", "w", "h"):
            assert _on_grid(element[field]),                 f"{element['type']} {element.get('label')}: {field} = {element[field]}"


def test_circle_radius_is_a_whole_number_of_cells():
    # Минимальный радиус у редактора — клетка, и ручка ресайза привязывает
    # радиус к сетке: радиус 14 он поднял бы сам, каждый по-своему
    for device in _devices(_elements(devices="circle")):
        assert device["radius"] >= hmi_export.GRID, "радиус мельче клетки"
        assert _on_grid(device["radius"]), f"радиус {device['radius']} не кратен клетке"
        assert device["w"] == device["h"] == 2 * device["radius"]

def test_orthogonal_pipes_reach_the_grid():
    # Требовать кратности от каждого отрезка нельзя — диагонали
    # деформируются. Ортогональные садятся, если это недалеко
    lines = [e for e in _elements() if e["type"] == "line"]
    ortho = [e for e in lines
             if abs(e["x2"] - e["x1"]) < 1 or abs(e["y2"] - e["y1"]) < 1]

    assert ortho, "ортогональных отрезков нет"
    snapped = [e for e in ortho
               if all(_on_grid(e[f]) for f in ("x1", "y1", "x2", "y2"))]
    assert snapped, "ни один ортогональный отрезок не сел на сетку"

    for element in lines:
        length = math.hypot(element["x2"] - element["x1"],
                            element["y2"] - element["y1"])
        assert length > 0, "отрезок схлопнулся в точку"


def test_sheet_is_scaled_so_a_symbol_takes_two_cells():
    # Минимальный осмысленный объект — две клетки: 40 единиц холста.
    # Символ устройства на листе около 32 пунктов, значит лист растёт
    elements = _elements()
    meta = _meta(elements)

    assert meta["canvas"]["scale"] > 1, "лист должен увеличиться"
    assert meta["canvas"]["grid"] == hmi_export.GRID
    for device in _devices(elements):
        assert device["w"] >= hmi_export.MIN_OBJECT_SIZE


def test_content_starts_at_the_origin():
    # Начальная камера редактора стоит в начале координат: схема,
    # начинающаяся с x = 1740, откроется пустым экраном
    elements = [e for e in _elements() if e["type"] != "meta"]

    assert min(e["x"] for e in elements) >= 0
    assert min(e["y"] for e in elements) >= 0
    assert min(e["x"] for e in elements) < 3 * hmi_export.GRID, "лист не прижат к краю"


def test_labels_are_readable_on_screen():
    # 8 пунктов печатного листа — это 2-3 пикселя при зуме «весь лист»
    for text in _texts(_elements()) + _sheet_texts(_elements()):
        assert text["font_size"] >= hmi_export.MIN_FONT_SIZE,             f"кегль {text['font_size']} не читается на экране"


def test_grid_can_be_switched_off():
    loose = _elements(grid=False)
    devices = _devices(loose)

    assert devices, "устройств нет"
    assert not all(_on_grid(d["x"]) for d in devices), "сетка не выключилась"


# ---------------------------------------------------------------- настройки

def test_scale_moves_everything():
    # Масштаб можно задать руками — он умножает размеры целиком. Сетка
    # при этом мешает сравнивать, поэтому здесь она выключена
    normal = _elements(scale=1.0, grid=False, devices="circle")
    half = _elements(scale=0.5, grid=False, devices="circle")

    device_normal = next(d for d in _devices(normal) if d["lua_name"] == "TANK1V1")
    device_half = next(d for d in _devices(half) if d["lua_name"] == "TANK1V1")

    assert abs(device_half["w"] - device_normal["w"] / 2) < 0.01
    assert abs(device_half["radius"] - device_normal["radius"] / 2) < 0.01

def test_lines_can_be_thinned_out():
    # Контрольный лист даёт 5780 элементов, и для холста редактора это может
    # оказаться много. Красная линия — контур устройства, а он и так нарисован
    # кружком, поэтому первым делом убираются именно они
    everything = _elements(symbols="drawing")
    pipes = _elements(lines="pipes", symbols="drawing")
    devices_only = _elements(lines="none", symbols="drawing")

    assert not [e for e in _drawing_lines(pipes) if e["contur_color"] == "red"], (
        "остались контуры устройств")
    assert [e for e in _drawing_lines(pipes) if e["contur_color"] == "blue"], (
        "трубы пропали вместе с ними")
    assert len(pipes) < len(everything)
    assert not _drawing_lines(devices_only), "чертёж должен был исчезнуть"
    assert len(_devices(devices_only)) == len(MATCHES), "устройства должны остаться"


def test_unknown_line_mode_is_refused():
    try:
        HMIExporter(lines="половина")
    except ValueError as e:
        assert "половина" in str(e)
    else:
        raise AssertionError("неизвестный отбор линий должен отвергаться")


def test_groups_are_off_by_default():
    # Группы техобъектов выключены: у группы дети живут в её системе
    # координат, и ошибка здесь двигает всю схему. Группы устройств —
    # другое дело, они и есть само устройство
    assert not _tech_groups(_elements())
    assert _tech_groups(_elements(groups=True))

def test_group_takes_the_name_and_labels_with_it():
    # В режиме групп рамкой служит прямоугольник внутри группы: сама группа
    # рисуется только когда выделена, и без него рамка невидима, а габарит
    # схлопывается при первом же перетаскивании ребёнка
    elements = _elements(groups=True, labels=True, contour_frames=True)

    group = next(e for e in elements if e.get("tech_object") and e["type"] == "group"
                 and not e.get("contur_device"))
    first = next(e for e in elements if e["key"] == group["children"][0])
    assert first["type"] == "rectangle", "первым ребёнком должна быть рамка"
    assert first["x"] == 0 and first["y"] == 0, "рамка в углу группы"
    assert first["w"] == group["w"] and first["h"] == group["h"]

    name = next(t for t in _texts(elements) if t.get("contour"))
    assert name["parentKey"] == group["key"], "имя техобъекта осталось вне группы"

def test_group_children_are_linked_both_ways():
    # Холст рисует детей по массиву children родителя, а не обходом
    # по parentKey: ребёнок с одной только ссылкой вверх не появится
    elements = _elements(groups=True)
    by_key = {e["key"]: e for e in elements}

    for group in (e for e in elements if e["type"] == "group"):
        by_parent = {e["key"] for e in elements if e["parentKey"] == group["key"]}
        assert by_parent == set(group["children"]), "связь односторонняя"
        for key in group["children"]:
            assert by_key[key]["parentKey"] == group["key"]


def test_label_inside_a_group_keeps_its_offset():
    # Подпись пересчитывается в систему группы вместе с устройством,
    # иначе она едет по холсту относительно своего кружка
    elements = _elements(groups=True, labels=True, devices="circle")
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")
    label = next(t for t in _texts(elements) if t.get("lua_name") == "TANK1V1")

    assert label["parentKey"] == device["parentKey"], "подпись осталась вне группы"
    assert label["x"] == device["x"] + hmi_export.GRID
    assert label["y"] == device["y"] - hmi_export.GRID

def test_group_children_are_relative_to_it():
    elements = _elements(groups=True, devices="circle")

    group = next(e for e in elements if e["type"] == "group")
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    assert group["composition"] is True
    assert device["parentKey"] == group["key"]
    assert device["key"] in group["children"]

    # Контур синтетического листа начинается в (50, 150), устройство
    # стоит в (115, 215) — внутри группы это (65, 65)
    scale = _meta(elements)["canvas"]["scale"]
    assert abs(device["x"] - 65 * scale) <= 10, (
        "координаты внутри группы не переведены в систему группы")
    assert abs(device["y"] - 65 * scale) <= 10


def test_groups_switch_on_by_environment(monkeypatch=None):
    # Ключа командной строки у окна нет, поэтому переключатель — переменная
    # окружения, как у профилей детекции
    import os

    was = os.environ.get("CONTUR_HMI_GROUPS")
    os.environ["CONTUR_HMI_GROUPS"] = "1"
    try:
        assert hmi_export._env_groups() is True
        assert HMIExporter().groups is True
    finally:
        if was is None:
            os.environ.pop("CONTUR_HMI_GROUPS", None)
        else:
            os.environ["CONTUR_HMI_GROUPS"] = was


def test_percent_request_is_ignored():
    # Подпись у всех выгрузок общая, и use_percent_coords в неё входит.
    # Редактор проценты не разбирает — параметр не должен ничего портить
    workdir = Path(tempfile.mkdtemp(prefix="contur_hmi_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(MARKED_SVG, encoding="utf-8")
    out_path = workdir / "hmi.json"

    with contextlib.redirect_stdout(io.StringIO()):
        assert export_current_visualization_hmi(str(svg_path), str(out_path),
                                                MATCHES, CONTOURS,
                                                use_percent_coords=True, pdf_size=PAGE)

    elements = json.loads(out_path.read_text(encoding="utf-8"))
    assert all(isinstance(e["x"], (int, float)) for e in elements if "x" in e)


# ---------------------------------------------------- готовые фигуры

def test_device_arrives_as_the_editor_figure():
    """Устройство приезжает библиотечной фигурой, а не перерисовкой.

    Ради этого всё и делалось: клапан, датчик и ёмкость в библиотеке уже
    нарисованы, и рисовать их заново значит отдавать схему, непохожую
    на мнемосхемы самого редактора.
    """
    device = next(d for d in _devices(_elements()) if d["lua_name"] == "TANK1V1")

    assert device["contur_symbol"] == "butterfly_nc", "клапан приехал не библиотечной фигурой"
    assert device["contur_symbol_origin"] == "editor"
    assert device["contur_symbol_title"] == (
        "Санитарная запорная заслонка с пневмоприводом, НЗ"), "потеряна их подпись"
    assert device["type"] == "group", "фигура должна быть цельным объектом"


def test_figure_matches_the_catalogue_one_to_one():
    """В свой размер фигура приезжает точь-в-точь из каталога.

    Размер фигуры в клетках — её собственный (заслонка библиотеки
    нарисована на 200 единицах, это десять клеток): множитель единица,
    все узлы совпадают с узлами холста, и в редакторе фигура неотличима
    от нарисованной там же руками.
    """
    cells = hmi_symbols.native_device_size() / hmi_symbols.GRID
    elements = _elements(symbol_cells=cells)
    by_key = {e["key"]: e for e in elements}
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")
    valve = hmi_symbols.catalogue()["butterfly_nc"]

    # Первый ребёнок — рамка, держащая габарит группы (спецификация, §5.5)
    parts = [by_key[k] for k in device["children"][1:]]
    assert len(parts) == len(valve.shapes), "фигура приехала не целиком"
    assert all(p["contur_symbol_part"] for p in parts)

    circle = next(p for p in parts if p["type"] == "circle")
    original = next(s for s in valve.shapes if s["type"] == "circle")
    assert circle["radius"] == original["radius"]
    # У круга уезжает центр: вычитание радиуса делает нормализатор редактора (§6)
    assert (circle["x"], circle["y"]) == (original["cx"], original["cy"])


def test_device_drawing_is_not_sent_under_the_figure():
    # Иначе символ Eplan просвечивал бы сквозь библиотечный клапан: рисунок один,
    # а линий два набора
    elements = _elements()
    by_key = {e["key"]: e for e in elements}
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    assert not [k for k in device["children"] if by_key[k].get("contur_color")], (
        "под фигурой остались линии чертежа")
    assert not [e for e in _drawing_lines(elements)
                if e.get("device_name") == "TANK1V1"], (
        "линии устройства уехали верхним уровнем")


def test_drawing_symbol_can_be_asked_back():
    # Старый вид никуда не делся: он нужен, когда важно видеть именно
    # чертёж, и для устройств, которым фигуры в каталоге нет
    elements = _elements(symbols="drawing")
    device = next(d for d in _devices(elements) if d["lua_name"] == "TANK1V1")

    assert "contur_symbol" not in device
    assert [e for e in _drawing_lines(elements) if e.get("device_name")], (
        "символ устройства с чертежа пропал")


def test_sheet_grows_so_the_figure_fits():
    """Масштаб листа считается от размера фигуры, а не от кружка.

    Библиотечная фигура нарисована на десяти клетках, и лист тянется
    под неё. С прежними двумя круг привода приехал бы радиусом семь
    при минимуме в двадцать, а полки корпуса стали бы тоньше клетки.
    """
    full = _meta(_elements())["canvas"]["scale"]
    half = _meta(_elements(symbol_cells=hmi_symbols.DEFAULT_SYMBOL_CELLS / 2))
    half = half["canvas"]["scale"]

    assert abs(full / half - 2) < 1e-6, "масштаб не следует за размером фигуры"
    # В свой размер фигура приезжает как нарисована: 200x160 у заслонки
    assert _devices(_elements())[0]["w"] == 200.0


def test_sensor_carries_its_tag_inside():
    # Так они и рисуют датчики: кружок с обозначением внутри
    matches = list(MATCHES)
    matches[0] = replace(matches[0], device_type="TE", lua_name="TANK1TE1",
                         pdf_name="-TE1")
    elements = _elements_with(matches)
    by_key = {e["key"]: e for e in elements}

    sensor = next(d for d in _devices(elements) if d["lua_name"] == "TANK1TE1")
    assert sensor["contur_symbol"] == "sensor"
    circle = next(by_key[k] for k in sensor["children"]
                  if by_key[k]["type"] == "circle")
    assert circle["text"] == "-TE1" and circle["font_size"] >= hmi_export.MIN_FONT_SIZE


def test_valve_without_lua_is_a_manual_one():
    # Клапан, которого нет в Lua, контроллером не управляется: на схеме
    # это «бабочка» из двух треугольников, а не корпус с приводом
    matches = list(MATCHES)
    matches[0] = replace(matches[0], lua_name="")
    device = next(d for d in _devices(_elements_with(matches))
                  if d["pdf_name"] == "-V1")

    assert device["contur_symbol"] == "manual_valve"
    # И размер у неё свой: ручной клапан рисуют вдвое ниже, чем шире,
    # и ниже клапана с приводом — множитель каталога один на все фигуры
    powered = next(d for d in _devices(_elements()) if d["lua_name"] == "TANK1V1")
    assert device["w"] == device["h"] * 2, "пропорции ручного клапана"
    assert device["h"] < powered["h"], "ручной клапан ниже клапана с приводом"


def test_tank_appears_only_without_the_drawing():
    """Ёмкость рисуется там, где чертежа нет.

    С чертежом аппарат приезжает дважды: на листе mozzarella у танка
    LA_TANK1 корпус и уровень жидкости нарисованы самим Eplan.
    """
    assert not [e for e in _elements() if e.get("contur_tank")], (
        "ёмкость нарисована поверх чертежа")

    tanks = [e for e in _elements(lines="none") if e.get("contur_tank")]
    assert len(tanks) == 1, "без чертежа ёмкость должна появиться"
    assert tanks[0]["tech_object"] == "TANK1"
    assert tanks[0]["contur_symbol"] == "tank"


def test_tank_follows_the_tech_object_bounds():
    elements = _elements(lines="none")
    tank = next(e for e in elements if e.get("contur_tank"))
    minx, miny = CONTOURS[0].bounds[:2]
    left, top = _place(elements, minx, miny)

    assert abs(tank["x"] - left) <= hmi_export.GRID
    assert abs(tank["y"] - top) <= hmi_export.GRID
    assert tank["w"] > 0 and tank["h"] > 0


def test_tank_nozzles_keep_their_size():
    # Техобъект бывает в двадцать раз крупнее символа, и растянутый заодно
    # с корпусом патрубок превратился бы в кляксу во всю стенку
    elements = _elements(lines="none")
    by_key = {e["key"]: e for e in elements}
    tank = next(e for e in elements if e.get("contur_tank"))

    parts = [by_key[k] for k in tank["children"][1:]]
    narrow = [p for p in parts if p["w"] <= 4 * hmi_export.GRID]
    assert len(narrow) == 4, f"патрубков должно быть четыре, а не {len(narrow)}"
    assert all(p["h"] <= 4 * hmi_export.GRID for p in narrow)


def test_unknown_symbol_source_is_refused():
    try:
        _elements(symbols="магия")
    except ValueError as e:
        assert "магия" in str(e)
    else:
        raise AssertionError("неизвестный источник символов принят молча")



def test_outline_size_does_not_reach_the_editor():
    # Обводка устройства нужна только окну: редактор рисует устройство
    # своей фигурой и про этот способ смотреть не знает
    marked = [replace(match, view_size=(48.0, 30.0),
                      view_shape=[(-10.0, -10.0, 10.0, 10.0)])
              for match in MATCHES]
    written = json.dumps(_elements_with(marked), ensure_ascii=False)

    for leaked in ("view_size", "view_shape"):
        assert leaked not in written, \
            f"обводка уехала в выгрузку для редактора: {leaked}"


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
