# scene.py
# Сцена листа: разбор размеченного SVG, приведение координат к пунктам PDF,
# точки сопряжения, трубопроводы, уточнение положения устройств по геометрии.
#
# Это стержень конвейера, а не часть выгрузки. Чертёж и описание контроллера
# сходятся здесь в один разобранный лист, и дальше его одинаково читают все
# четыре выгрузки и главное окно. Лежала сцена внутри `export`, и окну
# приходилось импортировать из выгрузки то, что никуда не выгружается.
#
# Собирается один раз на лист. Раньше этот блок дословно повторялся
# в xml_export и postgres_export, а с появлением выгрузки в JSON копий стало
# бы три: расхождение между ними означало бы, что каналы отдают разные данные
# об одном листе, и заметить это можно было бы только сравнением файлов.
#
# Модуль не знает про Qt и ничего не сериализует: как записать сцену — дело
# выгрузок. Про операции и состояния он тоже не знает, это `lua/queries.py`.
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from typing import List, Optional, Tuple

from contur.core.data_models import Contour, DeviceMatch
from contur.matching import device_dossier
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
