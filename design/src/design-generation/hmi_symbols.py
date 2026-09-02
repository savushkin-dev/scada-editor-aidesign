# hmi_symbols.py
# Готовые символы библиотеки редактора и правила, какому устройству какой.
#
# Зачем. До сих пор устройство уезжало отрисовкой конвейера: кружок или
# скопление красных отрезков, срисованных с чертежа Eplan. У редактора уже
# нарисованы свои фигуры — клапан, ёмкость, датчик-«шарик», — и схема,
# собранная из кружков, на его мнемосхемы не похожа. Теперь на место
# устройства подставляется библиотечная фигура.
#
# Откуда фигуры. Из выгрузки сцены редактора: `tools/extract_symbols.py`
# находит в сцене повторяющиеся группы и пишет `hmi_symbols.json`.
# Пересобирать каталог нужно только когда библиотека пополнится.
#
# Источников два. Сначала рабочая сцена MOZARELLA_01, где нашлись клапан,
# датчик и ёмкость; потом библиотека шаблонов (`MCA_1_components.json`)
# с 31 подписанной фигурой — три насоса, полтора десятка клапанов и заслонок,
# три сигнализатора уровня, теплообменники и фильтр. Имена фигур в каталоге
# внутренние, а библиотечная подпись едет рядом полем `title`.
#
# BUILTIN остался на случай, когда каталога нет вовсе (сборка без ресурса,
# чужая папка): насос, нарисованный по чертежу, и «бабочка» ручного клапана
# из двух библиотечных треугольников. Каталог перекрывает встроенные
# фигуры по имени.
#
# Как символ попадает на схему. Каталог хранит фигуру в её собственных
# координатах и габарите — как её нарисовали. При выгрузке фигура вписывается
# в габарит устройства (`Symbol.fit`), а элементы холста из неё собирает
# `hmi_export`: ключи, состояния и данные устройства — его забота, форма —
# каталога.
#
# Про сетку. Холст редактора размечен шагом 20, и символ нарисован по узлам. Если
# устройство на схеме меньше символа, при вписывании узлы делятся: половинный
# размер даёт полклетки, треть — треть клетки. Кратный размер (10 клеток при
# символе 200) сохраняет сетку точно — см. CONTUR_HMI_SYMBOL_CELLS.
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import config

# Сетка холста редактора (спецификация импорта, §0)
GRID = 20.0

# Каталог, собранный из выгрузки сцены. В собранном .exe он лежит среди
# вшитых ресурсов, рядом с моделью, — иначе приложение молча осталось бы
# со встроенными двумя фигурами и рисовало бы клапаны по-старому
CATALOGUE_PATH = config.BUNDLE_DIR / "hmi_symbols.json"

# Символы, которых в присланной сцене нет цельной фигурой.
#
# `pump` — насоса в библиотеке не нашлось вовсе. Нарисован по её же правилам
# (габарит 120x120, как у библиотечного клапана, всё по узлам сетки 20), но форма
# не выдумана: это символ насоса с самого чертежа Eplan — круг, вписанный
# треугольник остриём по потоку и горизонтальный диаметр. Так насос
# нарисован и на контрольном листе A0, и на листе 13 mozzarella. Пришлют
# свой — он перекроет этот по имени.
#
# `manual_valve` — «бабочка» из двух треугольников. На их схеме это два
# отдельных верхнеуровневых многоугольника, стоящих вплотную; группой они
# не оформлены, и извлечь их как одну фигуру нельзя. Точки — их, из сцены
# MOZARELLA_01 (белый треугольник остриём вправо и чёрный остриём влево).
BUILTIN: Dict[str, Dict[str, Any]] = {
    "pump": {
        "w": 120.0, "h": 120.0, "origin": "contur",
        "shapes": [
            {"type": "circle", "cx": 60.0, "cy": 60.0, "radius": 60.0,
             "bg": "transparent", "strokeColor": "#000000"},
            # Диаметр вдоль трубы и две хорды к правой точке круга — рабочее
            # колесо. Все три вершины лежат на самом круге, как на чертеже
            {"type": "line", "x1": 0.0, "y1": 60.0, "x2": 120.0, "y2": 60.0,
             "strokeColor": "#000000"},
            {"type": "line", "x1": 60.0, "y1": 0.0, "x2": 120.0, "y2": 60.0,
             "strokeColor": "#000000"},
            {"type": "line", "x1": 120.0, "y1": 60.0, "x2": 60.0, "y2": 120.0,
             "strokeColor": "#000000"},
        ],
    },
    "manual_valve": {
        "w": 80.0, "h": 40.0, "origin": "editor",
        "shapes": [
            {"type": "polygon", "points": [0.0, 0.0, 40.0, 20.0, 0.0, 40.0],
             "bg": "#ffffff", "strokeColor": "#000000", "sides": 3},
            {"type": "polygon", "points": [80.0, 0.0, 40.0, 20.0, 80.0, 40.0],
             "bg": "#000000", "strokeColor": "#000000", "sides": 3},
        ],
    },
}

