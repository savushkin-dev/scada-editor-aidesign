# hmi_export.py
# Выгрузка листа в формате редактора мнемосхем — того проекта, который
# принимает эти файлы дальше.
#
# Почему отдельно от json_export. `PlantGeometry` — дерево: техобъекты,
# внутри устройства, отдельными секциями трубы и связи. Редактор ждёт другое:
# **плоский массив элементов холста**, каждый со своим ключом, типом
# и координатами. Дерево он не разбирает вовсе — файл открывается, и на холсте
# пусто. Здесь те же данные разложены так, как их пишет сам редактор.
#
# Формат сверен с выгрузкой редактора (элементы line, circle, polygon, text,
# group) и с его же кодом импорта (`importElementsFromJson`). Что из этого
# кода следует:
#
#   - массив обязателен. Объект импортёр заворачивает в массив из одного
#     элемента (`Array.isArray(json) ? json : [json]`) — из дерева
#     PlantGeometry получается один элемент без типа, и холст остаётся пуст.
#     Это и была причина первой неудачной передачи;
#   - координаты числами — это пиксели холста, а проценты строкой импортёр
#     умножает на 5000 (`CANVAS_W = CANVAS_H = 5000`). Холст квадратный,
#     а лист — нет: в процентах A0 растянулся бы с 1.41:1 до 1:1. Поэтому
#     выгружаются пункты PDF как есть, 1:1 — A0 (3368x2384) в холст входит;
#   - ключи импортёр раздаёт заново, но `parentKey` и `children` переводит
#     по своей карте старых ключей. Значит ключи должны быть уникальны
#     и ссылки — согласованы; «null» строкой считается отсутствующим;
#   - `states` переносятся как есть, только пустой `id` заменяется новым;
#   - неизвестные поля импортёр сохраняет (`...rest`), поэтому имя устройства
#     и техобъект доезжают до редактора вместе с элементом.
#
# Ключи выводятся из содержимого (uuid5), а не случайные: один и тот же лист
# даёт один и тот же файл, и его можно сравнивать между прогонами.
#
# Что уезжает вместе с элементами. Файл должен нести всё, что конвейер знает
# о листе, — то же, что XML, а не только картинку:
#
#   - у устройства поле `contur_states`: каждое место описания операций, где
#     оно открывается или закрывается, со ссылкой на операцию, состояние
#     и шаг. Раньше было одно состояние-заглушка, и положение клапана на шаге
#     мойки редактор получить не мог. Своим полем, а не штатным
#     `states`: по спецификации импорта в `states` полагается ровно одно
#     состояние с пустым `overrides`, иначе базовые `x/y/w/h` при отрисовке
#     игнорируются — схему бы сдвинуло;
#   - у устройства поля XML целиком: тип, артикул, описание, категория,
#     подтип, всё из Lua (`extra_data`), состояние в выбранной операции;
#   - связность: у трубы номер и имя трубопровода, у устройства — соседи
#     по трубам. Граф собирается из самих элементов, без второго файла;
#   - надписи чертежа (обозначения Eplan, штамп листа) — элементами `text`
#     с полем `drawing`. В разметке они были всегда, в выгрузку не попадали;
#   - чертёж уезжает целиком: отрезки полосы поля листа помечены `frame`,
#     а не выброшены (`CONTUR_HMI_FRAME=0` их уберёт);
#   - элемент `meta` первым в массиве: холст, счётчики, текущая операция,
#     техобъекты, трубопроводы, связи, точки сопряжения и программы операций.
#     Это то, для чего в XML заведены секции — на холсте им места нет.
#
# Настройки через переменные окружения:
#   CONTUR_HMI_SCALE   — множитель координат, если холст редактора мельче листа
#   CONTUR_HMI_GROUPS  — «1»: обвести техобъекты группами (см. _groups)
#   CONTUR_HMI_LINES   — «pipes» (только трубы) или «none» (только устройства):
#                        контрольный лист даёт 5780 элементов, и это может
#                        оказаться много для холста редактора
#   CONTUR_HMI_DEVICES  — чем показывать устройство: «object» (по умолчанию,
#                        группа с его символом и данными), «circle» (кружок
#                        поверх чертежа, как было) или «none»
#   CONTUR_HMI_SYMBOLS  — откуда брать символ цельного объекта: «library»
#                        (по умолчанию, готовая фигура библиотеки редактора
#                        из hmi_symbols.json) или «drawing» (красные отрезки
#                        с чертежа, как было раньше)
#   CONTUR_HMI_SYMBOL_CELLS — размер устройства в клетках холста (по умолчанию
#                        шесть — столько занимает символ библиотеки; от него
#                        масштаб всего листа)
#   CONTUR_HMI_SYMBOL_MAP — поправки к карте «обозначение → символ»,
#                        например «M=valve,GS=»
#   CONTUR_HMI_TANKS    — рисовать ли техобъекты-ёмкости символом библиотеки:
#                        «auto» (по умолчанию — только когда чертёж
#                        не выгружается, иначе аппарат нарисован дважды),
#                        «1» всегда, «0» никогда
#   CONTUR_HMI_TANK_NAMES — по каким словам в имени техобъект считается
#                        ёмкостью (по умолчанию TANK, БАК, COAG, CIP и т. п.)
#   CONTUR_HMI_CONTOURS — «1»: выгружать рамки и имена техобъектов
#                        (по умолчанию выключено — это разметка конвейера)
#   CONTUR_HMI_LABELS   — «1»: выгружать подписи устройств из разметки
#   CONTUR_HMI_TEXTS    — «0»: не выгружать надписи чертежа
#   CONTUR_HMI_FRAME    — «0»: не выгружать рамку и разлиновку штампа листа
#   CONTUR_HMI_GRID     — «0»: не сажать объекты на сетку холста
#   CONTUR_HMI_META     — «0»: не добавлять элемент meta
#   CONTUR_HMI_JUNCTIONS — «0»: не перечислять точки сопряжения в meta
#                        (на контрольном листе их 4713)
#   CONTUR_HMI_STATES   — «0»: не выгружать состояния устройств
#   CONTUR_HMI_STATE_COLORS — «0»: состояния без overrides, оформление
#                        оставить на усмотрение редактора
#
# Что именно и как рисуется — в PROJECT.md, §6.2: правила отрисовки
# описаны так, чтобы редактор получил ту же картинку.
import console_utils  # noqa: F401  (настройка кодировки вывода)
import json
import math
import os
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

import config
import hmi_symbols
from data_models import Contour, DeviceMatch
from export_scene import (
    ExportScene, build_scene, controller_nodes, device_operation_state,
    device_states, object_details, operation_program, operation_summary,
    project_signals, state_text,
)
from svg_geometry import (
    REFERENCE_DEVICE_SIZE, DeviceCenter, LineSegment, SheetText,
    build_connection_graph,
)

# Пространство имён для uuid5: свой, чтобы ключи не совпали ни с чем чужим
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://contur.local/hmi-export")

# Размер символа, если геометрия устройства не нашлась и лист ничего
# не сказал о своём обычном символе (пункты PDF). Eplan рисует символы
# фиксированного размера: около 31 пт на A0
FALLBACK_DEVICE_SIZE = REFERENCE_DEVICE_SIZE

# Во сколько раз символ вправе отличаться от обычного для этого листа.
# Габарит берётся из кластера красных линий, а кластер прихватывает
# и соседние отводы: на контрольном листе у 105 устройств из 233 высота
# выходила до 482 пт вместо тридцати, и в редакторе такой «датчик»
# накрывал бы пол-схемы
MIN_DEVICE_RATIO, MAX_DEVICE_RATIO = 0.5, 1.5

# Мир холста редактора и его сетка (спецификация импорта, §0).
# Шаг сетки зашит в редакторе и не настраивается; минимальный осмысленный
# объект — две клетки
CANVAS_SIZE = 5000.0
GRID = 20.0
MIN_OBJECT_SIZE = 2 * GRID

STATE_NAME = "Нормальное"

# Версия состава файла. Меняется, когда в элементах появляются новые поля:
# редактору надо понимать, чего ждать. 1.0 — только геометрия,
# 1.1 — состояния устройств, надписи чертежа, связность и элемент meta
FORMAT_VERSION = "1.1"

# Элемент с данными о листе целиком. Тип не из тех, что рисует холст: это
# не фигура, а место для того, для чего в XML заведены секции (трубы, связи,
# точки сопряжения, операции). Помечен ещё и полем contur_meta — чтобы
# отобрать его одной проверкой, не разбирая тип
META_TYPE = "meta"

# Надпись SVG привязана к базовой линии, а элемент text редактора — к левому
# верхнему углу строки (INTEGRATION.md, §2). Разница — высота заглавной
# части шрифта, обычная доля от кегля
TEXT_BASELINE_TO_TOP = 0.8

# Поля элемента холста, которые нельзя перебивать данными из Lua: устройство
# в `extra_data` может принести что угодно, вплоть до ключа «x»
RESERVED_FIELDS = frozenset((
    "id", "key", "type", "composition", "x", "y", "w", "h", "parentId",
    "parentKey", "children", "label", "bg", "scripts", "bindings",
    "properties", "states", "borderColor", "radius", "text", "font_size",
))

