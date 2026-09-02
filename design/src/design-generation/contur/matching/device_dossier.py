# device_dossier.py
# Досье устройства: всё, что о нём известно, закреплено за ним самим.
#
# Зачем. Часть сведений об устройстве лежала при нём (описание, артикул,
# теги — каналы ввода-вывода с адресом, уставки, обмен с соседним
# контроллером), а часть добывалась заново каждым, кому она понадобилась:
# панель сведений спрашивала описание объектов при каждом щелчке, выгрузка
# считала то же самое в момент записи файла, а поле `operation_states`
# в модели устройства так и оставалось пустым — его никто не заполнял.
#
# Три источника одного и того же — это три способа разойтись. Здесь они
# сведены в один шаг: после сопоставления за устройством закрепляются
#
#   states     — где оно открывается и закрывается: операция, состояние,
#                шаг, что с ним происходит (на контрольном листе это
#                1911 записей на 233 устройства);
#   object     — его техобъект целиком: уставки, свойства, состав
#                оборудования, системные параметры;
#   neighbours — соседи по трубопроводам, когда разметка уже разобрана.
#
# Снимок, а не ссылка. Устройство самодостаточно: выгрузки и панель читают
# готовое и не могут показать разное. Плата — снимок устаревает, если
# описание объектов перезагрузили; поэтому окно пересобирает досье после
# каждой загрузки `main.objects.lua`, а `attach` дёшев и его не жалко
# позвать заново.
from typing import Any, Dict, Iterable, List, Optional

from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)

from contur.core.data_models import DeviceMatch
from contur.lua.objects_loader import TechObject, objects_data


def find_tech_object(name: str) -> Optional[TechObject]:
    """Техобъект по имени с чертежа, если описание объектов загружено.

    Имён у объекта три — своё («Танк рассола»), Eplan и BC, — и поиск
    по имени умеет все три. Но искать надо ещё и с номером: в описании
    объект зовут `BRINE_TANK`, а номер лежит отдельным полем `n`, тогда
    как на чертеже и в имени устройства они вместе — `BRINE_TANK1V1`,
    объект `BRINE_TANK1`. Без этого объект не находился почти никогда.
    """
    if not name:
        return None

    found = objects_data.get_object_by_name(name)
    if found is not None:
        return found

    upper = name.upper()
    for tech_object in objects_data.objects:
        for base in (tech_object.name_eplan, tech_object.name_BC):
            if base and f"{base}{tech_object.n}".upper() == upper:
                return tech_object
    return None


def device_states(match: DeviceMatch) -> List[Dict[str, Any]]:
    """Места в операциях, где устройство открывается или закрывается.

    Имён у устройства два: из контроллера (`lua_name`) и с чертежа
    (`pdf_name`). Описание операций знает первое, но у устройства без Lua
    его нет — тогда спрашиваем вторым.
    """
    return (objects_data.get_device_states(match.lua_name)
            or objects_data.get_device_states(match.pdf_name))


def attach(matches: Iterable[DeviceMatch],
           pipelines: Optional[Iterable[Any]] = None) -> Dict[str, int]:
    """Закрепляет за устройствами всё известное. Возвращает счётчики.

    `pipelines` появляются только после разбора разметки, поэтому
    необязательны: без них закрепляются состояния и техобъект, соседи
    добавятся следующим вызовом. Повторный вызов переписывает досье
    заново — так оно не расходится с перезагруженным описанием объектов.
    """
    matches = list(matches)

    # Соседи по трубам: у трубопровода записаны имена подключённых
    # устройств, а нужно обратное — у устройства имена его соседей
    neighbours: Dict[str, List[str]] = {}
    for pipeline in pipelines or ():
        connected = sorted(set(getattr(pipeline, "connected_devices", ()) or ()))
        for name in connected:
            others = [other for other in connected if other != name]
            if not others:
                continue
            known = neighbours.setdefault(name, [])
            known += [other for other in others if other not in known]

    counts = {"states": 0, "objects": 0, "neighbours": 0, "devices": len(matches)}

    for match in matches:
        states = device_states(match)
        match.states = states
        counts["states"] += len(states)

        tech_object = find_tech_object(match.tech_object)
        if tech_object is not None:
            details = objects_data.get_object_details(tech_object.id) or {}
            match.object_data = details
            counts["objects"] += 1
        else:
            match.object_data = {}

        if pipelines is not None:
            found = (neighbours.get(match.lua_name)
                     or neighbours.get(match.pdf_name) or [])
            match.neighbours = list(found)
            counts["neighbours"] += len(found)

    return counts


def summary(counts: Dict[str, int]) -> str:
    """Одна строка о том, что закрепилось, — для журнала и статус-бара."""
    parts = [f"устройств {counts.get('devices', 0)}",
             f"состояний {counts.get('states', 0)}",
             f"с техобъектом {counts.get('objects', 0)}"]
    if counts.get("neighbours"):
        parts.append(f"связей с соседями {counts['neighbours']}")
    return "Досье: " + ", ".join(parts)
