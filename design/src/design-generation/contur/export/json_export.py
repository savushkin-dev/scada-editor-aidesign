# json_export.py
# Выгрузка размеченного листа в JSON — тот же состав, что в XML.
#
# Зачем. XML читает нынешний потребитель, но бывает нужен формат,
# который разбирается штатными средствами языка без обхода дерева
# и без вытаскивания разметки из CDATA. Файл самодостаточен: разметка листа
# лежит строкой в поле "svg", как в секции SVGContent у XML.
#
# Отличия от XML только в записи, не в составе:
#   - числа остаются числами, а не строками «12.480%»; в каких они единицах,
#     говорит поле "coordinate_type" (percent — доля холста в процентах);
#   - границы и центры — массивы [minx, miny, maxx, maxy] и [x, y]
#     вместо строк через запятую;
#   - счётчики (count) не дублируются: длина массива и есть счётчик.
#
# Сцена (координаты, точки сопряжения, трубы) собирается в export_scene —
# тем же кодом, что и для XML, чтобы каналы не разъезжались.
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
import json
from typing import Any, Dict, List, Optional, Tuple

from contur.core.data_models import Contour, DeviceMatch
from contur.export.export_scene import (
    ExportScene, build_scene, device_operation_state, operation_summary, state_text,
)
from contur.pdf.svg_geometry import build_connection_graph

# Версия формата общая с XML: состав тот же, меняются вместе
FORMAT_VERSION = "1.3"


