# data_models.py
# Модели данных не зависят от Qt: их использует и headless-конвейер
# (сопоставление, сцена, выгрузки), и окно.
#
# Отрезки и контуры жили отдельным модулем (`segment_data.py`) — те же
# dataclass'ы без поведения и без зависимостей, разделённые только тем,
# что появились в разное время.
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Точка на листе: пара координат
Point = Tuple[float, float]

@dataclass
class DeviceMatch:
    # Единая модель сопоставленного устройства: раньше был второй такой же
    # класс в device_matcher.py и ручное переписывание полей между ними
    lua_name: str
    pdf_name: str
    tech_object: str
    coordinates: Tuple[float, float]
    confidence: float
    descr: str = ""
    article: str = ""
    device_type: str = ""
    category: str = ""
    subtype: str = ""
    dtype: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)
    # Теги устройства из main.io.lua: каналы ввода-вывода (DI/DO/AI/AO)
    # с адресом в контроллере и параметры устройства (par, rt_par, prop).
    # Сопоставление их не смотрит — они нужны мнемосхеме, чтобы привязать
    # изображение к живому сигналу
    tags: Dict[str, Any] = field(default_factory=dict)
    # Досье устройства: закрепляется после сопоставления
    # (device_dossier.attach), чтобы панель и выгрузки читали одно и то же,
    # а не добывали каждая по-своему.
    #
    # states — где устройство открывается и закрывается: операция,
    # состояние, шаг и что с ним происходит. object_data — его техобъект
    # целиком: уставки, свойства, состав оборудования. neighbours — соседи
    # по трубопроводам; появляются только после разбора разметки.
    states: List[Dict[str, Any]] = field(default_factory=list)
    object_data: Dict[str, Any] = field(default_factory=dict)
    neighbours: List[str] = field(default_factory=list)
    # Габарит символа устройства на чертеже (ширина, высота) в пунктах листа.
    # Заполняется разметкой по кластеру красных линий и нужен только окну:
    # им обводится устройство на схеме вместо закрашенного кружка.
    #
    # Отдельным полем, а не в extra_data: extra_data уезжает в выгрузки
    # целиком (hmi_export, json_export, xml_export перебирают его ключи),
    # а обводка — способ смотреть в окне, редактору она не нужна.
    view_size: Optional[Tuple[float, float]] = None
    # Линии символа устройства относительно его центра, в пунктах листа.
    # По ним обводка повторяет сам рисунок с чертежа, а не описанный вокруг
    # него прямоугольник. Тоже только для окна и тоже не в extra_data.
    view_shape: List[Tuple[float, float, float, float]] = field(default_factory=list)


@dataclass
class DeviceBox:
    # Рамка устройства, найденная YOLO.
    #
    # Раньше рамки передавались четвёрками координат, а класс и уверенность,
    # которые модель выдаёт вместе с ними, отбрасывались. Распаковка
    # `x1, y1, x2, y2 = box` продолжает работать — см. __iter__.
    x1: float
    y1: float
    x2: float
    y2: float
    cls_name: str = ""
    confidence: float = 0.0

    def __iter__(self):
        return iter((self.x1, self.y1, self.x2, self.y2))

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def scaled(self, scale_x: float, scale_y: float) -> "DeviceBox":
        return DeviceBox(self.x1 * scale_x, self.y1 * scale_y,
                         self.x2 * scale_x, self.y2 * scale_y,
                         self.cls_name, self.confidence)


@dataclass
class Contour:
    name: str
    bounds: Tuple[float, float, float, float]
    center: Tuple[float, float]
    tech_object: str


@dataclass
class Operation:
    id: str
    name: str
    base_operation: Optional[str]
    obj_id: str
    obj_name: str
    props: Dict[str, Any] = field(default_factory=dict)



@dataclass
class SegmentData:
    p1: Point
    p2: Point
    dashed: bool = False

@dataclass
class ClosedContour:
    segments: List[int]
    bounds: Tuple[float, float, float, float]
    center: Point
    name: Optional[str] = None
    name_position: Optional[Point] = None
