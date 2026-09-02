# theme.py
# Оформление окна одним листом стилей.
#
# Зачем. Вид собирался из случайных кусков: у каждой кнопки свой цвет прямо
# в коде сборки панели, у полей — стиль по умолчанию Fusion, разделители
# панелей не видно вовсе. Понять, где кончается одна панель и начинается
# другая, было можно только по содержимому.
#
# Здесь цвета названы один раз и применяются ко всему окну сразу. Смысл
# цветных кнопок остался прежним (загрузка Lua — синяя, чертёж — зелёный,
# разметка — сиреневая), но цвет теперь берётся из палитры по свойству
# `accent`, а не пишется строкой стиля рядом с кнопкой.
#
# Ничего, кроме внешнего вида: ни один обработчик, ни одно имя виджета
# и ни одна настройка отсюда не меняются. Проверки интерфейса собирают
# окно без темы — и должны проходить одинаково с ней и без неё.

# Палитра. Светлая, спокойная: на чертеже и так много цвета — красные линии
# разметки, цветные рамки техобъектов, — и окно не должно с ним спорить
BG = "#f3f4f6"           # фон окна
SURFACE = "#ffffff"      # панели, поля ввода, списки
CANVAS = "#eef0f3"       # подложка под схемой: белый лист должен читаться листом
BORDER = "#e3e6ea"       # обычная граница
BORDER_STRONG = "#cfd4da"  # граница под курсором
TEXT = "#1f2328"
MUTED = "#6b7280"
ACCENT = "#2563eb"       # выбранное, полоса вкладки, разделитель под курсором
ACCENT_SOFT = "#e8f0fe"  # подсветка строки списка

# Цвета кнопок по назначению. Кнопка объявляет своё назначение свойством
# `accent`, а не строкой стиля: одинаковые кнопки в разных местах окна
# перестали расходиться на пару оттенков
ACCENTS = {
    "lua": "#2f81f7",        # загрузка описания контроллера
    "objects": "#e08c1a",    # загрузка объектов
    "pdf": "#2da44e",        # чертёж
    "markup": "#8957e5",     # разметка моделью
    "export": "#8957e5",     # выгрузка в файл
    "db": "#0969da",         # выгрузка в базу
    "muted": "#5b6673",      # настройки
}

# Насколько затемнять цвет кнопки под курсором и при нажатии
HOVER_MIX = 0.12
PRESSED_MIX = 0.22


def _shade(color: str, amount: float) -> str:
    """Тот же цвет, но темнее: для состояний «под курсором» и «нажата»."""
    value = color.lstrip("#")
    parts = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(part * (1 - amount)):02x}" for part in parts)


def _accent_rules() -> str:
    rules = []
    for name, color in ACCENTS.items():
        rules.append(f"""
QPushButton[accent="{name}"] {{
    background-color: {color};
    border: 1px solid {_shade(color, 0.08)};
    color: #ffffff;
    font-weight: 600;
}}
QPushButton[accent="{name}"]:hover {{ background-color: {_shade(color, HOVER_MIX)}; }}
QPushButton[accent="{name}"]:pressed {{ background-color: {_shade(color, PRESSED_MIX)}; }}
QPushButton[accent="{name}"]:disabled {{
    background-color: {BORDER};
    border-color: {BORDER};
    color: {MUTED};
}}""")
    return "\n".join(rules)


STYLE = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-size: 12px;
}}
QToolTip {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    padding: 4px 6px;
}}

/* ------------------------------------------------ меню и строка состояния */
QMenuBar {{ background-color: {SURFACE}; border-bottom: 1px solid {BORDER}; }}
QMenuBar::item {{ padding: 6px 10px; background: transparent; }}
QMenuBar::item:selected {{ background-color: {ACCENT_SOFT}; color: {ACCENT}; }}
QMenu {{ background-color: {SURFACE}; border: 1px solid {BORDER}; padding: 4px; }}
QMenu::item {{ padding: 6px 24px 6px 12px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {ACCENT_SOFT}; color: {ACCENT}; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
QStatusBar {{ background-color: {SURFACE}; border-top: 1px solid {BORDER}; }}
QStatusBar QLabel {{ color: {MUTED}; }}

/* ------------------------------------------------------------ разделители */
/* Границу панели видно, и она подсвечивается, когда за неё можно взяться */
QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:hover {{ background-color: {ACCENT}; }}
QSplitter::handle:horizontal {{ width: 6px; }}
QSplitter::handle:vertical {{ height: 6px; }}

/* ------------------------------------------------------------------ схема */
QGraphicsView {{
    background-color: {CANVAS};
    border: 1px solid {BORDER};
}}

/* ---------------------------------------------------------------- кнопки */
QPushButton {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT};
}}
QPushButton:hover {{ background-color: #f6f7f9; border-color: {MUTED}; }}
QPushButton:pressed {{ background-color: #eceef1; }}
QPushButton:disabled {{ color: {MUTED}; background-color: {BG}; border-color: {BORDER}; }}
QPushButton:checked {{
    background-color: {ACCENT_SOFT};
    border-color: {ACCENT};
    color: {ACCENT};
}}
{_accent_rules()}

/* --------------------------------------------------------- поля и списки */
QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    border-radius: 6px;
    padding: 4px 6px;
    selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {ACCENT_SOFT};
    selection-color: {TEXT};
}}

QTreeWidget, QTableWidget, QListWidget {{
    background-color: {SURFACE};
    alternate-background-color: #fafbfc;
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QTreeWidget::item, QTableWidget::item {{ padding: 3px 2px; }}
QTreeWidget::item:hover, QTableWidget::item:hover {{ background-color: #f2f5fa; }}
QTreeWidget::item:selected, QTableWidget::item:selected {{
    background-color: {ACCENT_SOFT};
    color: {TEXT};
}}
QHeaderView::section {{
    background-color: {BG};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 5px 6px;
    color: {MUTED};
    font-weight: 600;
}}

/* --------------------------------------------------------------- вкладки */
QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 6px; top: -1px; }}
QTabBar::tab {{
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 10px;
    margin-right: 2px;
    color: {MUTED};
}}
QTabBar::tab:hover {{ color: {TEXT}; }}
QTabBar::tab:selected {{ color: {ACCENT}; border-bottom-color: {ACCENT}; }}

/* ---------------------------------------------------------------- группы */
QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {MUTED};
    font-weight: 600;
}}
QCheckBox {{ spacing: 6px; padding: 2px 0; }}

/* ------------------------------------------------------------- прогресс */
QProgressBar {{
    background-color: {BORDER};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: {TEXT};
}}
QProgressBar::chunk {{ background-color: {ACCENT}; border-radius: 4px; }}

/* ------------------------------------------------------------- прокрутка */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle {{ background: #c9ced6; border-radius: 5px; min-height: 24px; min-width: 24px; }}
QScrollBar::handle:hover {{ background: {MUTED}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QScrollArea {{ border: none; background-color: {BG}; }}
"""


def apply(app) -> None:
    """Одевает приложение. Зовётся один раз при запуске."""
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