class SVGToJSONExporter:
    """Экспортёр размеченного SVG в JSON."""

    def __init__(self, use_percent_coords: bool = True,
                 current_operation_id: Optional[str] = None,
                 pdf_size: Optional[Tuple[float, float]] = None,
                 snap_to_geometry: bool = True):
        self.use_percent_coords = use_percent_coords
        self.current_operation_id = current_operation_id
        self.pdf_size = pdf_size
        self.snap_to_geometry = snap_to_geometry
        self.scene: Optional[ExportScene] = None

    # ---------------------------------------------------------------- координаты

    def _x(self, value: float) -> float:
        return self._coord(value, self.scene.width)

    def _y(self, value: float) -> float:
        return self._coord(value, self.scene.height)

    def _coord(self, value: float, dimension: Optional[float]) -> float:
        # Значения уже приведены к пунктам PDF; в процентах — доля от холста.
        # Три знака после запятой, как в XML: на A0 это сотые доли пункта
        if self.scene.use_percent and dimension and dimension > 0:
            return round(self.scene.to_percent(value, dimension), 3)
        return round(value, 3)

    # ---------------------------------------------------------------- разделы

    def _device(self, match: DeviceMatch) -> Dict[str, Any]:
        device: Dict[str, Any] = {}

        if match.device_type:
            device["device_type"] = str(match.device_type)
        device["lua_name"] = str(match.lua_name)
        device["pdf_name"] = str(match.pdf_name)
        device["x"] = self._x(match.coordinates[0])
        device["y"] = self._y(match.coordinates[1])
        device["confidence"] = round(match.confidence, 2)

        for key, value in (("descr", match.descr), ("article", match.article),
                           ("category", match.category), ("subtype", match.subtype),
                           ("dtype", match.dtype)):
            if value or value == 0:
                device[key] = value

        # Поля из Lua, которых нет в модели: приходят как есть, включая числа
        for key, value in (match.extra_data or {}).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            device[key] = value if isinstance(value, (str, int, float, bool)) else str(value)

        status, details = device_operation_state(self.current_operation_id, match.lua_name)
        if status == "not_used":
            status, details = device_operation_state(self.current_operation_id, match.pdf_name)

        device["operation_state"] = state_text(status)

        if details:
            if details.get("state_name"):
                device["operation_state_name"] = details["state_name"]
            if details.get("step_name"):
                device["operation_step"] = details["step_name"]
            if details.get("step_number", -1) >= 0:
                device["operation_step_number"] = details["step_number"]

        return device

    def _contour(self, contour: Contour) -> Dict[str, Any]:
        minx, miny, maxx, maxy = contour.bounds
        return {
            "name": contour.name,
            "tech_object": contour.tech_object,
            "bounds": [self._x(minx), self._y(miny), self._x(maxx), self._y(maxy)],
            "center": [self._x(contour.center[0]), self._y(contour.center[1])],
            "width": self._x(maxx - minx),
            "height": self._y(maxy - miny),
        }

    def _tech_objects(self, matches: List[DeviceMatch],
                      contours: List[Contour]) -> List[Dict[str, Any]]:
        contours_by_tech: Dict[str, List[Contour]] = {}
        for contour in contours:
            contours_by_tech.setdefault(contour.tech_object, []).append(contour)

        devices_by_tech: Dict[str, List[DeviceMatch]] = {}
        for match in matches:
            devices_by_tech.setdefault(match.tech_object, []).append(match)

        tech_objects = []
        for name in sorted(set(contours_by_tech) | set(devices_by_tech)):
            entry: Dict[str, Any] = {"name": name}
            if name in contours_by_tech:
                entry["contour"] = self._contour(contours_by_tech[name][0])
            entry["devices"] = [self._device(m) for m in
                                sorted(devices_by_tech.get(name, []), key=lambda x: x.pdf_name)]
            tech_objects.append(entry)

        return tech_objects

    def _junction_points(self) -> List[Dict[str, Any]]:
        points = []
        for jp in self.scene.junction_points:
            point = {
                "x": self._x(jp.x),
                "y": self._y(jp.y),
                "red_line_id": jp.red_line_id,
                "blue_line_id": jp.blue_line_id,
            }
            if jp.red_device_name:
                point["red_device"] = jp.red_device_name
            point["confidence"] = round(jp.confidence, 2)
            points.append(point)
        return points

    def _pipelines(self) -> List[Dict[str, Any]]:
        pipelines = []
        for pipe in self.scene.pipelines:
            pipelines.append({
                "id": pipe.id,
                "name": pipe.name,
                "segment_count": pipe.segment_count,
                "total_length": round(pipe.total_length, 2),
                "connected_devices": list(pipe.connected_devices),
                "segments": [{
                    "id": seg.id,
                    "x1": self._x(seg.x1), "y1": self._y(seg.y1),
                    "x2": self._x(seg.x2), "y2": self._y(seg.y2),
                } for seg in pipe.segments],
            })
        return pipelines

    def _connections(self) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        # Связность: какие устройства соединены каким трубопроводом.
        # Отдельно точки сопряжения и отдельно трубы не отвечают на вопрос,
        # что с чем соединено
        graph = build_connection_graph(self.scene.pipelines)
        connections = [{
            "pipeline": c.pipeline_name,
            "devices": list(c.devices),
            "length": round(c.length, 2),
            "segment_count": c.segment_count,
        } for c in graph["connections"] if len(c.devices) >= 2]

        return connections, {"manifolds": graph["manifolds"], "dead_ends": graph["dead_ends"]}

    # ---------------------------------------------------------------- выгрузка

    def build(self, svg_path: str, matches: List[DeviceMatch],
              contours: List[Contour]) -> Optional[Dict[str, Any]]:
        """Собирает документ. Отдельно от записи — чтобы его можно было проверить."""
        self.scene = build_scene(svg_path, matches, contours, self.pdf_size,
                                 self.use_percent_coords, self.snap_to_geometry)
        if self.scene is None:
            return None

        self.use_percent_coords = self.scene.use_percent

        document: Dict[str, Any] = {
            "format": "CONTUR PlantGeometry",
            "version": FORMAT_VERSION,
            "coordinate_type": "percent" if self.scene.use_percent else "absolute",
            "original_svg_coord_system": self.scene.coord_system,
        }

        # Размеры холста в пунктах PDF: без них проценты обратно в координаты
        # не перевести
        if self.scene.width and self.scene.height:
            document["canvas"] = {
                "width": round(self.scene.width, 3),
                "height": round(self.scene.height, 3),
                "units": "pt",
            }

        operation = operation_summary(self.current_operation_id)
        if operation:
            document["current_operation"] = operation

        document["tech_objects"] = self._tech_objects(self.scene.matches, contours)
        document["junction_points"] = self._junction_points()
        document["pipelines"] = self._pipelines()

        connections, graph = self._connections()
        document["connections"] = connections
        document["graph"] = graph

        # Разметка листа строкой — как секция SVGContent у XML.
        # Зовётся последней: преобразование координат меняет дерево на месте
        document["svg"] = self.scene.svg_markup()

        return document

    def export(self, svg_path: str, output_json_path: str,
               matches: List[DeviceMatch], contours: List[Contour]) -> bool:
        try:
            print("\n📊 ДИАГНОСТИКА:")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств (matches): {len(matches)}")

            document = self.build(svg_path, matches, contours)
            if document is None:
                return False

            # ensure_ascii=False: иначе описания устройств превращаются
            # в Верх... и файл нечитаем глазами
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False, indent=2)

            print(f"✅ Экспорт завершен: {output_json_path}")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств: {len(matches)}")
            print(f"   - Точек сопряжения: {len(document['junction_points'])}")
            print(f"   - Трубопроводов: {len(document['pipelines'])}")
            print(f"   - Соединений: {len(document['connections'])}")
            print(f"   - Тип координат: "
                  f"{'проценты' if self.use_percent_coords else 'абсолютные'}")

            return True

        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
            return False


def export_current_visualization_json(svg_path: str, output_path: str,
                                      matches: List[DeviceMatch],
                                      contours: List[Contour],
                                      use_percent_coords: bool = True,
                                      current_operation_id: Optional[str] = None,
                                      pdf_size: Optional[Tuple[float, float]] = None,
                                      snap_to_geometry: bool = True) -> bool:
    # Экспорт текущей визуализации в JSON.
    # pdf_size — размер страницы исходного PDF в пунктах (для точного масштаба).
    exporter = SVGToJSONExporter(use_percent_coords=use_percent_coords,
                                 current_operation_id=current_operation_id,
                                 pdf_size=pdf_size, snap_to_geometry=snap_to_geometry)
    return exporter.export(svg_path, output_path, matches, contours)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        svg_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "exported.json"

        success = export_current_visualization_json(svg_file, output_file, [], [])
        print(f"Готово: {output_file}" if success else "Ошибка экспорта")
