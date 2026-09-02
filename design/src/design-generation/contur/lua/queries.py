# queries.py
# Запросы к описанию контроллера: состояния устройств, операции, техобъекты,
# сигналы и узлы.
#
# Зачем отдельным модулем. Эти функции лежали в подготовке выгрузки
# (`scene.py`), хотя к выгрузке отношения не имеют: они читают объектную
# модель, собранную из main.objects.lua, и одинаково нужны всем четырём
# выгрузкам и панели сведений. От геометрии листа они не зависят вовсе —
# сцена про операции ничего не знает, а операции ничего не знают про сцену.
#
# `objects_loader` держит саму модель и умеет её загружать; здесь — только
# чтение готовой, в том виде, в каком его ждут потребители.
import json
from typing import Any, Dict, List, Optional, Tuple

from contur.core import config
from contur.lua.objects_loader import objects_data


def device_operation_state(current_operation_id: Optional[str],
                           device_name: str) -> Tuple[str, Dict[str, Any]]:
    # Состояние устройства в текущей операции
    if not current_operation_id:
        return "not_used", {}

    details = objects_data.get_device_details_in_operation(current_operation_id, device_name)
    if details:
        return details.get("status", "not_used"), details
    return "not_used", {}


def device_states(device_name: str) -> List[Dict[str, Any]]:
    """Все места, где устройство открывается и закрывается.

    device_operation_state отвечает про одну выбранную операцию; здесь —
    весь список по всем операциям проекта. Разделены намеренно: XML пишет
    состояние в текущей операции, а выгрузка для редактора — все, чтобы
    мнемосхема могла показать положение клапана на любом шаге.
    """
    if not device_name:
        return []
    return objects_data.get_device_states(device_name)


def operation_program(operation_id: str) -> Optional[Dict[str, Any]]:
    """Состояния и шаги операции — то, что стоит за состояниями устройств."""
    if not operation_id:
        return None
    return objects_data.get_operation_program(operation_id)


def object_details(obj_id: str) -> Optional[Dict[str, Any]]:
    """Уставки, свойства и состав техобъекта — то, чем он настроен."""
    if not obj_id:
        return None
    return objects_data.get_object_details(obj_id)


def project_signals() -> List[Dict[str, Any]]:
    """Сигналы проекта: имя, тип и чей он."""
    return list(objects_data.signals)


def controller_nodes() -> List[Dict[str, Any]]:
    """Узлы контроллера из main.io.lua: имя, адрес, тип, модули.

    Читается из разобранного main.io.lua, а не из состояния приложения:
    узлы относятся к проекту целиком, и сцена листа про них ничего не знает.
    Файл перечитывается каждый раз — он маленький, а кэш между проектами
    показал бы узлы предыдущего.
    """
    try:
        with open(config.PARSED_LUA_JSON, "r", encoding="utf-8") as f:
            return list(json.load(f).get("nodes", []))
    except (OSError, ValueError):
        return []


def state_text(status: str) -> str:
    # Статус для показа человеку
    return {
        "opened": "открыто",
        "closed": "закрыто",
        "not_used": "не используется",
    }.get(status, "не известно")


def operation_summary(current_operation_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Текущая операция и сколько устройств в ней открыто и закрыто."""
    if not current_operation_id:
        return None

    current_op = objects_data.get_operation_by_id(current_operation_id)
    if not current_op:
        return None

    devices_status = objects_data.get_devices_for_operation(current_operation_id)
    return {
        "id": current_operation_id,
        "name": current_op.name,
        "tech_object": current_op.obj_name,
        "devices_opened": sum(1 for s in devices_status.values() if s == "opened"),
        "devices_closed": sum(1 for s in devices_status.values() if s == "closed"),
        "devices_total": len(devices_status),
    }
