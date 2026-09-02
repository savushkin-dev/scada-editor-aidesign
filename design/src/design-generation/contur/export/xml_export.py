from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from typing import List, Optional, Tuple, Dict

from contur.core.data_models import DeviceMatch, Contour
from contur.export.export_scene import build_scene, device_operation_state, operation_summary, state_text
from contur.pdf.svg_geometry import (
    JunctionPoint, LineSegment, Pipeline, build_connection_graph,
)


class SVGToXMLExporter:
    # Экспортёр SVG в XML с единой системой координат (PDF пункты).
    # Разбор геометрии SVG вынесен в модуль svg_geometry — он общий
    # с экспортом в PostgreSQL, а подготовка сцены (координаты, точки
    # сопряжения, трубы) — в export_scene, общий с выгрузкой в JSON.

    def __init__(self, use_percent_coords: bool = True, current_operation_id: str | None = None,
                 pdf_size: Optional[Tuple[float, float]] = None,
                 snap_to_geometry: bool = True):
        # Инициализация экспортёра.
        # pdf_size — размер страницы исходного PDF в пунктах. Если задан, масштаб SVG
        # вычисляется точно; иначе подбирается эвристикой (все ISO-форматы имеют
        # одинаковое соотношение сторон, поэтому подбор неоднозначен).

        self.use_percent_coords = use_percent_coords
        self.current_operation_id = current_operation_id
        self.pdf_size = pdf_size
        self.snap_to_geometry = snap_to_geometry

        # Размеры SVG (в PDF пунктах после нормализации)
        self.svg_width = None
        self.svg_height = None

        # Для хранения линий, точек сопряжения и трубопроводов
        self.line_segments: List[LineSegment] = []
        self.junction_points: List[JunctionPoint] = []
        self.pipelines: List[Pipeline] = []

        # Информация о системе координат SVG
        self._svg_coord_system = None  # 'pdf_pts', 'scaled_<k>', 'unknown'
        self._detected_scale = 1.0

    def set_current_operation(self, operation_id: str):
        # Устанавливает текущую операцию для экспорта состояний устройств
        self.current_operation_id = operation_id

    def _to_percent(self, value: float, dimension: float) -> str:
        # Преобразует абсолютное значение в проценты
        if dimension <= 0:
            return f"{value:.3f}"
        return f"{(value / dimension * 100):.3f}%"

    def _get_device_operation_state(self, device_name: str) -> Tuple[str, Dict]:
        # Возвращает состояние устройства в текущей операции
        return device_operation_state(self.current_operation_id, device_name)

    def _create_device_element(self, match: DeviceMatch) -> ET.Element:
        # Создаёт XML элемент для устройства
        device_elem = ET.Element("Device")

        if match.device_type:
            device_elem.set("device_type", str(match.device_type))
        device_elem.set("lua_name", str(match.lua_name))
        device_elem.set("pdf_name", str(match.pdf_name))

        x, y = match.coordinates[0], match.coordinates[1]

        if self.use_percent_coords and self.svg_width and self.svg_height:
            device_elem.set("x", self._to_percent(x, self.svg_width))
            device_elem.set("y", self._to_percent(y, self.svg_height))
        else:
            device_elem.set("x", f"{x:.3f}")
            device_elem.set("y", f"{y:.3f}")

        device_elem.set("confidence", f"{match.confidence:.2f}")

        # str() обязателен: subtype и dtype приходят из Lua числами,
        # а ElementTree падает при сериализации нестроковых атрибутов
        for attribute, value in (("descr", match.descr), ("article", match.article),
                                 ("category", match.category), ("subtype", match.subtype),
                                 ("dtype", match.dtype)):
            if value or value == 0:
                device_elem.set(attribute, str(value))

        if match.extra_data:
            for key, value in match.extra_data.items():
                if value is None or (isinstance(value, str) and not value.strip()):
                    continue
                device_elem.set(key, str(value))

        status, details = self._get_device_operation_state(match.lua_name)
        if status == "not_used":
            status, details = self._get_device_operation_state(match.pdf_name)

        device_elem.set("operation_state", state_text(status))

        if details:
            if details.get("state_name"):
                device_elem.set("operation_state_name", details["state_name"])
            if details.get("step_name"):
                device_elem.set("operation_step", details["step_name"])
            if details.get("step_number", -1) >= 0:
                device_elem.set("operation_step_number", str(details["step_number"]))

        return device_elem

    def _create_contour_element(self, contour: Contour) -> ET.Element:
        # Создаёт XML элемент для контура
        contour_elem = ET.Element("Contour")
        contour_elem.set("name", contour.name)
        contour_elem.set("tech_object", contour.tech_object)

        minx, miny, maxx, maxy = contour.bounds

        if self.use_percent_coords and self.svg_width and self.svg_height:
            contour_elem.set("bounds",
                             f"{self._to_percent(minx, self.svg_width)},{self._to_percent(miny, self.svg_height)},{self._to_percent(maxx, self.svg_width)},{self._to_percent(maxy, self.svg_height)}")
            contour_elem.set("center",
                             f"{self._to_percent(contour.center[0], self.svg_width)},{self._to_percent(contour.center[1], self.svg_height)}")
            contour_elem.set("width", self._to_percent(maxx - minx, self.svg_width))
            contour_elem.set("height", self._to_percent(maxy - miny, self.svg_height))
        else:
            contour_elem.set("bounds", f"{minx:.3f},{miny:.3f},{maxx:.3f},{maxy:.3f}")
            contour_elem.set("center", f"{contour.center[0]:.3f},{contour.center[1]:.3f}")
            contour_elem.set("width", f"{(maxx - minx):.3f}")
            contour_elem.set("height", f"{(maxy - miny):.3f}")

        return contour_elem

    def _add_junction_points_section(self, root: ET.Element):
        # Добавляет секцию с точками сопряжения в XML
        if not self.junction_points:
            return

        junctions_elem = ET.SubElement(root, "JunctionPoints")
        junctions_elem.set("count", str(len(self.junction_points)))
        junctions_elem.set("detected", "true")

        for jp in self.junction_points:
            jp_elem = ET.SubElement(junctions_elem, "JunctionPoint")

            if self.use_percent_coords and self.svg_width and self.svg_height:
                jp_elem.set("x", self._to_percent(jp.x, self.svg_width))
                jp_elem.set("y", self._to_percent(jp.y, self.svg_height))
            else:
                jp_elem.set("x", f"{jp.x:.3f}")
                jp_elem.set("y", f"{jp.y:.3f}")

            jp_elem.set("red_line_id", str(jp.red_line_id))
            jp_elem.set("blue_line_id", str(jp.blue_line_id))
            if jp.red_device_name:
                jp_elem.set("red_device", jp.red_device_name)
            jp_elem.set("confidence", f"{jp.confidence:.2f}")

        print(f"   Добавлено точек сопряжения: {len(self.junction_points)}")

    def _add_pipelines_section(self, root: ET.Element):
        # Добавляет секцию с трубопроводами в XML
        if not self.pipelines:
            return

        pipelines_elem = ET.SubElement(root, "Pipelines")
        pipelines_elem.set("count", str(len(self.pipelines)))

        for pipe in self.pipelines:
            pipe_elem = ET.SubElement(pipelines_elem, "Pipeline")
            pipe_elem.set("id", str(pipe.id))
            pipe_elem.set("name", pipe.name)
            pipe_elem.set("segment_count", str(pipe.segment_count))
            pipe_elem.set("total_length", f"{pipe.total_length:.2f}")

            if pipe.connected_devices:
                pipe_elem.set("connected_devices", ",".join(pipe.connected_devices))

            segments_elem = ET.SubElement(pipe_elem, "Segments")
            for seg in pipe.segments:
                seg_elem = ET.SubElement(segments_elem, "Segment")
                seg_elem.set("id", str(seg.id))

                if self.use_percent_coords and self.svg_width and self.svg_height:
                    seg_elem.set("x1", self._to_percent(seg.x1, self.svg_width))
                    seg_elem.set("y1", self._to_percent(seg.y1, self.svg_height))
                    seg_elem.set("x2", self._to_percent(seg.x2, self.svg_width))
                    seg_elem.set("y2", self._to_percent(seg.y2, self.svg_height))
                else:
                    seg_elem.set("x1", f"{seg.x1:.3f}")
                    seg_elem.set("y1", f"{seg.y1:.3f}")
                    seg_elem.set("x2", f"{seg.x2:.3f}")
                    seg_elem.set("y2", f"{seg.y2:.3f}")

        print(f"   Добавлено трубопроводов: {len(self.pipelines)}")

    def _add_connections_section(self, root: ET.Element):
        # Связность: какие устройства соединены каким трубопроводом.
        # Раньше в XML были отдельно точки сопряжения и отдельно трубы —
        # по ним нельзя было сказать, что с чем соединено.
        graph = build_connection_graph(self.pipelines)
        connections = [c for c in graph["connections"] if len(c.devices) >= 2]
        if not connections:
            return

        connections_elem = ET.SubElement(root, "Connections")
        connections_elem.set("count", str(len(connections)))
        connections_elem.set("manifolds", str(graph["manifolds"]))
        connections_elem.set("dead_ends", str(graph["dead_ends"]))

        for connection in connections:
            elem = ET.SubElement(connections_elem, "Connection")
            elem.set("pipeline", connection.pipeline_name)
            elem.set("devices", ",".join(connection.devices))
            elem.set("length", f"{connection.length:.2f}")
            elem.set("segment_count", str(connection.segment_count))

        print(f"   Добавлено соединений: {len(connections)} "
              f"(коллекторов: {graph['manifolds']}, тупиков: {graph['dead_ends']})")

    def _add_operation_info(self, root: ET.Element):
        # Добавляет информацию об операции
        operation_info_elem = ET.SubElement(root, "CurrentOperationInfo")
        operation = operation_summary(self.current_operation_id)
        if operation:
            for key, value in operation.items():
                operation_info_elem.set(key, str(value))

    def _add_tech_objects(self, parent: ET.Element, matches: List[DeviceMatch], contours: List[Contour]):
        # Добавляет технологические объекты в XML
        contours_by_tech = {}
        for contour in contours:
            if contour.tech_object not in contours_by_tech:
                contours_by_tech[contour.tech_object] = []
            contours_by_tech[contour.tech_object].append(contour)

        devices_by_tech = {}
        for match in matches:
            if match.tech_object not in devices_by_tech:
                devices_by_tech[match.tech_object] = []
            devices_by_tech[match.tech_object].append(match)

        all_tech_objects = set(contours_by_tech.keys()) | set(devices_by_tech.keys())

        for tech_obj_name in sorted(all_tech_objects):
            tech_obj_elem = ET.SubElement(parent, "TechnologicalObject")
            tech_obj_elem.set("name", tech_obj_name)

            if tech_obj_name in contours_by_tech:
                contour = contours_by_tech[tech_obj_name][0]
                contour_elem = self._create_contour_element(contour)
                tech_obj_elem.append(contour_elem)

            if tech_obj_name in devices_by_tech:
                devices_elem = ET.SubElement(tech_obj_elem, "Devices")
                for match in sorted(devices_by_tech[tech_obj_name], key=lambda x: x.pdf_name):
                    device_elem = self._create_device_element(match)
                    devices_elem.append(device_elem)

    def _pretty_xml(self, elem: ET.Element) -> str:
        # Форматирует XML для чтения
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

    def export(self, svg_path: str, output_xml_path: str,
               matches: List[DeviceMatch], contours: List[Contour]) -> bool:
        # Экспорт в XML с автоматической нормализацией координат
        try:
            print("\n📊 ДИАГНОСТИКА:")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств (matches): {len(matches)}")

            # Разбор SVG, координаты, точки сопряжения и трубы — общие
            # для всех каналов выгрузки, они собраны в export_scene
            scene = build_scene(svg_path, matches, contours, self.pdf_size,
                                self.use_percent_coords, self.snap_to_geometry)
            if scene is None:
                return False

            self._svg_coord_system = scene.coord_system
            self._detected_scale = scene.scale
            self.svg_width, self.svg_height = scene.width, scene.height
            self.use_percent_coords = scene.use_percent
            self.line_segments = scene.line_segments
            self.junction_points = scene.junction_points
            self.pipelines = scene.pipelines
            matches = scene.matches

            svg_str = scene.svg_markup()

            # Создаём корневой элемент
            root = ET.Element("PlantGeometry")
            root.set("version", "1.3")
            root.set("coordinate-type", "percent" if self.use_percent_coords else "absolute")
            root.set("original-svg-coord-system", self._svg_coord_system)

            # Размеры холста в PDF пунктах — нужны, чтобы обратно перевести
            # проценты в абсолютные координаты при загрузке файла
            if self.svg_width and self.svg_height:
                root.set("canvas-width", f"{self.svg_width:.3f}")
                root.set("canvas-height", f"{self.svg_height:.3f}")

            if self.junction_points:
                root.set("has-junction-points", "true")
                root.set("junction-points-count", str(len(self.junction_points)))

            if self.pipelines:
                root.set("has-pipelines", "true")
                root.set("pipelines-count", str(len(self.pipelines)))

            # Информация о текущей операции
            operation = operation_summary(self.current_operation_id)
            if operation:
                root.set("current_operation_id", operation["id"])
                root.set("current_operation_name", operation["name"])
                root.set("current_operation_object", operation["tech_object"])

            # Технологические объекты
            tech_objects_elem = ET.SubElement(root, "TechnologicalObjects")
            self._add_tech_objects(tech_objects_elem, matches, contours)

            # Точки сопряжения
            self._add_junction_points_section(root)

            # Трубопроводы
            self._add_pipelines_section(root)

            # Связность устройств через трубопроводы
            self._add_connections_section(root)

            # Информация об операции
            if self.current_operation_id:
                self._add_operation_info(root)

            # SVG содержимое
            svg_content_elem = ET.SubElement(root, "SVGContent")
            svg_content_elem.text = f"<![CDATA[{svg_str}]]>"

            # Сохраняем
            xml_str = self._pretty_xml(root)
            with open(output_xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            print(f"✅ Экспорт завершен: {output_xml_path}")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств: {len(matches)}")
            print(f"   - Точек сопряжения: {len(self.junction_points)}")
            print(f"   - Трубопроводов: {len(self.pipelines)}")
            print(f"   - Тип координат: {'проценты' if self.use_percent_coords else 'абсолютные'}")

            return True

        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
            return False


# Функция для экспорта
def export_current_visualization(svg_path: str, output_path: str,
                                 matches: List[DeviceMatch],
                                 contours: List[Contour],
                                 use_percent_coords: bool = True,
                                 current_operation_id: str | None = None,
                                 pdf_size: Optional[Tuple[float, float]] = None,
                                 snap_to_geometry: bool = True) -> bool:
    # Экспорт текущей визуализации в XML.
    # pdf_size — размер страницы исходного PDF в пунктах (для точного масштаба).
    exporter = SVGToXMLExporter(use_percent_coords=use_percent_coords,
                                current_operation_id=current_operation_id,
                                pdf_size=pdf_size, snap_to_geometry=snap_to_geometry)
    return exporter.export(svg_path, output_path, matches, contours)


def get_pdf_page_size(pdf_path: str, page_number: int = 0) -> Optional[Tuple[float, float]]:
    # Возвращает размер страницы PDF в пунктах или None, если файл недоступен
    if not pdf_path or not os.path.exists(pdf_path):
        return None
    try:
        import fitz
        with fitz.open(pdf_path) as doc:
            rect = doc[page_number].rect
            return rect.width, rect.height
    except Exception as e:
        print(f"⚠️ Не удалось определить размер страницы PDF: {e}")
        return None


if __name__ == "__main__":
    import sys

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
