from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.core import config
import collections
import json
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
import re

from contur.core.data_models import DeviceMatch

DEBUG = True

# Список типов задаётся в config.py и расширяется переменной CONTUR_DEVICE_TYPES
DEVICE_TYPES = config.device_types_pattern()

TOLERANCE = 5.0  # Допуск для определения нахождения точки внутри контура

# Уверенность привязки, выведенной по расположению подписи над кромкой контура
LABEL_ABOVE_CONFIDENCE = 0.9

# Уверенность привязки к установке листа из штампа: обозначение совпало точно,
# но владелец взят не с чертежа, а из основной надписи
SHEET_OBJECT_CONFIDENCE = 0.8

# Уверенность привязки устройства без техобъекта в имени: обозначение совпало
# точно и на листе оно одно, но владельца у устройства нет вовсе — ни в имени,
# ни в описании объектов, — и подтвердить привязку нечем
BARE_NAME_CONFIDENCE = 0.7


def load_lua_data(json_path: str) -> Dict:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки Lua данных: {e}")
        return {}


def extract_lua_names(lua_data: Dict) -> Dict:
    result = {}

    for obj in lua_data.get("tech_objects", []):
        name_eplan = obj.get("name_eplan", "")
        name_bc = obj.get("name_BC", "")

        if name_eplan:
            result[name_eplan.upper()] = obj
        if name_bc and name_bc != name_eplan:
            result[name_bc.upper()] = obj

    return result

# Поля устройства из main.io.lua, которые нужны мнемосхеме, но не нужны
# сопоставлению: каналы ввода-вывода с адресом в контроллере и параметры
# самого устройства. Раньше отбрасывались здесь же — сопоставление брало
# из описания только имя, артикул и подтип.
#
# `exchange` приходит не из main.io.lua, а из лежащего рядом shared.lua:
# у сигнала обмена там записано, с каким соседним контроллером он связан
# и в какую сторону. Мнемосхеме это нужно ровно затем же, зачем адрес
# канала, — чтобы знать, откуда берётся значение
TAG_FIELDS = ("DI", "DO", "AI", "AO", "par", "rt_par", "prop", "exchange")


def device_tags(lua_device: Dict) -> Dict:
    """Теги устройства: чем мнемосхема привяжет картинку к живому сигналу."""
    return {field: lua_device[field] for field in TAG_FIELDS if field in lua_device}


def classify_device_type(device_name: str) -> Optional[str]:
    if not device_name:
        return None

    device_name = device_name.upper()

    # Ищем: DEVICE_TYPE + цифры в конце строки
    pattern = rf'({DEVICE_TYPES})(\d+)$'
    match = re.search(pattern, device_name)

    if match:
        return match.group(1)

    return None


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

    # Сегменты нужны, чтобы проверять попадание точки в сам контур,
    # а не в его описанный прямоугольник
    segments = {}
    for segment in root.findall('.//Segments/Segment'):
        try:
            segments[segment.get('id')] = (
                (float(segment.get('x1')), float(segment.get('y1'))),
                (float(segment.get('x2')), float(segment.get('y2'))),
            )
        except (TypeError, ValueError):
            continue

    # Раскладываем сегменты по контурам
    for contour_data in contours:
        contour_data['segments'] = [
            segments[ref] for ref in contour_data['segment_refs'] if ref in segments
        ]

    return contours, segments


