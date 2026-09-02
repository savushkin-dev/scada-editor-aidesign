# tests/test_lua_shared.py
# Обмен сигналами с соседними контроллерами: разбор `shared.lua`.
#
# Сигнал `LINE2DI501` в main.io.lua выглядит как обычный канал ввода-вывода,
# и по нему не видно, что это строка обмена с чужим контроллером. Отчёт
# отсеивал такие имена косвенно — «сопоставился ли на этом листе хоть один
# сигнал», — а `shared.lua` говорит это прямо.
#
# Ловится здесь главным образом одно: имена сигналов в этом файле —
# необъявленные глобальные, и при обычном выполнении список выходит пустым
# (в Lua необъявленное имя это nil). Разбор вешает на _G метатаблицу,
# возвращающую само имя, и из-за неё же нельзя спрашивать «есть ли таблица
# remote_gateways» обычным способом: метатаблица ответит «есть» на что угодно.
#
# Запуск из папки CONTUR:
#     python tests/test_lua_shared.py
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import config
from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.lua import parse_lua_shared

MCA = config.INPUT_DIR.parent / "inputMCA"

SHARED = """
remote_gateways =
{
    ['BN1-Молокохранилище'] =
    {
        ip      = '10.170.98.140',
        port    = 10502,
        enabled = true,
        station = 201,
        DI =
        {
        __LINE1DI1101,
        __LINE1DI1102,
        },
        DO =
        {
        LINE1DO1101,
        },
    },
}
"""


def _file(text, name="shared.lua"):
    path = Path(tempfile.mkdtemp(prefix="contur_shared_")) / name
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- разбор

def test_signal_names_survive_being_undefined():
    """Имена сигналов — необъявленные глобальные, и это главная ловушка.

    Без метатаблицы на _G список выходит пустым: Lua честно возвращает nil
    на каждое имя, и обмен пропадает целиком, не сообщая об этом.
    """
    shared = parse_lua_shared.parse_shared_file(str(_file(SHARED)))

    assert len(shared["gateways"]) == 1, "шлюз не прочитан"
    assert sorted(shared["signals"]) == ["LINE1DI1101", "LINE1DI1102", "LINE1DO1101"]


def test_leading_underscores_are_dropped():
    # В DI сигнал записан как __LINE1DI1101 — это их запись локальной копии;
    # в main.io.lua устройство называется без подчёркиваний, иначе не сойдётся
    shared = parse_lua_shared.parse_shared_file(str(_file(SHARED)))

    assert "LINE1DI1101" in shared["signals"]
    assert not any(name.startswith("_") for name in shared["signals"])


def test_direction_says_who_reads_and_who_writes():
    shared = parse_lua_shared.parse_shared_file(str(_file(SHARED)))

    assert shared["signals"]["LINE1DI1101"]["direction"] == "приём"
    assert shared["signals"]["LINE1DO1101"]["direction"] == "передача"
    assert shared["signals"]["LINE1DO1101"]["station"] == 201
    assert shared["signals"]["LINE1DO1101"]["gateway"] == "BN1-Молокохранилище"


def test_file_without_gateways_gives_nothing():
    # Метатаблица отвечает на любое имя, поэтому «есть ли таблица» нельзя
    # спрашивать обычным способом: она ответит «есть» и вернёт строку
    shared = parse_lua_shared.parse_shared_file(str(_file("restrictions = {}\n")))

    assert shared == {"gateways": [], "signals": {}}


# ---------------------------------------------------------------- привязка

def test_attach_marks_only_the_exchange_signals():
    path = _file(SHARED)
    data = {"devices": [
        {"name": "LINE1DI1101", "descr": "Мойка готова"},
        {"name": "LINE1V1", "descr": "Клапан"},
    ]}

    touched = parse_lua_shared.attach(data, [str(path.parent / "main.io.lua")])

    assert touched == 1, "помечено не то количество устройств"
    assert data["devices"][0]["exchange"]["gateway"] == "BN1-Молокохранилище"
    assert "exchange" not in data["devices"][1], "клапан обменом не является"
    assert len(data["gateways"]) == 1


def test_without_the_file_nothing_changes():
    # Файл необязательный: у двух проектов из трёх его нет вовсе, и разбор
    # обязан пройти так, будто ничего не случилось
    data = {"devices": [{"name": "LINE1DI1101"}]}
    folder = Path(tempfile.mkdtemp(prefix="contur_noshared_"))

    assert parse_lua_shared.attach(data, [str(folder / "main.io.lua")]) == 0
    assert "exchange" not in data["devices"][0]
    assert "gateways" not in data


def test_real_project_joins_completely():
    """На настоящем проекте все сигналы обмена находятся среди устройств.

    Если бы имена расходились — например, у нас остались бы подчёркивания, —
    привязка молча дала бы ноль, и разбор выглядел бы работающим.
    """
    if not (MCA / "shared.lua").exists():
        return

    from contur.lua import parse_lua

    data = parse_lua.parse_lua_file(str(MCA / "main.io.lua"))
    names = {(d.get("name") or "").upper() for d in data["devices"]}
    shared = parse_lua_shared.parse_shared_file(str(MCA / "shared.lua"))

    assert len(shared["gateways"]) == 3
    missing = sorted(set(shared["signals"]) - names)
    assert not missing, f"сигналов обмена нет среди устройств: {missing[:5]}"
    assert sum(1 for d in data["devices"] if d.get("exchange")) == len(shared["signals"])


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
