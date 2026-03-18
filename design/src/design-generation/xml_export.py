# export_xml.py
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from typing import List, Optional, Tuple
import re
from PySide6.QtCore import QPointF
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QPainter
from PySide6.QtXml import QDomDocument
import io

from data_models import DeviceMatch, Contour


class SVGToXMLExporter:

    def __init__(self, scale_factor: float = 1.25):
        self.scale_factor = scale_factor

    def _parse_svg_content(self, svg_path: str) -> Tuple[ET.Element, str]:
        try:
            # Читаем SVG файл
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # Парсим SVG как XML
            svg_root = ET.fromstring(svg_content)

            return svg_root, svg_content

        except Exception as e:
            print(f"Ошибка парсинга SVG: {e}")
            return None, None

    def _transform_coordinate(self, value: float) -> float:
        return value * self.scale_factor

    def _transform_path_data(self, path_data: str) -> str:
        def replace_coord(match):
            num = float(match.group(0))
            transformed = num * self.scale_factor
            # Округляем до 3 знаков после запятой
            return f"{transformed:.3f}"

        # Ищем все числа в path данных
        pattern = r'-?\d+\.?\d*'
        transformed_data = re.sub(pattern, replace_coord, path_data)

        return transformed_data

    def _transform_svg_element(self, elem: ET.Element) -> ET.Element:
        # Трансформируем атрибуты с координатами
        coord_attrs = ['x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'width', 'height']

        for attr in coord_attrs:
            if attr in elem.attrib:
                try:
                    value = float(elem.attrib[attr])
                    elem.attrib[attr] = str(self._transform_coordinate(value))
                except ValueError:
                    pass  # Если не число, оставляем как есть

        # Трансформируем transform атрибут
        if 'transform' in elem.attrib:
            transform = elem.attrib['transform']
            # Масштабируем translate координаты
            translate_pattern = r'translate\(([^)]+)\)'

            def scale_translate(match):
                translate_values = match.group(1).strip().split(',')
                if len(translate_values) == 2:
                    try:
                        tx = float(translate_values[0]) * self.scale_factor
                        ty = float(translate_values[1]) * self.scale_factor
                        return f"translate({tx:.3f},{ty:.3f})"
                    except ValueError:
                        return match.group(0)
                return match.group(0)

            elem.attrib['transform'] = re.sub(translate_pattern, scale_translate, transform)

        # Трансформируем path данные
        if elem.tag.endswith('path') and 'd' in elem.attrib:
            elem.attrib['d'] = self._transform_path_data(elem.attrib['d'])

        # Трансформируем точки в polygon/polyline
        if elem.tag.endswith(('polygon', 'polyline')) and 'points' in elem.attrib:
            points = elem.attrib['points'].strip().split()
            transformed_points = []

            for point in points:
                coords = point.split(',')
                if len(coords) == 2:
                    try:
                        x = float(coords[0]) * self.scale_factor
                        y = float(coords[1]) * self.scale_factor
                        transformed_points.append(f"{x:.3f},{y:.3f}")
                    except ValueError:
                        transformed_points.append(point)
                else:
                    transformed_points.append(point)

            elem.attrib['points'] = ' '.join(transformed_points)

        # Рекурсивно обрабатываем дочерние элементы
        for child in elem:
            self._transform_svg_element(child)

        return elem

    def _create_device_element(self, match: DeviceMatch) -> ET.Element:
        device_elem = ET.Element("Device")
        device_elem.set("lua_name", match.lua_name)
        device_elem.set("pdf_name", match.pdf_name)
        device_elem.set("tech_object", match.tech_object)

        # Координаты (уже в масштабе 1:1, не применяем scale_factor повторно)
        device_elem.set("x", str(match.coordinates[0]))
        device_elem.set("y", str(match.coordinates[1]))

        device_elem.set("confidence", str(match.confidence))

        if match.descr:
            device_elem.set("descr", match.descr)
        if match.article:
            device_elem.set("article", match.article)
        if match.device_type:
            device_elem.set("device_type", match.device_type)
        if match.category:
            device_elem.set("category", match.category)

        # Дополнительные данные
        if match.extra_data:
            extra_elem = ET.SubElement(device_elem, "ExtraData")
            for key, value in match.extra_data.items():
                extra_elem.set(key, str(value))

        return device_elem

    def _create_contour_element(self, contour: Contour) -> ET.Element:
        contour_elem = ET.Element("Contour")
        contour_elem.set("name", contour.name)
        contour_elem.set("tech_object", contour.tech_object)

        # Координаты с учетом масштаба
        minx, miny, maxx, maxy = contour.bounds
        contour_elem.set("bounds", f"{minx},{miny},{maxx},{maxy}")
        contour_elem.set("center", f"{contour.center[0]},{contour.center[1]}")

        # Размеры
        width = maxx - minx
        height = maxy - miny
        contour_elem.set("width", str(width))
        contour_elem.set("height", str(height))

        return contour_elem

    def export(self, svg_path: str, output_xml_path: str,
               matches: List[DeviceMatch], contours: List[Contour]) -> bool:
        try:
            # Парсим исходный SVG
            svg_root, svg_content = self._parse_svg_content(svg_path)
            if svg_root is None:
                print("❌ Не удалось распарсить SVG файл")
                return False

            # Трансформируем SVG с учетом масштаба
            transformed_svg = self._transform_svg_element(svg_root)

            # Добавляем атрибут масштаба в корневой элемент SVG
            transformed_svg.set("data-scale-factor", str(self.scale_factor))

            # Создаем корневой элемент результата
            root = ET.Element("VisualizationData")
            root.set("version", "1.0")
            root.set("svg_scale", str(self.scale_factor))

            # Добавляем трансформированный SVG
            svg_elem = ET.SubElement(root, "SVGContent")
            # Преобразуем трансформированный SVG обратно в строку и сохраняем как CDATA
            svg_str = ET.tostring(transformed_svg, encoding='unicode')
            svg_elem.text = f"<![CDATA[{svg_str}]]>"

            # Добавляем информацию об исходном файле
            source_elem = ET.SubElement(root, "SVGSource")
            source_elem.set("path", os.path.basename(svg_path))
            source_elem.set("full_path", svg_path)

            # Добавляем контуры
            contours_elem = ET.SubElement(root, "Contours")
            for contour in contours:
                contour_elem = self._create_contour_element(contour)
                contours_elem.append(contour_elem)

            # Добавляем устройства
            devices_elem = ET.SubElement(root, "Devices")
            for match in matches:
                device_elem = self._create_device_element(match)
                devices_elem.append(device_elem)

            # Преобразуем в строку с форматированием
            xml_str = self._pretty_xml(root)

            # Сохраняем в файл
            with open(output_xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            print(f"✅ Экспорт завершен: {output_xml_path}")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств: {len(matches)}")
            print(f"   - Масштаб SVG: {self.scale_factor}")
            print(f"   - Размер SVG: {len(svg_str)} символов")

            return True

        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _pretty_xml(self, elem: ET.Element) -> str:
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def export_current_visualization(svg_path: str, output_path: str,
                                 matches: List[DeviceMatch],
                                 contours: List[Contour],
                                 scale_factor: float = 1.25) -> bool:
    exporter = SVGToXMLExporter(scale_factor=scale_factor)
    return exporter.export(svg_path, output_path, matches, contours)


# Если файл запущен как скрипт, можно использовать для тестирования
if __name__ == "__main__":
    import sys
    from data_models import DeviceMatch, Contour

    # Пример использования
    if len(sys.argv) > 1:
        svg_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "exported.xml"


        matches = []
        contours = []

        success = export_current_visualization(svg_file, output_file, matches, contours)
        if success:
            print(f"Готово: {output_file}")
        else:
            print("Ошибка экспорта")