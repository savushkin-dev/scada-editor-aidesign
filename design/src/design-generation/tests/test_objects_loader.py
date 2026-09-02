# tests/test_objects_loader.py
# Разбор описания технологических объектов.
#
# 434 строки, которыми пользуется окно: дерево операций, состояния устройств
# в операции, подсказки с шагами. Проверок не было ни одной, при том что
# данные приходят из чужого файла — выгрузки среды разработки контроллера,
# и её формат конвейеру не подчиняется.
#
# Проверяется в том числе поведение на неполных данных: состояние без шагов,
# шаг не словарём, устройство числом вместо имени. Всё это в настоящих
# выгрузках встречается.
#
# Запуск из папки CONTUR:
#     python tests/test_objects_loader.py
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from objects_loader import ObjectsData

# Выгрузка в том виде, в каком её отдаёт среда: техобъект с операциями,
# состояния отдельным списком, шаги внутри state_data словарём
DATA = {
    "tech_objects": [
        {
            "id": "1", "n": 1, "tech_type": 2,
            "name": "Танк", "name_eplan": "LA_TANK1", "name_BC": "TANK1",
            "base_tech_object": "tank", "cooper_param_number": 3,
            "properties": {"тип": "ёмкость"},
            "equipment": {"насос": "M1"},
            "operations": [
                {"id": "оп1", "name": "Мойка", "base_operation": "wash",
                 "props": {"время": 10}},
                {"id": "оп2", "name": "Выдача", "base_operation": "out"},
            ],
        },
        {
            "id": "2", "n": 2, "name": "Линия", "name_eplan": "LINE_M1",
            "operations": [],
        },
    ],
    "parameters": [
        {"id": "п1", "name": "Объём", "value": 1000, "meter": "л",
         "nameLua": "V", "oper": [1], "obj_id": "1"},
        {"id": "п2", "name": "Температура", "value": 60, "meter": "°C",
         "nameLua": "T", "oper": [], "obj_id": "1"},
    ],
    "states": [
        {
            "state_id": "с1", "operation_id": "оп1", "operation_name": "Мойка",
            "obj_id": "1", "obj_name": "Танк",
            "state_data": {
                "name": "Наполнение",
                "opened_devices": ["LA_TANK1V1"],
                "closed_devices": ["LA_TANK1V2"],
                "steps": {
                    "2": {"name": "Второй", "opened_devices": ["LA_TANK1V3"],
                          "next_step_n": 3},
                    "1": {"name": "Первый", "closed_devices": ["LA_TANK1V4"],
                          "time_param_n": 5},
                    "мусор": "шаг не словарём — в выгрузках встречается",
                },
            },
        },
        {
            "state_id": "с2", "operation_id": "оп2", "operation_name": "Выдача",
            "obj_id": "1", "obj_name": "Танк",
            "state_data": {"name": "Слив"},
        },
    ],
}


def _loaded() -> ObjectsData:
    data = ObjectsData()
    data.load_from_json(DATA)
    return data


# ---------------------------------------------------------------- разбор

def test_reads_every_section():
    data = _loaded()

    assert len(data.objects) == 2, f"техобъектов: {len(data.objects)}"
    assert len(data.operations) == 2, f"операций: {len(data.operations)}"
    assert len(data.states) == 2, f"состояний: {len(data.states)}"
    assert len(data.parameters) == 2, f"параметров: {len(data.parameters)}"
    assert len(data.steps) == 2, f"шагов: {len(data.steps)}"


def test_object_keeps_its_details():
    tank = _loaded().objects_by_id["1"]

    assert tank.name == "Танк" and tank.name_eplan == "LA_TANK1"
    assert tank.tech_type == 2 and tank.n == 1
    assert tank.properties == {"тип": "ёмкость"}
    assert tank.equipment == {"насос": "M1"}
    assert len(tank.operations) == 2, "операции не привязались к объекту"


def test_missing_fields_get_defaults():
    # Второй объект описан скупо — разбор не должен на этом падать
    line = _loaded().objects_by_id["2"]

    assert line.name == "Линия"
    assert line.tech_type == 0, f"тип по умолчанию: {line.tech_type}"
    assert line.cooper_param_number == -1
    assert line.properties == {} and line.operations == []


def test_operation_knows_its_object():
    operation = _loaded().get_operation_by_id("оп1")

    assert operation is not None, "операция не нашлась по идентификатору"
    assert operation.obj_id == "1" and operation.obj_name == "Танк", \
        "операция не знает, чьей она является"
    assert operation.props == {"время": 10}


def test_steps_are_sorted_by_number():
    # В выгрузке шаги лежат словарём, и их порядок произвольный:
    # в этих данных второй записан раньше первого
    state = _loaded().get_states_for_operation("оп1")[0]

    assert [step.step_number for step in state.steps] == [1, 2], \
        f"порядок шагов: {[s.step_number for s in state.steps]}"
    assert [step.name for step in state.steps] == ["Первый", "Второй"]