def similarity_score(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0

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
    # strict здесь не нужен: строки нарочно разной длины, сравнивается начало
    for c1, c2 in zip(s1, s2):  # noqa: B905
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


def is_point_inside_polygon(point: Tuple[float, float], segments: List[Tuple]) -> bool:
    # Проверка попадания внутрь замкнутого контура методом трассировки луча:
    # считаем пересечения луча вправо со сторонами контура, нечётное число —
    # точка внутри. В отличие от bounds учитывает реальную форму контура.
    x, y = point
    crossings = 0

    for (x1, y1), (x2, y2) in segments:
        if (y1 <= y < y2) or (y2 <= y < y1):
            if y2 != y1 and x1 + (y - y1) * (x2 - x1) / (y2 - y1) > x:
                crossings += 1

    return crossings % 2 == 1


def is_text_in_contour(point: Tuple[float, float], contour: Dict) -> bool:
    # Прямоугольник отсекает заведомо далёкие точки дёшево,
    # затем проверяем попадание в сам контур
    if not is_point_in_contour(point, contour['bounds']):
        return False

    segments = contour.get('segments')
    if not segments:
        # Геометрия сегментов недоступна — остаётся прежнее поведение по bounds
        return True

    return is_point_inside_polygon(point, segments)


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


def find_pdf_device_texts(pdf_path: str, page_number: Optional[int] = None) -> List[Dict]:
    # page_number=None — все страницы (прежнее поведение). Для многостраничного
    # файла это неверно: тексты со всех 265 страниц смешивались в один список,
    # и на одной странице получалось 600 «сопоставлений» вместо 221.
    from contur.pdf.extract_geometry import extract_text_elements

    all_texts = extract_text_elements(pdf_path, page_number)

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


def sheet_object_from_texts(texts: List[Dict]) -> Optional[str]:
    """Установка листа из основной надписи — ячейка «+» штампа Eplan.

    Полное обозначение устройства по Eplan — «=установка +расположение
    -устройство». Расположение берётся из блока «+...», которым устройство
    обведено, а если такого блока нет — из штампа самого листа: там знак «+»
    стоит отдельной ячейкой, а её содержимое написано той же строкой правее.
    Штамп внизу листа, поэтому из нескольких знаков «+» берётся самый нижний.
    """
    plus = [t for t in texts if t["text"].strip() == "+"]
    if not plus:
        return None

    px, py = max(plus, key=lambda t: t["center"][1])["center"]

    nearest = None
    for text in texts:
        tx, ty = text["center"]
        if tx <= px or abs(ty - py) > 2:
            continue
        if nearest is None or tx < nearest[0]:
            nearest = (tx, text["text"].strip())

    return nearest[1] if nearest else None


def find_sheet_object(pdf_path: str, page_number: Optional[int] = None) -> Optional[str]:
    from contur.pdf.extract_geometry import extract_text_elements

    return sheet_object_from_texts(extract_text_elements(pdf_path, page_number))


def match_devices(lua_data, pdf_contours, pdf_device_texts, sheet_object=None):
    matches = []
    lua_devices = lua_data.get("devices", [])

    # Группируем устройства по tech_object
    devices_by_tech = {}

    for device in lua_devices:
        dev_name = device.get("name", "")
        if not dev_name or not config.is_device_name(dev_name):
            continue

        # Техобъекта в имени может не быть вовсе: в проекте MCA1 так названы
        # 22 устройства из 356 — общая обвязка станции мойки (танки щелочи,
        # кислоты и воды, их уровни, дозаторы, расходомер). Раньше такие
        # имена не разбирались и устройство молча выпадало из работы, а
        # `FQT1` разбирался ещё и неверно — как объект «F» с устройством QT1
        pattern = rf'^(.*?){DEVICE_TYPES}\d+$'
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
        print("\nDEBUG: tech_objects из Lua")
        for k, v in devices_by_tech.items():
            print(f"{k}: {list(v.keys())}")

    # Обрабатываем каждый контур
    for contour in pdf_contours:
        contour_name = contour.get("name")
        if not contour_name:
            continue

        print(f"\nКонтур: {contour_name}")

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

            if not is_text_in_contour(text_point, contour):
                continue

            found_any = True
            print(f"    Текст в контуре: {short_name}")

            if short_name in expected_devices:
                lua_device = expected_devices[short_name]

                print(f"      ✅ MATCH → {tech_obj}{short_name}")

                matches.append(DeviceMatch(
                    lua_name=f"{tech_obj}{short_name}",
                    pdf_name=short_name,
                    tech_object=tech_obj,
                    coordinates=text_point,
                    confidence=1.0,
                    device_type=classify_device_type(f"{tech_obj}{short_name}"),
                    descr=lua_device.get("descr", ""),
                    article=lua_device.get("article", ""),
                    category=lua_device.get("category", ""),
                    subtype=lua_device.get("subtype", ""),
                    dtype=lua_device.get("dtype", ""),
                    tags=device_tags(lua_device),
                ))
            else:
                print("      ❌ Нет совпадения")

        if not found_any:
            print("  ⚠ Внутри контура нет текстов")

    above = match_labels_above_contours(devices_by_tech, pdf_contours,
                                        pdf_device_texts, matches)
    if above:
        print(f"\nПодписи над кромкой контура: {len(above)}")
        for match in above:
            print(f"  ✅ {match.lua_name}")
    matches.extend(above)

    by_sheet = match_labels_by_sheet_object(devices_by_tech, pdf_contours,
                                            pdf_device_texts, matches, sheet_object)
    if by_sheet:
        print(f"\nПодписи вне контуров, владелец из штампа «+{sheet_object}»: {len(by_sheet)}")
        for match in by_sheet:
            print(f"  ✅ {match.lua_name}")
    matches.extend(by_sheet)

    # Последними — устройства без техобъекта: у них нет владельца, поэтому
    # претендовать на подпись они могут только после всех, кто им владеет
    bare = match_bare_named_devices(devices_by_tech, pdf_contours,
                                    pdf_device_texts, matches)
    if bare:
        print(f"\nУстройства без техобъекта в имени: {len(bare)}")
        for match in bare:
            print(f"  ✅ {match.lua_name}")
    matches.extend(bare)

    return matches


def nearest_contour_below(point: Tuple[float, float],
                          contours: List[Dict]) -> Optional[Dict]:
    # Контур, чья верхняя кромка ближе всего снизу к точке.
    # Именно ближайший, а не ближайший подходящий: иначе подпись «дотянулась»
    # бы через контур, лежащий между ней и нужным.
    x, y = point
    best, best_gap = None, None

    for contour in contours:
        min_x, min_y, max_x, _ = contour["bounds"]
        if not (min_x - TOLERANCE <= x <= max_x + TOLERANCE):
            continue

        gap = min_y - y  # больше нуля — точка выше верхней кромки
        if gap <= 0 or gap > config.LABEL_ABOVE_CONTOUR_MAX:
            continue

        if best_gap is None or gap < best_gap:
            best, best_gap = contour, gap

    return best


def match_labels_above_contours(devices_by_tech: Dict[str, Dict],
                                pdf_contours: List[Dict],
                                pdf_device_texts: List[Dict],
                                matches: List[DeviceMatch]) -> List[DeviceMatch]:
    """Подписи, оказавшиеся не внутри контура, а сразу над его кромкой.

    Eplan ставит обозначение над символом устройства. Клапаны CIP-коллектора
    сидят на самой верхней кромке ряда: символ остаётся внутри контура,
    а подпись выходит наружу на 2-8 пт. Двенадцать устройств M1V91...M6V92
    из-за этого не сопоставлялись вовсе — на чертеже они нарисованы,
    а в отчёте числились пропавшими.

    Расстоянием тут не обойтись: ряды отстоят друг от друга на 11-14 пт,
    и подпись бывает ближе к нижней кромке ряда сверху (6.3 пт), чем
    к верхней кромке своего (7.9 пт) — по расстоянию половина ушла бы
    не туда. Решает направление: подпись стоит над своим устройством.

    От случайных совпадений держат два условия: контур должен ждать
    устройство с таким обозначением, и место не должно быть уже занято.
    На контрольном листе правило добирает ровно 12 нужных меток, а двенадцать
    подписей самих рядов (M1...M12 на левом поле) отсеивает как раз проверка
    ожидания — устройства «M3» у объекта M3 в Lua нет.
    """
    named_contours = [c for c in pdf_contours if c.get("name")]
    taken = {(m.tech_object, m.pdf_name) for m in matches}
    found = []

    for text in pdf_device_texts:
        short_name = (text.get("device_name") or "").upper()
        if not short_name:
            continue

        point = text["center"]
        if any(is_text_in_contour(point, contour) for contour in named_contours):
            continue  # подпись внутри контура — её разобрал первый проход

        contour = nearest_contour_below(point, named_contours)
        if contour is None:
            continue

        tech_obj = extract_tech_object_from_contour(contour["name"])
        lua_device = devices_by_tech.get(tech_obj, {}).get(short_name)
        if lua_device is None or (tech_obj, short_name) in taken:
            continue

        taken.add((tech_obj, short_name))
        found.append(DeviceMatch(
            lua_name=f"{tech_obj}{short_name}",
            pdf_name=short_name,
            tech_object=tech_obj,
            coordinates=point,
            # Ниже единицы: имя совпало точно, а вот контур выведен
            # по расположению подписи. Окно показывает такие с числом.
            confidence=LABEL_ABOVE_CONFIDENCE,
            device_type=classify_device_type(f"{tech_obj}{short_name}"),
            descr=lua_device.get("descr", ""),
            article=lua_device.get("article", ""),
            category=lua_device.get("category", ""),
            subtype=lua_device.get("subtype", ""),
            dtype=lua_device.get("dtype", ""),
            tags=device_tags(lua_device),
        ))

    return found


def match_labels_by_sheet_object(devices_by_tech: Dict[str, Dict],
                                 pdf_contours: List[Dict],
                                 pdf_device_texts: List[Dict],
                                 matches: List[DeviceMatch],
                                 sheet_object: Optional[str]) -> List[DeviceMatch]:
    """Подписи, не обведённые никаким контуром: владелец записан в штампе.

    На листах обмена сигналами блок «+...» рисуют не всегда: сигналы стоят
    столбцом посреди листа, а кому они принадлежат, сказано только в основной
    надписи. По Eplan это и есть правило — расположение устройства берётся
    из штампа, когда своего блока у него нет. На листе 5 так нарисованы
    двенадцать сигналов PRIEM (DI16...DI21, DO16...DO21): контуров вокруг
    них нет вовсе, и ни один не сопоставлялся.

    От случайных совпадений держат три условия: установка листа должна быть
    техобъектом из Lua, объект должен ждать устройство с таким обозначением,
    и обозначение должно встретиться вне контуров ровно один раз. Последнее
    существенно: на листе 34 вне контуров четыре подписи «-SB1», и без этой
    проверки одно устройство MCC1SB1 получило бы четыре привязки в разных
    местах листа.
    """
    if not sheet_object or sheet_object not in devices_by_tech:
        return []

    named_contours = [c for c in pdf_contours if c.get("name")]
    expected = devices_by_tech[sheet_object]
    taken = {(m.tech_object, m.pdf_name) for m in matches}

    outside = collections.defaultdict(list)
    for text in pdf_device_texts:
        short_name = (text.get("device_name") or "").upper()
        if short_name not in expected:
            continue
        if any(is_text_in_contour(text["center"], contour) for contour in named_contours):
            continue
        outside[short_name].append(text)

    found = []
    for short_name, texts in outside.items():
        if len(texts) != 1 or (sheet_object, short_name) in taken:
            continue

        lua_device = expected[short_name]
        found.append(DeviceMatch(
            lua_name=f"{sheet_object}{short_name}",
            pdf_name=short_name,
            tech_object=sheet_object,
            coordinates=texts[0]["center"],
            confidence=SHEET_OBJECT_CONFIDENCE,
            device_type=classify_device_type(f"{sheet_object}{short_name}"),
            descr=lua_device.get("descr", ""),
            article=lua_device.get("article", ""),
            category=lua_device.get("category", ""),
            subtype=lua_device.get("subtype", ""),
            dtype=lua_device.get("dtype", ""),
            tags=device_tags(lua_device),
        ))

    return found


def match_bare_named_devices(devices_by_tech: Dict[str, Dict],
                             pdf_contours: List[Dict],
                             pdf_device_texts: List[Dict],
                             matches: List[DeviceMatch]) -> List[DeviceMatch]:
    """Устройства, у которых в имени нет техобъекта: `V1`, `LT2`, `FQT1`.

    Так названа общая обвязка станции мойки в проекте MCA1 — танки щелочи,
    кислоты и воды, их уровни, дозаторы, расходомер: 22 устройства из 356.
    Своего техобъекта у них нет ни в имени, ни в описании объектов, и все
    прочие пути сопоставления их не видят — каждый ищет устройство внутри
    объекта. Из-за этого лист общей обвязки с 74 подписями давал одно
    сопоставление.

    Правила те же, что у привязки по штампу листа, и по той же причине:
    обозначение должно совпасть точно, встретиться на листе ровно один раз
    и не быть уже занятым. Занятость существенна — подпись «V1» на листе
    объекта LINE1 это его V1, а не безымянное устройство; владельцы
    разбираются раньше, и этот путь идёт последним.

    Подписи внутри именованных контуров не берём: там у устройства есть
    владелец, даже если тот его не ждал.
    """
    expected = devices_by_tech.get("", {})
    if not expected:
        return []

    named_contours = [c for c in pdf_contours if c.get("name")]
    taken = {match.pdf_name.upper() for match in matches}

    outside = collections.defaultdict(list)
    for text in pdf_device_texts:
        short_name = (text.get("device_name") or "").upper()
        if short_name not in expected or short_name in taken:
            continue
        if any(is_text_in_contour(text["center"], contour) for contour in named_contours):
            continue
        outside[short_name].append(text)

    found = []
    for short_name, texts in outside.items():
        if len(texts) != 1:
            continue

        lua_device = expected[short_name]
        found.append(DeviceMatch(
            lua_name=lua_device.get("name", short_name),
            pdf_name=short_name,
            # Объекта у устройства нет — окно показывает такие «Без объекта»,
            # и это честнее, чем приписать их первому попавшемуся
            tech_object="",
            coordinates=texts[0]["center"],
            confidence=BARE_NAME_CONFIDENCE,
            device_type=classify_device_type(short_name),
            descr=lua_device.get("descr", ""),
            article=lua_device.get("article", ""),
            category=lua_device.get("category", ""),
            subtype=lua_device.get("subtype", ""),
            dtype=lua_device.get("dtype", ""),
            tags=device_tags(lua_device),
        ))

    return found


def build_match_report(lua_data: Dict, pdf_contours: List[Dict],
                       pdf_device_texts: List[Dict], matches: List[DeviceMatch]) -> Dict:
    # Отчёт о расхождениях чертежа и конфигурации контроллера.
    #
    # Смысл инструмента — сверка одного с другим, но до сих пор нигде не было
    # видно, что именно не сошлось: молча терялись и устройства из Lua,
    # и подписи со схемы.
    matched_lua = {m.lua_name for m in matches}
    matched_points = {(m.pdf_name, round(m.coordinates[0], 1), round(m.coordinates[1], 1))
                      for m in matches}

    # Техобъекты, найденные на чертеже: только по ним есть смысл спрашивать.
    # Не только обведённые контуром: устройство могло привязаться к установке
    # из штампа, и тогда объект на листе есть, хотя блока вокруг него не рисуют
    contour_objects = {extract_tech_object_from_contour(c.get("name"))
                       for c in pdf_contours if c.get("name")}
    contour_objects.update(m.tech_object for m in matches)
    contour_objects.discard(None)

    # Правило разбора имени то же, что и у сопоставления: техобъекта в имени
    # может не быть вовсе. Иначе отчёт числил устройства без объекта
    # «неразобранными» и советовал дополнить список типов, хотя они
    # сопоставлены и стоят на схеме
    pattern = rf'^(.*?){DEVICE_TYPES}\d+$'

    def device_type(name: str) -> Optional[str]:
        parsed = re.match(pattern, name)
        return parsed.group(2) if parsed else None

    # Рисуют ли на этом листе сигналы ввода-вывода — спрашиваем у самого листа.
    #
    # Листы бывают двух родов. На технологических (P&ID) сигналов нет вовсе:
    # обозначений вида DI1 там не найти, и все они попадали бы в «нет на этом
    # листе», топя настоящие пропажи — на листе 13 mozzarella 36 строк против
    # пяти. А на листах обмена сигналами их рисуют: в контрольном проекте это
    # страницы 5-14 из 265, и на девяти из десяти, кроме сигналов, вообще
    # ничего нет. Всего по проекту сопоставилось 117 сигналов из 147.
    #
    # Поэтому не «сигналы не рисуют» (это неправда по проекту целиком),
    # а «сопоставился ли на этом листе хоть один»: если да — лист сигнальный,
    # и несопоставленный сигнал здесь настоящая пропажа.
    sheet_draws_signals = any(device_type(m.lua_name) in config.IO_SIGNAL_TYPES
                              for m in matches)

    missing_on_drawing, unparsed_names, foreign_objects = [], [], set()
    non_devices = 0
    io_signals = 0
    # Обмен с соседними контроллерами: имя, шлюз и направление берутся
    # из shared.lua, если он лежал рядом с main.io.lua. Такой сигнал —
    # не датчик проекта, а строка обмена, и «пропажей» он быть не может
    exchange = {}

    for device in lua_data.get("devices", []):
        name = device.get("name", "")
        if not name:
            continue

        if not config.is_device_name(name):
            # Программные сущности вроде WATCHDOG устройствами не являются
            non_devices += 1
            continue

        parsed = re.match(pattern, name)
        if not parsed:
            unparsed_names.append(name)
            continue

        tech_object = parsed.group(1)
        if tech_object not in contour_objects:
            # Устройство другого узла проекта — на этом листе его и не ждём
            foreign_objects.add(tech_object)
            continue

        if name not in matched_lua:
            gateway = (device.get("exchange") or {}).get("gateway")
            if gateway:
                # Сигнал обмена: у него есть хозяин на той стороне, и это
                # написано в конфигурации, а не выведено по признакам листа
                exchange[gateway] = exchange.get(gateway, 0) + 1
                continue

            if parsed.group(2) in config.IO_SIGNAL_TYPES and not sheet_draws_signals:
                # Сигнал ввода-вывода на листе, где сигналов не рисуют:
                # искать его здесь незачем, а вперемешку с настоящими
                # пропажами он их топил
                io_signals += 1
                continue

            missing_on_drawing.append({
                "name": name,
                "tech_object": tech_object,
                "descr": device.get("descr", ""),
                "article": device.get("article", ""),
            })

    # Подписи на схеме, которым не нашлось устройства в Lua.
    # Берём только те, что выглядят как обозначение устройства (V12, LS1),
    # иначе в отчёт попадают номера кабелей и артикулы.
    device_label = re.compile(rf'^{DEVICE_TYPES}\d+$')
    unknown_labels = []
    object_references = 0
    for text in pdf_device_texts:
        short_name = (text.get("device_name") or "").upper()
        if not short_name or not device_label.match(short_name):
            continue
        key = (short_name, round(text["center"][0], 1), round(text["center"][1], 1))
        if key in matched_points:
            continue
        for contour in pdf_contours:
            if contour.get("name") and is_text_in_contour(text["center"], contour):
                if short_name == extract_tech_object_from_contour(contour["name"]):
                    # Подпись повторяет имя своего же контура — это ссылка
                    # на линию, а не устройство: на контрольном листе так
                    # помечены красные стрелки «M7 -> К ПОУ 1» на пяти рядах.
                    # Настоящее устройство с таким именем сюда не попадёт:
                    # если бы M7M7 было в Lua, подпись сопоставилась бы выше.
                    object_references += 1
                    break

                unknown_labels.append({
                    "label": short_name,
                    "contour": contour["name"],
                    "x": round(text["center"][0], 1),
                    "y": round(text["center"][1], 1),
                })
                break

    return {
        "matched": len(matches),
        "missing_on_drawing": sorted(missing_on_drawing, key=lambda d: d["name"]),
        "unknown_labels": sorted(unknown_labels, key=lambda d: (d["contour"], d["label"])),
        "unparsed_lua_names": sorted(unparsed_names),
        "non_devices": non_devices,
        "io_signals": io_signals,
        "exchange_signals": dict(sorted(exchange.items())),
        "object_references": object_references,
        "objects_not_on_page": sorted(foreign_objects),
    }


def format_match_report(report: Dict, limit: int = 0) -> str:
    # Человекочитаемый вид отчёта; limit ограничивает длину списков (0 — без предела)
    def head(items):
        return items if limit <= 0 else items[:limit]

    lines = [
        "ОТЧЁТ О РАСХОЖДЕНИЯХ ЧЕРТЕЖА И КОНФИГУРАЦИИ",
        "=" * 60,
        f"Сопоставлено устройств: {report['matched']}",
        "",
        f"Есть в Lua, нет на этом листе: {len(report['missing_on_drawing'])}",
    ]
    if report["missing_on_drawing"]:
        # Раздел назывался «нет на чертеже» и читался как поломка распознавания.
        # На деле техобъект занимает несколько листов: на листе 13 mozzarella
        # у объекта CIP нарисован один клапан V7 из пяти, а M1, M2, V1 и V3 —
        # на других листах. По одному листу отличить «не нашли» от «нарисовано
        # в другом месте» нельзя, это видно только на прогоне по всему файлу.
        lines.append("   (техобъект бывает разложен по нескольким листам; "
                     "по всему файлу считает batch_process)")
    for item in head(report["missing_on_drawing"]):
        descr = f" — {item['descr']}" if item["descr"] else ""
        lines.append(f"   {item['name']}{descr}")
    if limit and len(report["missing_on_drawing"]) > limit:
        lines.append(f"   ... ещё {len(report['missing_on_drawing']) - limit}")

    lines += ["", f"Есть на чертеже, нет в Lua: {len(report['unknown_labels'])}"]
    for item in head(report["unknown_labels"]):
        lines.append(f"   {item['contour']}.{item['label']} (x={item['x']}, y={item['y']})")
    if limit and len(report["unknown_labels"]) > limit:
        lines.append(f"   ... ещё {len(report['unknown_labels']) - limit}")

    if report.get("object_references"):
        lines += ["", f"Ссылки на линии (подпись повторяет имя контура): "
                      f"{report['object_references']} — не устройства"]

    if report.get("exchange_signals"):
        total = sum(report["exchange_signals"].values())
        lines += ["", f"Обмен с соседними контроллерами: {total} сигналов — "
                      "это не устройства этого проекта"]
        for gateway, count in report["exchange_signals"].items():
            lines.append(f"   {gateway}: {count}")

    if report.get("io_signals"):
        lines += ["", f"Сигналы ввода-вывода (DI, DO, AI, AO): {report['io_signals']} — "
                      "на этом листе не рисуются"]

    if report.get("non_devices"):
        lines += ["", f"Не устройства (WATCHDOG и подобное): {report['non_devices']} — пропущены"]

    if report["unparsed_lua_names"]:
        lines += ["", f"Имена Lua, не разобранные по типу: {len(report['unparsed_lua_names'])}",
                  "   (добавьте тип в config.DEVICE_TYPES или CONTUR_DEVICE_TYPES)"]
        for name in head(report["unparsed_lua_names"]):
            lines.append(f"   {name}")

    # Пустое имя — устройства без техобъекта: в списке оно выглядело бы
    # как пропущенная запятая
    objects = [name or "без объекта" for name in report["objects_not_on_page"][:20]]
    lines += ["", f"Техобъекты не с этого листа: {len(report['objects_not_on_page'])}",
              "   " + ", ".join(objects)]

    return "\n".join(lines)


def generate_output_xml(matches: List[DeviceMatch], original_contours: List[Dict],
                        original_segments: List, lua_data: Dict | None = None,
                        output_path: str | None = None):
    output_path = output_path or str(config.MATCHED_DEVICES_XML)
    config.ensure_output_dir()
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
                device_elem.set("device_type", str(match.device_type))
            device_elem.set("lua_name", str(match.lua_name))
            device_elem.set("pdf_name", str(match.pdf_name))
            device_elem.set("x", f"{match.coordinates[0]:.3f}")
            device_elem.set("y", f"{match.coordinates[1]:.3f}")
            device_elem.set("confidence", f"{match.confidence:.2f}")

            # str() обязателен: subtype и dtype приходят из Lua числами,
            # и ElementTree падает при записи файла — «cannot serialize 13 (type int)»
            for attribute, value in (("descr", match.descr), ("article", match.article),
                                     ("category", match.category), ("subtype", match.subtype),
                                     ("dtype", match.dtype)):
                if value or value == 0:
                    device_elem.set(attribute, str(value))

    # Сохраняем XML
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    return output_path


def extract_tech_object_from_contour(contour_name: str) -> str | None:
    if not contour_name:
        return None

    # Берём всё после последнего '+'
    if '+' in contour_name:
        return contour_name.split('+')[-1].strip()

    # Если нет + — возможно имя сразу tech_object
    return contour_name.strip()

def main():
    print("🔍 Запуск сопоставления устройств...")

    # Загружаем данные из Lua
    try:
        lua_data = load_lua_data(str(config.PARSED_LUA_JSON))
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
        from contur.pdf.extract_geometry import extract_line_segments, extract_text_elements
        from contur.pdf.contour_detector import find_contours, find_all_contour_names_by_proximity, gen_xml
        from contur.core.data_models import SegmentData

        segments = extract_line_segments(pdf_path)
        texts = extract_text_elements(pdf_path)

        # Конвертируем в SegmentData
        segs = [SegmentData(**s) for s in segments]

        # Находим контуры
        contours = find_contours(segs)

        # Находим названия контуров (с приоритетом совпадений из Lua, если они есть)
        lua_names = {}
        if os.path.exists(config.PARSED_LUA_OBJECTS_JSON):
            lua_names = extract_lua_names(load_lua_data(str(config.PARSED_LUA_OBJECTS_JSON)))
        find_all_contour_names_by_proximity(contours, segs, texts, lua_names, max_distance=200)

        # Сохраняем во временный XML
        temp_geometry = str(config.ensure_output_dir() / "temp_geometry.xml")
        gen_xml(segs, contours).write(temp_geometry, encoding="utf-8", xml_declaration=True)
        pdf_contours, _ = load_pdf_geometry(temp_geometry)
        print(f"✓ Извлечено контуров: {len(pdf_contours)}")

    # Извлекаем тексты устройств из PDF
    pdf_device_texts = find_pdf_device_texts(pdf_path)
    print(f"✓ Найдено текстовых меток устройств на PDF: {len(pdf_device_texts)}")

    # Сопоставляем устройства
    matches = match_devices(lua_data, pdf_contours, pdf_device_texts,
                            find_sheet_object(pdf_path))

    print("\n📊 Результаты сопоставления:")
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
