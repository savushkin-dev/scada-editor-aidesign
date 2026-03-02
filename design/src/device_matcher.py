# match_devices.py
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
import math
from dataclasses import dataclass, asdict
import re
DEBUG = True

DEVICE_TYPES = r'(V|DI|DO|AI|AO|M|LS|LT|TE|QT|FQT|PT|PC)'

# Константы
TOLERANCE = 5.0  # Допуск для определения нахождения точки внутри контура


@dataclass
class DeviceMatch:
    lua_name: str
    pdf_name: str
    tech_object: str
    coordinates: Tuple[float, float]
    confidence: float
    device_type: Optional[str] = None


def classify_device_type(device_name: str) -> Optional[str]:
    if not device_name:
        return None

    device_name = device_name.upper()

    # Ищем DEVICE_TYPE + цифры в конце строки
    pattern = rf'({DEVICE_TYPES})(\d+)$'
    match = re.search(pattern, device_name)

    if match:
        return match.group(1)

    return None

def load_lua_data(json_path: str) -> Dict:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_pdf_geometry(xml_path: str) -> Tuple[List[Dict], List[Dict]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Загружаем контуры
    contours = []
    for contour in root.findall('.//ClosedContours/Contour'):
        bounds = contour.find('Bounds')
        center = contour.find('Center')
        name_elem = contour.find('Name')

        contour_data = {
            'id': contour.get('id'),
            'bounds': (
                float(bounds.get('min_x')),
                float(bounds.get('min_y')),
                float(bounds.get('max_x')),
                float(bounds.get('max_y'))
            ),
            'center': (
                float(center.get('x')),
                float(center.get('y'))
            ),
            'name': name_elem.text if name_elem is not None else None,
            'segment_refs': contour.find('SegmentRefs').text.split()
        }
        contours.append(contour_data)

    # Загружаем текстовые элементы (названия устройств)
    # В текущем XML нет текстов, поэтому мы их будем добавлять отдельно
    # Но для полноты функции оставим заглушку

    return contours, []


def find_best_tech_object_match(contour_name: str, lua_devices: List[Dict]) -> Optional[str]:
    if not contour_name:
        return None

    # Очищаем имя контура от возможных префиксов/суффиксов
    clean_name = contour_name.split('+')[-1] if '+' in contour_name else contour_name

    # Собираем все уникальные префиксы устройств (часть до первого числа или буквы)
    tech_objects = set()
    device_prefixes = {}

    for device in lua_devices:
        dev_name = device.get('name', '')
        if not dev_name:
            continue

        # Извлекаем префикс технологического объекта
        match = re.match(r'^([A-Za-z]+[0-9]*)', dev_name)
        if match:
            prefix = match.group(1)
            tech_objects.add(prefix)
            if prefix not in device_prefixes:
                device_prefixes[prefix] = []
            device_prefixes[prefix].append(dev_name)

    # Ищем наиболее похожий префикс
    best_match = None
    best_score = 0

    for tech_obj in tech_objects:
        # Сравниваем с очищенным именем контура
        score = similarity_score(clean_name.upper(), tech_obj.upper())
        if score > best_score and score > 0.6:  # Порог схожести
            best_score = score
            best_match = tech_obj

    return best_match


def similarity_score(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0

    # Приводим к верхнему регистру для сравнения
    s1, s2 = s1.upper(), s2.upper()

    # Проверяем на полное совпадение
    if s1 == s2:
        return 1.0

    # Проверяем, является ли одна строка подстрокой другой
    if s1 in s2:
        return len(s1) / len(s2)
    if s2 in s1:
        return len(s2) / len(s1)

    # Подсчитываем совпадающие символы в начале
    common_prefix = 0
    for c1, c2 in zip(s1, s2):
        if c1 == c2:
            common_prefix += 1
        else:
            break

    if common_prefix > 0:
        return common_prefix / max(len(s1), len(s2))

    return 0


def is_point_in_contour(point: Tuple[float, float], contour_bounds: Tuple[float, float, float, float]) -> bool:
    x, y = point
    min_x, min_y, max_x, max_y = contour_bounds

    # Добавляем небольшой допуск для точек на границе
    return (min_x - TOLERANCE <= x <= max_x + TOLERANCE and
            min_y - TOLERANCE <= y <= max_y + TOLERANCE)


def extract_device_name_from_text(text: str) -> str:
    # Ищем паттерны типа V1, V-1, V_1 и т.д.
    patterns = [
        r'([A-Z]+[-\s_]?\d+)',  # V1, V-1, V_1
        r'([A-Z]+\d+[A-Z]*)',  # V1A, P2B
    ]

    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            # Очищаем от разделителей
            return re.sub(r'[-\s_]', '', match.group(1))

    return text.strip()


def find_pdf_device_texts(pdf_path: str) -> List[Dict]:
    from extract_geometry import extract_text_elements

    all_texts = extract_text_elements(pdf_path)

    # Фильтруем только потенциальные имена устройств (короткие метки)
    device_texts = []
    for text in all_texts:
        clean_text = text['text'].strip()
        # Проверяем, похоже ли на имя устройства
        if (len(clean_text) <= 10 and  # Короткие тексты
                re.search(r'[A-Za-z]\d', clean_text)):  # Содержит букву и цифру
            text['device_name'] = extract_device_name_from_text(clean_text)
            device_texts.append(text)

    return device_texts


def match_devices(lua_data, pdf_contours, pdf_device_texts):
    matches = []
    lua_devices = lua_data.get("devices", [])

    # 1 Группируем устройства по tech_object
    devices_by_tech = {}

    for device in lua_devices:
        dev_name = device.get("name", "")
        if not dev_name:
            continue

        pattern = rf'^(.+?){DEVICE_TYPES}\d+$'
        match = re.match(pattern, dev_name)

        if not match:
            if DEBUG:
                print(f"⚠ Не удалось разобрать имя устройства: {dev_name}")
            continue

        tech_obj = match.group(1)
        short_name = dev_name[len(tech_obj):]

        devices_by_tech.setdefault(tech_obj, {})
        devices_by_tech[tech_obj][short_name.upper()] = device

    if DEBUG:
        print("\n===== DEBUG: tech_objects из Lua =====")
        for k, v in devices_by_tech.items():
            print(f"{k}: {list(v.keys())}")

    # 2 Обрабатываем каждый контур
    for contour in pdf_contours:
        contour_name = contour.get("name")
        if not contour_name:
            continue

        print("\n----------------------------------")
        print(f"Контур: {contour_name}")

        tech_obj = extract_tech_object_from_contour(contour_name)

        print(f"  Найден tech_object: {tech_obj}")

        if not tech_obj or tech_obj not in devices_by_tech:
            print("  ❌ Нет соответствующего tech_object в Lua")
            continue

        expected_devices = devices_by_tech[tech_obj]
        print(f"  Ожидаемые устройства: {list(expected_devices.keys())}")

        found_any = False

        for text in pdf_device_texts:
            text_point = text["center"]
            short_name = text.get("device_name", "").upper()

            if not short_name:
                continue

            if not is_point_in_contour(text_point, contour["bounds"]):
                continue

            found_any = True
            print(f"    Текст в контуре: {short_name}")

            if short_name in expected_devices:
                print(f"      ✅ MATCH → {tech_obj}{short_name}")

                matches.append(DeviceMatch(
                    lua_name=f"{tech_obj}{short_name}",
                    pdf_name=short_name,
                    tech_object=tech_obj,
                    coordinates=text_point,
                    confidence=1.0,
                    device_type=classify_device_type(f"{tech_obj}{short_name}")
                ))
            else:
                print(f"      ❌ Нет совпадения")

        if not found_any:
            print("  ⚠ Внутри контура нет текстов")

    return matches


def generate_output_xml(matches: List[DeviceMatch], original_contours: List[Dict],
                        original_segments: List, lua_data: Dict = None,
                        output_path: str = "output/matched_devices.xml"):
    # Создаем корневой элемент
    root = ET.Element("PlantGeometry")

    # Добавляем информацию о версии
    root.set("version", "1.0")

    # Группируем устройства по технологическим объектам
    devices_by_tech_obj = {}
    for match in matches:
        if match.tech_object not in devices_by_tech_obj:
            devices_by_tech_obj[match.tech_object] = []
        devices_by_tech_obj[match.tech_object].append(match)

    # Создаем элемент для технологических объектов
    tech_objects_elem = ET.SubElement(root, "TechnologicalObjects")

    # Создаем словарь для быстрого доступа к данным устройств из Lua
    lua_devices_dict = {}
    if lua_data and "devices" in lua_data:
        for device in lua_data["devices"]:
            dev_name = device.get("name", "")
            if dev_name:
                lua_devices_dict[dev_name.upper()] = device

    # Для каждого технологического объекта
    for tech_obj_name, obj_matches in devices_by_tech_obj.items():
        tech_obj_elem = ET.SubElement(tech_objects_elem, "TechnologicalObject")
        tech_obj_elem.set("name", tech_obj_name)

        # Ищем соответствующий контур
        for contour in original_contours:
            if contour.get('name') and tech_obj_name in contour['name'].upper():
                contour_elem = ET.SubElement(tech_obj_elem, "Contour")
                contour_elem.set("bounds",
                                 f"{contour['bounds'][0]},{contour['bounds'][1]},"
                                 f"{contour['bounds'][2]},{contour['bounds'][3]}")
                contour_elem.set("center", f"{contour['center'][0]},{contour['center'][1]}")
                break

        # Добавляем устройства
        devices_elem = ET.SubElement(tech_obj_elem, "Devices")
        for match in obj_matches:
            device_elem = ET.SubElement(devices_elem, "Device")
            if match.device_type:
                device_elem.set("device_type", match.device_type)
            device_elem.set("lua_name", match.lua_name)
            device_elem.set("pdf_name", match.pdf_name)
            device_elem.set("x", f"{match.coordinates[0]:.3f}")
            device_elem.set("y", f"{match.coordinates[1]:.3f}")
            device_elem.set("confidence", f"{match.confidence:.2f}")

            # Добавляем дополнительную информацию из Lua
            lua_device = lua_devices_dict.get(match.lua_name.upper())
            if lua_device:
                # Основные поля
                if "descr" in lua_device:
                    device_elem.set("descr", lua_device["descr"])
                if "article" in lua_device:
                    device_elem.set("article", lua_device["article"])
                if "type" in lua_device:
                    device_elem.set("type", lua_device["type"])
                if "category" in lua_device:
                    device_elem.set("category", lua_device["category"])

                # Дополнительные поля (если есть)
                for key, value in lua_device.items():
                    if key not in ["name", "descr", "article", "type", "category"] and isinstance(value,
                                                                                                  (str, int, float)):
                        device_elem.set(key, str(value))

    # Сохраняем XML
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    return output_path


def extract_tech_object_from_contour(contour_name: str) -> str | None:
    if not contour_name:
        return None

    # Берём всё после последнего +
    if '+' in contour_name:
        return contour_name.split('+')[-1].strip()

    # Если нет + — возможно имя сразу tech_object
    return contour_name.strip()

def main():
    print("🔍 Запуск сопоставления устройств...")

    # Загружаем данные из Lua
    try:
        lua_data = load_lua_data("output/parsed_lua.json")
        print(f"✓ Загружено устройств из Lua: {len(lua_data.get('devices', []))}")
    except FileNotFoundError:
        print("❌ Файл output/parsed_lua.json не найден. Сначала запустите parse_lua.py")
        return

    # Выбираем PDF файл
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    pdf_path = filedialog.askopenfilename(
        title="Выберите PDF файл с геометрией",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        print("❌ PDF файл не выбран")
        return

    # Загружаем геометрию из XML (если есть)
    try:
        pdf_contours, _ = load_pdf_geometry("output.xml")
        print(f"✓ Загружено контуров из XML: {len(pdf_contours)}")
    except FileNotFoundError:
        print("⚠️ Файл output.xml не найден. Извлекаем геометрию из PDF...")

        from extract_geometry import extract_line_segments, extract_text_elements
        from contour_detector import find_contours, gen_xml

        segments = extract_line_segments(pdf_path)
        texts = extract_text_elements(pdf_path)

        # Конвертируем в SegmentData
        from segment_data import SegmentData
        segs = [SegmentData(**s) for s in segments]

        # Находим контуры
        contours = find_contours(segs)

        # Находим названия контуров
        for c in contours:
            from contour_detector import find_text
            if name_pos := find_text(c, texts):
                c.name, c.name_position = name_pos

        # Сохраняем во временный XML
        gen_xml(segs, contours).write("temp_geometry.xml", encoding="utf-8", xml_declaration=True)
        pdf_contours, _ = load_pdf_geometry("temp_geometry.xml")
        print(f"✓ Извлечено контуров: {len(pdf_contours)}")

    # Извлекаем тексты устройств из PDF
    pdf_device_texts = find_pdf_device_texts(pdf_path)
    print(f"✓ Найдено текстовых меток устройств на PDF: {len(pdf_device_texts)}")

    # Сопоставляем устройства
    matches = match_devices(lua_data, pdf_contours, pdf_device_texts)

    print(f"\n📊 Результаты сопоставления:")
    print(f"  Сопоставлено устройств: {len(matches)}")

    # Группируем по технологическим объектам
    by_tech = {}
    for match in matches:
        if match.tech_object not in by_tech:
            by_tech[match.tech_object] = 0
        by_tech[match.tech_object] += 1

    for tech_obj, count in by_tech.items():
        print(f"  {tech_obj}: {count} устройств")

    # Генерируем выходной XML
    if matches:
        output_file = generate_output_xml(matches, pdf_contours, [], lua_data)
        print(f"\n💾 Результат сохранен в: {output_file}")
    else:
        print("\n❌ Не найдено сопоставлений")


if __name__ == "__main__":
    main()