def test_step_identifier_includes_state():
    # Номера шагов повторяются в каждом состоянии, поэтому идентификатор
    # составной — иначе шаги разных состояний склеились бы
    steps = _loaded().get_steps_for_state("с1")

    assert {step.id for step in steps} == {"с1_1", "с1_2"}, \
        f"идентификаторы шагов: {[s.id for s in steps]}"


def test_broken_step_is_skipped_not_fatal():
    # Среди шагов лежит строка вместо словаря — остальные обязаны прочитаться
    assert len(_loaded().get_steps_for_state("с1")) == 2, \
        "кривой шаг унёс с собой исправные"


def test_state_without_steps_is_fine():
    data = _loaded()
    state = data.get_states_for_operation("оп2")[0]

    assert state.name == "Слив"
    assert state.steps == [] and data.get_steps_for_state("с2") == []


def test_parameters_are_grouped_by_object():
    data = _loaded()

    assert len(data.get_parameters_for_object("1")) == 2
    assert data.get_parameters_for_object("нет такого") == []


# ---------------------------------------------------------------- поиск

def test_object_is_found_by_any_of_its_names():
    # Имя в Lua, обозначение Eplan и имя в системе управления — разные,
    # и сопоставление приходит то с одним, то с другим
    data = _loaded()

    for name in ("Танк", "LA_TANK1", "TANK1"):
        assert data.get_object_by_name(name) is not None, f"не нашёлся по {name!r}"
    assert data.get_object_by_name("нет такого") is None


def test_operation_names_are_sorted():
    assert _loaded().get_operation_names() == ["Выдача", "Мойка"]


def test_object_for_operation():
    data = _loaded()
    operation = data.get_operation_by_name("Мойка")

    assert data.get_object_for_operation(operation).name == "Танк"


# ---------------------------------------------------------------- устройства

def test_devices_take_state_and_steps():
    # Окно раскрашивает дерево устройств этим словарём
    devices = _loaded().get_devices_for_operation("оп1")

    assert devices == {
        "LA_TANK1V1": "opened",   # из состояния
        "LA_TANK1V2": "closed",   # из состояния
        "LA_TANK1V3": "opened",   # из шага
        "LA_TANK1V4": "closed",   # из шага
    }, f"состояния устройств: {devices}"


def test_operation_without_devices_gives_empty():
    assert _loaded().get_devices_for_operation("оп2") == {}
    assert _loaded().get_devices_for_operation("нет такой") == {}


def test_device_details_name_the_step():
    # Подсказка в дереве устройств показывает, на каком шаге это происходит
    data = _loaded()

    from_state = data.get_device_details_in_operation("оп1", "LA_TANK1V1")
    assert from_state["status"] == "opened"
    assert from_state["state_name"] == "Наполнение"
    assert from_state["step_name"] is None, "устройство состояния приписано шагу"

    from_step = data.get_device_details_in_operation("оп1", "LA_TANK1V3")
    assert from_step["step_name"] == "Второй", f"шаг: {from_step}"
    assert from_step["step_number"] == 2

    assert data.get_device_details_in_operation("оп1", "нет такого") is None


def test_device_name_survives_the_shapes_it_arrives_in():
    data = ObjectsData()

    assert data._extract_device_name("LA_TANK1V1") == "LA_TANK1V1"
    assert data._extract_device_name("  LA_TANK1V1  ") == "LA_TANK1V1"
    assert data._extract_device_name("LA_TANK1V1 открыть") == "LA_TANK1V1", \
        "пояснение после имени не отброшено"
    assert data._extract_device_name('"LA_TANK1V1"') == "LA_TANK1V1"
    assert data._extract_device_name({"name": "LA_TANK1V1"}) == "LA_TANK1V1"
    assert data._extract_device_name({"dev": "LA_TANK1V1"}) == "LA_TANK1V1"
    assert data._extract_device_name(42) == "42"
    assert data._extract_device_name(None) is None
    assert data._extract_device_name({"чужой ключ": "V1"}) is None


# ---------------------------------------------------------------- файл

def test_reload_forgets_the_previous_file():
    # Окно грузит другой проект поверх открытого, и остатки прежнего
    # смешались бы с новым
    data = _loaded()
    assert data.objects, "нечего забывать"

    data.load_from_json({"tech_objects": [], "states": [], "parameters": []})

    assert not data.objects and not data.operations and not data.states
    assert not data.steps and not data.parameters
    assert not data.objects_by_id and not data.states_by_operation_id, \
        "указатели остались от прежнего проекта"


def test_missing_file_is_refused_not_fatal():
    data = ObjectsData()
    assert data.load(str(Path(tempfile.gettempdir()) / "нет-такого-файла.json")) is False


def _temp_json(text: str) -> Path:
    path = Path(tempfile.mkdtemp(prefix="contur_objects_")) / "объекты.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_broken_file_is_refused_not_fatal():
    path = _temp_json('{"tech_objects": [')
    try:
        assert ObjectsData().load(str(path)) is False, \
            "обрезанный файл прочитался как исправный"
    finally:
        shutil.rmtree(path.parent, ignore_errors=True)