# Какому обозначению устройства какой символ. Обозначения — из config.DEVICE_TYPES.
# Датчики все одинаковые: в библиотеке это кружок с тегом внутри, и различает их
# сам тег (-TE1, -PT1, -PC1), а не форма.
#
# Имена фигур — из библиотеки шаблонов (`MCA_1_components.json`), где
# у каждой стоит подпись: `butterfly_nc` это «Санитарная запорная заслонка
# с пневмоприводом, НЗ», `control_valve` — «Санитарный регулирующий клапан»,
# `pump_centrifugal` — «Насос центробежный». Отсечной клапан на этих схемах
# именно заслонка с пневмоприводом: та же фигура стояла и в их собственной
# сцене MOZARELLA_01, откуда взят прежний `valve`
DEFAULT_DEVICE_SYMBOLS: Dict[str, str] = {
    "V": "butterfly_nc", "VC": "control_valve",
    "M": "pump_centrifugal",
    "LS": "sensor", "LT": "sensor",
    "TE": "sensor", "TC": "sensor",
    "QT": "sensor",
    "FQT": "sensor", "FC": "sensor",
    "PT": "sensor", "PC": "sensor",
    "GS": "sensor",
    "FS": "sensor", "WT": "sensor", "WC": "sensor", "LC": "sensor",
    # Электрические устройства: в библиотеке этого нет, фигуры нарисованы
    # отдельно (tools/make_contur_symbols.py). Лампа и кнопка срисованы
    # с чертежа Eplan, сирена и колонна — по общепринятому виду: Eplan
    # показывает их клеммным блоком, из которого мнемосхемы не сделать
    "HL": "lamp", "SB": "button", "HA": "siren", "HLA": "beacon",
}

# У сигнализатора уровня в библиотеке три фигуры — верхний, средний
# и нижний уровень, — а обозначение у всех трёх одно (LS). Какая нужна,
# видно только из описания в Lua: «Датчик верхнего уровня танка 1».
# Не нашлось слова — остаётся общий кружок с тегом
LEVEL_TYPES = frozenset(("LS",))
DEFAULT_LEVEL_WORDS: Tuple[Tuple[str, str], ...] = (
    ("level_high", "ВЕРХН"), ("level_high", "ВЕРХ"), ("level_high", "HIGH"),
    ("level_low", "НИЖН"), ("level_low", "НИЖ"), ("level_low", "LOW"),
    ("level_mid", "СРЕДН"), ("level_mid", "СРЕД"), ("level_mid", "MID"),
)

# Клапан без имени в Lua — ручной: у него нет ни одного канала ввода-вывода,
# контроллер про него не знает, и на схеме он рисуется «бабочкой», а не
# корпусом с приводом. `manual_valve` — библиотечный «Клапан с ручным
# приводом»; до библиотеки под этим именем лежала «бабочка», собранная
# из двух треугольников сцены (осталась встроенной, на случай без каталога)
MANUAL_VALVE_TYPES = frozenset(("V", "VC"))
MANUAL_VALVE_SYMBOL = "manual_valve"

