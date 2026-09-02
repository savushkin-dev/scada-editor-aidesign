# tests/test_device_names.py
# Разбор имён устройств из Lua на техобъект, тип и номер.
#
# Имя в Lua устроено как <техобъект><ТИП><номер>: LA_TANK1V101 — это клапан
# V101 объекта LA_TANK1. Не разобралось имя — устройство не сопоставляется
# с чертежом вовсе и молча выпадает из работы.
#
# Список типов уже дважды оказывался неполным. Сначала в нём не было
# GS, HDOG, SB, G, HL, HLA — терялись 29 устройств из 401. Пополненный под
# один проект, он снова не подошёл ко второму: в mozzarella не разбирались
# VC (регулирующие клапаны), HA (сирены), TC и FC (регуляторы) — 13 из 730.
#
# Поэтому проверка идёт по двум независимым проектам сразу. Второго нет
# в репозитории, и без него проверки пропускаются, а не падают.
#
# Запуск из папки CONTUR:
#     python tests/test_device_names.py
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from device_matcher import DEVICE_TYPES

# Все проекты контроллеров, какие есть под рукой
PROJECTS = {
    "молокохранилище": config.INPUT_DIR / "test1" / "main.io.lua",
    "mozzarella": config.INPUT_DIR.parent / "mozzarella_master_01" / "main.io.lua",
    "MCA1": config.INPUT_DIR.parent / "inputMCA" / "main.io.lua",
}

# Техобъекта в имени может не быть вовсе — `(.*?)`, а не `(.+?)`. В проекте
# MCA1 так названы 22 устройства из 356: общая обвязка станции мойки
# (`V1`, `LT2`, `FQT1`). Правило здесь должно совпадать с правилом
# сопоставления, иначе проверка сторожит не то, что работает
PATTERN = rf"^(.*?){DEVICE_TYPES}\d+$"


def _devices(path: Path):
    from parse_lua import parse_lua_file

    return [device.get("name", "")
            for device in parse_lua_file(str(path)).get("devices", [])
            if device.get("name") and config.is_device_name(device["name"])]


def _split(name: str):
    match = re.match(PATTERN, name)
    return (match.group(1), match.group(2)) if match else None


# ---------------------------------------------------------------- полнота

def test_every_name_in_every_project_parses():
    checked = 0
    for label, path in PROJECTS.items():
        if not path.exists():
            print(f"  ПРОПУСК {label}: нет {path.name}")
            continue

        names = _devices(path)
        assert names, f"{label}: устройств не найдено вовсе"

        unparsed = [name for name in names if not _split(name)]
        assert not unparsed, (
            f"{label}: не разобрано {len(unparsed)} имён из {len(names)} — "
            f"эти устройства не будут сопоставлены: {sorted(set(unparsed))[:10]}")
        checked += 1

    assert checked, "не проверен ни один проект"


def test_second_project_is_actually_checked():
    # Проверка по двум проектам имеет смысл, только пока второй на месте.
    # Если он пропал, лучше знать об этом, чем считать список полным
    path = PROJECTS["mozzarella"]
    if not path.exists():
        print(f"  ПРОПУСК: второго проекта нет ({path})")
        return

    names = _devices(path)
    assert len(names) > 500, f"устройств во втором проекте всего {len(names)}"


# ---------------------------------------------------------------- разбор

def test_name_splits_into_object_and_type():
    assert _split("LA_TANK1V101") == ("LA_TANK1", "V")
    assert _split("BRINE_TANK1V1") == ("BRINE_TANK1", "V")
    assert _split("CIPV16") == ("CIP", "V")
    assert _split("HEATER1VC1") == ("HEATER1", "VC")


def test_name_without_tech_object_parses():
    # Общая обвязка станции мойки MCA1: объекта у устройства нет ни в имени,
    # ни в описании объектов. Раньше такие имена не разбирались, устройство
    # молча выпадало из работы, а FQT1 разбирался ещё и неверно — как объект
    # «F» с устройством QT1
    assert _split("V1") == ("", "V")
    assert _split("LT2") == ("", "LT")
    assert _split("FQT1") == ("", "FQT"), "расходомер разобран как объект F"
    assert _split("M3") == ("", "M")


def test_types_missing_from_the_list_are_back():
    # Четыре типа значились в ОБОЗНАЧЕНИЯ.md как «вне списка»: устройства
    # с ними не разбирались и в сопоставление не попадали
    assert _split("LINE1FS1") == ("LINE1", "FS"), "реле потока"
    assert _split("ALMIX1WT1") == ("ALMIX1", "WT"), "тензодатчик"
    assert _split("ALMIX1WC1") == ("ALMIX1", "WC"), "весовой регулятор"
    assert _split("CW_TANK1LC1") == ("CW_TANK1", "LC"), "регулятор уровня"


def test_longer_designation_wins():
    # FQT не должен разбираться как FC или F, HLA — как HL, TC — как TE.
    # Порядок веток в device_types_pattern() сортирует длинные первыми,
    # и добавление FC рядом с FQT — ровно тот случай, ради которого это нужно
    assert _split("M10FQT1") == ("M10", "FQT"), "FQT перехвачен более коротким типом"
    assert _split("WR1FC1") == ("WR1", "FC")
    assert _split("MCC1HLA1") == ("MCC1", "HLA"), "HLA разобран как HL"
    assert _split("LINE_M10HL1") == ("LINE_M10", "HL")
    assert _split("HEATER1TC1") == ("HEATER1", "TC"), "TC спутан с TE"
    assert _split("TANK1TE1") == ("TANK1", "TE")


def test_software_entities_are_not_devices():
    # Из WATCHDOG вырезалось «HDOG», и девять программных сторожевых таймеров
    # превращались в устройства с искажённым техобъектом
    assert not config.is_device_name("LINE_M1WATCHDOG11")
    assert config.is_device_name("LA_TANK1V101")


# ---------------------------------------------------------------- классы

def test_class_matches_designation():
    # Сверка класса модели с подписью: модель видит насос, а подпись
    # говорит V12 — привязка подписи почти наверняка неверна
    assert config.device_type_matches_class("V", "valve") is True
    assert config.device_type_matches_class("VC", "valve") is True, \
        "регулирующий клапан не признан клапаном"
    assert config.device_type_matches_class("TC", "sensor") is True
    assert config.device_type_matches_class("FC", "sensor") is True
    assert config.device_type_matches_class("M", "pump") is True

    assert config.device_type_matches_class("V", "pump") is False
    assert config.device_type_matches_class("M", "valve") is False


def test_signalling_has_no_class():
    # Сирены и лампы на схеме не технологические устройства: модель такого
    # класса не знает, и сверка давала бы ложные расхождения
    for designation in ("HA", "HL", "HLA", "SB"):
        for cls in ("valve", "sensor", "pump"):
            assert config.device_type_matches_class(designation, cls) is False, \
                f"{designation} сочтён классом {cls}"


def test_unknown_input_gives_no_verdict():
    assert config.device_type_matches_class("", "valve") is None
    assert config.device_type_matches_class("V", "") is None
    assert config.device_type_matches_class("V", "мешалка") is None, \
        "класса, которого модель не знает, судить не по чему"


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
