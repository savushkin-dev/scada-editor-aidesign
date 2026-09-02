# tests/test_hmi_symbols.py
# Каталог готовых фигур редактора и его извлечение из сцены.
#
# Проверяется то, из-за чего фигура приезжает не той: узнавание одинаковых
# фигур (в сцене один и тот же клапан нарисован с разных вершин, и без
# приведения к общему порядку он разъезжался на два символа), выбор символа
# по обозначению устройства и растяжение ёмкости, при котором корпус тянется,
# а патрубок остаётся патрубком.
#
# Запуск из папки CONTUR:
#     python tests/test_hmi_symbols.py
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import hmi_symbols
import extract_symbols

GRID = hmi_symbols.GRID


def _catalogue(**symbols):
    """Каталог во временном файле — чтобы не трогать рабочий."""
    path = Path(tempfile.mkdtemp(prefix="contur_sym_")) / "symbols.json"
    path.write_text(json.dumps({"grid": GRID, "symbols": symbols},
                               ensure_ascii=False), encoding="utf-8")
    hmi_symbols.reset_cache()
    return str(path)


def _env(name, value):
    was = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    return was


def _library_scene(label, w, h, shapes):
    """Сцена из одной подписанной группы — как в присланной библиотеке."""
    children = []
    for index, shape in enumerate(shapes):
        children.append(dict(shape, key=f"c{index}", parentKey="g"))
    group = {"key": "g", "type": "group", "x": 0, "y": 0, "w": w, "h": h,
             "label": label, "children": [c["key"] for c in children],
             "parentKey": "undefined"}
    return [group, *children]


# ------------------------------------------------------------------ каталог

def test_catalogue_has_the_editor_figures():
    # Рабочий каталог собран из сцены MOZARELLA_01: без него подставлять
    # нечего, и выгрузка молча вернулась бы к отрисовке с чертежа
    hmi_symbols.reset_cache()
    known = hmi_symbols.catalogue()

    for name in ("valve", "valve_v", "sensor", "tank"):
        assert name in known, f"в каталоге нет фигуры {name}"
        assert known[name].shapes, f"фигура {name} пуста"
        assert known[name].origin == "editor", f"{name} должен быть фигурой редактора"


def test_catalogue_has_the_library_figures():
    """Библиотека, присланная отдельным файлом: 31 фигура с подписями.

    До неё каталог знал один клапан на все случаи, а насос был нарисован
    отдельно. Теперь у отсечного клапана, регулирующего и ручного — свои
    фигуры, у насоса три вида, у сигнализатора уровня три.
    """
    hmi_symbols.reset_cache()
    known = hmi_symbols.catalogue()

    for name in ("butterfly_nc", "butterfly_no", "control_valve",
                 "manual_valve", "three_way_valve", "check_valve",
                 "pump_centrifugal", "pump_vacuum", "pump_membrane",
                 "level_high", "level_mid", "level_low",
                 "filter", "drain_funnel", "heat_exchanger_plate"):
        assert name in known, f"в каталоге нет фигуры {name}"
        assert known[name].shapes, f"фигура {name} пуста"
        assert known[name].title, f"у {name} потеряна их подпись"


def test_electrical_figures_are_drawn_here():
    """Кнопка, лампа, сирена и колонна нарисованы отдельно — в библиотеке их нет.

    Библиотека редактора про технологию: клапаны, насосы, датчики.
    Электрических устройств в ней нет вовсе, и на их месте в объекте
    оставалась пустая рамка. Лампа и кнопка срисованы с чертежа Eplan,
    сирена и колонна нарисованы по общепринятому виду: Eplan показывает
    их клеммным блоком, из которого мнемосхемы не сделать.
    """
    hmi_symbols.reset_cache()

    for device_type, name in (("HL", "lamp"), ("SB", "button"),
                              ("HA", "siren"), ("HLA", "beacon")):
        symbol = hmi_symbols.symbol_for_device(device_type, "MCC1" + device_type + "1")
        assert symbol is not None, f"у {device_type} нет фигуры"
        assert symbol.name == name
        # Заимствованную фигуру редактор отличает по этому полю:
        # собственную он вправе заменить
        assert symbol.origin == "contur", f"{name} выдаётся за фигуру редактора"
        assert symbol.title, f"у {name} нет подписи"