# Как подпись стоит относительно устройства и имя — относительно центра
# контура. Числа те же, что в окне (scene_painter.LABEL_OFFSET и draw_contours).
# При включённой сетке сдвиг берётся целыми клетками: устройство сидит в узле,
# и сдвиг в 12 единиц привязка съела бы — подпись легла бы на сам кружок
DEVICE_LABEL_OFFSET = (8.0, -10.0)
CONTOUR_LABEL_OFFSET = (-30.0, -15.0)
DEVICE_LABEL_CELLS = (1, -1)
CONTOUR_LABEL_CELLS = (-2, -1)

# Кегли подписей — сразу в единицах холста, а не в пунктах листа.
# У нас в окне Arial 8 у устройства и Arial 10 у контура, но это расчёт
# на печатный лист: на экране при зуме «весь лист» (0.2-0.35) восемь пунктов
# превращаются в 2-3 пикселя и не читаются вовсе. Их спецификация импорта
# (§4) просит 12 и 16, и меньше 12 не советует никому
DEVICE_LABEL_SIZE = 12.0
CONTOUR_LABEL_SIZE = 16.0
MIN_FONT_SIZE = 12.0

# Оценка габарита строки по кеглю (спецификация импорта, §5.4).
# Габарит нужен: по нему считаются рамка группы, выделение прямоугольником
# и «вписать в экран»
TEXT_WIDTH_PER_CHAR = 0.55
TEXT_HEIGHT_RATIO = 1.2

# Цвет линии для редактора: он рисует по borderColor. Смысл линии — труба
# это или контур устройства — уезжает своим полем contur_color: в сцене
# редактора `color` означает заливку фигуры, и классифицировать им нельзя (§6)
LINE_COLORS = {"red": "#e53935", "blue": "#1e88e5"}

# Толщина линии ступенями: до какой толщины какая ступень.
# Тоньше половины пикселя импорт редактора всё равно поднимает сам
STROKE_STEPS = ((1.0, 1.0), (2.0, 2.0), (float("inf"), 3.0))

# Все устройства — круги. Был режим CONTUR_HMI_SHAPES=class, рисовавший
# клапаны и насосы многоугольниками, и он оказался прямой причиной жалобы
# «часть кругов приехала ромбами»: многоугольник уходил без списка
# точек, а редактор в этом случае строит правильный многоугольник по своему
# `sides` в габарите w x h (спецификация импорта, §5.6). Различать клапан
# и датчик можно по полям device_type и lua_name, которые едут вместе
# с элементом, — режим ничего не добавлял и был убран. Вернуть его можно,
# когда понадобится: система координат для points теперь описана
DEVICE_SHAPE = "circle"

# Чем показывать устройство.
#   object  — цельный объект: группа с его же символом с чертежа внутри
#             и всеми данными на самой группе. Устройство можно выделить
#             и подвинуть целиком, а не выбирать из россыпи отрезков
#   circle  — кружок-маркер поверх чертежа, как было раньше
#   none    — устройств на холсте нет вовсе (данные остаются в meta)
DEVICE_MODES = ("object", "circle", "none")

# Какие линии чертежа выгружать.
#   all   — все: и трубы (синие), и контуры самих устройств (красные)
#   pipes — только трубы: контур устройства и так нарисован кружком,
#           а элементов на контрольном листе становится вдвое меньше
#   none  — ни одной: остаются только устройства
LINE_MODES = ("all", "pipes", "none")

# Откуда берётся символ цельного объекта.
#   library — готовая фигура из библиотеки редактора: клапан, ёмкость,
#             кружок датчика с тегом внутри. Схема получается такой,
#             какой её рисует сам редактор, а не перерисовкой чертежа Eplan
#   drawing — красные отрезки с чертежа, как было раньше. Остаётся для
#             устройств, которым символа в каталоге нет, и на случай,
#             когда важно видеть именно чертёж
SYMBOL_MODES = ("library", "drawing")

# Рисовать ли техобъект-ёмкость символом библиотеки.
#   auto — только когда чертёж не выгружается. С чертежом аппарат уже
#          нарисован — на листе mozzarella у танка LA_TANK1 виден и корпус,
#          и уровень жидкости, — и вторая ёмкость поверх него только мешает
#   1     — всегда
#   0     — никогда
TANK_MODES = ("auto", "1", "0")

# Толщина линии готовой фигуры, если каталог своей не задал: в сцене
# редактора стоит 2. Цвет фигура тоже несёт свой, чёрный, — перекрасить её
# в цвет типа устройства значило бы отдать уже не библиотечный символ. Цвет типа
# остаётся в данных элемента (device_type), где он ничего не портит
SYMBOL_STROKE_WIDTH = 2.0


def _env_scale() -> Optional[float]:
    # Пусто — масштаб считается по самому листу (_sheet_scale)
    raw = os.environ.get("CONTUR_HMI_SCALE", "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def _env_groups() -> bool:
    return os.environ.get("CONTUR_HMI_GROUPS", "").strip().lower() in ("1", "true", "да")


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "да")


def _env_lines() -> str:
    value = os.environ.get("CONTUR_HMI_LINES", "").strip().lower()
    return value if value in LINE_MODES else "all"


def _env_devices() -> str:
    value = os.environ.get("CONTUR_HMI_DEVICES", "").strip().lower()
    return value if value in DEVICE_MODES else "object"


def _env_tanks() -> str:
    value = os.environ.get("CONTUR_HMI_TANKS", "").strip().lower()
    if value in ("да", "true"):
        return "1"
    if value in ("нет", "false"):
        return "0"
    return value if value in TANK_MODES else "auto"


def _env_symbols() -> str:
    value = os.environ.get("CONTUR_HMI_SYMBOLS", "").strip().lower()
    return value if value in SYMBOL_MODES else "library"


def _env_symbol_cells() -> float:
    raw = os.environ.get("CONTUR_HMI_SYMBOL_CELLS", "").strip()
    if not raw:
        return hmi_symbols.DEFAULT_SYMBOL_CELLS
    try:
        cells = float(raw.replace(",", "."))
    except ValueError:
        return hmi_symbols.DEFAULT_SYMBOL_CELLS
    return max(hmi_symbols.MIN_SYMBOL_CELLS, cells)


