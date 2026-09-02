# export_scene.py
# Общая подготовка данных к выгрузке: разбор размеченного SVG, приведение
# координат к пунктам PDF, точки сопряжения, трубопроводы, уточнение положения
# устройств по геометрии.
#
# Зачем отдельным модулем. Этот блок дословно повторялся в xml_export
# и postgres_export, а с появлением выгрузки в JSON копий стало бы три.
# Расхождение между копиями означало бы, что каналы выгрузки отдают разные
# данные об одном и том же листе, и заметить это можно было бы только
# сравнением файлов вручную.
#
# Модуль не знает про Qt и ничего не сериализует: как записать сцену —
# дело xml_export и json_export.
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Optional, Tuple

from contur.core import config
from contur.core.data_models import Contour, DeviceMatch
from contur.matching import device_dossier
from contur.lua.objects_loader import objects_data
from contur.pdf.svg_geometry import (
    DeviceCenter, JunctionPoint, LineSegment, Pipeline, SheetText,
    build_pipelines, detect_coordinate_system, device_centers,
    extract_line_segments, extract_texts, find_junction_points,
    get_svg_dimensions, merge_collinear, resolve_device_names,
    snap_devices_to_geometry, tolerance_scale,
)

# Атрибуты SVG, значения которых являются координатами
COORD_ATTRS = ("x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "width", "height")
X_ATTRS = ("x", "x1", "x2", "cx", "width")


@dataclass
class ExportScene:
    """Размеченный лист, разобранный один раз для любой выгрузки."""

    svg_root: ET.Element
    coord_system: str          # 'pdf_pts', 'scaled_<k>' или 'unknown'
    scale: float               # во сколько раз координаты SVG крупнее пунктов PDF
    width: Optional[float]     # размеры холста в пунктах PDF
    height: Optional[float]
    use_percent: bool
    geometry_scale: float      # множитель допусков для листа другого формата
    line_segments: List[LineSegment]
    # Тот же лист, но для показа: рамка помечена, а не выброшена.
    # Анализ ведётся по line_segments — иначе рамка полезет в граф труб
    drawing_segments: List[LineSegment]
    junction_points: List[JunctionPoint]
    pipelines: List[Pipeline]
    matches: List[DeviceMatch]   # с уточнёнными по геометрии координатами
    contours: List[Contour]
    # Габариты устройств из красных сегментов. Считаются один раз: при
    # уточнении координат они уже нужны, а выгрузке в редактор мнемосхем
    # нужен ещё и размер символа
    centers: Optional[List[DeviceCenter]] = None
    # Надписи чертежа. Тоже лениво: XML и PostgreSQL их не пишут,
    # а разбирать 784 элемента ради каждой выгрузки незачем
    texts: Optional[List[SheetText]] = None

    def device_boxes(self) -> List[DeviceCenter]:
        if self.centers is None:
            self.centers = device_centers(self.line_segments, scale=self.geometry_scale)
        return self.centers

    def sheet_texts(self) -> List[SheetText]:
        # Считается до svg_markup(): тот переводит дерево в проценты на месте,
        # и координаты надписей после него были бы в других единицах
        if self.texts is None:
            self.texts = extract_texts(self.svg_root, self.scale)
        return self.texts

    def dimension(self, is_x: bool) -> Optional[float]:
        return self.width if is_x else self.height

    def to_percent(self, value: float, dimension: Optional[float]) -> float:
        # Доля от размера холста в процентах
        if not dimension or dimension <= 0:
            return value
        return value / dimension * 100

    def svg_markup(self) -> str:
        """Разметка листа в той системе координат, в которой идёт выгрузка.

        Преобразование меняет дерево на месте — за один экспорт зовётся один раз.
        """
        if self.use_percent:
            _to_percent_tree(self.svg_root, self)
        self.svg_root.set("coordinate-type", "percent" if self.use_percent else "absolute")
        return ET.tostring(self.svg_root, encoding="unicode")


def build_scene(svg_path: str, matches: List[DeviceMatch], contours: List[Contour],
                pdf_size: Optional[Tuple[float, float]] = None,
                use_percent_coords: bool = True,
                snap_to_geometry: bool = True) -> Optional[ExportScene]:
    """Разбирает размеченный SVG и считает всё, что нужно любой выгрузке.

    pdf_size — размер страницы исходного PDF в пунктах. Если задан, масштаб SVG
    вычисляется точно; иначе подбирается эвристикой (все ISO-форматы имеют
    одинаковое соотношение сторон, поэтому подбор неоднозначен).

    Возвращает None, если SVG не разобрался.
    """
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_root = ET.fromstring(f.read())
    except Exception as e:
        print(f"Ошибка парсинга SVG: {e}")
        print("❌ Не удалось распарсить SVG файл")
        return None

    coord_system, scale = detect_coordinate_system(svg_root, pdf_size)
    print(f"🔍 Детектирована система координат SVG: {coord_system}")

    width, height = get_svg_dimensions(svg_root, scale)
    print(f"📐 Нормализованные размеры SVG: {width} x {height}")

    # Без известных размеров холста проценты посчитать нельзя —
    # переключаемся на абсолютные координаты, чтобы не выдать значения вида 1178%
    if use_percent_coords and not (width and height):
        print("⚠️ Размеры холста неизвестны — экспорт в абсолютных координатах")
        use_percent_coords = False

    print("🔍 Извлечение сегментов линий из SVG...")
    drawing_segments: List[LineSegment] = []
    line_segments = extract_line_segments(svg_root, scale, (width, height),
                                          drawing=drawing_segments)

    # Чертёж склеивается: в редакторе отрезок короче клетки сетки
    # схлопывается в точку и пропадает с холста. Помогает мало — Eplan рисует
    # углами, а не цепочками, — но то, что можно склеить, склеивается
    drawing_segments = merge_collinear(drawing_segments)

    # Допуски геометрии подобраны под A0; на листе другого формата
    # их надо пропорционально изменить
    geometry_scale = tolerance_scale(svg_root)
    if abs(geometry_scale - 1.0) > 0.01:
        print(f"📐 Допуски геометрии масштабированы: x{geometry_scale:.2f}")

    print("🔍 Поиск точек сопряжения...")
    junction_points = find_junction_points(line_segments, scale=geometry_scale)

    # Короткие подписи из SVG ('V1') разрешаем в полные имена ('LA_TANK1V1'),
    # иначе связь с устройством неоднозначна: подпись повторяется у каждого объекта
    resolve_device_names(
        junction_points,
        [(m.lua_name, m.pdf_name, m.coordinates[0], m.coordinates[1]) for m in matches],
        scale=geometry_scale)

    # Уточняем положение устройств по геометрии (координаты приходят
    # от текстовой метки, а она нарисована рядом с устройством).
    # Работаем на копиях, чтобы не менять состояние вызывающего кода.
    centers = None
    if snap_to_geometry:
        matches = [replace(m) for m in matches]
        centers = device_centers(line_segments, scale=geometry_scale)
        snap_devices_to_geometry(matches, centers, scale=geometry_scale)

    print("🔧 Построение трубопроводов...")
    blue_segments = [seg for seg in line_segments if seg.color == "blue"]
    pipelines = build_pipelines(blue_segments, junction_points, scale=geometry_scale)

    # Досье устройства: состояния, техобъект и соседи по трубам — при самом
    # устройстве, чтобы выгрузки и панель читали одно и то же. Здесь для
    # этого есть всё сразу, включая трубопроводы
    counts = device_dossier.attach(matches, pipelines)
    print(f"🧾 {device_dossier.summary(counts)}")

    return ExportScene(
        svg_root=svg_root, coord_system=coord_system, scale=scale,
        width=width, height=height, use_percent=use_percent_coords,
        geometry_scale=geometry_scale, line_segments=line_segments,
        drawing_segments=drawing_segments,
        junction_points=junction_points, pipelines=pipelines,
        matches=matches, contours=contours, centers=centers)


# ---------------------------------------------------------------- состояния устройств

def device_operation_state(current_operation_id: Optional[str],
                           device_name: str) -> Tuple[str, Dict[str, Any]]:
    # Состояние устройства в текущей операции
    if not current_operation_id:
        return "not_used", {}

    details = objects_data.get_device_details_in_operation(current_operation_id, device_name)
    if details:
        return details.get("status", "not_used"), details
    return "not_used", {}


def device_states(device_name: str) -> List[Dict[str, Any]]:
    """Все места, где устройство открывается и закрывается.

    device_operation_state отвечает про одну выбранную операцию; здесь —
    весь список по всем операциям проекта. Разделены намеренно: XML пишет
    состояние в текущей операции, а выгрузка для редактора — все, чтобы
    мнемосхема могла показать положение клапана на любом шаге.
    """
    if not device_name:
        return []
    return objects_data.get_device_states(device_name)


def operation_program(operation_id: str) -> Optional[Dict[str, Any]]:
    """Состояния и шаги операции — то, что стоит за состояниями устройств."""
    if not operation_id:
        return None
    return objects_data.get_operation_program(operation_id)


def object_details(obj_id: str) -> Optional[Dict[str, Any]]:
    """Уставки, свойства и состав техобъекта — то, чем он настроен."""
    if not obj_id:
        return None
    return objects_data.get_object_details(obj_id)


def project_signals() -> List[Dict[str, Any]]:
    """Сигналы проекта: имя, тип и чей он."""
    return list(objects_data.signals)


def controller_nodes() -> List[Dict[str, Any]]:
    """Узлы контроллера из main.io.lua: имя, адрес, тип, модули.

    Читается из разобранного main.io.lua, а не из состояния приложения:
    узлы относятся к проекту целиком, и сцена листа про них ничего не знает.
    Файл перечитывается каждый раз — он маленький, а кэш между проектами
    показал бы узлы предыдущего.
    """
    try:
        with open(config.PARSED_LUA_JSON, "r", encoding="utf-8") as f:
            return list(json.load(f).get("nodes", []))
    except (OSError, ValueError):
        return []


def state_text(status: str) -> str:
    # Статус для показа человеку
    return {
        "opened": "открыто",
        "closed": "закрыто",
        "not_used": "не используется",
    }.get(status, "не известно")


def operation_summary(current_operation_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Текущая операция и сколько устройств в ней открыто и закрыто."""
    if not current_operation_id:
        return None

    current_op = objects_data.get_operation_by_id(current_operation_id)
    if not current_op:
        return None

    devices_status = objects_data.get_devices_for_operation(current_operation_id)
    return {
        "id": current_operation_id,
        "name": current_op.name,
        "tech_object": current_op.obj_name,
        "devices_opened": sum(1 for s in devices_status.values() if s == "opened"),
        "devices_closed": sum(1 for s in devices_status.values() if s == "closed"),
        "devices_total": len(devices_status),
    }


# ---------------------------------------------------------------- координаты SVG

def _percent_string(value: float, dimension: Optional[float], scene: ExportScene) -> str:
    # Координаты внутри SVG заданы в его собственном масштабе, а размеры уже
    # приведены к пунктам PDF — нормализуем и значение
    unknown_scale = scene.coord_system in (None, "unknown") or not scene.scale
    normalized = value if unknown_scale else value / scene.scale
    if not dimension or dimension <= 0:
        return f"{normalized:.3f}"
    return f"{scene.to_percent(normalized, dimension):.3f}%"


def _to_percent_tree(elem: ET.Element, scene: ExportScene) -> ET.Element:
    # Переводит координаты элемента и всех вложенных в проценты холста
    for attr in COORD_ATTRS:
        if attr in elem.attrib:
            try:
                value = float(elem.attrib[attr])
            except ValueError:
                continue
            dimension = scene.dimension(attr in X_ATTRS)
            if dimension and dimension > 0:
                elem.attrib[attr] = _percent_string(value, dimension, scene)

    if elem.tag.endswith("path") and "d" in elem.attrib:
        elem.attrib["d"] = _path_to_percent(elem.attrib["d"], scene)

    if elem.tag.endswith(("polygon", "polyline")) and "points" in elem.attrib:
        elem.attrib["points"] = _points_to_percent(elem.attrib["points"], scene)

    for child in elem:
        _to_percent_tree(child, scene)

    return elem


def _path_to_percent(path_data: str, scene: ExportScene) -> str:
    # Числа в d идут парами x,y (команды M/L/C, которые генерирует pdf_processor),
    # поэтому чередуем ширину и высоту — раньше ко всем числам применялась ширина
    counter = {"i": 0}

    def replace_coord(match):
        num = float(match.group(0))
        is_x = counter["i"] % 2 == 0
        counter["i"] += 1
        dimension = scene.dimension(is_x)
        if not dimension or dimension <= 0:
            return match.group(0)
        return _percent_string(num, dimension, scene)

    return re.sub(r"-?\d+\.?\d*", replace_coord, path_data)


def _points_to_percent(points_str: str, scene: ExportScene) -> str:
    # Точки polygon/polyline записаны парами "x,y" через пробел
    transformed = []

    for point in points_str.strip().split():
        coords = point.split(",")
        if len(coords) != 2:
            transformed.append(point)
            continue
        try:
            x = _percent_string(float(coords[0]), scene.width, scene)
            y = _percent_string(float(coords[1]), scene.height, scene)
        except ValueError:
            transformed.append(point)
            continue
        transformed.append(f"{x},{y}")

    return " ".join(transformed)