def test_builtin_figures_are_there_too():
    # Насоса в присланной сцене не было вовсе, а «бабочка» ручного клапана
    # нарисована двумя отдельными треугольниками — обе живут в коде
    hmi_symbols.reset_cache()
    known = hmi_symbols.catalogue()

    assert known["pump"].origin == "contur", "насос нарисован отдельно, это надо видеть"
    assert known["manual_valve"].origin == "editor", "«бабочка» собрана из фигур редактора"


def test_catalogue_overrides_builtin():
    # Появится библиотечный насос — подставляться должен он, а не встроенный
    path = _catalogue(pump={"w": 40.0, "h": 40.0, "origin": "editor",
                            "shapes": [{"type": "circle", "cx": 20.0, "cy": 20.0,
                                        "radius": 20.0}]})
    pump = hmi_symbols.catalogue(path)["pump"]

    assert pump.origin == "editor" and pump.w == 40.0
    hmi_symbols.reset_cache()


def test_missing_catalogue_leaves_builtin():
    # Файла нет — выгрузка не должна падать: встроенных фигур хватает
    hmi_symbols.reset_cache()
    known = hmi_symbols.catalogue(str(Path(tempfile.mkdtemp()) / "нет.json"))

    assert set(known) == set(hmi_symbols.BUILTIN)
    hmi_symbols.reset_cache()


# ------------------------------------------------------------------ выбор

def test_symbol_is_chosen_by_device_type():
    # Имена фигур — из библиотеки: отсечной клапан на этих схемах
    # заслонка с пневмоприводом, регулирующий — свой, у насоса три вида
    assert hmi_symbols.symbol_for_device("V", "TANK1V1").name == "butterfly_nc"
    assert hmi_symbols.symbol_for_device("VC", "TANK1VC1").name == "control_valve"
    assert hmi_symbols.symbol_for_device("M", "TANK1M1").name == "pump_centrifugal"
    assert hmi_symbols.symbol_for_device("TE", "TANK1TE1").name == "sensor"
    assert hmi_symbols.symbol_for_device("PT", "TANK1PT1").name == "sensor"


def test_library_figure_knows_its_own_name():
    # Имя в каталоге короткое и латинское, а рядом лежит библиотечная
    # подпись: по ней человек и проверяет, та ли фигура подставлена
    known = hmi_symbols.catalogue()
    assert known["butterfly_nc"].title == "Санитарная запорная заслонка с пневмоприводом, НЗ"
    assert known["pump_centrifugal"].title == "Насос центробежный"


def test_level_switch_takes_the_figure_from_the_description():
    """Сигнализатор уровня один по обозначению и трёх видов по чертежу.

    В библиотеке верхний, средний и нижний уровень — три разные фигуры,
    а обозначение у всех LS. Различает их только описание из Lua.
    """
    assert hmi_symbols.symbol_for_device(
        "LS", "TANK1LS1", "Датчик верхнего уровня").name == "level_high"
    assert hmi_symbols.symbol_for_device(
        "LS", "TANK1LS2", "Сигнализатор нижнего уровня").name == "level_low"
    assert hmi_symbols.symbol_for_device(
        "LS", "TANK1LS3", "Средний уровень").name == "level_mid"
    # Слова нет — остаётся общий кружок с тегом, а не случайный из трёх
    assert hmi_symbols.symbol_for_device("LS", "TANK1LS4", "").name == "sensor"


def test_level_words_can_be_replaced():
    was = _env("CONTUR_HMI_LEVEL_NAMES", "level_low=ОТСЕЧК")
    try:
        assert hmi_symbols.symbol_for_device(
            "LS", "X", "Отсечка по уровню").name == "level_low"
        # Прежние слова заменены целиком, а не дополнены
        assert hmi_symbols.symbol_for_device(
            "LS", "X", "Датчик верхнего уровня").name == "sensor"
    finally:
        _env("CONTUR_HMI_LEVEL_NAMES", was)


