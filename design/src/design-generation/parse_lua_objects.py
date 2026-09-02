import console_utils  # noqa: F401  (настройка кодировки вывода)
import config
# parse_lua_objects.py
import json
import os
from typing import Dict

INPUT_LUA_FILE = str(config.INPUT_DIR / "test1" / "main.objects.lua")
OUTPUT_JSON = str(config.PARSED_LUA_OBJECTS_JSON)


# Поля, которые в Lua заданы как отображение «номер -> запись»,
# а не как массив. Для них целочисленные ключи сохраняются,
# остальные таблицы с ключами 1..N становятся списками.
MAP_FIELDS = frozenset({
    "modes", "states", "steps", "par_float", "rt_par_float",
    "properties", "system_parameters", "equipment",
})


def _lua_to_python(value, field_name: str | None = None, top_level: bool = False):
    # Переводит структуру Lua в Python.
    #
    # Раньше файл разбирался самописным парсером на регулярных выражениях.
    # Он, в частности, не понимал ключи вида '[ 1 ]' (с пробелами) и ломал
    # devices_data: ключом становился обрывок текста, а значением —
    # неразобранная строка, из-за чего группы DI/DO и устройств терялись.
    # Здесь файл выполняется тем же lupa, что и main.io.lua.
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if not hasattr(value, "keys"):
        return value

    keys = list(value.keys())
    if not keys:
        return {} if (top_level or field_name in MAP_FIELDS) else []

    is_array = all(isinstance(k, int) for k in keys) and         sorted(keys) == list(range(1, max(keys) + 1))

    # Отображение: верхний уровень (объекты) и поля вроде modes/states/steps
    if top_level or field_name in MAP_FIELDS or not is_array:
        return {str(k): _lua_to_python(value[k], str(k)) for k in keys}

    return [_lua_to_python(value[i], field_name) for i in range(1, max(keys) + 1)]


def parse_objects_file(file_path: str) -> Dict:
    # Выполняет main.objects.lua и возвращает таблицу технологических объектов
    from lupa import LuaRuntime

    from parse_lua import read_file_with_encoding

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(read_file_with_encoding(file_path))

    init_modes = lua.globals().init_tech_objects_modes
    if init_modes is None:
        raise ValueError(
            f"В файле {os.path.basename(file_path)} нет функции init_tech_objects_modes")

    return _lua_to_python(init_modes(), top_level=True)


