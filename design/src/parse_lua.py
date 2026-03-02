import json
import os
import tkinter as tk
from tkinter import filedialog
from lupa import LuaRuntime

OUTPUT_JSON = "output/parsed_lua.json"


def lua_table_to_python(obj):
    # Простые типы
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Lua table
    if hasattr(obj, "keys"):
        keys = list(obj.keys())

        # Проверяем: это массив (1..N)?
        if all(isinstance(k, int) for k in keys):
            max_index = max(keys) if keys else 0
            if sorted(keys) == list(range(1, max_index + 1)):
                # Это список
                return [
                    lua_table_to_python(obj[i])
                    for i in range(1, max_index + 1)
                ]

        # Иначе это dict
        return {
            str(k): lua_table_to_python(obj[k])
            for k in keys
        }

    return obj


def parse_lua_file(lua_path):
    lua = LuaRuntime(unpack_returned_tuples=True)

    with open(lua_path, "r", encoding="utf-8") as f:
        lua_code = f.read()

    # Выполняем Lua-код
    lua.execute(lua_code)

    globals_ = lua.globals()

    nodes = globals_.nodes if "nodes" in globals_ else None
    devices = globals_.devices if "devices" in globals_ else None

    if nodes is None:
        raise ValueError(f"❌ В Lua-файле {os.path.basename(lua_path)} не найден блок 'nodes'")
    if devices is None:
        raise ValueError(f"❌ В Lua-файле {os.path.basename(lua_path)} не найден блок 'devices'")

    parsed = {
        "nodes": lua_table_to_python(nodes),
        "devices": lua_table_to_python(devices)
    }

    return parsed


def merge_lua_data(data_list):
    merged = {
        "nodes": [],
        "devices": []
    }

    for file_data in data_list:
        merged["nodes"].extend(file_data["nodes"])
        merged["devices"].extend(file_data["devices"])

    return merged


def main():
    # Создаем временное tkinter окно и сразу его скрываем
    root = tk.Tk()
    root.withdraw()

    print("🔎 Выберите Lua файлы для парсинга...")

    # Открываем диалог выбора файлов
    lua_files = filedialog.askopenfilenames(
        title="Выберите Lua файлы",
        filetypes=[("Lua files", "*.lua"), ("All files", "*.*")]
    )

    if not lua_files:
        print("❌ Файлы не выбраны. Программа завершена.")
        return

    print(f"📄 Выбрано файлов: {len(lua_files)}")

    # Создаем output директорию
    os.makedirs("output", exist_ok=True)

    all_data = []
    successful_files = 0

    for lua_file in lua_files:
        try:
            print(f"\n  Парсинг: {os.path.basename(lua_file)}...")
            file_data = parse_lua_file(lua_file)
            all_data.append(file_data)
            successful_files += 1
            print(f"    ✓ IO узлов: {len(file_data['nodes'])}")
            print(f"    ✓ Устройств: {len(file_data['devices'])}")
        except Exception as e:
            print(f"    ✗ Ошибка: {e}")

    if not all_data:
        print("\n❌ Не удалось обработать ни одного файла")
        return

    # Объединяем данные
    merged_data = merge_lua_data(all_data)

    # Сохраняем результат
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Обработано файлов: {successful_files}/{len(lua_files)}")
    print(f"📊 Итоговая статистика:")
    print(f"  Всего IO узлов: {len(merged_data['nodes'])}")
    print(f"  Всего устройств: {len(merged_data['devices'])}")
    print(f"💾 Сохранено: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()