def test_type_without_a_figure_keeps_the_drawing():
    # Сигналу контроллера и «прочему оборудованию» фигуры нет: такое
    # устройство должно уехать своим символом с чертежа, а не превратиться
    # в чужой клапан. Сигнал на чертеже — стрелка с подписью, а не прибор
    assert hmi_symbols.symbol_for_device("DI", "LINE_M1DI1") is None
    assert hmi_symbols.symbol_for_device("G", "CAB2G1") is None
    assert hmi_symbols.symbol_for_device("", "") is None


def test_valve_without_lua_is_manual():
    # У ручного клапана нет ни одного канала ввода-вывода, контроллер
    # про него не знает — на схеме это «бабочка», а не корпус с приводом
    assert hmi_symbols.symbol_for_device("V", "").name == "manual_valve"
    assert hmi_symbols.symbol_for_device("V", "   ").name == "manual_valve"
    assert hmi_symbols.symbol_for_device("V", "TANK1V1").name == "butterfly_nc"


def test_agitator_is_not_a_pump():
    """Мешалка и насос носят общее обозначение M, а рисуются по-разному.

    На чертеже насос — круг с рабочим колесом прямо на трубе, а мешалка —
    кружок с обозначением внутри и лопасть в самом танке. На контрольном
    листе A0 из пятнадцати устройств M восемь мешалки, и все восемь
    приезжали насосом. Различить их можно только по описанию из Lua.
    """
    assert (hmi_symbols.symbol_for_device("M", "TANK1M1", "Насос. продукта").name
            == "pump_centrifugal")
    assert hmi_symbols.symbol_for_device("M", "TANK1M1", "Мешалка").name == "agitator"
    # Без описания судить не по чему — остаётся насос
    assert hmi_symbols.symbol_for_device("M", "TANK1M1", "").name == "pump_centrifugal"


def test_agitator_borrows_the_sensor_figure():
    # Отдельной фигуры мешалки в библиотеке нет, а Eplan рисует её тем же
    # кружком с обозначением внутри, что и датчик. Имя при этом своё:
    # появится библиотечная мешалка — встанет на это место
    known = hmi_symbols.catalogue()
    assert known["agitator"].shapes == known["sensor"].shapes
    assert known["agitator"].origin == "contur", "заимствованную фигуру надо видеть"


def test_own_figure_beats_the_borrowed_one():
    path = _catalogue(agitator={"w": 40.0, "h": 40.0, "origin": "editor",
                                "shapes": [{"type": "circle", "cx": 20.0, "cy": 20.0,
                                            "radius": 20.0}]})
    assert hmi_symbols.catalogue(path)["agitator"].origin == "editor"
    hmi_symbols.reset_cache()


def test_agitator_words_can_be_replaced():
    was = _env("CONTUR_HMI_AGITATOR_NAMES", "ДОЗАТОР")
    try:
        assert (hmi_symbols.symbol_for_device("M", "X", "Мешалка").name
                == "pump_centrifugal")
        assert hmi_symbols.symbol_for_device("M", "X", "Насос-дозатор").name == "agitator"
    finally:
        _env("CONTUR_HMI_AGITATOR_NAMES", was)


def test_pump_repeats_the_drawing_symbol():
    # Форма не выдумана: на чертеже насос — круг, вписанный треугольник
    # остриём по потоку и горизонтальный диаметр. Все вершины на самом круге
    pump = hmi_symbols.catalogue()["pump"]
    circle = next(s for s in pump.shapes if s["type"] == "circle")
    lines = [s for s in pump.shapes if s["type"] == "line"]

    assert len(lines) == 3, "круг с колесом — это три отрезка"
    cx, cy, r = circle["cx"], circle["cy"], circle["radius"]
    for line in lines:
        for x, y in ((line["x1"], line["y1"]), (line["x2"], line["y2"])):
            off = abs(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 - r)
            assert off < 1e-6, f"вершина ({x},{y}) не на круге"