# Обозначение M носят и насосы, и мешалки, а Eplan рисует их по-разному:
# насос — круг с рабочим колесом на трубе, мешалка — кружок с обозначением
# внутри и лопасть в самом танке. На контрольном листе A0 из пятнадцати
# устройств M восемь мешалки, и все восемь приезжали насосом. Различить
# их можно только по описанию из Lua — своей приметы в чертеже нет
AGITATOR_TYPES = frozenset(("M",))
AGITATOR_SYMBOL = "agitator"
DEFAULT_AGITATOR_WORDS = ("МЕШАЛ", "AGITATOR", "STIRRER")

# Фигура, которой рисуется другая, если своей в каталоге нет. Мешалку
# Eplan рисует тем же кружком с обозначением внутри, что и датчик, —
# отдельной фигуры мешалки в библиотеке нет. Имя при этом остаётся
# своим: появится библиотечная мешалка — она встанет на это место
ALIASES = {AGITATOR_SYMBOL: "sensor"}

# Стоячий вид символа: в библиотеке клапан нарисован и лёжа, и стоя. Какой брать,
# видно по чертежу — устройство вытянуто вдоль трубы
VERTICAL_SUFFIX = "_v"

# Размер устройства на холсте, в клетках сетки. Библиотечная фигура
# нарисована на десяти клетках (200 при сетке 20), и это же значение
# по умолчанию: множитель выходит единицей, фигура приезжает точь-в-точь
# как нарисована, все её узлы совпадают с узлами холста.
#
# Меньше — символ вписывается с делением клетки: 0.6 при шести клетках,
# 0.4 при четырёх. Больше не нужно: крупнее собственного размера фигуру
# никто не рисует. Предела холста у редактора нет — размер сцены задаётся
# блоком canvas и служит рамкой, а не запретом; нижняя граница зума
# опущена до 0.03, чтобы лист любого формата открывался целиком даже
# в небольшом окне. На таких масштабах редактор показывает только крупную
# сетку с шагом 200: клетка в 20 единиц вырождается в пиксель
DEFAULT_SYMBOL_CELLS = 10.0
MIN_SYMBOL_CELLS = 2.0

# Сколько занимает фигура устройства в собственных единицах каталога.
# От этого числа считается единый множитель — один на все фигуры сразу,
# иначе «бабочка» ручного клапана, вписанная в тот же квадрат, что и клапан
# с приводом, стала бы в полтора раза крупнее, чем её рисуют.
#
# Раньше здесь стояло число: в сцене MOZARELLA_01 клапан, датчик и насос
# нарисованы в габарите 120x120. В присланной позже библиотеке те же фигуры
# нарисованы крупнее — заслонка 200x160, — и прежнее число сделало бы
# устройство в полтора раза больше его места на чертеже: на контрольном
# листе 27 налезающих друг на друга пар вместо 19. Поэтому размер берётся
# из самого каталога, по той фигуре, которой рисуется отсечной клапан:
# на этих схемах он и есть обычное устройство.
REFERENCE_SYMBOL_TYPE = "V"
FALLBACK_NATIVE_SIZE = DEFAULT_SYMBOL_CELLS * GRID

# Какую долю символа деталь должна занимать вдоль оси, чтобы считаться
# его корпусом и тянуться вместе с ним (см. Symbol.stretch)
SPAN_RATIO = 0.6

# Чем рисуется техобъект-ёмкость и как узнать, что он ёмкость.
# Список слов настраивается: у другого проекта танки называются иначе
TANK_SYMBOL = "tank"
DEFAULT_TANK_WORDS = ("TANK", "БАК", "ЁМКОСТ", "ЕМКОСТ", "COAG", "BATH",
                      "VAT", "SILO", "TNK", "CIP")


def native_device_size(path: Optional[str] = None) -> float:
    """Габарит фигуры обычного устройства в единицах каталога."""
    symbol = catalogue(path).get(device_symbols().get(REFERENCE_SYMBOL_TYPE, ""))
    if symbol is None or not max(symbol.w, symbol.h):
        return FALLBACK_NATIVE_SIZE
    return max(symbol.w, symbol.h)