def extract_all_data(parsed_data: Dict) -> Dict:
    result = {
        "tech_objects": [],
        "devices": [],
        "operations": [],
        "states": [],
        "steps": [],
        "signals": [],
        "parameters": []
    }

    if not isinstance(parsed_data, dict):
        return result

    device_names = set()  # для удаления дубликатов устройств
    signal_names = set()  # для удаления дубликатов сигналов

    def add_device(name: str, source: str, parent: str | None = None, obj_id: str | None = None):
        if name and isinstance(name, str) and name.strip() and name != "Нет":
            if name not in device_names:
                device_names.add(name)
                result["devices"].append({
                    "name": name,
                    "source": source,
                    "parent": parent,
                    "obj_id": obj_id
                })

    def add_signal(name: str, signal_type: str, parent: str | None = None):
        if name and isinstance(name, str) and name.strip() and name != "Нет":
            signal_key = f"{name}_{signal_type}"
            if signal_key not in signal_names:
                signal_names.add(signal_key)
                result["signals"].append({
                    "name": name,
                    "type": signal_type,
                    "parent": parent
                })

    # Проходим по всем технологическим объектам
    for obj_id, obj_data in parsed_data.items():
        if not isinstance(obj_data, dict):
            continue

        # Основная информация об объекте
        tech_obj = {
            "id": str(obj_id),
            "n": obj_data.get("n"),
            "tech_type": obj_data.get("tech_type"),
            "name": obj_data.get("name"),
            "name_eplan": obj_data.get("name_eplan"),
            "name_BC": obj_data.get("name_BC"),
            "base_tech_object": obj_data.get("base_tech_object"),
            "attached_objects": obj_data.get("attached_objects"),
            "cooper_param_number": obj_data.get("cooper_param_number")
        }

        # Уставки объекта. par_float — заданные значения, rt_par_float —
        # рабочие параметры: имя, единица измерения и имя в Lua без значения.
        # В проекте MCA1 объекты описаны только вторыми, и до сих пор они
        # терялись целиком — 140 записей на объект. Номера у двух списков
        # свои, поэтому у рабочих к номеру приписывается «rt»
        params = []
        for field, prefix in (("par_float", ""), ("rt_par_float", "rt")):
            block = obj_data.get(field)
            if not isinstance(block, dict):
                continue

            for param_id, param_data in block.items():
                if not isinstance(param_data, dict):
                    continue

                param_info = {
                    "id": f"{prefix}{param_id}",
                    "name": param_data.get("name", ""),
                    "value": param_data.get("value", 0),
                    "meter": param_data.get("meter", ""),
                    "nameLua": param_data.get("nameLua", ""),
                    "oper": param_data.get("oper", [])
                }
                params.append(param_info)

                # Добавляем параметр в общий список
                result["parameters"].append({
                    "obj_id": str(obj_id),
                    "obj_name": tech_obj["name"],
                    **param_info
                })

        if params:
            tech_obj["parameters"] = params

        # Добавляем system_parameters
        system_params = obj_data.get("system_parameters")
        if isinstance(system_params, dict):
            tech_obj["system_parameters"] = system_params

        # Добавляем properties
        properties = obj_data.get("properties")
        if isinstance(properties, dict):
            tech_obj["properties"] = properties

        # Добавляем оборудование
        equipment = obj_data.get("equipment")
        if isinstance(equipment, dict):
            tech_obj["equipment"] = equipment
            for eq_name in equipment.values():
                if isinstance(eq_name, str):
                    add_device(eq_name, "equipment", tech_obj["name"], str(obj_id))

        # Извлекаем режимы работы (modes) как операции
        modes = obj_data.get("modes")
        if isinstance(modes, dict):
            operations_for_obj = []
            for mode_id, mode_data in modes.items():
                if not isinstance(mode_data, dict):
                    continue

                # Создаем операцию с правильной структурой
                operation_id = f"{obj_id}_{mode_id}"
                operation = {
                    "id": operation_id,
                    "name": mode_data.get("name", f"Операция {mode_id}"),
                    "base_operation": mode_data.get("base_operation"),
                    "obj_id": str(obj_id),
                    "obj_name": tech_obj["name"],
                    "props": mode_data.get("props", {})
                }

                # Добавляем в общий список операций
                result["operations"].append(operation)
                operations_for_obj.append(operation)

                # Извлекаем состояния (states)
                states = mode_data.get("states")
                if isinstance(states, dict):
                    for state_id, state_data in states.items():
                        if not isinstance(state_data, dict):
                            continue

                        # Создаем состояние
                        state_info = {
                            "state_id": f"{operation_id}_{state_id}",
                            "operation_id": operation_id,
                            "operation_name": operation["name"],
                            "obj_id": str(obj_id),
                            "obj_name": tech_obj["name"],
                            "state_data": {}
                        }

                        # Копируем все данные состояния
                        for key, value in state_data.items():
                            if key not in ["id", "name"]:
                                state_info["state_data"][key] = value

                        # Добавляем имя состояния если есть
                        if "name" in state_data:
                            state_info["state_data"]["name"] = state_data["name"]
                        else:
                            state_info["state_data"]["name"] = f"Состояние {state_id}"

                        # Извлекаем устройства из различных полей состояния
                        for field in ["opened_devices", "closed_devices", "checked_devices"]:
                            devices = state_data.get(field)
                            if isinstance(devices, list):
                                state_info["state_data"][field] = devices
                                for dev in devices:
                                    if isinstance(dev, str):
                                        add_device(dev, f"{field}",
                                                   f"{tech_obj['name']}.{operation['name']}",
                                                   str(obj_id))
                                    elif isinstance(dev, dict):
                                        for sub_dev in dev.values():
                                            if isinstance(sub_dev, str):
                                                add_device(sub_dev, f"{field}_nested",
                                                           f"{tech_obj['name']}.{operation['name']}",
                                                           str(obj_id))

                        # Извлекаем devices_data
                        devices_data = state_data.get("devices_data")
                        if isinstance(devices_data, list):
                            state_info["state_data"]["devices_data"] = devices_data
                            for group in devices_data:
                                if isinstance(group, dict):
                                    group_devices = group.get("devices")
                                    if isinstance(group_devices, list):
                                        for dev in group_devices:
                                            if isinstance(dev, str):
                                                add_device(dev, "devices_data",
                                                           f"{tech_obj['name']}.{operation['name']}",
                                                           str(obj_id))

                        # Извлекаем DI_DO группы
                        di_do = state_data.get("DI_DO")
                        if isinstance(di_do, list):
                            state_info["state_data"]["DI_DO"] = di_do
                            for di_do_group in di_do:
                                if isinstance(di_do_group, list) and len(di_do_group) > 0:
                                    signals = di_do_group[0]
                                    if isinstance(signals, list):
                                        for signal in signals:
                                            if isinstance(signal, str):
                                                add_signal(signal, "DI_DO",
                                                           f"{tech_obj['name']}.{operation['name']}")

                        # Извлекаем шаги (steps) с полной информацией
                        steps = state_data.get("steps")
                        if isinstance(steps, dict):
                            state_info["state_data"]["steps"] = steps
                            steps_list = []

                            for step_id, step_data in steps.items():
                                if isinstance(step_data, dict):
                                    # Создаем запись шага с полной информацией
                                    step_info = {
                                        "step_id": f"{state_info['state_id']}_{step_id}",
                                        "state_id": state_info['state_id'],
                                        "step_number": step_id,
                                        "name": step_data.get("name", f"Шаг {step_id}"),
                                        "time_param_n": step_data.get("time_param_n", -1),
                                        "next_step_n": step_data.get("next_step_n", -1),
                                        "baseStep": step_data.get("baseStep"),
                                        "opened_devices": step_data.get("opened_devices", []),
                                        "closed_devices": step_data.get("closed_devices", []),
                                        "devices_data": step_data.get("devices_data", []),
                                        "DI_DO": step_data.get("DI_DO", []),
                                        "enable_step_by_signal": step_data.get("enable_step_by_signal"),
                                        "jump_if": step_data.get("jump_if")
                                    }

                                    # Добавляем шаг в общий список
                                    result["steps"].append({
                                        "obj_id": str(obj_id),
                                        "obj_name": tech_obj["name"],
                                        "operation_id": operation_id,
                                        "operation_name": operation["name"],
                                        "state_id": state_info['state_id'],
                                        "state_name": state_info["state_data"]["name"],
                                        **step_info
                                    })

                                    steps_list.append(step_info)

                                    # Извлекаем устройства из шагов
                                    for dev in step_data.get("opened_devices", []):
                                        if isinstance(dev, str):
                                            add_device(dev, "step_opened_devices",
                                                       f"{tech_obj['name']}.{operation['name']}.{step_id}",
                                                       str(obj_id))

                                    for dev in step_data.get("closed_devices", []):
                                        if isinstance(dev, str):
                                            add_device(dev, "step_closed_devices",
                                                       f"{tech_obj['name']}.{operation['name']}.{step_id}",
                                                       str(obj_id))

                            # Сохраняем шаги в состоянии
                            state_info["state_data"]["steps_list"] = steps_list

                        result["states"].append(state_info)

            # Сохраняем операции в tech_obj
            tech_obj["operations"] = operations_for_obj

        result["tech_objects"].append(tech_obj)

    # Удаляем дубликаты устройств по имени
    unique_devices = {}
    for device in result["devices"]:
        name = device["name"]
        if name not in unique_devices:
            unique_devices[name] = device

    result["devices"] = list(unique_devices.values())

    return result


