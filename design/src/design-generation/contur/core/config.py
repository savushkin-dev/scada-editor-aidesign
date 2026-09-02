# config.py
# Настройки проекта в одном месте.
#
# Пути раньше были зашиты в код абсолютными строками вида
# C:\Users\1\Desktop\gendis\CONTUR\runs\... — на другой машине это не работало.
# Здесь всё считается относительно расположения проекта и может быть
# переопределено переменными окружения.
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Optional

# Собрано ли приложение PyInstaller
IS_FROZEN = getattr(sys, "frozen", False)

# Корень проекта.
# В обычном запуске — папка с исходниками, то есть та, где лежат точка входа
# и каталог фигур. Сам модуль лежит на два уровня глубже (contur/core), и
# отсчёт ведётся от него: parents[2].
# В сборке PyInstaller __file__ указывает во временную папку распаковки,
# поэтому за корень берём папку рядом с exe: именно там пользователь
# держит модель, входные файлы и получает output.
BASE_DIR = (Path(sys.executable).resolve().parent if IS_FROZEN
            else Path(__file__).resolve().parents[2])

# Папка с ресурсами, вшитыми в сборку (sys._MEIPASS). Для обычного
# запуска совпадает с BASE_DIR.
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


# ---------------------------------------------------------------- каталоги
# CONTUR_OUTPUT_DIR — куда складывать промежуточные JSON и результаты
OUTPUT_DIR = _env_path("CONTUR_OUTPUT_DIR", BASE_DIR / "output")


def _input_default() -> Path:
    """Где искать чертежи и выгрузки контроллера.

    Рядом с кодом (`input`) — как в сборке, где пользователь кладёт файлы
    возле exe. Если такой папки нет, берётся `doc/input` уровнем выше:
    исходные материалы проекта весят гигабайты и лежат вне репозитория.
    """
    local = BASE_DIR / "input"
    if local.is_dir():
        return local
    external = BASE_DIR.parent / "doc" / "input"
    return external if external.is_dir() else local


INPUT_DIR = _env_path("CONTUR_INPUT_DIR", _input_default())

# Промежуточные файлы конвейера
PARSED_LUA_JSON = OUTPUT_DIR / "parsed_lua.json"
PARSED_LUA_OBJECTS_JSON = OUTPUT_DIR / "parsed_lua_objects.json"
MATCHED_DEVICES_XML = OUTPUT_DIR / "matched_devices.xml"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


# ---------------------------------------------------------------- модель YOLO
# CONTUR_YOLO_MODEL — путь к весам. По умолчанию ищем обученные модели
# в runs/detect/<запуск>/weights/best.pt, начиная с train2.
YOLO_RUNS_DIR = _env_path("CONTUR_YOLO_RUNS_DIR", BASE_DIR / "runs" / "detect")
YOLO_PREFERRED_RUNS = ("train2", "train8", "train82", "train22", "train")


def find_yolo_model() -> Path:
    # Возвращает путь к весам YOLO. Явно заданный путь важнее найденного.
    explicit = os.environ.get("CONTUR_YOLO_MODEL")
    if explicit:
        return Path(explicit).expanduser()

    # Порядок поиска: рядом с приложением, затем внутри сборки (если модель вшита)
    search_roots = [YOLO_RUNS_DIR]
    if BUNDLE_DIR != BASE_DIR:
        search_roots.append(BUNDLE_DIR / "runs" / "detect")

    for root in search_roots:
        for run in YOLO_PREFERRED_RUNS:
            candidate = root / run / "weights" / "best.pt"
            if candidate.exists():
                return candidate

    # Ничего не нашли — отдаём ожидаемый путь, чтобы сообщение об ошибке
    # показало, куда именно положить модель
    return YOLO_RUNS_DIR / YOLO_PREFERRED_RUNS[0] / "weights" / "best.pt"


YOLO_MODEL_PATH = find_yolo_model()