def test_upright_valve_has_its_own_figure():
    # В библиотеке клапан нарисован и лёжа, и стоя — 14 и 7 штук в сцене
    assert (hmi_symbols.symbol_for_device("V", "X", vertical=True).name
            == "butterfly_nc_v")
    # А у датчика стоячего вида нет, и просить его нечего
    assert hmi_symbols.symbol_for_device("TE", "X", vertical=True).name == "sensor"


def test_map_can_be_corrected_from_the_environment():
    was = _env("CONTUR_HMI_SYMBOL_MAP", "M=valve,TE=")
    try:
        assert hmi_symbols.symbol_for_device("M", "X").name == "valve"
        assert hmi_symbols.symbol_for_device("TE", "X") is None
    finally:
        _env("CONTUR_HMI_SYMBOL_MAP", was)


def test_tank_is_recognised_by_name():
    assert hmi_symbols.symbol_for_tech_object("LA_TANK1", "").name == "tank"
    assert hmi_symbols.symbol_for_tech_object("COAG1", "Коагулятор").name == "tank"
    assert hmi_symbols.symbol_for_tech_object("LINE_M1", "Линия розлива") is None


def test_tank_words_can_be_replaced():
    was = _env("CONTUR_HMI_TANK_NAMES", "СЫРОДЕЛ")
    try:
        assert hmi_symbols.symbol_for_tech_object("LA_TANK1", "") is None
        assert hmi_symbols.symbol_for_tech_object("СЫРОДЕЛ2", "").name == "tank"
    finally:
        _env("CONTUR_HMI_TANK_NAMES", was)


# ------------------------------------------------------------------ размер

def test_native_size_keeps_the_grid():
    """Множитель единица — там, где размер устройства равен фигуре каталога.

    Тогда все узлы фигуры совпадают с узлами холста. Раньше это было
    зашито числом (их прежний клапан 120x120 — шесть клеток), а фигуры
    библиотеки нарисованы крупнее, и размер берётся из самого каталога.
    """
    native = hmi_symbols.native_device_size()
    cells = native / hmi_symbols.GRID

    assert native == 200.0, "обычное устройство — их заслонка 200x160"
    assert hmi_symbols.symbol_scale(cells) == 1.0
    assert hmi_symbols.symbol_scale(cells / 2) == 0.5


def test_native_size_falls_back_without_a_catalogue():
    # Без каталога подставлять нечего, но множитель обязан остаться числом:
    # на нём считается масштаб всего листа
    path = _catalogue()
    assert hmi_symbols.native_device_size(path) == hmi_symbols.FALLBACK_NATIVE_SIZE
    hmi_symbols.reset_cache()


def test_fit_keeps_proportions():
    # Ручной клапан вдвое шире своей высоты и в квадрате не должен стать
    # ромбом: вписывается по меньшей стороне, а не растягивается
    manual = hmi_symbols.catalogue()["manual_valve"]
    ratio = manual.w / manual.h
    width, height, shapes = manual.fit(120, 120)

    assert (width, height) == (120.0, 120.0 / ratio), "пропорции не сохранены"
    assert shapes


def test_stretch_pulls_the_body_and_keeps_the_details():
    """Ёмкость по границам техобъекта: корпус тянется, патрубок — нет.

    Техобъект на листе mozzarella занимает 3880x3040 единиц. Растянув
    всё подряд, патрубок шириной в клетку раздуло бы до полутысячи,
    и ёмкость превратилась бы в четыре кляксы по углам.
    """
    tank = hmi_symbols.catalogue()["tank"]
    width, height = 3880.0, 3040.0
    shapes = tank.stretch(width, height, detail=1.0)
    kx = width / tank.w

    def span(shape):
        minx, miny, maxx, maxy = hmi_symbols.shape_bounds(shape)
        return (maxx - minx, maxy - miny)

    narrow = 0
    for before, after in zip(tank.shapes, shapes, strict=True):
        was, now = span(before)[0], span(after)[0]
        if was < tank.w * hmi_symbols.SPAN_RATIO:
            narrow += 1
            assert now == was, f"деталь шириной {was} раздулась до {now}"
        else:
            assert abs(now - was * kx) < 1, "корпус не растянулся по техобъекту"

    assert narrow == 4, f"патрубков должно быть четыре, а не {narrow}"


