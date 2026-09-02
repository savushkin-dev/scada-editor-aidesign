# tests/test_json_export.py
# Выгрузка в JSON.
#
# Смысл проверок не в том, что JSON записывается, а в том, что он описывает
# тот же лист, что и XML. Каналов выдачи два, собираются они одним кодом
# (export_scene), и разъехаться могут только в сериализации — значит именно
# её и надо сверять: те же устройства, те же координаты, те же связи.
#
# Лист собирается синтетический: настоящая разметка весит полтора мегабайта
# и в репозитории не лежит (см. golden.py), а для сверки двух записей одного
# и того же хватает нескольких линий.
#
# Запуск из папки CONTUR:
#     python tests/test_json_export.py
import contextlib
import io
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import ClassVar

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import export_scene
import exporters
from data_models import Contour, DeviceMatch, Operation
from json_export import export_current_visualization_json
from xml_export import export_current_visualization

# Холст A4 в пунктах: система координат сойдётся как pdf_pts.
# Геометрия держится подальше от кромок — линии в 3% от края
# отбрасываются как рамка чертежа
PAGE = (595.0, 842.0)

MARKED_SVG = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="595" height="842"
     viewBox="0 0 595 842" data-device-count="2" data-device-named="2">
  <rect x="100" y="200" width="30" height="30" stroke="red" stroke-width="1"
        fill="none" data-device-name="TANK1V1" data-device-class="valve"
        data-device-confidence="0.91"/>
  <rect x="300" y="200" width="30" height="30" stroke="red" stroke-width="1"
        fill="none" data-device-name="TANK1V2" data-device-class="valve"
        data-device-confidence="0.85"/>
  <line x1="130" y1="215" x2="300" y2="215" stroke="blue" stroke-width="2"/>
  <line x1="130" y1="230" x2="130" y2="400" stroke="blue" stroke-width="2"/>
  <path d="M 330,215 L 420,215 L 420,300" stroke="blue" stroke-width="2" fill="none"/>
  <text fill="red" font-size="8" x="103" y="198">-V1</text>
  <text fill="blue" font-size="10" x="200" y="600">Схема мойки</text>