# ---------------------------------------------------------------- движок вывода
# Детекция — единственная медленная операция проекта, и OpenVINO её ускоряет.
# Замер на контрольном листе A0, минимум из трёх прогонов:
#
#   PyTorch          73 с   257 рамок
#   OpenVINO CPU     49 с   257 рамок, все совпали попарно без единого сдвига
#   OpenVINO GPU     24 с   256 рамок, десять сдвинуты на 34-1202 пикселя
#
# Встроенная графика быстрее втрое, но меняет результат, поэтому устройство
# задано жёстко: съехать на неё случайно нельзя.
#
# CONTUR_YOLO_ENGINE: auto (по умолчанию) | torch | openvino.
# При auto берётся выгруженная модель, если она есть, иначе веса .pt —
# приложение работает и без установленного openvino.
YOLO_ENGINE = os.environ.get("CONTUR_YOLO_ENGINE", "auto").strip().lower()
OPENVINO_DEVICE = "intel:cpu"


def find_openvino_model(weights: Optional[Path] = None) -> Optional[Path]:
    """Папка с выгруженной моделью рядом с весами, если ею можно пользоваться.

    ultralytics называет её best_openvino_model. Выгружать надо той же
    пачкой, какой пользуется детектор, и с изменяемой размерностью —
    иначе последняя, неполная пачка плиток отвергается:
        python tools/export_openvino.py

    Наличия папки мало: без установленного openvino загрузка такой модели
    падает. Проверка спасает от состояния, в котором выгрузка осталась
    от прежней установки, а сам пакет уже удалён.
    """
    if YOLO_ENGINE == "torch":
        return None

    if importlib.util.find_spec("openvino") is None:
        return None

    weights = Path(weights or YOLO_MODEL_PATH)
    exported = weights.with_name(weights.stem + "_openvino_model")
    return exported if exported.is_dir() else None


# Параметры нарезки изображения для детекции.
# TILE_SIZE — размер вырезаемого куска растра, IMGSZ — размер входа сети.
# Раньше они были склеены: плитка всегда подавалась в сеть один к одному,
# и относительный размер символа нельзя было менять, не меняя DPI.
# Модель обучалась при imgsz=1024, поэтому его и держим.
#
# Профили подобраны замерами (tools/calibrate_scale.py) на листе A0.
# При обучении рамка занимала 0.20-0.30 стороны кадра; относительный размер
# на входе задаётся отношением «размер символа / размер плитки».
#
# Сквозной замер на листе A0 (не только детекция, но и результат конвейера):
#
#   профиль    dpi/плитка  найдено  опознано  связок  труб  соединений  время
#   fast       200/1024    279      156       4675    655   251         36 с
#   balanced   300/1024    257      174       4297    877   226         80 с
#   accurate   200/512     269      157       4482    743   244         131 с
#
# Ни один вариант не лучше остальных по всем показателям. По умолчанию стоит
# balanced: он опознаёт по подписи на 18 устройств больше (174 против 156),
# а неопознанные устройства — главный источник потерь. Плата — вдвое больше
# фрагментов трубопроводов и на 25 соединений меньше.
#
# fast быстрее вдвое и даёт более цельные трубы, accurate — меньше всего
# сомнительных детекций (12 против 30 у fast).
YOLO_PROFILES = {
    "fast": {"dpi": 200, "tile": 1024, "step": 768},
    "balanced": {"dpi": 300, "tile": 1024, "step": 768},
    "accurate": {"dpi": 200, "tile": 512, "step": 384},
}
YOLO_PROFILE = os.environ.get("CONTUR_YOLO_PROFILE", "balanced").strip().lower()
_profile = YOLO_PROFILES.get(YOLO_PROFILE, YOLO_PROFILES["balanced"])

YOLO_TILE_SIZE = int(os.environ.get("CONTUR_YOLO_TILE_SIZE", _profile["tile"]))
YOLO_IMGSZ = int(os.environ.get("CONTUR_YOLO_IMGSZ", 1024))
YOLO_STEP = int(os.environ.get("CONTUR_YOLO_STEP", _profile["step"]))
YOLO_CONF_THRESHOLD = float(os.environ.get("CONTUR_YOLO_CONF", 0.25))
YOLO_DPI = int(os.environ.get("CONTUR_YOLO_DPI", _profile["dpi"]))

