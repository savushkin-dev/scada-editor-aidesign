from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.core import config
# parse_lua.py
import json
import os
import tkinter as tk
from tkinter import filedialog
from lupa import LuaRuntime

OUTPUT_JSON = str(config.PARSED_LUA_JSON)


def read_file_with_encoding(file_path):
    encodings = ['utf-8', 'cp1251', 'latin-1', 'cp866', 'windows-1251']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"  📄 Файл прочитан в кодировке: {encoding}")
            return content
        except UnicodeDecodeError:
            continue

    # Если ничего не помогло, читаем в бинарном режиме и игнорируем ошибки
    with open(file_path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')
    print("  ⚠️ Файл прочитан с игнорированием ошибок кодировки")
    return content


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

    # Читаем файл с определением кодировки
    lua_code = read_file_with_encoding(lua_path)

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

    # Рядом может лежать shared.lua — обмен сигналами с соседними
    # контроллерами. Файл необязательный: нет его — ничего не меняется.
    # Импорт здесь, а не наверху: parse_lua_shared сам читает из этого модуля
    from contur.lua import parse_lua_shared

    parse_lua_shared.attach(parsed, [lua_path])

    return parsed


def _is_empty(value):
    # Ноль и False — это значения, а не пустота: subtype 0 затирать нечем
    return value is None or value == "" or value == [] or value == {}


def _merge_records(records):
    # Записи с одним именем сливаются в одну: первая главная, последующие
    # дополняют её пустые поля. Записи без имени опознать нельзя — идут как есть.
    merged, by_name = [], {}

    for record in records:
        name = record.get("name") if isinstance(record, dict) else None
        if not name:
            merged.append(record)
            continue

        first = by_name.get(name)
        if first is None:
            by_name[name] = dict(record)
            merged.append(by_name[name])
            continue

        for key, value in record.items():
            if _is_empty(first.get(key)) and not _is_empty(value):
                first[key] = value

    return merged


def merge_lua_data(data_list):
    """Объединяет разбор нескольких файлов Lua в один набор.

    Раньше списки просто склеивались. Но одно и то же устройство описано
    в нескольких файлах сразу: в проекте mozzarella main.io.lua и
    main.wago.lua дают 730 + 568 = 1298 записей при 771 разном имени —
    527 повторов, узлов 13 при семи. Приложение отчитывалось о вдвое
    большем хозяйстве, чем есть, а отчёт о расхождениях показывал одно
    и то же устройство дважды.

    Повторы почти всегда совпадают побайтово (514 из 527). В остальных
    тринадцати различается одно поле, и полнее оно в первом файле:
    артикул «SE.XB4BS8445» против «XB4BS8445». У узлов та же картина —
    в main.io.lua на модуль больше. Поэтому первое описание главное,
    последующие лишь дополняют его пустые поля.
    """
    return {
        "nodes": _merge_records([node for data in data_list for node in data["nodes"]]),
        "devices": _merge_records([device for data in data_list
                                   for device in data["devices"]]),
    }


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
    print("📊 Итоговая статистика:")
    print(f"  Всего IO узлов: {len(merged_data['nodes'])}")
    print(f"  Всего устройств: {len(merged_data['devices'])}")
    print(f"💾 Сохранено: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