def test_stretch_moves_the_details_to_the_edges():
    # Патрубок обязан остаться на своей стенке, а не съехать к середине
    tank = hmi_symbols.catalogue()["tank"]
    shapes = tank.stretch(1000, 500, detail=1.0)
    narrow = [hmi_symbols.shape_bounds(s) for s in shapes
              if (lambda b: b[2] - b[0])(hmi_symbols.shape_bounds(s)) <= 4 * GRID]

    assert any(b[0] < 1000 * 0.2 for b in narrow), "у левой стенки нет патрубка"
    assert any(b[2] > 1000 * 0.8 for b in narrow), "у правой стенки нет патрубка"


# ------------------------------------------------------------------ извлечение

SCENE = [
    {"key": "g1", "type": "group", "x": 100, "y": 100, "w": 40, "h": 40,
     "children": ["a1", "a2"], "parentKey": "undefined"},
    {"key": "a1", "type": "polygon", "x": 0, "y": 0, "w": 40, "h": 40,
     "points": [0, 0, 40, 0, 40, 40, 0, 40], "parentKey": "g1", "children": []},
    {"key": "a2", "type": "circle", "x": 10, "y": 10, "w": 20, "h": 20,
     "radius": 10, "parentKey": "g1", "children": []},
    # Та же фигура, но многоугольник начат с другой вершины и в другую сторону
    {"key": "g2", "type": "group", "x": 500, "y": 300, "w": 40, "h": 40,
     "children": ["b1", "b2"], "parentKey": "undefined"},
    {"key": "b1", "type": "polygon", "x": 0, "y": 0, "w": 40, "h": 40,
     "points": [40, 40, 40, 0, 0, 0, 0, 40], "parentKey": "g2", "children": []},
    {"key": "b2", "type": "circle", "x": 10, "y": 10, "w": 20, "h": 20,
     "radius": 10, "parentKey": "g2", "children": []},
]


def test_same_figure_drawn_differently_is_one_symbol():
    """Одинаковые фигуры обязаны узнаваться независимо от порядка вершин.

    В исходной сцене клапан нарисован то с левого верхнего угла,
    то с правого: без приведения к общему порядку 21 одинаковый клапан
    распадался на два разных символа — 14 и 7.
    """
    found = extract_symbols.clusters(SCENE)

    assert len(found) == 1, f"фигур должно быть одна, а не {len(found)}"
    assert found[0]["instances"] == 2
    assert found[0]["grouped"] is True


def test_lone_shape_becomes_a_symbol_only_when_it_repeats():
    # Иначе в каталог попал бы каждый кружок чертежа
    single = [{"key": "c1", "type": "circle", "x": 0, "y": 0, "w": 40, "h": 40,
               "radius": 20, "parentKey": "undefined", "children": []}]
    assert extract_symbols.clusters(single) == []

    many = []
    for index in range(extract_symbols.MIN_SINGLE_INSTANCES):
        many.append({"key": f"c{index}", "type": "circle", "x": index * 100,
                     "y": 0, "w": 40, "h": 40, "radius": 20,
                     "parentKey": "undefined", "children": []})
    assert len(extract_symbols.clusters(many)) == 1


def test_exemplar_is_the_common_size_not_the_biggest():
    """За образец берётся самый частый размер.

    На их схеме кружок датчика нарисован радиусом 40 и 60, а рядом обод
    аппарата радиусом 780 — та же фигура. По самому крупному экземпляру
    символ датчика уехал бы в габарит 1560.
    """
    scene = []
    for index, radius in enumerate([20, 20, 20, 780]):
        scene.append({"key": f"c{index}", "type": "circle", "x": index * 2000,
                      "y": 0, "w": radius * 2, "h": radius * 2, "radius": radius,
                      "parentKey": "undefined", "children": []})

    found = extract_symbols.clusters(scene)
    assert len(found) == 1
    assert found[0]["w"] == 40.0, f"габарит образца {found[0]['w']}"


