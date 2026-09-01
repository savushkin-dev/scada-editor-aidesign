# ui_panel.py
# Сборка левой панели окна.
#
# _create_left_panel был на 256 строк подряд: кнопки загрузки, выбор схемы,
# переход по листам, профиль детекции, экспорт, полоса прогресса, фильтр,
# слои, легенда, мини-карта, поиск и дерево устройств — всё одним куском,
# где найти нужный виджет можно было только прокруткой.
#
# Здесь то же самое, но блоками: create_left_panel показывает состав панели
# целиком на одном экране, а подробности каждого блока лежат рядом.
#
# Это сборщик, а не отдельный слой: создаваемые виджеты становятся полями
# окна (window.load_pdf_btn, window.device_tree и так далее) — их гасят
# на время работы, обновляют и читают из обработчиков. Разрывать эту связь
# здесь нечем и незачем; вынесена именно сборка.
#
# Порядок важен: MiniMap берёт window.graphics_view, поэтому панель
# собирается после создания сцены.
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QLineEdit, QProgressBar, QPushButton,
                               QTreeWidget, QVBoxLayout, QWidget)

import config
from widgets import MiniMap

# Назначение кнопки вместо строки стиля рядом с ней: цвет, наведение,
# нажатие и погашенное состояние берутся из палитры (`theme.ACCENTS`).
# Раньше у каждой кнопки был свой кусок CSS, и одинаковые по смыслу кнопки
# в разных местах окна расходились на пару оттенков

# Слои поверх чертежа: поле окна -> подпись
LAYERS = (
    ("layer_background", "Разметка (подложка)"),
    ("layer_contours", "Контуры"),
    ("layer_contour_names", "Имена контуров"),
    ("layer_devices", "Устройства"),
    ("layer_device_names", "Подписи устройств"),
)


def create_left_panel(window) -> QWidget:
    """Собирает левую панель целиком. Состав виден здесь, подробности ниже."""
    panel = QWidget()
    layout = QVBoxLayout(panel)

    layout.addWidget(_load_group(window))
    layout.addLayout(_progress_row(window))

    window.status_label = QLabel("Готов к работе")
    window.status_label.setWordWrap(True)
    window.status_label.setStyleSheet("color: gray; font-style: italic;")
    layout.addWidget(window.status_label)

    window.file_info_label = QLabel("Файлы не загружены")
    window.file_info_label.setWordWrap(True)
    layout.addWidget(window.file_info_label)

    layout.addWidget(QLabel(""))
    layout.addWidget(_settings_button(window))
    layout.addWidget(QLabel(""))

    layout.addWidget(_filter_group(window))
    _add_view_block(window, layout)

    layout.addWidget(QLabel(""))
    layout.addWidget(QLabel("Устройства:"))
    _add_device_block(window, layout)

    return panel


# ---------------------------------------------------------------- загрузка

def _load_group(window) -> QGroupBox:
    group = QGroupBox("Загрузка данных")
    layout = QVBoxLayout(group)

    # Кнопки держим полями: на время обработки их нужно гасить, иначе
    # можно запустить загрузку другого файла поверх идущей разметки
    window.load_lua_btn = _button(
        "Lua: устройства", "Загрузить main.io.lua и main.wago.lua (Ctrl+O)",
        window.load_lua_files, accent="lua")
    layout.addWidget(window.load_lua_btn)

    window.load_objects_btn = _button(
        "Lua: объекты", "Загрузить main.objects.lua (Ctrl+Shift+O)",
        window.load_lua_objects_file, accent="objects")
    layout.addWidget(window.load_objects_btn)

    window.load_pdf_btn = _button(
        "Открыть PDF", "Загрузить чертёж схемы (Ctrl+P)", window.load_pdf_file,
        accent="pdf")
    layout.addWidget(window.load_pdf_btn)

    layout.addLayout(_scheme_row(window))
    layout.addLayout(_page_row(window))
    layout.addLayout(_profile_row(window))
    _add_action_buttons(window, layout)

    return group