def main():
    import sys

    config.ensure_output_dir()

    # Путь можно передать аргументом; по умолчанию берётся файл из config
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_LUA_FILE

    print("🔍 Парсинг Lua файла...")
    print(f"  Файл: {input_file}")

    # Парсим Lua
    try:
        parsed_data = parse_objects_file(input_file)
        print("  ✅ Базовая структура распарсена")
    except Exception as e:
        print(f"  ❌ Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
        return

    # Извлекаем все данные
    extracted_data = extract_all_data(parsed_data)

    # Сохраняем в JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False, default=str)

    print("\n✅ Парсинг завершен")
    print(f"  Технологических объектов: {len(extracted_data['tech_objects'])}")
    print(f"  Устройств: {len(extracted_data['devices'])}")
    print(f"  Операций (режимов работы): {len(extracted_data['operations'])}")
    print(f"  Состояний: {len(extracted_data['states'])}")
    print(f"  Шагов: {len(extracted_data.get('steps', []))}")  # НОВОЕ
    print(f"  Сигналов: {len(extracted_data['signals'])}")
    print(f"  Параметров: {len(extracted_data['parameters'])}")
    print(f"💾 Результат сохранен в {OUTPUT_JSON}")

    # Показываем примеры найденных операций
    if extracted_data["operations"]:
        print("\n📋 Примеры найденных операций:")
        for i, op in enumerate(extracted_data["operations"][:10]):
            print(f"  {i + 1}. {op['obj_name']} -> {op['name']} (ID: {op['id']})")
        if len(extracted_data["operations"]) > 10:
            print(f"     ... и еще {len(extracted_data['operations']) - 10}")

    # Показываем примеры найденных шагов
    if extracted_data.get("steps"):
        print("\n📋 Примеры найденных шагов:")
        for i, step in enumerate(extracted_data["steps"][:5]):
            print(
                f"  {i + 1}. {step['obj_name']} -> {step['operation_name']} -> {step['state_name']} -> {step['name']}")
            if step.get('opened_devices'):
                print(f"     Открываемые устройства: {step['opened_devices'][:3]}")
            if step.get('closed_devices'):
                print(f"     Закрываемые устройства: {step['closed_devices'][:3]}")
        if len(extracted_data["steps"]) > 5:
            print(f"     ... и еще {len(extracted_data['steps']) - 5}")


if __name__ == "__main__":
    main()