# ---------------------------------------------------------------- PostgreSQL
DB_CONFIG = {
    "host": os.environ.get("CONTUR_DB_HOST", "localhost"),
    "port": int(os.environ.get("CONTUR_DB_PORT", 5432)),
    "database": os.environ.get("CONTUR_DB_NAME", "hmi_design"),
    "user": os.environ.get("CONTUR_DB_USER", "postgres"),
    "password": os.environ.get("CONTUR_DB_PASSWORD", ""),
}

# ---------------------------------------------------------------- типы устройств
# Обозначения устройств: имя в Lua = <техобъект><ТИП><номер>, например LA_TANK1V101.
# Список был зашит в device_matcher и не содержал GS, HDOG, SB, G, HL, HLA —
# 29 устройств из 401 не разбирались и не могли быть сопоставлены вовсе.
# Пополненный под один проект, он снова оказался неполон под второй:
# в mozzarella не разбирались VC, HA, TC, FC — 13 устройств из 730.
# Полноту списка держит tests/test_device_names.py на обоих проектах.
# Дополняется через CONTUR_DEVICE_TYPES (через запятую).
DEVICE_TYPES = [
    "V", "VC",                            # клапаны, в т.ч. регулирующие
    "M",                                  # моторы, насосы, мешалки
    "DI", "DO", "AI", "AO",               # дискретные и аналоговые сигналы
    "LS", "LT",                           # уровень
    "TE", "TC",                           # температура и её регуляторы
    "QT",                                 # проводимость
    "FQT", "FC",                          # расход и его регуляторы
    "PT", "PC",                           # давление
    "GS",                                 # датчики положения
    "FS",                                 # реле потока
    "WT", "WC",                           # вес и его регулятор
    "LC",                                 # регулятор уровня
    "SB", "HL", "HLA",                    # кнопки и лампы
    "HA",                                 # аварийная сигнализация, сирены
    "G",                                  # прочее оборудование
]

# Что означает обозначение — словами. Собрано из ОБОЗНАЧЕНИЯ.md, где типы
# разобраны по всем main.io.lua проекта; здесь та же таблица рядом со списком,
# чтобы они не разъезжались.
#
# Нужно только окну — карточке устройства: имя `LA_TANK1V1` само по себе
# не говорит, клапан это или лампа. В выгрузки не уходит: редактор получает
# обозначение (`device_type`) и разбирает его по-своему.
DEVICE_TYPE_NAMES = {
    "V": "Клапан: отсечной, донный, дренажный, CIP",
    "VC": "Регулирующий клапан",
    "M": "Мотор: насос, мешалка, вибромотор",
    "DI": "Дискретный вход — сигнал от смежной системы",
    "DO": "Дискретный выход — сигнал смежной системе",
    "AI": "Аналоговый вход",
    "AO": "Аналоговый выход",
    "LS": "Сигнализатор уровня, дискретный",
    "LT": "Уровнемер, текущий уровень",
    "TE": "Термометр, текущая температура",
    "TC": "ПИД-регулятор температуры",
    "QT": "Преобразователь проводимости, граница сред",
    "FQT": "Расходомер со счётчиком",
    "FC": "ПИД-регулятор расхода",
    "PT": "Датчик давления",
    "PC": "ПИД-регулятор разряжения",
    "GS": "Датчик положения люка",
    "FS": "Реле потока",
    "WT": "Тензодатчик, весы",
    "WC": "Весовой регулятор",
    "LC": "Регулятор уровня",
    "SB": "Кнопка, аварийная",
    "HL": "Лампа: зелёная, оранжевая, красная, освещение",
    "HLA": "Сигнальная колонна, проблесковый маячок",
    "HA": "Сирена",
    "G": "Прочее: IO-Link-хабы, связь с постами, watchdog",
}