class HMIExporter:
    """Собирает плоский массив элементов холста из размеченного листа."""

    def __init__(self, pdf_size: Optional[Tuple[float, float]] = None,
                 scale: Optional[float] = None, groups: Optional[bool] = None,
                 lines: Optional[str] = None,
                 devices: Optional[str] = None,
                 contour_frames: Optional[bool] = None,
                 labels: Optional[bool] = None,
                 texts: Optional[bool] = None,
                 frame: Optional[bool] = None,
                 grid: Optional[bool] = None,
                 meta: Optional[bool] = None,
                 junctions: Optional[bool] = None,
                 snap_to_geometry: bool = True,
                 current_operation_id: Optional[str] = None,
                 states: Optional[bool] = None,
                 state_colors: Optional[bool] = None,
                 symbols: Optional[str] = None,
                 symbol_cells: Optional[float] = None,
                 tanks: Optional[str] = None):
        self.pdf_size = pdf_size
        # None — подобрать по листу в build(), см. _sheet_scale
        self.scale = _env_scale() if scale is None else scale
        self.groups = _env_groups() if groups is None else groups
        self.lines = _env_lines() if lines is None else lines
        self.devices = _env_devices() if devices is None else devices
        # Рамки техобъектов и подписи разметки по умолчанию не выгружаются:
        # редактору нужен чертёж и данные, а разметка ложится поверх него
        # своим слоем. Обозначения Eplan и так есть в самом чертеже
        self.contour_frames = (_env_flag("CONTUR_HMI_CONTOURS", False)
                               if contour_frames is None else contour_frames)
        self.labels = _env_flag("CONTUR_HMI_LABELS", False) if labels is None else labels
        self.texts = _env_flag("CONTUR_HMI_TEXTS", True) if texts is None else texts
        self.frame = _env_flag("CONTUR_HMI_FRAME", True) if frame is None else frame
        self.grid = _env_flag("CONTUR_HMI_GRID", True) if grid is None else grid
        self.meta = _env_flag("CONTUR_HMI_META", True) if meta is None else meta
        self.junctions = (_env_flag("CONTUR_HMI_JUNCTIONS", True)
                          if junctions is None else junctions)
        self.states = _env_flag("CONTUR_HMI_STATES", True) if states is None else states
        self.state_colors = (_env_flag("CONTUR_HMI_STATE_COLORS", True)
                             if state_colors is None else state_colors)
        if self.lines not in LINE_MODES:
            raise ValueError(f"неизвестный отбор линий: {self.lines!r}; "
                             f"допустимы {', '.join(LINE_MODES)}")
        if self.devices not in DEVICE_MODES:
            raise ValueError(f"неизвестный вид устройства: {self.devices!r}; "
                             f"допустимы {', '.join(DEVICE_MODES)}")
        self.symbols = _env_symbols() if symbols is None else symbols
        if self.symbols not in SYMBOL_MODES:
            raise ValueError(f"неизвестный источник символов: {self.symbols!r}; "
                             f"допустимы {', '.join(SYMBOL_MODES)}")
        self.symbol_cells = _env_symbol_cells() if symbol_cells is None else symbol_cells
        self.tanks = _env_tanks() if tanks is None else tanks
        if self.tanks not in TANK_MODES:
            raise ValueError(f"неизвестный вид ёмкостей: {self.tanks!r}; "
                             f"допустимы {', '.join(TANK_MODES)}")
        self.snap_to_geometry = snap_to_geometry
        self.current_operation_id = current_operation_id
        self.scene: Optional[ExportScene] = None
        # Сдвиг листа в начало координат, уже в единицах холста
        self._origin: Tuple[float, float] = (0.0, 0.0)
        self._seed = ""
        self._group_origins: Dict[str, Tuple[float, float]] = {}
        self._group_of: Dict[str, str] = {}
        # Связность и принадлежность сегментов трубам: считаются один раз
        # в build(), а нужны и линиям, и устройствам
        self._graph: Dict[str, Any] = {}
        self._pipeline_of: Dict[int, Tuple[int, str]] = {}
        # Операции, встреченные в состояниях устройств листа
        self._operations: Set[str] = set()

    # ---------------------------------------------------------------- служебное

    def _key(self, *parts: Any) -> str:
        # Ключ выводится из содержимого: одинаковый лист — одинаковый файл
        return str(uuid.uuid5(NAMESPACE, "|".join([self._seed, *map(str, parts)])))

    def _n(self, value: float) -> float:
        """Длина в единицах холста: пункты листа, умноженные на масштаб."""
        return round(value * self.scale, 3)

    def _x(self, value: float) -> float:
        """Координата X: масштаб плюс сдвиг листа в начало координат."""
        return round(value * self.scale - self._origin[0], 3)

    def _y(self, value: float) -> float:
        return round(value * self.scale - self._origin[1], 3)

    def _content_origin(self) -> Tuple[float, float]:
        """Куда сдвинуть лист, чтобы содержимое начиналось в (0, 0).

        Начальная камера редактора стоит в начале координат при зуме 1,
        и схема, начинающаяся с x = 1740, откроется пустым экраном
        (спецификация импорта, §2). Сдвиг сам кратен шагу сетки —
        иначе на неё не сядет ничего.
        """
        xs: List[float] = []
        ys: List[float] = []
        for segment in self.scene.drawing_segments:
            xs.extend((segment.x1, segment.x2))
            ys.extend((segment.y1, segment.y2))
        for contour in self.scene.contours:
            xs.extend((contour.bounds[0], contour.bounds[2]))
            ys.extend((contour.bounds[1], contour.bounds[3]))
        # Подписи стоят со сдвигом от своего устройства и выходят за него
        # вверх: без них схема начиналась бы с отрицательной координаты
        device_offset = self._label_offset(DEVICE_LABEL_OFFSET,
                                           self._device_label_cells())
        contour_offset = self._label_offset(CONTOUR_LABEL_OFFSET, CONTOUR_LABEL_CELLS)
        for match in self.scene.matches:
            xs.append(match.coordinates[0] + device_offset[0])
            ys.append(match.coordinates[1] + device_offset[1])
        for contour in self.scene.contours:
            xs.append(contour.center[0] + contour_offset[0])
            ys.append(contour.center[1] + contour_offset[1])

        if not xs or not ys:
            return (0.0, 0.0)

        # Половина клетки в запас: привязка к сетке двигает объект в любую
        # сторону, и без запаса самый верхний уехал бы за край холста
        return (math.floor((min(xs) * self.scale - GRID / 2) / GRID) * GRID,
                math.floor((min(ys) * self.scale - GRID / 2) / GRID) * GRID)

    def _device_label_cells(self) -> Tuple[int, int]:
        """На сколько клеток отодвинуть подпись от устройства.

        Пока устройство было кружком в две клетки, хватало одной: подпись
        вставала рядом. Готовая фигура занимает шесть, и подпись со сдвигом
        в клетку легла бы прямо на неё — отодвигаем на половину фигуры
        и ещё клетку сверху.
        """
        if self.symbols == "library" and self.devices == "object":
            return (0, -(math.ceil(self.symbol_cells / 2) + 1))
        return DEVICE_LABEL_CELLS

    def _label_offset(self, offset: Tuple[float, float],
                      cells: Tuple[int, int]) -> Tuple[float, float]:
        # В единицах листа: после масштаба выйдет ровно целое число клеток
        if not self.grid:
            return offset
        return (cells[0] * GRID / self.scale, cells[1] * GRID / self.scale)

    def _stroke_width(self, width: float) -> float:
        """Толщина линии ступенями 1 / 2 / 3.

        Из PDF приходит медиана 0.71 при минимуме 0.057: при зуме «весь лист»
        это уходит в 0.2 пикселя, и чертёж бледнеет до нечитаемости. Импорт
        поднимает всё ниже 0.5, но ступени задаются на стороне файла (§4) —
        так чертёж контрастнее, а файл лучше сжимается.
        """
        for limit, step in STROKE_STEPS:
            if width <= limit:
                return step
        return STROKE_STEPS[-1][1]

    def _snap(self, value: float) -> float:
        """Ближайший узел сетки холста.

        Редактор привязывает к сетке только то, что двигает человек, и делает
        это по-разному: прямоугольник и текст прыгают на узел при первом же
        касании, а круг и отрезок едут на целое число клеток, сохраняя своё
        смещение навсегда (спецификация импорта, §3). Значит выровнять
        обязан экспортёр — иначе схема разъезжается по мере работы с ней.
        """
        return round(value / GRID) * GRID if self.grid else round(value, 3)

    def _snap_size(self, value: float) -> float:
        # Размер объекта — не меньше клетки, иначе редактор поднимет сам
        return max(GRID, round(value / GRID) * GRID) if self.grid else round(value, 3)

    def _ceil_size(self, value: float) -> float:
        # Габарит строки округляется вверх: обрезанная подпись хуже широкой
        return max(GRID, math.ceil(value / GRID) * GRID) if self.grid else round(value, 3)

    def _device_size(self) -> float:
        """Сколько единиц холста занимает обычное устройство листа.

        Раньше это были две клетки — минимальный осмысленный объект
        (спецификация импорта, §2 и §4). Теперь на место устройства
        встаёт готовая фигура библиотеки, а она нарисована
        на шести клетках, и меньший размер пришлось бы делить: половина
        клетки при трёх, треть при двух.
        """
        if self.symbols == "library" and self.devices == "object":
            return self.symbol_cells * GRID
        return MIN_OBJECT_SIZE

    def _sheet_scale(self) -> float:
        """Во сколько раз увеличить лист, чтобы устройство заняло свой размер.

        Их холст размечен сеткой 20, символ устройства на листе около
        31 пункта. Под кружок в две клетки лист растягивался в 1.28 раза,
        под фигуру библиотеки в шесть клеток — примерно в 3.6.

        Множитель один на весь лист. Про холст 5000x5000: пока устройство
        было кружком, лист в него вписывался и множитель на этом
        ограничивался. Готовую фигуру так ужимать нельзя — ужмётся и она,
        а приехать она должна такой, какой её нарисовали. Предел здесь
        и не предел вовсе: их собственная сцена MOZARELLA_01 занимает
        6360x5820, то есть за 5000 они выходят сами.
        """
        usual = (self.scene.geometry_scale * REFERENCE_DEVICE_SIZE
                 if self.scene else FALLBACK_DEVICE_SIZE)
        scale = self._device_size() / usual if usual > 0 else 1.0

        width, height = (self.scene.width or 0), (self.scene.height or 0)
        if self._device_size() <= MIN_OBJECT_SIZE:
            for size in (width, height):
                if size > 0:
                    scale = min(scale, CANVAS_SIZE / size)

        return scale if scale > 0 else 1.0

    def _element(self, kind: str, key: str, x: float, y: float, w: float, h: float,
                 label: str = "Element", parent_key: Optional[str] = None,
                 placed: bool = False, **extra: Any) -> Dict[str, Any]:
        # Координаты ребёнка группы отсчитываются от её угла, то есть это
        # длины, а не положения на холсте: сдвиг листа в них уже учтён
        # самой группой, и вычитать его второй раз нельзя
        local = parent_key in self._group_origins

        if placed:
            # Значения уже в единицах холста — так приходит чертёж, у него
            # своя мера привязки (см. _line)
            px, py, pw, ph = round(x, 3), round(y, 3), round(w, 3), round(h, 3)
        else:
            px = self._n(x) if local else self._x(x)
            py = self._n(y) if local else self._y(y)
            px, py = self._snap(px), self._snap(py)
            pw, ph = self._snap_size(self._n(w)), self._snap_size(self._n(h))

        element = {
            "id": None,
            "key": key,
            "type": kind,
            "x": px,
            "y": py,
            "w": pw,
            "h": ph,
            "parentId": None,
            "parentKey": parent_key or "undefined",
            "children": [],
            "label": label,
            "bg": "transparent",
            "scripts": [],
            "bindings": [],
            "properties": [],
        }
        element.update(extra)
        element["states"] = [{
            "id": self._key(key, "state"),
            "name": STATE_NAME,
            "overrides": {},
            "isDefault": True,
        }]
        return element

    # ---------------------------------------------------------------- элементы

    def _line(self, segment: LineSegment,
              parent_key: Optional[str] = None) -> Dict[str, Any]:
        # Линия: у редактора помимо концов есть центр и габарит.
        # Ключ по обоим номерам: у кусков одной кривой source_id общий,
        # а номер в наборе чертежа свой.
        # Символ устройства уходит детьми своей группы — тогда координаты
        # отсчитываются от её угла, как у любого ребёнка
        key = self._key("line", segment.source_id, segment.id)
        origin = self._group_origins.get(parent_key) if parent_key else None
        if origin:
            x1, y1 = self._n(segment.x1 - origin[0]), self._n(segment.y1 - origin[1])
            x2, y2 = self._n(segment.x2 - origin[0]), self._n(segment.y2 - origin[1])
        else:
            x1, y1 = self._x(segment.x1), self._y(segment.y1)
            x2, y2 = self._x(segment.x2), self._y(segment.y2)
        x1, y1, x2, y2 = self._snap_segment(x1, y1, x2, y2)

        element = self._element(
            "line", key, placed=True, parent_key=parent_key,
            x=(x1 + x2) / 2, y=(y1 + y2) / 2,
            w=abs(x2 - x1), h=abs(y2 - y1),
            x1=x1, y1=y1, x2=x2, y2=y2,
            borderColor=LINE_COLORS.get(segment.color, "#1e88e5"),
            contur_color=segment.color,
            stroke_width=self._stroke_width(segment.stroke_width))

        # Номер сегмента есть только у того, что видел разбор геометрии:
        # по нему связаны трубы и точки сопряжения. У рамки листа его нет
        if segment.source_id:
            element["line_id"] = segment.source_id

        # Красная линия — контур самого устройства, а не труба
        if segment.device_name:
            element["device_name"] = segment.device_name

        # Рамка чертежа и разлиновка штампа: не трубопровод и не устройство
        if segment.frame:
            element["frame"] = True

        # Синяя — часть трубопровода. Номер трубы делает граф связей
        # читаемым по самим элементам: раньше трубы были только
        # в XML отдельной секцией, а на холсте лежали россыпью отрезков
        pipeline = self._pipeline_of.get(segment.source_id)
        if pipeline:
            element["pipeline_id"], element["pipeline_name"] = pipeline

        return element

    def _snap_segment(self, x1: float, y1: float, x2: float,
                      y2: float) -> Tuple[float, float, float, float]:
        """Концы ортогонального отрезка — на узлы сетки, если это недалеко.

        Требовать кратности от каждого отрезка перерисованного PDF нельзя:
        диагонали и разложенные кривые заметно деформируются. Их
        спецификация импорта (§3.1) предлагает разделение — ортогональные
        сегменты садятся на сетку, если это смещает конец не больше чем
        на полклетки, остальное остаётся как есть.

        Ещё одно условие своё: отрезок не должен схлопнуться. У отрезка
        короче клетки обе ручки садятся в один узел, и он исчезает с холста
        вовсе — это одна из причин «линии местами обрываются».
        """
        if not self.grid:
            return x1, y1, x2, y2
        if abs(x2 - x1) >= 1.0 and abs(y2 - y1) >= 1.0:
            return x1, y1, x2, y2

        ends = (x1, y1, x2, y2)
        snapped = [self._snap(v) for v in ends]
        if any(abs(v - s) > GRID / 2 for v, s in zip(ends, snapped, strict=True)):
            return ends
        if math.hypot(snapped[2] - snapped[0], snapped[3] - snapped[1]) < GRID:
            return ends
        return snapped[0], snapped[1], snapped[2], snapped[3]

    def _device_payload(self, match: DeviceMatch, key: str) -> Dict[str, Any]:
        """Всё, что известно об устройстве, — полями элемента.

        Одно и то же и у кружка, и у цельного объекта: вид фигуры к данным
        отношения не имеет.
        """
        payload: Dict[str, Any] = {
            # Признак устройства: по нему оно отбирается независимо от того,
            # цельным объектом оно приехало или кружком
            "contur_device": True,
            "lua_name": match.lua_name,
            "pdf_name": match.pdf_name,
            "device_type": match.device_type,
            "tech_object": match.tech_object,
            "confidence": round(match.confidence, 2),
        }

        # Поля XML целиком: до сих пор из них доезжали только описание
        # и артикул, а категория, подтип и всё, что пришло из Lua,
        # оставались только в формате PlantGeometry
        for field, value in (("descr", match.descr), ("article", match.article),
                             ("category", match.category), ("subtype", match.subtype),
                             ("dtype", match.dtype)):
            if value or value == 0:
                payload[field] = value

        for field, value in (match.extra_data or {}).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            if field in RESERVED_FIELDS or field in payload:
                continue
            payload[field] = value if isinstance(value, (str, int, float, bool)) else str(value)

        payload.update(self._operation_state(match))
        payload.update(self._connections(match))

        # Теги: каналы ввода-вывода с адресом в контроллере и параметры
        # устройства. Ими мнемосхема привязывает картинку к живому сигналу —
        # без них файл описывает, что нарисовано, но не к чему это подключено
        if match.tags:
            payload["contur_tags"] = match.tags

        if self.states:
            states = self._device_states(match, key,
                                         config.device_color(match.device_type))
            if states:
                payload["contur_states"] = states

        return payload

    def _device_key(self, match: DeviceMatch) -> str:
        return self._key("device", match.lua_name or match.pdf_name, match.coordinates)

    def _device_circle(self, match: DeviceMatch, box: Optional[DeviceCenter],
                       payload: Dict[str, Any],
                       parent_key: Optional[str]) -> Dict[str, Any]:
        # Круг задаётся радиусом, и габарит обязан быть квадратом: редактор
        # строит фигуру по w/h, и при w != h круг выходил сплющенным —
        # на листе mozzarella так рисовались 26 устройств из 35.
        # Радиус округляется один раз: габарит считается от него же, иначе
        # w и 2*radius расходятся на последнем знаке, а редактор
        # проверяет равенство (спецификация импорта, §5.2)
        radius = self._n(self._symbol_size(max(box.width, box.height) if box else 0) / 2)
        # Радиус кратен клетке и не меньше её: у редактора ручка ресайза круга
        # привязывает радиус к сетке, минимум — одна клетка (спецификация
        # импорта, §4). Радиус 14 он поднял бы сам, каждый по-своему
        if self.grid:
            radius = max(GRID, self._snap(radius))

        x, y = self._local(*match.coordinates, parent_key)
        color = config.device_color(match.device_type)

        element = self._element(DEVICE_SHAPE, self._device_key(match), x=x, y=y,
                                w=0, h=0,
                                label=match.lua_name or match.pdf_name or "Element",
                                parent_key=parent_key,
                                bg=color, borderColor=color, radius=radius, **payload)
        # Габарит берётся от уже округлённого радиуса, а не считается заново:
        # _element округляет своё, и w расходилось с 2*radius на 0.001
        element["w"] = element["h"] = radius * 2
        return element

    def _operation_state(self, match: DeviceMatch) -> Dict[str, Any]:
        """Положение устройства в выбранной операции — как в XML.

        Операция выбирается в окне, и до сих пор выгрузка для редактора
        её просто не смотрела: считалось, что состояния редактор ведёт сам.
        Ведёт, но по данным выгрузки, а их в файле не было.
        """
        if not self.current_operation_id:
            return {}

        status, details = device_operation_state(self.current_operation_id,
                                                 match.lua_name)
        if status == "not_used":
            status, details = device_operation_state(self.current_operation_id,
                                                     match.pdf_name)

        fields: Dict[str, Any] = {"operation_state": state_text(status)}
        if details:
            if details.get("state_name"):
                fields["operation_state_name"] = details["state_name"]
            if details.get("step_name"):
                fields["operation_step"] = details["step_name"]
            if details.get("step_number", -1) >= 0:
                fields["operation_step_number"] = details["step_number"]
        return fields

    def _connections(self, match: DeviceMatch) -> Dict[str, Any]:
        """С чем устройство соединено трубами.

        Граф связности в XML лежит отдельной секцией, а на холсте связь
        нужна у самого устройства: по ней мнемосхема ведёт среду от клапана
        к клапану. Имена — те же, что в `lua_name` соседей.
        """
        neighbours = self._graph.get("neighbours") or {}
        connected = (match.neighbours
                     or neighbours.get(match.lua_name)
                     or neighbours.get(match.pdf_name))
        return {"connected_devices": list(connected)} if connected else {}

    def _device_states(self, match: DeviceMatch, key: str,
                       color: str) -> List[Dict[str, Any]]:
        """Положение устройства в каждом шаге каждой операции.

        Это и есть то, чего в файле не было: редактор не мог
        показать, открыт клапан на шаге мойки или закрыт. Описание операций
        знает про это всё — надо было донести.

        Уезжает **своим полем `contur_states`**, а не штатным `states`
        редактора. Так велит спецификация импорта (§7): в `states`
        полагается ровно одно состояние с пустым `overrides`, иначе базовые
        `x/y/w/h` элемента при отрисовке игнорируются — то есть восемьдесят
        состояний у клапана сдвинули бы саму схему. Неизвестные
        поля импорт сохраняет без потерь, поэтому данные доезжают целиком,
        а рисуется элемент по-прежнему по своей геометрии.

        `overrides` в этих состояниях — поля, которые состояние меняет.
        Цвет положения общий с окном (config.DEVICE_STATE_COLORS); если
        редактору удобнее решать оформление самому,
        `CONTUR_HMI_STATE_COLORS=0` оставит overrides пустыми, а описание
        состояния — на месте.
        """
        # Досье устройства, если оно закреплено (device_dossier.attach);
        # иначе спрашиваем описание операций сами — выгрузку зовут
        # и в обход окна
        entries = (match.states
                   or device_states(match.lua_name)
                   or device_states(match.pdf_name))
        if not entries:
            return []

        states = []
        for entry in entries:
            self._operations.add(entry["operation_id"])
            status = entry["status"]
            state = {
                "id": self._key(key, "state", entry["operation_id"],
                                entry["state_id"], entry["step_id"], status),
                "name": self._state_name(entry),
                "overrides": self._state_overrides(status, color),
                "isDefault": False,
                "status": status,
                "status_text": state_text(status),
                "operation_id": entry["operation_id"],
                "operation": entry["operation"],
                "operation_object": entry["tech_object"],
                "operation_object_id": entry["tech_object_id"],
                "state_id": entry["state_id"],
                "state": entry["state"],
            }
            if entry["step_id"]:
                state["step_id"] = entry["step_id"]
                state["step"] = entry["step"]
                state["step_number"] = entry["step_number"]
            states.append(state)

        return self._unique_names(states)

    @staticmethod
    def _unique_names(states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Имена состояний собираются из имён операции и техобъекта, а те
        # в описании не уникальны: «Танк / Мойка / шаг 1» есть у каждого
        # из восьми танков. В списке одного устройства такие состояния
        # различались бы только идентификатором — допишем его в имя
        seen: Dict[str, int] = {}
        for state in states:
            seen[state["name"]] = seen.get(state["name"], 0) + 1

        for state in states:
            if seen[state["name"]] > 1 and state.get("operation_id"):
                state["name"] += f" [{state['operation_id']}]"

        return states

    @staticmethod
    def _state_name(entry: Dict[str, Any]) -> str:
        # Имя состояния человеку: операция, состояние, шаг и что происходит
        parts = [entry["operation"] or entry["operation_id"], entry["state"]]
        if entry["step_id"]:
            step = f"шаг {entry['step_number']}"
            if entry["step"]:
                step += f" {entry['step']}"
            parts.append(step)
        return " / ".join(p for p in parts if p) + f" — {state_text(entry['status'])}"

    def _state_overrides(self, status: str, color: str) -> Dict[str, Any]:
        if not self.state_colors:
            return {}
        painted = config.DEVICE_STATE_COLORS.get(status)
        if not painted:
            return {}
        # Обводка остаётся цветом типа устройства: по ней клапан видно
        # и в состоянии, а заливка показывает положение
        return {"bg": painted, "borderColor": color}

    def _device_object(self, match: DeviceMatch, box: Optional[DeviceCenter],
                       payload: Dict[str, Any],
                       parent_key: Optional[str] = None,
                       symbol: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Устройство одной фигурой: группа с его символом внутри.

        Кружок-маркер поверх чертежа редактору не нужен, а нужен
        сам объект: чтобы устройство выделялось и двигалось целиком и несло
        на себе всё, что о нём известно. Символ — те же красные линии
        с чертежа, только теперь они дети своей группы, а не россыпь
        верхнеуровневых отрезков.

        У группы обязателен прямоугольник первым ребёнком (спецификация
        импорта, §5.5): сама группа ничего не рисует, а её габарит без него
        схлопывается при первом же перетаскивании.
        """
        key = self._device_key(match)
        color = config.device_color(match.device_type)

        side = self._symbol_size(max(box.width, box.height) if box else 0)
        width = height = side
        if symbol is not None:
            # У готовой фигуры размер свой, взятый из каталога. Измеренный
            # по чертежу габарит гуляет от половины обычного символа
            # до полутора, и фигура вписывалась бы в него с делением
            # клетки — то есть съезжала бы с сетки, каждая по-своему.
            # Множитель один на весь каталог: «бабочка» 80x40 остаётся
            # вдвое ниже клапана, как её и рисуют
            fit = hmi_symbols.symbol_scale(self.symbol_cells)
            width = symbol.w * fit / self.scale
            height = symbol.h * fit / self.scale
        left, top = (match.coordinates[0] - width / 2,
                     match.coordinates[1] - height / 2)
        origin = (left, top)
        left, top = self._local(left, top, parent_key)

        group = self._element(
            "group", key, x=left, y=top, w=width, h=height, parent_key=parent_key,
            label=match.lua_name or match.pdf_name or "Element",
            borderColor=color, **payload)
        group["composition"] = True
        # Начало группы в единицах листа: от него дети считают свои координаты
        self._group_origins[key] = origin

        if symbol is not None:
            # Имя фигуры — ради него всё и затевалось: увидев его, редактор
            # вправе выбросить детей группы и поставить свой готовый элемент
            group["contur_symbol"] = symbol.name
            group["contur_symbol_size"] = [symbol.w, symbol.h]
            group["contur_symbol_origin"] = symbol.origin
            if symbol.title:
                # Их же подпись фигуры: по ней видно, что подставлено,
                # не сверяясь с каталогом
                group["contur_symbol_title"] = symbol.title

        frame = self._element(
            "rectangle", self._key("device-frame", key), x=0, y=0, w=0, h=0,
            label="", parent_key=key,
            # Под готовой фигурой рамка невидима: картинку рисует символ,
            # а рамка только держит габарит группы (спецификация
            # импорта, §5.5). Своим символом с чертежа устройство приезжает
            # без обводки вовсе, и цветная рамка была там единственным
            # признаком типа
            strokeColor="transparent" if symbol is not None else color,
            strokeWidth=1.0,
            contur_device_frame=True, lua_name=match.lua_name)
        # Габарит рамки — габарит группы: она его и держит
        frame["w"], frame["h"] = group["w"], group["h"]
        group["children"] = [frame["key"]]

        return [group, frame]

    # ------------------------------------------------- готовые символы

    def _device_symbol(self, match: DeviceMatch,
                       box: Optional[DeviceCenter]) -> Optional[Any]:
        """Готовая фигура библиотеки для этого устройства.

        None — фигуры для такого обозначения в каталоге нет, устройство
        поедет как раньше: своим символом с чертежа.
        """
        if self.symbols != "library" or self.devices != "object":
            return None
        # Лежачий клапан или стоячий, видно по чертежу: кластер красных
        # линий вытянут вдоль трубы. Порог в четверть — чтобы почти
        # квадратный кластер не бросало между двумя видами
        vertical = bool(box and box.height > box.width * 1.25)
        # Описание нужно, чтобы отличить мешалку от насоса: обозначение
        # в Eplan общее (M), а рисуются они по-разному
        return hmi_symbols.symbol_for_device(match.device_type, match.lua_name,
                                             descr=match.descr,
                                             vertical=vertical)

    def _symbol_parts(self, symbol: Any, parent: Dict[str, Any],
                      tag: str = "") -> List[Dict[str, Any]]:
        """Фигура детьми группы: по элементу на примитив каталога.

        Фигура вписывается в габарит группы с сохранением пропорций
        и ставится по центру: ёмкость 160x240 в квадрате превратилась бы
        в куб, а «бабочка» ручного клапана 80x40 — в ромб.
        """
        width, height, shapes = symbol.fit(parent["w"], parent["h"])
        dx, dy = (parent["w"] - width) / 2, (parent["h"] - height) / 2

        parts: List[Dict[str, Any]] = []
        for index, shape in enumerate(shapes):
            key = self._key("symbol", parent["key"], symbol.name, index)
            element = self._shape(shape, key, parent["key"], dx, dy, tag)
            if element is not None:
                parts.append(element)
        return parts

    def _snap_shape(self, shape: Dict[str, Any]) -> Dict[str, Any]:
        """Примитив по узлам сетки — для фигур, растянутых по чужому габариту.

        Символ устройства так не выравнивают: он мелкий, и сдвиг на полклетки
        его деформирует. А ёмкость растягивается по границам техобъекта —
        сотни единиц, и десяток туда-сюда на ней не виден.
        """
        if not self.grid:
            return shape
        # Ось, вдоль которой деталь мельче клетки, не выравнивается вовсе:
        # обе её стороны сели бы в один узел и деталь схлопнулась. Так
        # у ёмкости пропадали все четыре патрубка: корпус растянут
        # на тысячи единиц, а патрубок остаётся своей ширины — клетка
        # в натуральную величину фигуры и полклетки при половинной
        minx, miny, maxx, maxy = hmi_symbols.shape_bounds(shape)
        wide, tall = (maxx - minx) >= GRID, (maxy - miny) >= GRID
        fx = self._snap if wide else (lambda value: round(value, 3))
        fy = self._snap if tall else (lambda value: round(value, 3))
        item = hmi_symbols.transform_shape(shape, fx, fy, 1.0)
        if item.get("type") == "circle" and item["radius"] >= GRID:
            item["radius"] = self._snap(item["radius"])
        return item

    def _shape(self, shape: Dict[str, Any], key: str, parent_key: str,
               dx: float, dy: float, tag: str = "",
               snap: bool = False) -> Optional[Dict[str, Any]]:
        """Примитив каталога — элементом холста.

        Цвет кладётся сразу двумя именами. Их нормализатор переводит
        `borderColor` в `strokeColor` только у `line` и `circle` (их §6),
        а в символе есть ещё и многоугольники: у них уцелеет только
        родное имя. Два имени с одним значением работают в обоих случаях.
        """
        if snap:
            shape = self._snap_shape(shape)
        kind = shape.get("type")
        color = shape.get("strokeColor") or "#000000"
        style: Dict[str, Any] = {
            "strokeColor": color,
            "borderColor": color,
            "stroke_width": shape.get("strokeWidth") or SYMBOL_STROKE_WIDTH,
            "bg": shape.get("bg", "transparent"),
            "contur_symbol_part": True,
        }
        if shape.get("strokeDasharray"):
            style["strokeDasharray"] = shape["strokeDasharray"]

        if kind == "line":
            x1, y1 = shape["x1"] + dx, shape["y1"] + dy
            x2, y2 = shape["x2"] + dx, shape["y2"] + dy
            return self._element("line", key, placed=True, parent_key=parent_key,
                                 label="", x=(x1 + x2) / 2, y=(y1 + y2) / 2,
                                 w=abs(x2 - x1), h=abs(y2 - y1),
                                 x1=round(x1, 3), y1=round(y1, 3),
                                 x2=round(x2, 3), y2=round(y2, 3), **style)

        if kind == "circle":
            radius = shape["radius"]
            # Центр, а не угол: их нормализатор вычитает радиус сам,
            # как и у кружка устройства (их §6)
            element = self._element("circle", key, placed=True,
                                    parent_key=parent_key, label="",
                                    x=shape["cx"] + dx, y=shape["cy"] + dy,
                                    w=radius * 2, h=radius * 2,
                                    radius=round(radius, 3), **style)
            text = hmi_symbols.tag_text(shape, tag)
            if text:
                # Обозначение внутри кружка — так они и рисуют датчики.
                # Только в `text`, без `label`: в сцене редактора у такого
                # кружка стоит `"text": "-TE1"` при `"label": "Element"`,
                # то есть подпись читается из `text`, а второе имя
                # задвоило бы её. Кегль каталог хранит свой (в сцене 32);
                # без него берётся радиус — тег из четырёх знаков в круг
                # такого кегля как раз помещается
                element["text"] = text
                element["font_size"] = max(MIN_FONT_SIZE,
                                           round(shape.get("fontSize") or radius, 2))
            return element

        if kind in ("polygon", "curve"):
            values = shape.get("points") or []
            xs, ys = values[0::2], values[1::2]
            if not xs:
                return None
            left, top = min(xs) + dx, min(ys) + dy
            # `points` отсчитываются от x, y самого элемента (их §5.6)
            points = [round(value + (dx - left if index % 2 == 0 else dy - top), 3)
                      for index, value in enumerate(values)]
            element = self._element(kind, key, placed=True, parent_key=parent_key,
                                    label="", x=left, y=top,
                                    w=max(xs) - min(xs), h=max(ys) - min(ys),
                                    points=points, **style)
            if shape.get("sides"):
                element["sides"] = shape["sides"]
            return element

        if kind == "rectangle":
            return self._element("rectangle", key, placed=True,
                                 parent_key=parent_key, label="",
                                 x=shape["x"] + dx, y=shape["y"] + dy,
                                 w=shape.get("w", 0), h=shape.get("h", 0), **style)

        return None

    def _wanted_tanks(self) -> bool:
        """Рисовать ли ёмкости на этом листе.

        Сам по себе символ ёмкости полезен, но с выгруженным чертежом
        аппарат приезжает дважды: на листе mozzarella у LA_TANK1 корпус
        и уровень жидкости нарисованы самим Eplan, и ёмкость библиотеки поверх
        них — лишние линии. Значит по умолчанию она появляется там, где
        чертежа нет вовсе.
        """
        if self.symbols != "library" or self.tanks == "0":
            return False
        return self.tanks == "1" or self.lines == "none"

    def _tank(self, contour: Contour) -> List[Dict[str, Any]]:
        """Техобъект-ёмкость символом библиотеки вместо пунктирной рамки.

        Символ растягивается по границам контура, а не вписывается
        с пропорциями: контур задан чертежом, и вписанная ёмкость 160x240
        оказалась бы посреди своих же устройств. Растянутая читается тем,
        чем она и является, — стенкой аппарата, внутри которой стоит
        оборудование техобъекта.
        """
        symbol = hmi_symbols.symbol_for_tech_object(contour.tech_object, contour.name)
        if symbol is None:
            return []

        minx, miny, maxx, maxy = contour.bounds
        key = self._key("tank", contour.tech_object, contour.bounds)
        group = self._element(
            "group", key, x=minx, y=miny, w=maxx - minx, h=maxy - miny,
            label=contour.name or contour.tech_object,
            tech_object=contour.tech_object,
            contur_tank=True, contur_symbol=symbol.name,
            contur_symbol_size=[symbol.w, symbol.h],
            contur_symbol_origin=symbol.origin)
        group["composition"] = True
        self._group_origins[key] = (minx, miny)

        frame = self._element(
            "rectangle", self._key("tank-frame", contour.tech_object, contour.bounds),
            x=0, y=0, w=0, h=0, label="", parent_key=key,
            strokeColor="transparent", strokeWidth=1.0,
            contur_tank_frame=True, tech_object=contour.tech_object)
        frame["w"], frame["h"] = group["w"], group["h"]
        group["children"] = [frame["key"]]

        # Мелкие детали ёмкости увеличены ровно так же, как символы устройств:
        # патрубок ёмкости и патрубок клапана должны быть одной толщины
        detail = hmi_symbols.symbol_scale(self.symbol_cells)
        parts = [frame]
        for index, shape in enumerate(symbol.stretch(group["w"], group["h"], detail)):
            element = self._shape(shape, self._key("tank-part", key, index), key,
                                  0, 0, snap=True)
            if element is not None:
                group["children"].append(element["key"])
                parts.append(element)

        return [group, *parts]

    def _text(self, key: str, content: str, x: float, y: float,
              color: str, size: float, parent_key: Optional[str] = None,
              **extra: Any) -> Dict[str, Any]:
        """Подпись. Строка лежит и в `text`, и в `label`.

        Какое из полей читает редактор, по его выгрузке не понять: у пустого
        текстового элемента там осталось `label: "Element"` и никакого
        содержимого. Пишем в оба — лишние поля импортёр сохраняет.

        Цвет — в `borderColor`, как у линий. Поле `color` намеренно только
        у линий чертежа, и означает оно не оттенок, а смысл: «red» — контур
        устройства, «blue» — труба.
        """
        element = self._element("text", key, x=x, y=y, w=0, h=0,
                                label=content, text=content, parent_key=parent_key,
                                borderColor=color, **extra)
        # Кегль и габарит — уже в единицах холста, масштабировать их нечем:
        # строка должна читаться на экране, а не повторять печатный лист
        element["font_size"] = round(size, 2)
        element["w"] = self._ceil_size(len(content) * size * TEXT_WIDTH_PER_CHAR)
        element["h"] = self._ceil_size(size * TEXT_HEIGHT_RATIO)
        return element

    def _contour(self, contour: Contour) -> List[Dict[str, Any]]:
        """Рамка техобъекта прямоугольником плюс его имя.

        Раньше собиралась из четырёх линий: тип `rect` в присланных образцах
        не встречался, и казалось, что его нет. Их спецификация импорта
        (§5.3) описывает `rectangle` прямо — одна фигура вместо четырёх,
        её можно выделить и подвинуть целиком, а на контрольном листе это
        33 элемента вместо 132.

        Цвет обводки идёт полем `strokeColor`: `borderColor` их нормализатор
        переводит только у линии, круга и текста (§6), у прямоугольника
        он остался бы неузнанным.
        """
        minx, miny, maxx, maxy = contour.bounds
        color = config.tech_object_color(contour.tech_object or contour.name)

        elements = [self._element(
            "rectangle", self._key("contour", contour.name, contour.bounds),
            x=minx, y=miny, w=maxx - minx, h=maxy - miny,
            label="", strokeColor=color, strokeWidth=2.0,
            contour=True, tech_object=contour.tech_object)]

        name = self._contour_name(contour)
        if name is not None:
            elements.append(name)

        return elements

    def _contour_name(self, contour: Contour,
                      parent_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # Имя техобъекта у центра контура — как в окне
        if not contour.name:
            return None

        offset = self._label_offset(CONTOUR_LABEL_OFFSET, CONTOUR_LABEL_CELLS)
        x = contour.center[0] + offset[0]
        y = contour.center[1] + offset[1]
        x, y = self._local(x, y, parent_key)

        return self._text(
            self._key("contour-name", contour.name, contour.bounds),
            contour.name, x=x, y=y,
            color=config.tech_object_color(contour.tech_object or contour.name),
            size=CONTOUR_LABEL_SIZE, parent_key=parent_key,
            contour=True, tech_object=contour.tech_object)

    def _device_label(self, match: DeviceMatch,
                      parent_key: Optional[str] = None) -> Dict[str, Any]:
        # В окне подпись — это pdf_name, а при неполной уверенности
        # ещё и она сама в скобках
        content = match.pdf_name or match.lua_name or ""
        if match.confidence < 1.0:
            content += f" ({match.confidence:.1f})"

        offset = self._label_offset(DEVICE_LABEL_OFFSET, self._device_label_cells())
        x, y = match.coordinates
        x, y = self._local(x + offset[0], y + offset[1], parent_key)

        return self._text(
            self._key("label", match.lua_name or match.pdf_name, match.coordinates),
            content, x=x, y=y, color="#000000", size=DEVICE_LABEL_SIZE,
            parent_key=parent_key,
            lua_name=match.lua_name, tech_object=match.tech_object)

    def _sheet_text(self, index: int, text: SheetText) -> Dict[str, Any]:
        """Надпись самого чертежа: обозначение Eplan, номер позиции, штамп.

        В разметке они были всегда, а в выгрузку не попадали — редактор
        получал схему без единой подписи с чертежа. Помечены полем
        `drawing`, чтобы отличать их от подписей устройств
        и, если мешают, не рисовать.

        `y` пересчитан: в SVG это базовая линия, а у элемента `text`
        привязка — левый верхний угол строки.
        """
        sheet_size = text.font_size or DEVICE_LABEL_SIZE / self.scale
        return self._text(
            self._key("sheet-text", index, text.text, round(text.x, 2), round(text.y, 2)),
            text.text, x=text.x, y=text.y - sheet_size * TEXT_BASELINE_TO_TOP,
            color=LINE_COLORS.get(text.color, text.color or "#000000"),
            size=max(MIN_FONT_SIZE, self._n(sheet_size)),
            drawing=True, contur_color=text.color)

    def _meta(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Всё про лист, чему нет места на холсте.

        В XML для этого заведены секции — JunctionPoints, Pipelines,
        Connections, CurrentOperationInfo, — а формат редактора это плоский
        массив фигур. Данные складываются в один элемент, чтобы файл нёс
        то же, что XML, и по-прежнему оставался массивом элементов холста.
        Отбирается он одной проверкой: `contur_meta`.
        """
        counts: Dict[str, int] = {}
        for element in elements:
            counts[element["type"]] = counts.get(element["type"], 0) + 1

        # Габарит содержимого, а не листа: по нему редактор проверяет,
        # что схема влезла в свой мир 5000x5000. У отрезка x, y —
        # середина, поэтому его край берётся по концам, а не по габариту
        far_x, far_y = 0.0, 0.0
        for element in elements:
            if element["parentKey"] != "undefined":
                continue
            if element["type"] == "line":
                far_x = max(far_x, element["x1"], element["x2"])
                far_y = max(far_y, element["y1"], element["y2"])
            else:
                far_x = max(far_x, element["x"] + element["w"])
                far_y = max(far_y, element["y"] + element["h"])
        extent = (round(far_x, 3), round(far_y, 3))

        scene = self.scene
        meta: Dict[str, Any] = {
            "contur_meta": True,
            "format": "CONTUR HMI",
            "version": FORMAT_VERSION,
            "canvas": {
                "width": extent[0],
                "height": extent[1],
                "units": "px",
                "grid": GRID,
                "scale": round(self.scale, 6),
                "origin": list(self._origin),
            },
            "sheet": {
                "width": round(scene.width or 0, 3),
                "height": round(scene.height or 0, 3),
                "units": "pt",
            },
            "source": {
                "coordinate_system": scene.coord_system,
                "svg_scale": round(scene.scale, 4),
                "geometry_scale": round(scene.geometry_scale, 4),
            },
            "counts": dict(sorted(counts.items())),
            "tech_objects": self._meta_tech_objects(),
            "pipelines": self._meta_pipelines(),
            "connections": self._meta_connections(),
            "graph": {
                "connections": self._graph.get("linking", 0),
                "manifolds": self._graph.get("manifolds", 0),
                "dead_ends": self._graph.get("dead_ends", 0),
            },
            "operations": self._meta_operations(),
        }

        # Проект целиком, а не лист: узлы контроллера, к которым привязаны
        # каналы устройств, и сигналы проекта
        nodes = controller_nodes()
        if nodes:
            meta["nodes"] = nodes
        signals = project_signals()
        if signals:
            meta["signals"] = signals

        operation = operation_summary(self.current_operation_id)
        if operation:
            meta["current_operation"] = operation

        if self.junctions:
            meta["junction_points"] = [
                {"x": self._x(jp.x), "y": self._y(jp.y),
                 "red_line_id": jp.red_line_id, "blue_line_id": jp.blue_line_id,
                 "red_device": jp.red_device_name,
                 "confidence": round(jp.confidence, 2)}
                for jp in scene.junction_points]

        return self._element(META_TYPE, self._key("meta"), x=0, y=0, w=0, h=0,
                             label="CONTUR", placed=True, visible=False, **meta)

    def _meta_tech_objects(self) -> List[Dict[str, Any]]:
        # Техобъекты листа деревом — как секция TechnologicalObjects в XML:
        # рамка, устройства и операции, в которых они участвуют
        contours = {c.tech_object: c for c in self.scene.contours}
        devices: Dict[str, List[DeviceMatch]] = {}
        for match in self.scene.matches:
            devices.setdefault(match.tech_object, []).append(match)

        objects = []
        for name in sorted(set(contours) | set(devices)):
            entry: Dict[str, Any] = {"name": name}
            contour = contours.get(name)
            if contour is not None:
                minx, miny, maxx, maxy = contour.bounds
                entry["contour"] = {
                    "name": contour.name,
                    "bounds": [self._x(minx), self._y(miny),
                               self._x(maxx), self._y(maxy)],
                    "center": [self._x(contour.center[0]), self._y(contour.center[1])],
                }
            entry["devices"] = sorted(m.lua_name or m.pdf_name
                                      for m in devices.get(name, []))
            # Техобъект листа связывается с описанием через свои устройства:
            # имя контура («BRINE_TANK1») и имя в описании («Танк рассола») —
            # разные вещи, а состояние устройства несёт идентификатор объекта
            places = [e for m in devices.get(name, [])
                      for e in (device_states(m.lua_name) or device_states(m.pdf_name))]
            operations = sorted({e["operation_id"] for e in places})
            if operations:
                entry["operations"] = operations

            for obj_id in sorted({e["tech_object_id"] for e in places}):
                details = object_details(obj_id)
                if details:
                    entry.setdefault("lua_objects", []).append(details)

            objects.append(entry)

        return objects

    def _meta_pipelines(self) -> List[Dict[str, Any]]:
        # Сегменты не повторяем: они и есть элементы line, у каждого
        # проставлен pipeline_id
        return [{"id": pipe.id, "name": pipe.name,
                 "segment_count": pipe.segment_count,
                 "total_length": round(pipe.total_length, 2),
                 "connected_devices": sorted(set(pipe.connected_devices))}
                for pipe in self.scene.pipelines]

    def _meta_connections(self) -> List[Dict[str, Any]]:
        return [{"pipeline": c.pipeline_name, "pipeline_id": c.pipeline_id,
                 "devices": c.devices, "length": round(c.length, 2),
                 "segment_count": c.segment_count}
                for c in self._graph.get("connections", []) if len(c.devices) >= 2]

    def _meta_operations(self) -> List[Dict[str, Any]]:
        # Программы операций, в которых участвуют устройства листа: состояния,
        # шаги и что каждый шаг открывает и закрывает. Состояние устройства
        # ссылается сюда по operation_id
        programs = []
        for operation_id in sorted(self._operations):
            program = operation_program(operation_id)
            if program:
                programs.append(program)
        return programs

    def _local(self, x: float, y: float,
               parent_key: Optional[str]) -> Tuple[float, float]:
        # Внутри группы координаты отсчитываются от её угла: холст рисует
        # детей в системе родителя
        origin = self._group_origins.get(parent_key) if parent_key else None
        if not origin:
            return x, y
        return x - origin[0], y - origin[1]

    def _wanted_lines(self) -> List[LineSegment]:
        # Чертёж берётся из своего набора: в нём ничего не выброшено,
        # а рамка помечена (см. svg_geometry.extract_line_segments)
        if self.lines == "none":
            return []
        segments = [s for s in self.scene.drawing_segments
                    if self.frame or not s.frame]
        if self.lines == "pipes":
            return [s for s in segments if s.color != "red"]
        return segments

    def _symbol_size(self, measured: float) -> float:
        """Размер стороны символа: измеренный, но в разумных пределах.

        Обычный размер символа на этом листе генератор записал в разметку
        (`data-device-size`), а сцена держит его как множитель допусков.
        """
        usual = (self.scene.geometry_scale * REFERENCE_DEVICE_SIZE
                 if self.scene else FALLBACK_DEVICE_SIZE)
        # Геометрия нашлась не у всех: на контрольном листе у 41 устройства
        # из 233 нет своего скопления красных линий. Раньше им доставались
        # жёстко заданные 20 пт — заметно мельче обычного символа листа
        # (31.32), и в редакторе такие устройства выглядели чужими
        if measured <= 0:
            return usual
        return max(usual * MIN_DEVICE_RATIO, min(usual * MAX_DEVICE_RATIO, measured))

    def _groups(self, matches: List[DeviceMatch],
                contours: List[Contour]) -> List[Dict[str, Any]]:
        """Техобъекты группами редактора — по CONTUR_HMI_GROUPS=1.

        По умолчанию выключено намеренно: у группы дети живут в её системе
        координат (в выгрузке редактора круг с x=184 внутри группы с x=676
        стоит на холсте в 860), и стоит ошибиться — вся схема разъедется.
        Принадлежность к техобъекту и так записана полем tech_object
        у каждого устройства.
        """
        by_tech: Dict[str, List[DeviceMatch]] = {}
        for match in matches:
            if match.tech_object:
                by_tech.setdefault(match.tech_object, []).append(match)

        groups: List[Dict[str, Any]] = []
        frames: List[Dict[str, Any]] = []
        for contour in contours:
            if contour.tech_object not in by_tech:
                continue

            minx, miny, maxx, maxy = contour.bounds
            key = self._key("group", contour.tech_object, contour.bounds)
            self._group_origins[key] = (minx, miny)
            self._group_of[contour.tech_object] = key

            group = self._element(
                "group", key, x=minx, y=miny, w=maxx - minx, h=maxy - miny,
                label=contour.name or contour.tech_object,
                bg="rgba(59,130,246,0.08)",
                borderStyle="dashed", borderColor="#3b82f6",
                tech_object=contour.tech_object)
            group["composition"] = True   # у группы это их же поле, см. §6
            group["children"] = []
            groups.append(group)

            # Группа сама по себе ничего не рисует: её рамка видна только
            # когда она выделена (спецификация импорта, §5.5). Видимую
            # рамку даёт отдельный прямоугольник первым ребёнком — он же
            # держит габарит группы, иначе тот схлопнется до скопления
            # кружков при первом же перетаскивании ребёнка
            frame = self._element(
                "rectangle",
                self._key("group-frame", contour.tech_object, contour.bounds),
                x=0, y=0, w=maxx - minx, h=maxy - miny,
                label="", parent_key=key,
                bg="rgba(59,130,246,0.08)", strokeColor="#3b82f6",
                strokeWidth=1.5, strokeDasharray="6 4",
                contour=True, tech_object=contour.tech_object)
            group["children"].append(frame["key"])
            frames.append(frame)

        return groups + frames

    # ---------------------------------------------------------------- сборка

    def build(self, svg_path: str, matches: List[DeviceMatch],
              contours: List[Contour]) -> Optional[List[Dict[str, Any]]]:
        """Собирает массив элементов. Отдельно от записи — чтобы проверять."""
        self.scene = build_scene(svg_path, matches, contours, self.pdf_size,
                                 use_percent_coords=False,
                                 snap_to_geometry=self.snap_to_geometry)
        if self.scene is None:
            return None

        # Масштаб и сдвиг — до первой координаты: через них проходит всё
        if self.scale is None:
            self.scale = self._sheet_scale()
        self._origin = self._content_origin()

        # Затравка ключей — размер холста и число сегментов: разные листы
        # дают разные ключи, один и тот же лист — одинаковые
        self._seed = f"{self.scene.width}x{self.scene.height}:{len(self.scene.line_segments)}"
        self._group_origins.clear()
        self._group_of.clear()
        self._operations.clear()

        # Связность считается до элементов: линия узнаёт свою трубу,
        # устройство — соседей по трубам
        self._graph = build_connection_graph(self.scene.pipelines)
        self._pipeline_of = {segment.id: (pipe.id, pipe.name)
                             for pipe in self.scene.pipelines
                             for segment in pipe.segments}

        # Порядок в массиве — это порядок отрисовки, и он повторяет слои
        # окна: рамки контуров (z=0), чертёж (z=-1 лежит ниже, но рамка
        # контура прозрачная и не закрывает его), устройства (z=3),
        # подписи (z=2) сверху всего, чтобы их не перекрывали трубы
        elements: List[Dict[str, Any]] = []
        labels: List[Dict[str, Any]] = []

        group_elements = self._groups(self.scene.matches, contours) if self.groups else []
        elements.extend(group_elements)
        by_key = {group["key"]: group for group in group_elements}

        def adopt(element: Dict[str, Any]) -> Dict[str, Any]:
            # Холст рисует детей по массиву children родителя, а не обходом
            # по parentKey: ребёнок с одной только ссылкой вверх не появится
            parent = by_key.get(element["parentKey"])
            if parent is not None:
                parent["children"].append(element["key"])
            return element

        # Ёмкости — подложкой под всё остальное: внутри их стенок стоят
        # и чертёж, и устройства техобъекта
        if self._wanted_tanks():
            for contour in contours:
                elements.extend(self._tank(contour))

        if self.contour_frames:
            for contour in contours:
                if self.groups:
                    # Рамкой служит сама группа, остаётся дать ей имя
                    name = self._contour_name(contour, self._group_of.get(contour.tech_object))
                    if name is not None:
                        labels.append(adopt(name))
                    continue
                for element in self._contour(contour):
                    # Имя контура уходит наверх вместе с подписями: у нас
                    # в окне оно z=2, то есть поверх чертежа, а не под ним
                    (labels if element["type"] == "text" else elements).append(element)

        # Какие отрезки чертежа — символы устройств: они уйдут детьми своих
        # групп, а не верхним уровнем. Устройство привязано к своему кластеру
        # по координате: сопоставление уже поставило её в центр кластера
        clusters = {(round(c.x, 3), round(c.y, 3)): c for c in self.scene.device_boxes()}
        symbol_of: Dict[int, DeviceMatch] = {}
        # Каким устройствам нашлась готовая фигура: символ с чертежа
        # им не нужен вовсе — он не уезжает ни детьми группы, ни верхним
        # уровнем, иначе линии Eplan просвечивали бы сквозь клапан библиотеки
        symbols: Dict[str, Any] = {}
        if self.devices == "object":
            for match in self.scene.matches:
                cluster = clusters.get((round(match.coordinates[0], 3),
                                        round(match.coordinates[1], 3)))
                symbol = self._device_symbol(match, cluster)
                if symbol is not None:
                    symbols[self._device_key(match)] = symbol
                if cluster:
                    for segment in cluster.segments:
                        symbol_of[segment.id] = match

        for segment in self._wanted_lines():
            if segment.source_id not in symbol_of:
                elements.append(self._line(segment))

        # Надписи чертежа лежат вместе с ним, ниже устройств: это тот же
        # слой, что линии, а не слой подписей устройств
        if self.texts:
            for index, text in enumerate(self.scene.sheet_texts()):
                elements.append(self._sheet_text(index, text))

        # Символы устройств, отобранные выше, — по своим устройствам
        symbol_lines: Dict[str, List[LineSegment]] = {}
        for segment in self._wanted_lines():
            match = symbol_of.get(segment.source_id)
            if match is not None:
                symbol_lines.setdefault(self._device_key(match), []).append(segment)

        for match in self.scene.matches:
            if self.devices == "none":
                if self.labels:
                    labels.append(adopt(self._device_label(match, None)))
                continue

            box = clusters.get((round(match.coordinates[0], 3),
                                round(match.coordinates[1], 3)))
            parent_key = self._group_of.get(match.tech_object) if self.groups else None
            payload = self._device_payload(match, self._device_key(match))

            if self.devices == "circle":
                elements.append(adopt(self._device_circle(match, box, payload,
                                                          parent_key)))
            else:
                symbol = symbols.get(self._device_key(match))
                group, frame = self._device_object(match, box, payload,
                                                   parent_key, symbol)
                elements.append(adopt(group))
                elements.append(frame)
                if symbol is not None:
                    tag = match.pdf_name or match.lua_name or ""
                    for part in self._symbol_parts(symbol, group, tag):
                        group["children"].append(part["key"])
                        elements.append(part)
                else:
                    for segment in symbol_lines.get(group["key"], []):
                        line = self._line(segment, parent_key=group["key"])
                        group["children"].append(line["key"])
                        elements.append(line)

            if self.labels:
                labels.append(adopt(self._device_label(match, parent_key)))

        elements.extend(labels)

        # meta знает счётчики готового массива и операции, встреченные
        # в состояниях устройств, поэтому собирается последним, а встаёт
        # первым: так его видно, не читая файл целиком
        if self.meta:
            elements.insert(0, self._meta(elements))

        return elements

    def export(self, svg_path: str, output_path: str, matches: List[DeviceMatch],
               contours: List[Contour]) -> bool:
        try:
            print("\n📊 ДИАГНОСТИКА:")
            print(f"   - Контуров: {len(contours)}")
            print(f"   - Устройств (matches): {len(matches)}")

            elements = self.build(svg_path, matches, contours)
            if elements is None:
                return False

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(elements, f, ensure_ascii=False, indent=2)

            counts: Dict[str, int] = {}
            for element in elements:
                counts[element["type"]] = counts.get(element["type"], 0) + 1

            device_states_count = sum(
                len(e.get("contur_states", [])) for e in elements
                if e["type"] == DEVICE_SHAPE)

            print(f"✅ Экспорт для редактора мнемосхем завершён: {output_path}")
            print(f"   - Элементов: {len(elements)} "
                  f"({', '.join(f'{k}: {v}' for k, v in sorted(counts.items()))})")
            print(f"   - Координаты: единицы холста, множитель {self.scale:.4g}"
                  f" (сетка {GRID:g})")
            if self.states:
                print(f"   - Состояний устройств в операциях: {device_states_count} "
                      f"(операций: {len(self._operations)})")
            if self.meta:
                print(f"   - В meta: труб {len(self.scene.pipelines)}, "
                      f"связей {self._graph.get('linking', 0)}, "
                      f"точек сопряжения "
                      f"{len(self.scene.junction_points) if self.junctions else 0}")
            if self.groups:
                print("   - Техобъекты обведены группами (CONTUR_HMI_GROUPS)")

            return True

        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
            return False


def export_current_visualization_hmi(svg_path: str, output_path: str,
                                     matches: List[DeviceMatch],
                                     contours: List[Contour],
                                     use_percent_coords: bool = True,
                                     current_operation_id: Optional[str] = None,
                                     pdf_size: Optional[Tuple[float, float]] = None,
                                     snap_to_geometry: bool = True) -> bool:
    # Подпись общая с остальными выгрузками, чтобы формат выбирался
    # по расширению файла (exporters.py).
    #
    # use_percent_coords игнорируется намеренно: редактор разбирает только
    # числа, «73.1%» для него не координата. А вот current_operation_id
    # теперь доходит: раньше считалось, что состояния редактор ведёт сам,
    # но вести их он может только по данным выгрузки — а их в файле не было.
    exporter = HMIExporter(pdf_size=pdf_size, snap_to_geometry=snap_to_geometry,
                           current_operation_id=current_operation_id)
    return exporter.export(svg_path, output_path, matches, contours)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        svg_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "hmi_export.json"

        ok = export_current_visualization_hmi(svg_file, output_file, [], [])
        print(f"Готово: {output_file}" if ok else "Ошибка экспорта")