def _scheme_row(window) -> QHBoxLayout:
    # Загруженные схемы: переключение между ними не требует повторной
    # разметки, а раньше новый PDF ложился поверх старого
    row = QHBoxLayout()
    row.addWidget(QLabel("Схема:"))

    window.scheme_selector = QComboBox()
    window.scheme_selector.setToolTip(
        "Загруженные схемы — переключение без повторной обработки")
    window.scheme_selector.currentIndexChanged.connect(window._on_scheme_selected)
    window.scheme_selector.setEnabled(False)
    # Иначе длинное имя файла растягивает панель на всю его ширину
    window.scheme_selector.setSizeAdjustPolicy(
        QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    window.scheme_selector.setMinimumContentsLength(12)
    row.addWidget(window.scheme_selector, 1)

    window.close_scheme_btn = _button("✕", "Убрать текущую схему из списка",
                                      window.close_current_scheme)
    window.close_scheme_btn.setMaximumWidth(32)
    window.close_scheme_btn.setEnabled(False)
    row.addWidget(window.close_scheme_btn)
    return row


def _page_row(window) -> QHBoxLayout:
    # Переход по листам многостраничного файла. Раньше соседнюю страницу
    # можно было открыть только заново выбрав файл и введя её номер
    row = QHBoxLayout()

    window.prev_page_btn = _button("‹", "Предыдущий лист того же файла",
                                   lambda: window._step_page(-1))
    window.prev_page_btn.setMaximumWidth(32)
    row.addWidget(window.prev_page_btn)

    window.page_label = QLabel("Лист —")
    window.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    row.addWidget(window.page_label, 1)

    window.next_page_btn = _button("›", "Следующий лист того же файла",
                                   lambda: window._step_page(1))
    window.next_page_btn.setMaximumWidth(32)
    row.addWidget(window.next_page_btn)

    window.page_list_btn = _button("Все листы…", "Выбрать лист из списка с названиями",
                                   window.choose_page)
    row.addWidget(window.page_list_btn)

    for widget in (window.prev_page_btn, window.next_page_btn, window.page_list_btn):
        widget.setEnabled(False)
    return row


def _profile_row(window) -> QHBoxLayout:
    # Профиль детекции: точный находит меньше сомнительных устройств,
    # но нарезает лист мельче и потому считает дольше.
    # Подписи короткие, пояснения в подсказке: длинные строки в списке
    # требовали 426 пикселей ширины и раздували всю панель
    row = QHBoxLayout()
    row.addWidget(QLabel("Точность:"))

    window.detection_profile = QComboBox()
    window.detection_profile.addItem("Обычно", "balanced")
    window.detection_profile.addItem("Быстро", "fast")
    window.detection_profile.addItem("Точнее", "accurate")
    window.detection_profile.setToolTip(
        "Обычно — ~88 с, больше опознанных устройств\n"
        "Быстро — ~40 с, цельнее трубопроводы\n"
        "Точнее — ~2 мин, меньше ложных срабатываний")
    # Ширина по содержимому, а не по самой длинной строке списка
    window.detection_profile.setSizeAdjustPolicy(
        QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    window.detection_profile.setMinimumContentsLength(8)
    order = {"balanced": 0, "fast": 1, "accurate": 2}
    window.detection_profile.setCurrentIndex(order.get(config.YOLO_PROFILE, 0))
    row.addWidget(window.detection_profile, 1)
    return row


def _add_action_buttons(window, layout: QVBoxLayout) -> None:
    window.markup_pdf_btn = _button(
        "Разметить схему", "Найти устройства моделью YOLO (Ctrl+M)",
        window.start_markup, accent="markup")
    window.markup_pdf_btn.setEnabled(False)
    layout.addWidget(window.markup_pdf_btn)

    layout.addWidget(_button("Открыть SVG", "Подложить готовую разметку (Ctrl+Shift+S)",
                             window.load_svg_background))

    window.report_btn = _button(
        "Отчёт", "Что есть в Lua, но не найдено на чертеже, и наоборот",
        window.show_match_report)
    window.report_btn.setEnabled(False)
    layout.addWidget(window.report_btn)

    layout.addWidget(_button(
        "В файл", "Экспорт схемы в XML или JSON (Ctrl+E)", window.export_to_file,
        accent="export"))

    window.export_pg_btn = _button(
        "В PostgreSQL", "Выгрузить схему в базу (Ctrl+D)", window.export_to_postgresql,
        accent="db")
    window.export_pg_btn.setEnabled(False)
    layout.addWidget(window.export_pg_btn)


# ---------------------------------------------------------------- ход работы

def _progress_row(window) -> QHBoxLayout:
    # Полоса и кнопка отмены живут вместе: разметка идёт до двух минут,
    # и раньше прервать её было нечем — оставалось закрывать приложение
    row = QHBoxLayout()

    window.progress_bar = QProgressBar()
    window.progress_bar.setVisible(False)
    row.addWidget(window.progress_bar, 1)

    window.cancel_btn = _button("Отмена", "Прервать разметку", window.cancel_markup)
    window.cancel_btn.setMaximumWidth(80)
    window.cancel_btn.setVisible(False)
    row.addWidget(window.cancel_btn)
    return row


def _settings_button(window) -> QPushButton:
    return _button("⚙️ Отображение", "Настройки отображения схемы",
                   window.open_settings_dialog, accent="muted")


# ---------------------------------------------------------------- что показывать

def _filter_group(window) -> QGroupBox:
    group = QGroupBox("Фильтр и слои")
    layout = QVBoxLayout(group)

    window.tech_filter = QComboBox()
    window.tech_filter.addItem("Все объекты")
    window.tech_filter.currentTextChanged.connect(window.update_display)
    layout.addWidget(QLabel("Тех. объект:"))
    layout.addWidget(window.tech_filter)

    # Что показывать поверх чертежа. Раньше эти переключатели жили
    # в отдельном окне настроек, куда за ними надо было ходить
    for attribute, title in LAYERS:
        box = QCheckBox(title)
        box.setChecked(True)
        box.stateChanged.connect(window.update_display)
        setattr(window, attribute, box)
        layout.addWidget(box)

    return group


def _add_view_block(window, layout: QVBoxLayout) -> None:
    # Легенда цветов: тип устройства читался только из подсказки
    window.legend_label = QLabel("")
    window.legend_label.setWordWrap(True)
    window.legend_label.setVisible(False)
    layout.addWidget(window.legend_label)

    # Мини-карта: на листе A0 при увеличении вчетверо на экране помещается
    # около процента чертежа, и понять, в каком углу находишься, нельзя
    window.mini_map = MiniMap(window.graphics_view)
    window.graphics_view.view_changed.connect(window.mini_map.update)
    layout.addWidget(window.mini_map)

    layout.addWidget(_button("Вписать схему (F)", "", window.reset_view))


def _add_device_block(window, layout: QVBoxLayout) -> None:
    # Устройств больше двух сотен в трёх десятках групп — без поиска
    # нужное приходилось прокручивать глазами
    window.device_search = QLineEdit()
    window.device_search.setPlaceholderText("Поиск: имя, тип или тех. объект (Ctrl+F)")
    window.device_search.setClearButtonEnabled(True)
    window.device_search.textChanged.connect(window._filter_device_tree)
    layout.addWidget(window.device_search)

    window.device_tree = QTreeWidget()
    window.device_tree.setHeaderLabels(["Устройство", "Тип", "Артикул"])
    window.device_tree.itemClicked.connect(window.on_tree_item_clicked)
    window.device_tree.itemDoubleClicked.connect(window.on_tree_item_double_clicked)
    layout.addWidget(window.device_tree)

    window.search_result_label = QLabel("")
    window.search_result_label.setStyleSheet("color: gray;")
    layout.addWidget(window.search_result_label)


def _button(title: str, tooltip: str, handler, accent: str = "") -> QPushButton:
    """Кнопка панели. `accent` — назначение из палитры (`theme.ACCENTS`)."""
    button = QPushButton(title)
    if tooltip:
        button.setToolTip(tooltip)
    button.clicked.connect(handler)
    if accent:
        button.setProperty("accent", accent)
    return button