def symbol_scale(cells: float, path: Optional[str] = None) -> float:
    """Во сколько раз увеличен весь каталог при заданном размере устройства.

    Множитель один на все фигуры: и на клапан, и на «бабочку», и на детали
    ёмкости. Единица получается там, где заданный размер устройства совпал
    с габаритом фигуры в каталоге: тогда она приезжает точь-в-точь такой,
    какой её нарисовали, и все её узлы совпадают с сеткой холста. У их
    библиотеки это десять клеток (заслонка нарисована на 200 единицах),
    у прежней сцены было шесть.
    """
    native = native_device_size(path)
    return (cells * GRID) / native if native else 1.0


@dataclass(frozen=True)
class Symbol:
    """Готовая фигура в собственных координатах: угол в (0, 0)."""

    name: str
    w: float
    h: float
    shapes: Tuple[Dict[str, Any], ...]
    origin: str = "editor"
    # Как фигура называется в библиотеке: «Насос центробежный», «Клапан, НЗ».
    # Наше имя короткое и латинское, а это — их подпись из библиотеки,
    # по которой человек узнаёт, та ли фигура подставлена
    title: str = ""

    def fit(self, width: float, height: Optional[float] = None
            ) -> Tuple[float, float, List[Dict[str, Any]]]:
        """Символ, вписанный в габарит с сохранением пропорций.

        Возвращает (ширина, высота, примитивы) — уже в единицах холста.
        Пропорции держатся намеренно: ёмкость 200x280 в квадрате
        превратилась бы в куб, а «бабочка» 80x40 — в ромб.
        """
        if height is None:
            height = width
        if self.w <= 0 or self.h <= 0:
            return (width, height, [])
        scale = min(width / self.w, height / self.h)
        return (self.w * scale, self.h * scale,
                [transform_shape(shape, lambda x: x * scale, lambda y: y * scale, scale)
                 for shape in self.shapes])

    def stretch(self, width: float, height: float,
                detail: Optional[float] = None) -> List[Dict[str, Any]]:
        """Символ по чужому габариту: корпус тянется, детали — нет.

        Нужен ёмкости: её рисуют по границам техобъекта, а те задаются
        чертежом и пропорций символа не знают. Растянуть всё подряд нельзя —
        техобъект на листе mozzarella занимает 3880x3040 единиц, и патрубок
        шириной в клетку раздулся бы до полутысячи.

        Правило простое: деталь, занимающая вдоль оси почти весь символ
        (корпус, полки внутри), тянется вместе с ним; мелкая деталь
        сохраняет свой размер, а её место переезжает пропорционально.
        `detail` — во сколько раз увеличены мелкие детали; по умолчанию
        по меньшей стороне, но выгрузка передаёт сюда тот же множитель,
        с каким уехали символы устройств, чтобы патрубок ёмкости совпал
        по толщине с патрубком клапана.
        """
        if self.w <= 0 or self.h <= 0:
            return []
        kx, ky = width / self.w, height / self.h
        small = detail if detail and detail > 0 else min(kx, ky)

        out: List[Dict[str, Any]] = []
        for shape in self.shapes:
            minx, miny, maxx, maxy = shape_bounds(shape)
            sx = kx if (maxx - minx) >= self.w * SPAN_RATIO else small
            sy = ky if (maxy - miny) >= self.h * SPAN_RATIO else small
            cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
            out.append(transform_shape(
                shape,
                lambda x, cx=cx, sx=sx: cx * kx + (x - cx) * sx,
                lambda y, cy=cy, sy=sy: cy * ky + (y - cy) * sy,
                min(sx, sy)))
        return out


