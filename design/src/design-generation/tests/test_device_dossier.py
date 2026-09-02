# tests/test_device_dossier.py
# Досье устройства: всё известное — при самом устройстве.
#
# Раньше сведения жили в трёх местах: часть при устройстве (описание, теги),
# часть панель добывала при каждом щелчке, часть выгрузка считала в момент
# записи файла, а поле состояний в модели так и оставалось пустым. Три
# источника одного и того же — три способа разойтись.
#
# Проверяется здесь то, из-за чего досье молча оказалось бы неполным:
# устройство ищется в описании операций двумя именами (из контроллера
# и с чертежа), техобъект — с номером и без, а повторный вызов обязан
# переписать досье целиком, иначе после перезагрузки описания объектов
# в нём осталось бы старое.
#
# Запуск из папки CONTUR:
#     python tests/test_device_dossier.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.matching import device_dossier
from contur.core.data_models import DeviceMatch
from contur.lua.objects_loader import objects_data

OBJECTS = {
    "tech_objects": [
        {
            "id": "1", "n": 1, "tech_type": 2,
            "name": "Танк №1", "name_eplan": "LA_TANK1", "name_BC": "TANK1",
            "base_tech_object": "tank", "cooper_param_number": 3,
            "properties": {"среда": "молоко"},
            "equipment": {"насос": "M1"},
            "operations": [
                {"id": "оп1", "name": "Мойка", "base_operation": "wash",
                 "props": {"время": 10}},
            ],
        },
        # Объект назван без номера, номер отдельным полем — так его пишет
        # среда разработки контроллера почти всегда
        {
            "id": "2", "n": 1, "tech_type": 3,
            "name": "Танк рассола", "name_eplan": "BRINE_TANK",
            "name_BC": "BrineTank1Obj1", "base_tech_object": "tank",
            "operations": [],
        },
    ],
    "parameters": [
        {"id": "п1", "name": "Объём", "value": 1000, "meter": "л",
         "nameLua": "V_TANK", "oper": [1], "obj_id": "1"},
    ],
    "states": [
        {
            "state_id": "с1", "operation_id": "оп1", "operation_name": "Мойка",
            "obj_id": "1", "obj_name": "Танк №1",
            "state_data": {
                "name": "Наполнение",
                "opened_devices": ["LA_TANK1V1"],
                "steps": {
                    "1": {"name": "Первый", "opened_devices": ["LA_TANK1V1"]},
                    "2": {"name": "Второй", "closed_devices": ["LA_TANK1V1"]},
                },
            },
        },
    ],
}


class _Pipeline:
    """Трубопровод в том виде, в каком его отдаёт разбор геометрии."""

    def __init__(self, devices):
        self.connected_devices = list(devices)


def _valve(**kwargs):
    fields = {"lua_name": "LA_TANK1V1", "pdf_name": "V1",
              "tech_object": "LA_TANK1", "coordinates": (100.0, 200.0),
              "confidence": 1.0, "device_type": "V", "descr": "Донный клапан"}
    fields.update(kwargs)
    return DeviceMatch(**fields)


def _loaded():
    objects_data.load_from_json(OBJECTS)


# ---------------------------------------------------------------- состояния

def test_states_are_pinned_to_the_device():
    """Состояний в модели устройства не было вовсе — поле пустовало."""
    _loaded()
    valve = _valve()

    counts = device_dossier.attach([valve])

    assert valve.states, "состояния не закрепились"
    assert counts["states"] == len(valve.states)
    assert {s["operation"] for s in valve.states} == {"Мойка"}
    assert {s["status"] for s in valve.states} == {"opened", "closed"}


def test_states_are_found_by_the_drawing_name_too():
    # В описании операций устройство записывают и полным именем, и подписью
    # с чертежа; у устройства без Lua есть только вторая
    _loaded()
    valve = _valve(lua_name="", pdf_name="LA_TANK1V1")

    device_dossier.attach([valve])

    assert valve.states, "по подписи с чертежа состояния не нашлись"


def test_device_without_operations_gets_an_empty_dossier():
    # Сигнал не участвует ни в одной операции — и это не повод падать
    _loaded()
    signal = _valve(lua_name="LINE_M1DI3", pdf_name="DI3", tech_object="LINE_M1",
                    device_type="DI")

    device_dossier.attach([signal])

    assert signal.states == []
    assert signal.object_data == {}


# ---------------------------------------------------------------- техобъект

def test_tech_object_is_pinned_with_its_settings():
    _loaded()
    valve = _valve()

    device_dossier.attach([valve])

    assert valve.object_data.get("name") == "Танк №1"
    assert valve.object_data.get("properties") == {"среда": "молоко"}
    assert valve.object_data.get("equipment") == {"насос": "M1"}
    assert [p["name"] for p in valve.object_data.get("parameters", [])] == ["Объём"]


def test_tech_object_is_found_with_the_number():
    # В описании объект зовут BRINE_TANK, номер лежит отдельным полем,
    # а на чертеже они вместе — BRINE_TANK1
    _loaded()
    valve = _valve(lua_name="BRINE_TANK1V1", tech_object="BRINE_TANK1")

    device_dossier.attach([valve])

    assert valve.object_data.get("name") == "Танк рассола"


# ---------------------------------------------------------------- соседи

def test_neighbours_come_from_the_pipelines():
    """У трубы записаны её устройства, а нужно обратное — соседи у устройства."""
    _loaded()
    first, second = _valve(), _valve(lua_name="LA_TANK1V2", pdf_name="V2")
    pipe = _Pipeline(["LA_TANK1V1", "LA_TANK1V2"])

    device_dossier.attach([first, second], [pipe])

    assert first.neighbours == ["LA_TANK1V2"]
    assert second.neighbours == ["LA_TANK1V1"]


def test_device_is_not_its_own_neighbour():
    _loaded()
    valve = _valve()

    device_dossier.attach([valve], [_Pipeline(["LA_TANK1V1"])])

    assert valve.neighbours == []


def test_neighbours_are_left_alone_until_the_markup():
    # До разметки трубопроводов нет, и соседей взять неоткуда: досье
    # закрепляется дважды, и первый раз не должен затирать второй
    _loaded()
    valve = _valve()
    device_dossier.attach([valve], [_Pipeline(["LA_TANK1V1", "LA_TANK1V2"])])

    device_dossier.attach([valve])

    assert valve.neighbours == ["LA_TANK1V2"], "соседи потерялись при пересборке"


# ---------------------------------------------------------------- пересборка

def test_second_attach_replaces_and_does_not_double():
    """Описание объектов перезагрузили — досье обязано смениться целиком."""
    _loaded()
    valve = _valve()
    device_dossier.attach([valve])
    was = len(valve.states)

    device_dossier.attach([valve])
    assert len(valve.states) == was, "состояния удвоились"

    objects_data.load_from_json({"tech_objects": [], "parameters": [], "states": []})
    device_dossier.attach([valve])

    assert valve.states == [], "досье осталось от прежнего описания"
    assert valve.object_data == {}


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
