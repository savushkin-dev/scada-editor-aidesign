# xml_reader.py
# Чтение своего XML с результатами сопоставления.
#
# Лежит рядом с `xml_export.py`, хотя читает, а не пишет: это две стороны
# одного формата, и меняться им положено вместе. Назывался `xml_io.py` —
# имя обещало обе стороны, а модуль только читает.
#
# Разбор жил внутри окна: load_xml_file на 105 строк вместе с диалогом
# выбора файла, окнами сообщений и перестройкой интерфейса. Проверить
# разбор было нельзя, не подняв окно целиком, — а ошибки здесь уже были,
# и обидные: свой же файл не открывался, потому что float("62.064%")
# падал, а проценты доходили до 1178%.
#
# Модуль не знает про Qt. Цвета устройств назначает окно: это оформление,
# а не данные.
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from contur.core.data_models import Contour, DeviceMatch


@dataclass
class LoadedDocument:
    """Что удалось прочитать из файла и что не удалось."""

    contours: List[Contour] = field(default_factory=list)
    matches: List[DeviceMatch] = field(default_factory=list)
    canvas: Tuple[Optional[float], Optional[float]] = (None, None)
    coordinate_type: str = ""

    # Записи, которые не разобрались. Раньше о них сообщал print в консоль,
    # которой у собранного приложения нет
    problems: List[str] = field(default_factory=list)

    @property
    def skipped(self) -> int:
        return len(self.problems)

    @property
    def needs_canvas(self) -> bool:
        # Файл в процентах без размеров холста: координаты восстановить нечем
        return self.coordinate_type == "percent" and not self.canvas[0]


def canvas_size(root: ET.Element) -> Tuple[Optional[float], Optional[float]]:
    # Размеры холста в PDF пунктах для обратного перевода процентов.
    # Приоритет: атрибуты canvas-* > viewBox встроенного SVG.
    try:
        width = float(root.get("canvas-width", ""))
        height = float(root.get("canvas-height", ""))
        if width > 0 and height > 0:
            return width, height
    except (TypeError, ValueError):
        pass

    # Запасной вариант для файлов, экспортированных до появления canvas-*
    svg_elem = root.find("SVGContent")
    if svg_elem is not None and svg_elem.text:
        match = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', svg_elem.text)
        if match:
            parts = match.group(1).split()
            if len(parts) == 4:
                try:
                    width, height = float(parts[2]), float(parts[3])
                    # Учитываем масштаб, с которым был снят SVG
                    scale_match = re.match(r'scaled_([\d.]+)',
                                           root.get("original-svg-coord-system", ""))
                    if scale_match:
                        scale = float(scale_match.group(1))
                        if scale > 0:
                            width, height = width / scale, height / scale
                    if width > 0 and height > 0:
                        return width, height
                except ValueError:
                    pass

    return None, None


def parse_coord(value: str, dimension: Optional[float]) -> float:
    # Разбирает координату: '62.064%' -> абсолютное значение, '123.4' -> как есть
    value = (value or "").strip()
    if value.endswith('%'):
        percent = float(value[:-1])
        if not dimension:
            raise ValueError(f"координата в процентах ({value}) без размеров холста")
        return percent / 100.0 * dimension
    return float(value)


def _parse_pair_list(raw: str, width: Optional[float],
                     height: Optional[float]) -> Tuple[float, ...]:
    # Координаты чередуются: x берёт ширину, y — высоту
    return tuple(parse_coord(value, width if index % 2 == 0 else height)
                 for index, value in enumerate(raw.split(',')))


def _read_contour(tech_name: str, contour_elem: ET.Element,
                  width: Optional[float], height: Optional[float]) -> Contour:
    bounds = _parse_pair_list(contour_elem.get("bounds", ""), width, height)
    center = _parse_pair_list(contour_elem.get("center", ""), width, height)

    # Проверка длины: раньше её не было, и контур из трёх чисел вместо
    # четырёх доживал до отрисовки, где падал уже без всякой связи с файлом
    if len(bounds) != 4 or len(center) != 2:
        raise ValueError(f"границ {len(bounds)} вместо 4, центр из {len(center)} чисел")

    return Contour(name=tech_name, bounds=bounds, center=center,
                   tech_object=tech_name)


def _read_device(device: ET.Element, tech_name: str,
                 width: Optional[float], height: Optional[float]) -> DeviceMatch:
    return DeviceMatch(
        lua_name=device.get("lua_name", ""),
        pdf_name=device.get("pdf_name", ""),
        tech_object=tech_name,
        coordinates=(parse_coord(device.get("x", "0"), width),
                     parse_coord(device.get("y", "0"), height)),
        confidence=float(device.get("confidence", 0)),
        descr=device.get("descr", ""),
        article=device.get("article", ""),
        device_type=device.get("device_type", ""),
        category=device.get("category", ""),
        extra_data={},
    )


def load_document(file_path: str) -> LoadedDocument:
    """Читает XML целиком. Ошибку самого файла отдаёт наверх.

    Неразобранная запись файл не отменяет: она попадает в problems,
    а остальное загружается. Один кривой контур не повод потерять лист.
    """
    root = ET.parse(file_path).getroot()
    width, height = canvas_size(root)

    document = LoadedDocument(canvas=(width, height),
                              coordinate_type=root.get("coordinate-type", ""))

    for tech_obj in root.findall(".//TechnologicalObject"):
        tech_name = tech_obj.get("name", "")
        if not tech_name:
            continue

        contour_elem = tech_obj.find("Contour")
        if contour_elem is not None and contour_elem.get("bounds") and contour_elem.get("center"):
            try:
                document.contours.append(
                    _read_contour(tech_name, contour_elem, width, height))
            except ValueError as e:
                document.problems.append(f"контур {tech_name}: {e}")

        devices_elem = tech_obj.find("Devices")
        if devices_elem is None:
            continue

        for device in devices_elem.findall("Device"):
            try:
                document.matches.append(_read_device(device, tech_name, width, height))
            except (ValueError, TypeError) as e:
                document.problems.append(
                    f"устройство {device.get('lua_name', '?')}: {e}")

    return document