def shape_bounds(shape: Dict[str, Any]) -> Tuple[float, float, float, float]:
    kind = shape.get("type")
    if kind == "line":
        xs, ys = [shape["x1"], shape["x2"]], [shape["y1"], shape["y2"]]
    elif kind == "circle":
        radius = shape["radius"]
        xs = [shape["cx"] - radius, shape["cx"] + radius]
        ys = [shape["cy"] - radius, shape["cy"] + radius]
    elif kind in ("polygon", "curve"):
        xs, ys = shape["points"][0::2], shape["points"][1::2]
    else:
        x, y = shape.get("x", 0.0), shape.get("y", 0.0)
        xs, ys = [x, x + shape.get("w", 0.0)], [y, y + shape.get("h", 0.0)]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0.0, 0.0, 0.0, 0.0)


def transform_shape(shape: Dict[str, Any], fx: Any, fy: Any,
               kr: float) -> Dict[str, Any]:
    """Примитив в новых координатах: `fx`/`fy` двигают точки, `kr` — размеры.

    Радиус и кегль — величины без направления, и множитель у них один:
    круг с разными множителями по осям редактор всё равно нарисует кругом,
    а габарит разойдётся с ним.
    """
    item = dict(shape)
    kind = item.get("type")
    if kind == "line":
        item["x1"], item["x2"] = fx(item["x1"]), fx(item["x2"])
        item["y1"], item["y2"] = fy(item["y1"]), fy(item["y2"])
    elif kind == "circle":
        item["cx"], item["cy"] = fx(item["cx"]), fy(item["cy"])
        item["radius"] *= kr
    elif kind in ("polygon", "curve"):
        item["points"] = [(fx if index % 2 == 0 else fy)(value)
                          for index, value in enumerate(item["points"])]
    else:
        x, y = item.get("x", 0.0), item.get("y", 0.0)
        item["x"], item["y"] = fx(x), fy(y)
        if "w" in item:
            item["w"] = fx(x + item["w"]) - item["x"]
        if "h" in item:
            item["h"] = fy(y + item["h"]) - item["y"]
    if "fontSize" in item:
        item["fontSize"] *= kr
    return item


# ------------------------------------------------------------------ каталог

_cache: Dict[str, Dict[str, Symbol]] = {}