def device_type_name(device_type: str) -> str:
    """Обозначение словами: «V» → «Клапан: отсечной, донный, дренажный, CIP»."""
    return DEVICE_TYPE_NAMES.get((device_type or "").upper(), "")


# Имена, которые не являются устройствами и не должны разбираться на тип.
# Сюда попал WATCHDOG: из него вырезалось «HDOG», и девять программных
# сторожевых таймеров превращались в устройства с искажённым техобъектом
# (LINE_M1WATCHDOG11 -> объект 'LINE_M1WATC', тип 'HDOG').
NON_DEVICE_MARKERS = ("WATCHDOG",)


def is_device_name(name: str) -> bool:
    upper = (name or "").upper()
    return bool(name) and not any(marker in upper for marker in NON_DEVICE_MARKERS)


# Сигналы ввода-вывода контроллера: канал, а не оборудование.
#
# На технологических листах (P&ID) их не рисуют — обозначений вида DI1/DO2/AI3
# там нет вовсе (0 из 430 меток контрольного листа и 0 из 100 на листе 13
# mozzarella). Но на листах обмена сигналами рисуют: прогон по всем 265
# страницам проекта сопоставил 117 сигналов из 147, и все они на страницах
# 5-14, где на девяти из десяти вообще ничего, кроме сигналов, нет.
#
# Сигналов много — 38% устройств молокохранилища и 63% mozzarella, — поэтому
# на технологическом листе они топили настоящие пропажи. Но признак «не
# рисуются» относится к листу, а не к проекту: см. sheet_draws_signals
# в device_matcher.build_match_report, где лист спрашивают о нём самого.
IO_SIGNAL_TYPES = {"DI", "DO", "AI", "AO"}

_extra_types = os.environ.get("CONTUR_DEVICE_TYPES", "")
if _extra_types:
    DEVICE_TYPES += [t.strip().upper() for t in _extra_types.split(",") if t.strip()]


# Какие обозначения соответствуют классам модели YOLO (valve, sensor, pump).
# Нужно, чтобы сверять распознанный класс с подписью на чертеже: если модель
# видит насос, а подпись говорит V12 — привязка подписи почти наверняка неверна.
# HA (сирены) сюда намеренно не входит: на схеме это не технологическое
# устройство, модель такого класса не знает, и сверка давала бы ложные
# расхождения — как у ламп HL/HLA, которых здесь тоже нет.
DEVICE_CLASS_TYPES = {
    "valve": {"V", "VC"},
    "pump": {"M"},
    "sensor": {"LS", "LT", "TE", "TC", "QT", "FQT", "FC", "PT", "PC", "GS"},
}


def device_type_matches_class(device_type: str, cls_name: str) -> Optional[bool]:
    # True — согласуются, False — противоречат, None — судить не по чему
    if not device_type or not cls_name:
        return None
    expected = DEVICE_CLASS_TYPES.get(cls_name.lower())
    if not expected:
        return None
    return device_type.upper() in expected


# ---------------------------------------------------------------- цвета

# Цвет устройства по обозначению. Живёт здесь, а не в окне: этими же цветами
# красится выгрузка для редактора мнемосхем, а она работает без Qt.
DEVICE_TYPE_COLORS = {
    "V": "#e74c3c",
    "DI": "#3498db",
    "DO": "#2980b9",
    "AI": "#2ecc71",
    "AO": "#27ae60",
    "PT": "#f39c12",
    "LT": "#9b59b6",
    "TE": "#1abc9c",
    "LS": "#8e44ad",
    "QT": "#d35400",
    "FQT": "#c0392b",
    "PC": "#7f8c8d",
    "M": "#34495e",
    "GS": "#16a085",
    "HDOG": "#e67e22",
    "SB": "#2c3e50",
    "HL": "#f1c40f",
    "HLA": "#f39c12",
    "G": "#95a5a6",
}

DEFAULT_DEVICE_COLOR = "#000000"