# ------------------------------------------- состояния устройства во всех операциях

def test_device_states_collect_every_place():
    # Выгрузке для редактора нужно не «состояние в выбранной операции»,
    # а весь список: где устройство открывается и где закрывается
    states = _loaded().get_device_states("LA_TANK1V1")

    assert len(states) == 1, f"мест: {len(states)}"
    assert states[0]["status"] == "opened"
    assert states[0]["operation"] == "Мойка" and states[0]["state"] == "Наполнение"
    assert states[0]["tech_object"] == "Танк" and states[0]["tech_object_id"] == "1"
    assert states[0]["step_id"] == "", "здесь открывает состояние, а не шаг"


def test_device_states_see_steps():
    states = _loaded().get_device_states("LA_TANK1V3")

    assert len(states) == 1
    assert states[0]["status"] == "opened"
    assert states[0]["step"] == "Второй" and states[0]["step_number"] == 2


def test_device_states_are_ordered():
    # Порядок задаётся содержимым: один и тот же проект должен давать
    # одинаковую выгрузку от прогона к прогону
    data = _loaded()

    for name in ("LA_TANK1V1", "LA_TANK1V2", "LA_TANK1V3", "LA_TANK1V4"):
        states = data.get_device_states(name)
        keys = [(s["operation"], s["operation_id"], s["state"],
                 s["step_number"], s["step"], s["status"]) for s in states]
        assert keys == sorted(keys), f"{name}: состояния не упорядочены"


def test_unknown_device_has_no_states():
    assert _loaded().get_device_states("НЕТ_ТАКОГО") == []
    assert _loaded().get_device_states("") == []


def test_device_states_survive_reload():
    # Индекс считается лениво и кэшируется — после повторной загрузки
    # он обязан пересчитаться, иначе останутся состояния прошлого проекта
    data = _loaded()
    assert data.get_device_states("LA_TANK1V1")

    data.load_from_json({"tech_objects": [], "states": []})
    assert data.get_device_states("LA_TANK1V1") == [], "индекс не сбросился"


def test_operation_device_states_look_from_the_other_side():
    # Тот же индекс, но со стороны операции: панель сведений показывает
    # и устройство, и операцию, и рассказать про них разное не должна
    data = _loaded()
    places = data.get_operation_device_states("оп1")
    devices = sorted({place["device"] for place in places})

    assert devices == ["LA_TANK1V1", "LA_TANK1V2", "LA_TANK1V3", "LA_TANK1V4"], \
        f"устройства операции: {devices}"
    assert all(place["operation_id"] == "оп1" for place in places), \
        "в операцию попали записи чужой операции"
    assert {place["status"] for place in places} == {"opened", "closed"}, \
        "положения потерялись"


def test_operation_device_states_agree_with_the_device_side():
    data = _loaded()
    from_device = data.get_device_states("LA_TANK1V3")
    from_operation = [place for place in data.get_operation_device_states("оп1")
                      if place["device"] == "LA_TANK1V3"]

    assert len(from_operation) == len(from_device), "стороны насчитали разное"
    assert from_operation[0]["step"] == from_device[0]["step"], "шаг разошёлся"
    assert from_operation[0]["status"] == from_device[0]["status"], "положение разошлось"


def test_operation_device_states_are_ordered():
    # Порядок задаётся содержимым, а не порядком обхода словаря
    places = _loaded().get_operation_device_states("оп1")
    keys = [(p["state"], p["state_id"], p["step_number"], p["step"],
             p["device"], p["status"]) for p in places]

    assert keys == sorted(keys), "записи операции не упорядочены"


def test_unknown_operation_has_no_device_states():
    assert _loaded().get_operation_device_states("нет-такой") == []
    assert _loaded().get_operation_device_states("") == []


def test_operation_program_lists_steps():
    # Состояние устройства ссылается на операцию по operation_id —
    # сама программа должна доставаться по тому же идентификатору
    program = _loaded().get_operation_program("оп1")

    assert program is not None, "программа операции не нашлась"
    assert program["name"] == "Мойка" and program["tech_object"] == "Танк"
    assert len(program["states"]) == 1

    steps = program["states"][0]["steps"]
    assert [s["number"] for s in steps] == [1, 2], "шаги не по порядку"
    assert steps[1]["opened_devices"] == ["LA_TANK1V3"]
    assert steps[0]["closed_devices"] == ["LA_TANK1V4"]


def test_unknown_operation_has_no_program():
    assert _loaded().get_operation_program("нет") is None


def test_real_file_is_read():
    path = _temp_json(json.dumps(DATA, ensure_ascii=False))
    try:
        data = ObjectsData()
        assert data.load(str(path)) is True, "исправный файл не прочитался"
        assert len(data.objects) == 2
    finally:
        shutil.rmtree(path.parent, ignore_errors=True)


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