def catalogue(path: Optional[str] = None) -> Dict[str, Symbol]:
    """Все известные символы: встроенные плюс извлечённые из сцены.

    Каталог перекрывает встроенные по имени — как только они пришлют
    свой насос, подставляться будет он.
    """
    key = str(path or CATALOGUE_PATH)
    if key in _cache:
        return _cache[key]

    symbols: Dict[str, Symbol] = {
        name: _symbol(name, data) for name, data in BUILTIN.items()
    }
    try:
        with open(key, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        data = {}
    for name, item in (data.get("symbols") or {}).items():
        symbols[name] = _symbol(name, item)

    # Замены — после каталога: своя фигура всегда сильнее заимствованной
    for name, source in ALIASES.items():
        if name not in symbols and source in symbols:
            borrowed = symbols[source]
            symbols[name] = Symbol(name=name, w=borrowed.w, h=borrowed.h,
                                   shapes=borrowed.shapes, origin="contur",
                                   title=borrowed.title)

    _cache[key] = symbols
    return symbols


def _symbol(name: str, data: Dict[str, Any]) -> Symbol:
    return Symbol(name=name,
                  w=float(data.get("w") or 0),
                  h=float(data.get("h") or 0),
                  shapes=tuple(data.get("shapes") or ()),
                  origin=str(data.get("origin") or "editor"),
                  title=str(data.get("title") or ""))


def reset_cache() -> None:
    """Забыть прочитанный каталог — для проверок."""
    _cache.clear()


# ------------------------------------------------------------------ выбор

def device_symbols() -> Dict[str, str]:
    """Карта «обозначение устройства → символ», с поправкой из окружения.

    CONTUR_HMI_SYMBOL_MAP="V=valve,M=pump,TE=" — пустое имя убирает тип
    из карты, и такое устройство рисуется как раньше.
    """
    mapping = dict(DEFAULT_DEVICE_SYMBOLS)
    raw = os.environ.get("CONTUR_HMI_SYMBOL_MAP", "").strip()
    for item in raw.split(","):
        device_type, sep, name = item.partition("=")
        device_type = device_type.strip().upper()
        if not device_type or not sep:
            continue
        name = name.strip()
        if name:
            mapping[device_type] = name
        else:
            mapping.pop(device_type, None)
    return mapping


def agitator_words() -> Tuple[str, ...]:
    raw = os.environ.get("CONTUR_HMI_AGITATOR_NAMES", "").strip()
    if not raw:
        return DEFAULT_AGITATOR_WORDS
    return tuple(word.strip().upper() for word in raw.split(",") if word.strip())


def level_words() -> Tuple[Tuple[str, str], ...]:
    """Пары «фигура — слово в описании» для сигнализатора уровня.

    CONTUR_HMI_LEVEL_NAMES="level_high=ВЕРХ,level_low=НИЖ" — порядок важен:
    берётся первое совпавшее слово, поэтому длинные пишутся раньше коротких.
    """
    raw = os.environ.get("CONTUR_HMI_LEVEL_NAMES", "").strip()
    if not raw:
        return DEFAULT_LEVEL_WORDS
    pairs = []
    for item in raw.split(","):
        name, sep, word = item.partition("=")
        if sep and name.strip() and word.strip():
            pairs.append((name.strip(), word.strip().upper()))
    return tuple(pairs) or DEFAULT_LEVEL_WORDS


def symbol_for_device(device_type: str, lua_name: str = "",
                      descr: str = "", vertical: bool = False,
                      path: Optional[str] = None) -> Optional[Symbol]:
    """Символ устройства или None, если для такого типа его нет.

    `vertical` — символ стоит поперёк трубы: в библиотеке клапан нарисован в двух
    видах, лежачим и стоячим (14 и 7 штук в присланной сцене), и брать
    надо тот, что совпадает с положением устройства на чертеже.

    `descr` — описание из Lua. По нему мешалка отличается от насоса:
    обозначение в Eplan общее (M), а рисуются они по-разному.
    """
    known = catalogue(path)
    device_type = (device_type or "").upper()

    if device_type in MANUAL_VALVE_TYPES and not (lua_name or "").strip():
        manual = known.get(MANUAL_VALVE_SYMBOL)
        if manual is not None:
            return manual

    if device_type in AGITATOR_TYPES:
        haystack = (descr or "").upper()
        if any(word in haystack for word in agitator_words()):
            agitator = known.get(AGITATOR_SYMBOL)
            if agitator is not None:
                return agitator

    if device_type in LEVEL_TYPES:
        haystack = (descr or "").upper()
        for level_name, word in level_words():
            if word in haystack and level_name in known:
                return known[level_name]

    name = device_symbols().get(device_type)
    if not name:
        return None
    if vertical and f"{name}{VERTICAL_SUFFIX}" in known:
        name = f"{name}{VERTICAL_SUFFIX}"
    return known.get(name)


def tank_words() -> Tuple[str, ...]:
    raw = os.environ.get("CONTUR_HMI_TANK_NAMES", "").strip()
    if not raw:
        return DEFAULT_TANK_WORDS
    return tuple(word.strip().upper() for word in raw.split(",") if word.strip())


def symbol_for_tech_object(tech_object: str, name: str = "",
                           path: Optional[str] = None) -> Optional[Symbol]:
    """Символ ёмкости, если техобъект похож на неё по имени.

    Судить приходится по имени: в Lua у техобъекта нет поля «это танк»,
    а на чертеже ёмкость от участка трубопровода отличает только контур.
    """
    haystack = f"{tech_object or ''} {name or ''}".upper()
    if not any(word in haystack for word in tank_words()):
        return None
    return catalogue(path).get(TANK_SYMBOL)


def tag_text(shape: Dict[str, Any], tag: str) -> Optional[str]:
    """Что написать внутри фигуры: `$tag` в каталоге — место под тег."""
    text = shape.get("text")
    if not text:
        return None
    return tag if text == "$tag" else str(text)