# Обводка устройства в окне. Заменила закрашенный кружок: он вставал поверх
# символа Eplan и прятал ровно то, на что человек смотрит. Обводка идёт
# по габариту символа, внутри остаётся сам чертёж.
#
# Только для окна: ни в один экспорт эти значения не попадают — устройство
# уезжает своей геометрией и своими данными, а подсветка в окне
# редактора не касается.
DEVICE_OUTLINE_COLOR = os.environ.get("CONTUR_DEVICE_OUTLINE", "#ffffff")
# Толщина в пикселях экрана: обводка не должна утолщаться с масштабом
DEVICE_OUTLINE_WIDTH = float(os.environ.get("CONTUR_DEVICE_OUTLINE_WIDTH", "2"))
# Габарит, когда своей геометрии у устройства нет (лист ещё не размечен)
DEVICE_OUTLINE_FALLBACK = float(os.environ.get("CONTUR_DEVICE_OUTLINE_SIZE", "16"))

# Цвета положения устройства в операции. Ими красится состояние элемента
# в выгрузке для редактора мнемосхем: у каждого устройства список states
# по всем шагам, где оно открывается или закрывается
DEVICE_STATE_COLORS = {
    "opened": "#2ecc71",
    "closed": "#e74c3c",
}


# Цвета рамок технологических объектов: раздаются по имени объекта
TECH_OBJECT_PALETTE = [
    "#ff0000", "#009600", "#0000ff", "#ffa500", "#800080",
    "#ffc0cb", "#a52a2a", "#008080", "#ffff00", "#808000",
]


def device_color(device_type: str) -> str:
    return DEVICE_TYPE_COLORS.get((device_type or "").upper(), DEFAULT_DEVICE_COLOR)


def tech_object_color(name: str) -> str:
    # Цвет по имени объекта. Раньше индекс брался из hash(str), а он
    # рандомизируется при каждом запуске Python: у одного и того же объекта
    # цвет менялся от запуска к запуску, и выгрузка не совпала бы с окном.
    digest = hashlib.md5((name or "").encode("utf-8")).digest()
    return TECH_OBJECT_PALETTE[digest[0] % len(TECH_OBJECT_PALETTE)]


def device_types_pattern() -> str:
    # Готовая группа для регулярного выражения.
    # Длинные обозначения идут первыми, чтобы FQT не разбирался как QT.
    ordered = sorted(set(DEVICE_TYPES), key=lambda t: (-len(t), t))
    return "(" + "|".join(ordered) + ")"


# ---------------------------------------------------------------- распознавание
# Максимальное расстояние от текста до контура при подборе имени, пункты
CONTOUR_NAME_MAX_DISTANCE = float(os.environ.get("CONTUR_NAME_MAX_DISTANCE", 200))
# На сколько пунктов подпись может выступать над верхней кромкой контура
# и всё ещё считаться его подписью. Eplan ставит обозначение над символом,
# и у устройств на самой кромке ряда подпись выходит наружу — на контрольном
# листе на 2.2-8.0 пт. Порог тут не решающий: от 10 до 50 пт результат
# один и тот же, отбор держит проверка «контур такое устройство ждёт»
# (см. device_matcher.match_labels_above_contours). Взята примерно строка
# текста, чтобы подпись не притягивалась с другого конца листа.
LABEL_ABOVE_CONTOUR_MAX = float(os.environ.get("CONTUR_LABEL_ABOVE_CONTOUR", 15))
# Допуск при сшивании пунктирных сегментов в контур, пункты
CONTOUR_POINT_TOLERANCE = float(os.environ.get("CONTUR_POINT_TOLERANCE", 0.5))
# Насколько подпись может выйти за поперечный размер контура и всё ещё
# считаться стоящей над ним (или сбоку от него), пункты. Нужен, чтобы
# подпись не притягивалась к углу тесной рамки, от которой она стоит
# по диагонали — см. contour_detector.find_all_contour_names_by_proximity.
CONTOUR_NAME_SPAN_TOLERANCE = float(os.environ.get("CONTUR_NAME_SPAN_TOLERANCE", 5))
