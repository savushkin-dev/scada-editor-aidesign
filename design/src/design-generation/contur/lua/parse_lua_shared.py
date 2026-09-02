# parse_lua_shared.py
# Обмен сигналами с соседними контроллерами: `shared.lua`.
#
# Зачем. Сигнал `LINE2DI501` в `main.io.lua` выглядит как обычный канал
# ввода-вывода, и по нему не видно, что это не датчик проекта, а строка обмена
# с чужим контроллером. Отчёт о расхождениях такие имена приходилось
# отсеивать косвенно — «сопоставился ли на этом листе хоть один сигнал», —
# а на мнемосхеме про них нельзя было сказать ничего.
#
# `shared.lua` говорит это прямо: список удалённых шлюзов (имя, адрес, номер
# станции Modbus) и под каждым — какие сигналы у него читаются (`DI`)
# и какие ему пишутся (`DO`). В проекте станции мойки это три соседних
# контроллера и 146 сигналов, и все 146 нашлись в `main.io.lua`.
#
# Как читается. Файл выполняется настоящим Lua (как и остальные), но имена
# сигналов в нём — необъявленные глобальные (`__LINE2DI501`), и при обычном
# выполнении такой список выходит пустым: в Lua необъявленное имя это `nil`.
# Поэтому перед выполнением на `_G` вешается метатаблица, возвращающая само
# имя, — тогда в списке оказываются строки. В контроллере эти имена
# существуют как объекты устройств, у нас нужно только имя.
#
# Двойное подчёркивание в `DI` — их запись локальной копии удалённого
# сигнала; в `main.io.lua` устройство называется без него, поэтому при
# сопоставлении ведущие подчёркивания снимаются.
#
# Файл необязательный: он есть у проектов, где контроллер обменивается
# с соседями, и отсутствует у остальных. Нет файла — ничего не меняется.
import os
from typing import Any, Dict, List, Optional

from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)

from contur.lua.parse_lua import read_file_with_encoding

# Имя файла и таблицы в нём
FILE_NAME = "shared.lua"
GATEWAYS = "remote_gateways"

# Что чем является: у соседа читается его `DI`, а пишется ему `DO`
DIRECTIONS = {"DI": "приём", "DO": "передача"}

# Необъявленное имя возвращает само себя — иначе список сигналов пуст
NAME_METATABLE = "setmetatable(_G, {__index = function(t, k) return k end})"


def find_beside(paths: List[str]) -> Optional[str]:
    """`shared.lua` рядом с любым из файлов ввода-вывода."""
    for path in paths:
        if not path:
            continue
        candidate = os.path.join(os.path.dirname(os.path.abspath(path)), FILE_NAME)
        if os.path.isfile(candidate):
            return candidate
    return None


def _values(table: Any) -> List[str]:
    if table is None:
        return []
    try:
        return [str(value) for value in table.values() if value is not None]
    except AttributeError:
        return [str(value) for value in table if value is not None]


def parse_shared_file(path: str) -> Dict[str, Any]:
    """Шлюзы и сигналы обмена: {'gateways': [...], 'signals': {ИМЯ: {...}}}."""
    from lupa import LuaRuntime

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(NAME_METATABLE)
    lua.execute(read_file_with_encoding(path))

    # Метатаблица отвечает на любое имя, поэтому спрашиваем rawget:
    # иначе вместо отсутствующей таблицы вернётся строка «remote_gateways»
    table = lua.eval(f"rawget(_G, '{GATEWAYS}')")
    if table is None:
        return {"gateways": [], "signals": {}}

    gateways: List[Dict[str, Any]] = []
    signals: Dict[str, Dict[str, Any]] = {}

    for name in table:
        gateway = table[name]
        record = {
            "name": str(name),
            "ip": str(gateway.ip) if gateway.ip is not None else "",
            "station": int(gateway.station) if gateway.station is not None else 0,
            "port": int(gateway.port) if gateway.port is not None else 0,
            "enabled": bool(gateway.enabled),
            "signals": 0,
        }

        for block, direction in DIRECTIONS.items():
            for raw in _values(getattr(gateway, block, None)):
                # Ведущие подчёркивания — их запись локальной копии
                device = raw.lstrip("_").upper()
                if not device:
                    continue
                signals[device] = {
                    "gateway": record["name"],
                    "ip": record["ip"],
                    "station": record["station"],
                    "direction": direction,
                    "block": block,
                }
                record["signals"] += 1

        gateways.append(record)

    gateways.sort(key=lambda item: item["name"])
    return {"gateways": gateways, "signals": signals}


def attach(lua_data: Dict[str, Any], paths: List[str]) -> int:
    """Проставляет устройствам обмен, если `shared.lua` лежит рядом.

    Возвращает, скольким устройствам он проставлен. Ошибку разбора глотаем
    сознательно: файл необязательный и к работе конвейера отношения не имеет —
    без него всё то же самое, что было раньше.
    """
    path = find_beside(paths)
    if not path:
        return 0

    try:
        shared = parse_shared_file(path)
    except Exception as error:
        print(f"⚠️  {FILE_NAME} прочитать не удалось: {error}")
        return 0

    signals = shared["signals"]
    if not signals:
        return 0

    touched = 0
    for device in lua_data.get("devices", []):
        if not isinstance(device, dict):
            continue
        exchange = signals.get((device.get("name") or "").upper())
        if exchange:
            device["exchange"] = exchange
            touched += 1

    lua_data["gateways"] = shared["gateways"]
    if touched:
        print(f"🔗 Обмен с соседями: {len(shared['gateways'])} шлюзов, "
              f"{touched} сигналов ({os.path.basename(path)})")
    return touched
