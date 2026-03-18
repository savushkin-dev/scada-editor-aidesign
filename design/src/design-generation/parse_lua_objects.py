# parse_lua_objects.py
import re
import json
import os
from typing import Any, Dict, List, Union

INPUT_LUA_FILE = "input/test1/main.objects.lua"
OUTPUT_JSON = "output/parsed_lua_objects.json"


class LuaTableParser:
    def __init__(self):
        self.max_recursion = 100  # Защита от слишком глубокой рекурсии

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Удаляем комментарии
        content = self._remove_comments(content)

        # Находим основную функцию init_tech_objects_modes
        main_table = self._extract_main_table(content)
        if not main_table:
            raise ValueError("Не удалось найти таблицу init_tech_objects_modes")

        # Парсим основную таблицу
        result = self._parse_table(main_table, depth=0)

        return result

    def _remove_comments(self, content: str) -> str:
        # Удаляем однострочные комментарии --
        lines = []
        for line in content.split('\n'):
            # Ищем -- не внутри строки
            in_string = False
            string_char = None
            comment_pos = -1

            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i - 1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif string_char == char:
                        in_string = False
                        string_char = None
                elif char == '-' and i < len(line) - 1 and line[i + 1] == '-' and not in_string:
                    comment_pos = i
                    break

            if comment_pos >= 0:
                line = line[:comment_pos]

            lines.append(line)

        content = '\n'.join(lines)

        # Удаляем многострочные комментарии --[[ ... ]]
        content = re.sub(r'--\[\[.*?\]\]', '', content, flags=re.DOTALL)

        return content

    def _extract_main_table(self, content: str) -> str:
        # Ищем return {...} в функции
        pattern = r'init_tech_objects_modes\s*=\s*function\s*\(\s*\)\s*return\s*(\{.*?\})\s*end'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    def _find_matching_brace(self, text: str, start_pos: int) -> int:
        count = 1
        in_string = False
        string_char = None
        i = start_pos + 1

        while i < len(text) and count > 0:
            char = text[i]

            # Пропускаем строки
            if char in ['"', "'"] and (i == 0 or text[i - 1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
                    string_char = None

            if not in_string:
                if char == '{':
                    count += 1
                elif char == '}':
                    count -= 1

            i += 1

        if count == 0:
            return i - 1
        return -1

    def _parse_table(self, text: str, depth: int) -> Union[Dict, List, str, int, float, bool, None]:
        if depth > self.max_recursion:
            return None

        text = text.strip()

        # Пустая таблица
        if text == '{}':
            return {}

        # Убираем внешние фигурные скобки
        if text.startswith('{') and text.endswith('}'):
            # Проверяем, что скобки правильно сбалансированы
            if self._find_matching_brace(text, 0) == len(text) - 1:
                inner = text[1:-1].strip()
                if not inner:
                    return {}
            else:
                # Неправильная структура, возвращаем как есть
                return text
        else:
            return self._parse_value(text)

        # Разбиваем на элементы
        items = self._split_table_items(inner, depth)

        # Определяем, является ли таблица словарем или списком
        is_dict = False
        result_dict = {}
        result_list = []

        for item in items:
            if not item:
                continue

            if '=' in item:
                # Это пара ключ=значение
                key_part, value_part = item.split('=', 1)
                key = self._parse_key(key_part.strip())
                value = self._parse_value(value_part.strip(), depth + 1)

                result_dict[key] = value
                is_dict = True
            else:
                # Это элемент списка
                value = self._parse_value(item.strip(), depth + 1)
                result_list.append(value)

        if is_dict:
            return result_dict
        else:
            return result_list

    def _split_table_items(self, text: str, depth: int) -> List[str]:
        items = []
        current = []
        bracket_level = 0
        in_string = False
        string_char = None
        i = 0
        n = len(text)

        while i < n:
            char = text[i]

            # Обработка строк
            if char in ['"', "'"] and (i == 0 or text[i - 1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
                    string_char = None

            if not in_string:
                if char == '{':
                    bracket_level += 1
                elif char == '}':
                    bracket_level -= 1
                elif char == ',' and bracket_level == 0:
                    # Конец элемента
                    items.append(''.join(current).strip())
                    current = []
                    i += 1
                    continue

            current.append(char)
            i += 1

        # Добавляем последний элемент
        if current:
            items.append(''.join(current).strip())

        return [item for item in items if item]

    def _parse_key(self, key: str) -> Union[int, str]:
        key = key.strip()

        # Ключ в квадратных скобках [1]
        match = re.match(r'\[(\d+)\]', key)
        if match:
            return int(match.group(1))

        # Ключ в квадратных скобках со строкой ["name"]
        match = re.match(r'\["([^"]+)"\]', key)
        if match:
            return match.group(1)

        match = re.match(r'\[\'([^\']+)\'\]', key)
        if match:
            return match.group(1)

        # Обычный идентификатор
        return key

    def _parse_value(self, value: str, depth: int = 0) -> Any:
        value = value.strip()

        if not value:
            return None

        # Вложенная таблица
        if value.startswith('{'):
            return self._parse_table(value, depth + 1)

        # Строка в кавычках
        if (value.startswith('"') and value.endswith('"')) or \
                (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # Число
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Булево значение
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # Ничего из вышеперечисленного - возвращаем как строку
        return value


def extract_all_data(parsed_data: Dict) -> Dict:
    result = {
        "tech_objects": [],
        "devices": [],
        "operations": [],
        "states": [],
        "steps": [],  # НОВОЕ: добавляем список шагов
        "signals": [],
        "parameters": []
    }

    if not isinstance(parsed_data, dict):
        return result

    device_names = set()  # для удаления дубликатов устройств
    signal_names = set()  # для удаления дубликатов сигналов

    def add_device(name: str, source: str, parent: str = None, obj_id: str = None):
        if name and isinstance(name, str) and name.strip() and name != "Нет":
            if name not in device_names:
                device_names.add(name)
                result["devices"].append({
                    "name": name,
                    "source": source,
                    "parent": parent,
                    "obj_id": obj_id
                })

    def add_signal(name: str, signal_type: str, parent: str = None):
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

        # Добавляем параметры par_float
        par_float = obj_data.get("par_float")
        if isinstance(par_float, dict):
            params = []
            for param_id, param_data in par_float.items():
                if isinstance(param_data, dict):
                    param_info = {
                        "id": str(param_id),
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

                        # НОВОЕ: Извлекаем шаги (steps) с полной информацией
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


def save_sample_data(parsed_data: Dict, output_file: str):
    sample = {
        "tech_objects_count": len(parsed_data.get("tech_objects", [])),
        "devices_count": len(parsed_data.get("devices", [])),
        "operations_count": len(parsed_data.get("operations", [])),
        "states_count": len(parsed_data.get("states", [])),
        "steps_count": len(parsed_data.get("steps", [])),  # НОВОЕ
        "signals_count": len(parsed_data.get("signals", [])),
        "parameters_count": len(parsed_data.get("parameters", [])),
        "sample_object": parsed_data.get("tech_objects", [])[0] if parsed_data.get("tech_objects") else None,
        "sample_state": parsed_data.get("states", [])[0] if parsed_data.get("states") else None,
        "sample_step": parsed_data.get("steps", [])[0] if parsed_data.get("steps") else None  # НОВОЕ
    }

    sample_file = output_file.replace(".json", "_sample.json")
    with open(sample_file, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False, default=str)

    return sample_file


def main():
    os.makedirs("output", exist_ok=True)

    print("🔍 Парсинг Lua файла...")
    print(f"  Файл: {INPUT_LUA_FILE}")

    # Парсим Lua
    parser = LuaTableParser()
    try:
        parsed_data = parser.parse_file(INPUT_LUA_FILE)
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

    # Сохраняем образец для отладки
    sample_file = save_sample_data(extracted_data, OUTPUT_JSON)

    print(f"\n✅ Парсинг завершен")
    print(f"  Технологических объектов: {len(extracted_data['tech_objects'])}")
    print(f"  Устройств: {len(extracted_data['devices'])}")
    print(f"  Операций (режимов работы): {len(extracted_data['operations'])}")
    print(f"  Состояний: {len(extracted_data['states'])}")
    print(f"  Шагов: {len(extracted_data.get('steps', []))}")  # НОВОЕ
    print(f"  Сигналов: {len(extracted_data['signals'])}")
    print(f"  Параметров: {len(extracted_data['parameters'])}")
    print(f"💾 Результат сохранен в {OUTPUT_JSON}")
    print(f"📊 Образец данных сохранен в {sample_file}")

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