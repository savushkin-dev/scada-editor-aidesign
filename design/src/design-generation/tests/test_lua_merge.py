# tests/test_lua_merge.py
# Слияние разбора нескольких файлов Lua в один набор.
#
# Файлов с устройствами у проекта бывает несколько, и одно устройство описано
# сразу в нескольких: в mozzarella main.io.lua и main.wago.lua дают 730 + 568
# записей при 771 разном имени. Склейка списков подряд удваивала хозяйство —
# приложение показывало 1298 устройств вместо 771, а отчёт о расхождениях
# перечислял одно и то же устройство дважды.
#
# Повторы почти всегда одинаковы, но не всегда: в тринадцати записях
# различается одно поле, и полнее оно в первом файле. Отсюда правило,
# которое и сторожат проверки: первая запись главная, последующие дополняют
# только её пустые поля.
#
# Запуск из папки CONTUR:
#     python tests/test_lua_merge.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from parse_lua import merge_lua_data

MOZZARELLA = Path(__file__).resolve().parent.parent.parent / "mozzarella_master_01"


def data(nodes=(), devices=()):
    return {"nodes": list(nodes), "devices": list(devices)}


# ---------------------------------------------------------------- повторы

def test_same_device_in_two_files_counted_once():
    merged = merge_lua_data([
        data(devices=[{"name": "V1", "descr": "Приём"}]),
        data(devices=[{"name": "V1", "descr": "Приём"}]),
    ])
    assert len(merged["devices"]) == 1, "одно устройство, описанное дважды, — одно устройство"
    assert merged["devices"][0]["descr"] == "Приём"


def test_nodes_are_merged_too():
    merged = merge_lua_data([
        data(nodes=[{"name": "A1", "IP": "10.0.0.1"}]),
        data(nodes=[{"name": "A1", "IP": "10.0.0.1"}, {"name": "A2"}]),
    ])
    assert [n["name"] for n in merged["nodes"]] == ["A1", "A2"]


def test_first_file_wins_on_conflict():
    # Настоящий случай: в main.io.lua артикул с приставкой поставщика,
    # в main.wago.lua — усечённый
    merged = merge_lua_data([
        data(devices=[{"name": "SB1", "article": "SE.XB4BS8445"}]),
        data(devices=[{"name": "SB1", "article": "XB4BS8445"}]),
    ])
    assert merged["devices"][0]["article"] == "SE.XB4BS8445", \
        "полнее описание в первом файле, его и держим"


def test_later_file_fills_empty_fields():
    merged = merge_lua_data([
        data(devices=[{"name": "V1", "article": "", "descr": "Приём"}]),
        data(devices=[{"name": "V1", "article": "OMR.E2A", "subtype": 13}]),
    ])
    device = merged["devices"][0]
    assert device["article"] == "OMR.E2A", "пустое поле дополняется из следующего файла"
    assert device["descr"] == "Приём", "непустое поле остаётся своим"
    assert device["subtype"] == 13, "поле, которого не было вовсе, добавляется"


def test_zero_is_a_value_not_a_gap():
    merged = merge_lua_data([
        data(devices=[{"name": "V1", "subtype": 0}]),
        data(devices=[{"name": "V1", "subtype": 13}]),
    ])
    assert merged["devices"][0]["subtype"] == 0, "ноль — это значение, затирать его нечем"


def test_order_is_kept():
    merged = merge_lua_data([
        data(devices=[{"name": "V1"}, {"name": "V2"}]),
        data(devices=[{"name": "V3"}, {"name": "V1"}]),
    ])
    assert [d["name"] for d in merged["devices"]] == ["V1", "V2", "V3"], \
        "порядок первого появления сохраняется"


def test_nameless_records_are_kept():
    merged = merge_lua_data([data(devices=[{"descr": "без имени"}, {"descr": "и ещё"}])])
    assert len(merged["devices"]) == 2, "запись без имени опознать нельзя, выбрасывать нечего"


def test_single_file_is_unchanged():
    devices = [{"name": "V1"}, {"name": "V2"}]
    merged = merge_lua_data([data(devices=devices)])
    assert merged["devices"] == devices, "одному файлу сливать не с чем"


# ------------------------------------------------- на настоящем проекте

def test_mozzarella_two_files_give_unique_devices():
    # Второго проекта в репозитории нет — без него проверка пропускается
    io_lua, wago_lua = MOZZARELLA / "main.io.lua", MOZZARELLA / "main.wago.lua"
    if not (io_lua.exists() and wago_lua.exists()):
        return

    from parse_lua import parse_lua_file

    merged = merge_lua_data([parse_lua_file(str(io_lua)), parse_lua_file(str(wago_lua))])
    names = [d.get("name") for d in merged["devices"]]
    assert len(names) == len(set(names)), \
        f"устройств {len(names)}, разных имён {len(set(names))}"

    node_names = [n.get("name") for n in merged["nodes"]]
    assert len(node_names) == len(set(node_names)), "узлы тоже не должны повторяться"

    # Артикул аварийной кнопки берётся из main.io.lua, а не из усечённой копии
    buttons = [d for d in merged["devices"] if d.get("name") == "CAB1SB1"]
    if buttons:
        assert buttons[0].get("article") == "SE.XB4BS8445", \
            f"артикул усечён: {buttons[0].get('article')}"


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