</svg>
"""

MATCHES = [
    DeviceMatch(lua_name="TANK1V1", pdf_name="-V1", tech_object="TANK1",
                coordinates=(115.0, 215.0), confidence=0.91, device_type="V",
                descr="Клапан нижнего слива", article="SE.XB4BS8445",
                extra_data={"subtype_num": 3, "пустое": "  ", "нет": None},
                tags={"DI": [{"node": 1, "offset": 1617, "module_offset": 1616,
                              "physical_port": 1, "logical_port": 2}],
                      "par": [5000, 1]}),
    DeviceMatch(lua_name="TANK1V2", pdf_name="-V2", tech_object="TANK1",
                coordinates=(315.0, 215.0), confidence=0.85, device_type="V"),
]

CONTOURS = [Contour(name="TANK1", bounds=(50.0, 150.0, 500.0, 500.0),
                    center=(275.0, 325.0), tech_object="TANK1")]


def _export_both(**kwargs):
    """Выгружает один и тот же лист в оба формата, возвращает (xml_root, json)."""
    workdir = Path(tempfile.mkdtemp(prefix="contur_json_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(MARKED_SVG, encoding="utf-8")

    xml_path, json_path = workdir / "export.xml", workdir / "export.json"
    options = {"pdf_size": PAGE, **kwargs}

    # Экспортёры разговорчивы, а проверкам нужен только результат
    with contextlib.redirect_stdout(io.StringIO()):
        assert export_current_visualization(str(svg_path), str(xml_path),
                                            MATCHES, CONTOURS, **options)
        assert export_current_visualization_json(str(svg_path), str(json_path),
                                                 MATCHES, CONTOURS, **options)

    return (ET.parse(xml_path).getroot(),
            json.loads(json_path.read_text(encoding="utf-8")))


def _percent(value: str) -> float:
    return float(value[:-1]) if value.endswith("%") else float(value)


# ---------------------------------------------------------------- тот же лист

def test_devices_match_xml():
    # Главная проверка: устройства, их имена и координаты совпадают с XML.
    # Разъехаться каналы могут только здесь — данные им готовит общий код
    root, document = _export_both()

    xml_devices = {d.get("lua_name"): d for d in root.iter("Device")}
    json_devices = {d["lua_name"]: d
                    for obj in document["tech_objects"] for d in obj["devices"]}

    assert set(xml_devices) == set(json_devices) == {"TANK1V1", "TANK1V2"}

    for name, xml_device in xml_devices.items():
        json_device = json_devices[name]
        assert abs(_percent(xml_device.get("x")) - json_device["x"]) < 0.001, \
            f"{name}: координата x разошлась с XML"
        assert abs(_percent(xml_device.get("y")) - json_device["y"]) < 0.001, \
            f"{name}: координата y разошлась с XML"
        assert abs(float(xml_device.get("confidence")) - json_device["confidence"]) < 0.001
        assert xml_device.get("pdf_name") == json_device["pdf_name"]


def test_geometry_counts_match_xml():
    # Точки сопряжения, трубы и связи считаются один раз в export_scene,
    # но записываются по-разному: в XML счётчиками, в JSON длиной массивов
    root, document = _export_both()

    assert int(root.get("junction-points-count") or 0) == len(document["junction_points"])
    assert int(root.get("pipelines-count") or 0) == len(document["pipelines"])

    connections = root.find("Connections")
    xml_connections = int(connections.get("count")) if connections is not None else 0
    assert xml_connections == len(document["connections"])


def test_contour_bounds_match_xml():
    root, document = _export_both()

    xml_bounds = [float(v[:-1]) for v in
                  root.find(".//Contour").get("bounds").split(",")]
    json_bounds = document["tech_objects"][0]["contour"]["bounds"]

    assert len(json_bounds) == 4, "границы контура должны быть массивом из четырёх чисел"
    for expected, got in zip(xml_bounds, json_bounds, strict=True):
        assert abs(expected - got) < 0.001, "границы контура разошлись с XML"


def test_canvas_and_coordinate_type():
    # Без размеров холста проценты обратно в координаты не перевести —
    # именно на этом когда-то ломалось чтение своего же файла
    _, document = _export_both()

    assert document["coordinate_type"] == "percent"
    assert abs(document["canvas"]["width"] - PAGE[0]) < 0.001
    assert abs(document["canvas"]["height"] - PAGE[1]) < 0.001
    assert document["version"] == "1.3", "версия формата общая с XML"


def test_absolute_coordinates_stay_in_points():
    _, document = _export_both(use_percent_coords=False)

    device = document["tech_objects"][0]["devices"][0]
    assert document["coordinate_type"] == "absolute"
    assert 100 < device["x"] < 130, "в абсолютном режиме координаты остаются пунктами"


# ---------------------------------------------------------------- запись

def test_numbers_are_numbers():
    # Смысл JSON в том, что потребителю не надо разбирать «12.480%»
    _, document = _export_both()

    device = document["tech_objects"][0]["devices"][0]
    assert isinstance(device["x"], float), "координата должна быть числом"
    assert isinstance(device["confidence"], float)
    assert 0 <= device["x"] <= 100, "процент вне диапазона 0..100"


def test_russian_text_stays_readable():
    # ensure_ascii по умолчанию превратил бы описания в Кл...
    workdir = Path(tempfile.mkdtemp(prefix="contur_json_"))
    svg_path = workdir / "marked.svg"
    svg_path.write_text(MARKED_SVG, encoding="utf-8")
    json_path = workdir / "export.json"

    with contextlib.redirect_stdout(io.StringIO()):
        assert export_current_visualization_json(str(svg_path), str(json_path),
                                                 MATCHES, CONTOURS, pdf_size=PAGE)

    assert "Клапан нижнего слива" in json_path.read_text(encoding="utf-8")


def test_markup_travels_inside_the_file():
    # Файл самодостаточен: разметка лежит строкой, как секция SVGContent у XML
    _, document = _export_both()

    assert document["svg"].lstrip().startswith("<"), "разметка не попала в файл"
    assert "TANK1V1" in document["svg"], "в разметке нет подписей устройств"
    assert "%" in document["svg"], "координаты разметки не переведены в проценты"


def test_empty_fields_are_skipped():
    # Пустые поля из Lua в файл не идут — как и в XML
    _, document = _export_both()

    device = document["tech_objects"][0]["devices"][0]
    assert "пустое" not in device and "нет" not in device
    assert device["subtype_num"] == 3, "числа из Lua остаются числами"


# ---------------------------------------------------------------- текущая операция

class _FakeObjectsData:
    """Одна операция в два шага: первый клапан открывается, второй закрывается.

    Настоящий objects_data читает Lua-описание операций. Выгрузка в XML
    и PlantGeometry спрашивает про выбранную операцию, выгрузка для
    редактора — про все состояния устройства сразу, поэтому здесь есть
    и то, и другое.
    """

    OPERATION = Operation(id="OP1", name="Мойка", base_operation=None,
                          obj_id="TANK1", obj_name="TANK1")

    STATES: ClassVar[dict] = {
        "TANK1V1": [
            {"operation_id": "OP1", "operation": "Мойка", "tech_object": "TANK1",
             "tech_object_id": "1", "state_id": "OP1_1", "state": "Наполнение",
             "step_id": "OP1_1_1", "step": "Шаг 1", "step_number": 1,
             "status": "opened"},
            {"operation_id": "OP1", "operation": "Мойка", "tech_object": "TANK1",
             "tech_object_id": "1", "state_id": "OP1_1", "state": "Наполнение",
             "step_id": "OP1_1_2", "step": "Шаг 2", "step_number": 2,
             "status": "closed"},
        ],
        "TANK1V2": [
            {"operation_id": "OP1", "operation": "Мойка", "tech_object": "TANK1",
             "tech_object_id": "1", "state_id": "OP1_1", "state": "Наполнение",
             "step_id": "", "step": "", "step_number": -1, "status": "closed"},
        ],
    }

    def get_operation_by_id(self, op_id):
        return self.OPERATION if op_id == "OP1" else None

    def get_devices_for_operation(self, op_id):
        return {"TANK1V1": "opened", "TANK1V2": "closed"}

    def get_device_details_in_operation(self, op_id, device_name):
        if device_name != "TANK1V1":
            return None
        return {"status": "opened", "state_name": "Наполнение",
                "step_name": "Шаг 1", "step_number": 1}

    # Сигналы проекта и сводка по техобъекту: выгрузка для редактора
    # спрашивает и это
    signals: ClassVar[list] = [
        {"name": "TANK1DI1", "type": "DI_DO", "parent": "Танк.Мойка"},
    ]

    def get_object_details(self, obj_id):
        if obj_id != "1":
            return None
        return {"id": "1", "name": "Танк", "name_eplan": "TANK",
                "base_tech_object": "tank", "tech_type": 2,
                "properties": {"IGNORE_LS_DOWN": "false"},
                "equipment": {"LT": ""},
                "parameters": [{"id": "п1", "name": "Объём", "value": 1000,
                                "meter": "л", "nameLua": "V", "oper": [1]}]}

    def get_device_states(self, device_name):
        return self.STATES.get(device_name, [])

    def get_operation_program(self, op_id):
        if op_id != "OP1":
            return None
        return {"id": "OP1", "name": "Мойка", "tech_object": "TANK1",
                "base_operation": None,
                "states": [{"id": "OP1_1", "name": "Наполнение", "steps": [
                    {"number": 1, "name": "Шаг 1",
                     "opened_devices": ["TANK1V1"], "closed_devices": []},
                    {"number": 2, "name": "Шаг 2",
                     "opened_devices": [], "closed_devices": ["TANK1V1"]},
                ]}]}


def _with_operation():
    was = export_scene.objects_data
    export_scene.objects_data = _FakeObjectsData()
    try:
        return _export_both(current_operation_id="OP1")
    finally:
        export_scene.objects_data = was


def test_operation_reaches_both_formats():
    # Этот путь однажды уже был сломан целиком: экспорт с выбранной операцией
    # падал на удалённом импорте, а проверки его не касались, потому что
    # обычная выгрузка идёт без операции
    root, document = _with_operation()

    assert root.get("current_operation_name") == "Мойка"
    assert document["current_operation"]["name"] == "Мойка"
    assert document["current_operation"]["devices_opened"] == 1
    assert document["current_operation"]["devices_closed"] == 1


def test_device_state_matches_xml():
    root, document = _with_operation()

    xml_device = next(d for d in root.iter("Device") if d.get("lua_name") == "TANK1V1")
    json_device = next(d for obj in document["tech_objects"] for d in obj["devices"]
                       if d["lua_name"] == "TANK1V1")

    assert xml_device.get("operation_state") == json_device["operation_state"] == "открыто"
    assert json_device["operation_state_name"] == "Наполнение"
    assert json_device["operation_step_number"] == 1

    other = next(d for obj in document["tech_objects"] for d in obj["devices"]
                 if d["lua_name"] == "TANK1V2")
    assert other["operation_state"] == "не используется"


# ---------------------------------------------------------------- выбор формата

def test_format_chosen_by_extension():
    # Простой «.json» — формат редактора мнемосхем: его читает конечный
    # проект, и именно он нужен человеку по умолчанию
    assert exporters.format_name("схема.json") == "JSON для редактора"
    assert exporters.format_name("схема.plant.json") == "PlantGeometry JSON"
    assert exporters.format_name("схема.xml") == "XML"


def test_compound_suffix_wins_over_plain():
    # «.plant.json» заканчивается на «.json», и порядок проверки решает,
    # какой из двух форматов получится
    assert exporters.suffix_of("выгрузка.plant.json") == ".plant.json"
    assert exporters.suffix_of("выгрузка.json") == ".json"


def test_unknown_format_is_refused():
    # Молча записать XML под именем .txt хуже, чем отказаться
    try:
        exporters.export_visualization("m.svg", "выгрузка.txt", MATCHES, CONTOURS)
    except ValueError as e:
        assert "txt" in str(e)
    else:
        raise AssertionError("неизвестное расширение должно отвергаться")


def test_missing_suffix_taken_from_dialog_filter():
    # Диалог сохранения отдаёт имя без расширения, если его не набрали руками
    assert exporters.with_suffix(
        "выгрузка", "JSON для редактора мнемосхем (*.json)").endswith(".json")
    assert exporters.with_suffix(
        "выгрузка", "JSON PlantGeometry (*.plant.json)").endswith(".plant.json")
    assert exporters.with_suffix("выгрузка", "XML files (*.xml)").endswith(".xml")
    assert exporters.with_suffix("выгрузка.json", "XML files (*.xml)").endswith(".json"), \
        "набранное руками расширение важнее фильтра"


def test_outline_size_stays_in_the_window():
    """Обводка устройства — способ смотреть в окне, в выгрузки она не уходит.

    view_size (габарит) и view_shape (линии символа) заполняет разметка,
    и живут они отдельно от extra_data намеренно: extra_data экспортёры
    перебирают целиком, и любой ключ оттуда уехал бы потребителю.
    """
    saved = [(match.view_size, match.view_shape) for match in MATCHES]
    try:
        for match in MATCHES:
            match.view_size = (48.0, 30.0)
            match.view_shape = [(-10.0, -10.0, 10.0, 10.0)]
        root, data = _export_both()
    finally:
        for match, (size, shape) in zip(MATCHES, saved, strict=True):
            match.view_size, match.view_shape = size, shape

    written = json.dumps(data, ensure_ascii=False) + ET.tostring(root, encoding="unicode")
    for leaked in ("view_size", "view_shape"):
        assert leaked not in written, f"обводка уехала в выгрузку: {leaked}"


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