def test_symbol_is_normalised_to_its_own_corner():
    # Символ хранится в собственных координатах: где он стоял на их схеме,
    # к форме отношения не имеет
    found = extract_symbols.clusters(SCENE)[0]
    minx, miny, _, _ = extract_symbols.bounds(found["shapes"])

    assert (minx, miny) == (0.0, 0.0)


def test_names_come_from_the_labels():
    """У фигур библиотеки настоящие подписи — имена берутся из них.

    В их прежней сцене все группы назывались «Group (8)», и называть
    фигуры приходилось руками, номером. Ошибиться номером — поставить
    на место устройства чужую фигуру.
    """
    scene = _library_scene("Насос центробежный", 120, 120, [
        {"type": "circle", "x": 0, "y": 0, "w": 120, "h": 120, "radius": 60},
        {"type": "line", "x1": 0, "y1": 60, "x2": 120, "y2": 60},
    ])
    entries = extract_symbols.clusters(scene)
    names = {index: extract_symbols.LIBRARY_NAMES[entry["label"]]
             for index, entry in enumerate(entries, 1)
             if entry["label"] in extract_symbols.LIBRARY_NAMES}
    data = extract_symbols.catalogue(entries, names, "библиотека.json")

    assert "pump_centrifugal" in data["symbols"], "фигура не названа по подписи"
    assert (data["symbols"]["pump_centrifugal"]["title"]
            == "Насос центробежный"), "их подпись должна остаться в каталоге"


def test_upright_twin_is_built_by_rotation():
    """Второй вид клапана — поворот первого, а не вторая фигура.

    В библиотеке клапан нарисован один раз, стоя: корпус на трубе, привод
    над ним, оттого фигура выше, чем шире. На чертеже он встречается
    и поперёк, и выгрузка просит вид по тем же пропорциям — значит
    лежачий вид собирается поворотом, и путать их местами нельзя.
    """
    scene = _library_scene("Клапан, НЗ", 40, 80, [
        {"type": "line", "x1": 0, "y1": 40, "x2": 40, "y2": 40},
        {"type": "line", "x1": 20, "y1": 0, "x2": 20, "y2": 80},
    ])
    entries = extract_symbols.clusters(scene)
    symbols = extract_symbols.catalogue(entries, {1: "valve_nc"}, "x.json")["symbols"]

    # Библиотечная фигура выше, чем шире, — это стоячий вид
    assert (symbols["valve_nc_v"]["w"], symbols["valve_nc_v"]["h"]) == (40.0, 80.0)
    assert (symbols["valve_nc"]["w"], symbols["valve_nc"]["h"]) == (80.0, 40.0)
    # Поворот не искажает: отрезок вдоль трубы остаётся той же длины
    turned = [s for s in symbols["valve_nc"]["shapes"] if s["type"] == "line"]
    assert any(abs(s["x2"] - s["x1"]) == 80.0 for s in turned)


def test_instrument_circle_keeps_a_place_for_the_tag():
    """Кружок прибора в библиотеке пустой, а на схеме в нём стоит тег.

    Тег вписывает человек, когда ставит фигуру; выгрузка ставит туда
    имя устройства. Без пометки датчик уехал бы безымянным кружком.
    """
    scene = _library_scene("Датчик верхнего предельного уровня", 80, 80, [
        {"type": "circle", "x": 0, "y": 0, "w": 80, "h": 80, "radius": 40},
        {"type": "text", "x": 100, "y": 20, "text": "H"},
    ])
    entries = extract_symbols.clusters(scene)
    symbols = extract_symbols.catalogue(entries, {1: "level_high"}, "x.json")["symbols"]

    circle = [s for s in symbols["level_high"]["shapes"] if s["type"] == "circle"]
    assert circle and circle[0].get("text") == "$tag"
    # Буква уровня — их, и подменять её тегом нельзя
    letters = [s for s in symbols["level_high"]["shapes"] if s["type"] == "text"]
    assert [s["text"] for s in letters] == ["H"]


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
