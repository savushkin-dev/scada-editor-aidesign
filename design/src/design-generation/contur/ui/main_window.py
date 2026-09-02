# main_window.py
# Главное окно приложения: загрузка данных, запуск этапов конвейера,
# отображение схемы и экспорт.
#
# Фоновые потоки вынесены в workers.py, виджеты — в widgets.py.
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.ui import app_log
from contur.core import config
from contur.core import errors
from contur.ui import scene_painter
from contur.ui import theme
from contur.ui import ui_panel
from contur.export import xml_io

import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QRectF, QTimer, qInstallMessageHandler
from PySide6.QtGui import (QAction, QBrush, QColor, QGuiApplication,
                           QKeySequence)
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QFrame,
                               QScrollArea, QStyle,
                               QHBoxLayout, QInputDialog, QLabel, QMainWindow,
                               QMessageBox, QPushButton,
                               QTextEdit, QTreeWidgetItem, QVBoxLayout,
                               QWidget, QCheckBox, QSpinBox)

from contur.ui import app_settings
from contur.pdf import markup_cache
from contur.core.data_models import Contour, DeviceMatch
from contur.ui.details_panel import DetailsPanel
from contur.matching import device_dossier
from contur.scene import build_scene
from contur.matching.device_matcher import build_match_report, format_match_report, generate_output_xml
from contur.pdf.extract_geometry import page_count
from contur.lua.objects_loader import Operation as TechOperation, objects_data
from contur.pdf.svg_geometry import (build_pipelines, detect_coordinate_system, detected_device_count,
                          device_centers, extract_line_segments, find_junction_points,
                          format_markup_report, get_svg_dimensions, markup_quality_report,
                          named_device_count,
                          snap_devices_to_geometry, tolerance_scale)
from contur.export import exporters
from contur.export.xml_export import get_pdf_page_size

from contur.ui.workers import (DeviceMatchingThread, GeometryExtractionThread, LuaObjectsParsingThread,
                     LuaParsingThread, PostgresExportThread, YOLOMarkingThread)
from contur.ui.widgets import (DeviceGraphicsItem, GraphicsView, OperationsBrowserWidget,
                     PageChooser, PostgresDialog, SettingsDialog, Splitter)


@dataclass
class LoadedScheme:
    """Одна загруженная схема: страница PDF со всем, что по ней получено.

    Раньше приложение держало ровно одну схему, но при загрузке следующей
    ничего не сбрасывало: старый размеченный SVG оставался фоном под новыми
    контурами, и две схемы накладывались друг на друга. Здесь состояние
    каждой схемы хранится отдельно, между ними можно переключаться,
    не размечая заново (разметка листа стоит около 80 секунд).
    """
    pdf_path: str
    page: int
    total_pages: int = 1
    contours: List[Contour] = field(default_factory=list)
    matches: List[DeviceMatch] = field(default_factory=list)
    svg_path: Optional[str] = None
    geometry_xml: Optional[str] = None
    match_context: Optional[tuple] = None
    tech_colors: Dict[str, object] = field(default_factory=dict)

    @property
    def key(self) -> tuple:
        return (os.path.abspath(self.pdf_path), self.page)

    @property
    def title(self) -> str:
        name = os.path.basename(self.pdf_path)
        if self.total_pages > 1:
            return f"{name} — стр. {self.page + 1}"
        return name


class DeviceVisualizer(QMainWindow):
    # Стартовая ширина левой панели. Раньше ширина бралась целиком из
    # содержимого: длинные подписи кнопок и списков требовали 690 пикселей
    # минимума, а при разворачивании окна панель забирала треть экрана.
    #
    # Это именно стартовые границы, а не потолок: тянуть панель можно куда
    # угодно, вплоть до полного сворачивания. Пределы держат только первый
    # запуск, дальше ширина берётся из запомненного положения разделителя
    PANEL_MIN_WIDTH = 240
    PANEL_MAX_WIDTH = 420
    # Насколько панель разрешено сжимать перетаскиванием, прежде чем она
    # свернётся совсем
    PANEL_FOLD_WIDTH = 140

    # Панель сведений справа. Ширина стартовая: разделитель тянется,
    # и его положение запоминается между запусками
    DETAILS_MIN_WIDTH = 260
    DETAILS_WIDTH = 380

    # Потоки, которые могут работать в момент закрытия окна, и как назвать
    # каждый пользователю. Дожидались здесь только разметку, а остальные пять
    # уничтожались на ходу: Qt отвечает на это «QThread: Destroyed while
    # thread is still running», и выгрузка в базу обрывалась посреди записи.
    # Порядок — от самого долгого к самому короткому.
    BACKGROUND_THREADS: ClassVar[tuple] = (
        ("yolo_thread", "разметка чертежа"),
        ("matching_thread", "сопоставление устройств"),
        ("postgres_thread", "выгрузка в PostgreSQL"),
        ("geometry_thread", "извлечение геометрии"),
        ("lua_thread", "разбор Lua"),
        ("lua_objects_thread", "разбор объектов"),
    )

    # Общий срок ожидания на все потоки, мс. Срок общий, а не на каждый:
    # ожидание идёт в потоке окна, и шесть отдельных сроков подряд означали бы
    # полминуты замершего окна вместо пяти секунд.
    THREAD_WAIT_MS = 5000

    # Состояние устройства в технологической операции. Лежали внутри метода
    # и пересоздавались при каждой перестройке дерева
    OPERATION_STATUS_ICONS: ClassVar[dict] = {
        "opened": "🔓 ",
        "closed": "🔒 ",
        "not_used": "⚪ ",
    }
    OPERATION_STATUS_COLORS: ClassVar[dict] = {
        "opened": QColor(76, 175, 80),
        "closed": QColor(244, 67, 54),
        "not_used": QColor(158, 158, 158),
    }
    OPERATION_STATUS_TEXT: ClassVar[dict] = {
        "opened": "ОТКРЫТО",
        "closed": "ЗАКРЫТО",
        "not_used": "Не используется",
    }

    # Цвета живут в config.py: теми же красится выгрузка для редактора
    # мнемосхем, а она работает без Qt
    DEVICE_TYPE_COLORS: ClassVar[dict] = {
        device_type: QColor(value)
        for device_type, value in config.DEVICE_TYPE_COLORS.items()
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация сопоставленных устройств")
        # Размер был зашит как 1800x1000: на ноутбуке 1366x768 окно вылезало
        # за края экрана, и до нижних кнопок было не добраться
        if not app_settings.restore_geometry(self):
            available = QGuiApplication.primaryScreen().availableGeometry()
            self.resize(min(1800, available.width() - 80),
                        min(1000, available.height() - 80))
            self.move(available.left() + 40, available.top() + 40)

        self.matches: List[DeviceMatch] = []
        self.contours: List[Contour] = []
        self.tech_object_colors: Dict[str, QColor] = {}
        self.svg_background_path: Optional[str] = None

        self.current_pdf_path: Optional[str] = None
        self.current_page: int = 0
        self._last_match_context = None

        # Загруженные схемы и активная из них. Поля выше — состояние активной;
        # при переключении оно сохраняется в схему и восстанавливается из другой
        self.schemes: List[LoadedScheme] = []
        self.active_scheme: Optional[LoadedScheme] = None
        self.current_geometry_xml: Optional[str] = None
        self.current_lua_json: Optional[str] = None
        self.current_lua_objects_json: Optional[str] = None

        # Исходные пути — чтобы восстановить сеанс при следующем запуске
        self.current_lua_files: List[str] = []
        self.current_objects_file: Optional[str] = None

        self.geometry_thread: Optional[GeometryExtractionThread] = None
        self.matching_thread: Optional[DeviceMatchingThread] = None
        self.lua_thread: Optional[LuaParsingThread] = None
        self.lua_objects_thread: Optional[LuaObjectsParsingThread] = None

        self.yolo_thread: Optional[YOLOMarkingThread] = None
        self.postgres_thread: Optional[PostgresExportThread] = None
        # Параметры подключения к базе, кроме пароля
        self.db_settings: Dict[str, object] = {}

        self.contour_alpha = QSpinBox()
        self.contour_alpha.setRange(0, 255)
        self.contour_alpha.setValue(50)

        self.show_contour_names = QCheckBox()
        self.show_contour_names.setChecked(True)

        self.show_device_names = QCheckBox()
        self.show_device_names.setChecked(True)

        self.show_tooltips = QCheckBox()
        self.show_tooltips.setChecked(True)

        self.current_selected_operation = None
        # Устройство, выбранное в дереве: подсвечивается на схеме
        self.selected_match: Optional[DeviceMatch] = None
        # Пока показано временное сообщение, координаты в подпись не пишутся
        self._status_message_shown = False
        # Что было доступно до начала обработки — чтобы вернуть ровно это
        self._enabled_when_idle = {}
        # Разметку из кэша показываем молча, по кнопке — с сообщением
        self._markup_started_by_user = True

        self._init_ui()
        # Путь к чертежу проще бросить в окно, чем искать его в диалоге
        self.setAcceptDrops(True)

    def _create_actions(self):
        # Раньше горячими клавишами были одиночные буквы без модификатора:
        # нажатие «S» открывало диалог выбора SVG, «P» — выбора PDF. Из-за
        # этого в окне нельзя было завести ни одного поля ввода
        def action(title, slot, shortcut=None, tip=None):
            item = QAction(title, self)
            item.triggered.connect(slot)
            if shortcut:
                item.setShortcut(QKeySequence(shortcut))
            if tip:
                item.setStatusTip(tip)
            return item

        self.act_load_lua = action("Загрузить Lua (устройства)…", self.load_lua_files,
                                   "Ctrl+O", "devices.lua и nodes.lua")
        self.act_load_objects = action("Загрузить Lua (объекты)…", self.load_lua_objects_file,
                                       "Ctrl+Shift+O", "main.objects.lua")
        self.act_load_pdf = action("Загрузить PDF…", self.load_pdf_file,
                                   "Ctrl+P", "Чертёж схемы")
        self.act_load_svg = action("Загрузить готовый SVG…", self.load_svg_background,
                                   "Ctrl+Shift+S")
        self.act_load_xml = action("Открыть XML…", self.load_xml_file, "Ctrl+Shift+X")
        self.act_markup = action("Разметить схему", self.start_markup,
                                 "Ctrl+M", "Найти устройства моделью YOLO")
        self.act_match = action("Сопоставить устройства", self.rematch_devices,
                                "Ctrl+Shift+M",
                                "Пересобрать каталог по загруженным Lua")
        self.act_cancel = action("Прервать разметку", self.cancel_markup, "Esc")
        self.act_report = action("Отчёт о расхождениях", self.show_match_report, "Ctrl+R")
        self.act_clear_cache = action(
            "Очистить кэш разметки…", self.clear_markup_cache,
            tip="Удалить сохранённую разметку всех листов")
        self.act_export_file = action("Экспорт в XML или JSON…", self.export_to_file, "Ctrl+E")
        self.act_export_pg = action("Экспорт в PostgreSQL…", self.export_to_postgresql,
                                    "Ctrl+D")
        self.act_fit = action("Вписать схему", self.reset_view, "F")
        self.act_find = action("Найти устройство", self.focus_device_search, "Ctrl+F")
        self.act_clear_details = action(
            "Сбросить выбранное", self.clear_selection, "Ctrl+Shift+D",
            "Очистить панель сведений и снять подсветку со схемы")

        # Показ панелей. Схему закрывать нечем — она остаётся всегда,
        # а всё вокруг убирается с глаз и возвращается теми же клавишами
        self.act_show_panel = self._pane_action(
            "Левая панель", "Ctrl+B", lambda visible: self._show_pane("panel", visible))
        self.act_show_details = self._pane_action(
            "Панель сведений", "Ctrl+I", lambda visible: self._show_pane("details", visible))
        self.act_show_operations = self._pane_action(
            "Список операций", "Ctrl+J", lambda visible: self._show_pane("operations", visible))
        self.act_settings = action("Настройки отображения…", self.open_settings_dialog)
        self.act_quit = action("Выход", self.close, "Ctrl+Q")

        # Начальное состояние совпадает с кнопками: пока нет ни схемы,
        # ни разметки, эти действия недоступны
        for item in (self.act_markup, self.act_match, self.act_report,
                     self.act_export_pg, self.act_cancel):
            item.setEnabled(False)

    def _create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")
        file_menu.addAction(self.act_load_lua)
        file_menu.addAction(self.act_load_objects)
        file_menu.addAction(self.act_load_pdf)
        file_menu.addSeparator()
        # Списки последних файлов: те же схемы открываются изо дня в день
        self.recent_pdf_menu = file_menu.addMenu("Последние PDF")
        self.recent_lua_menu = file_menu.addMenu("Последние Lua")
        file_menu.addSeparator()
        file_menu.addAction(self.act_load_svg)
        file_menu.addAction(self.act_load_xml)
        file_menu.addSeparator()
        file_menu.addAction(self.act_quit)

        process_menu = menu.addMenu("Обработка")
        process_menu.addAction(self.act_markup)
        process_menu.addAction(self.act_match)
        process_menu.addAction(self.act_cancel)
        process_menu.addSeparator()
        process_menu.addAction(self.act_report)
        process_menu.addSeparator()
        process_menu.addAction(self.act_clear_cache)

        export_menu = menu.addMenu("Экспорт")
        export_menu.addAction(self.act_export_file)
        export_menu.addAction(self.act_export_pg)

        view_menu = menu.addMenu("Вид")
        view_menu.addAction(self.act_find)
        view_menu.addAction(self.act_fit)
        view_menu.addAction(self.act_clear_details)
        view_menu.addSeparator()
        view_menu.addAction(self.act_show_panel)
        view_menu.addAction(self.act_show_details)
        view_menu.addAction(self.act_show_operations)
        view_menu.addSeparator()
        view_menu.addAction(self.act_settings)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self._create_actions()
        self._create_menu()

        self.status_bar = self.statusBar()

        self.navigation_hint = QLabel(
            "Колесо — масштаб · зажатое колесо или пробел+ЛКМ — перетаскивание · "
            "стрелки — шаг (Shift — крупнее) · двойной щелчок или Home — вписать · "
            "щелчок по устройству — сведения о нём")
        self.navigation_hint.setStyleSheet("color: gray;")
        self.status_bar.addWidget(self.navigation_hint)

        self.zoom_label = QLabel("Масштаб: —")
        self.zoom_label.setMinimumWidth(110)
        self.status_bar.addPermanentWidget(self.zoom_label)

        self.coord_label = QLabel("Координаты: --, --")
        self.coord_label.setMinimumWidth(200)
        self.status_bar.addPermanentWidget(self.coord_label)

        outer_layout = QVBoxLayout(central_widget)

        # Полоска предложения открыть прошлый сеанс. Не модальное окно:
        # молчание — тоже ответ, и оно не должно ничего открывать
        session_row = QHBoxLayout()
        self.session_bar = QLabel("")
        self.session_bar.setVisible(False)
        self.session_bar.setStyleSheet(
            "background-color: #FFF8E1; padding: 6px; border: 1px solid #FFE082;")
        session_row.addWidget(self.session_bar, 1)

        self.session_open_btn = QPushButton("Открыть")
        self.session_open_btn.setVisible(False)
        self.session_open_btn.clicked.connect(self._restore_last_session)
        session_row.addWidget(self.session_open_btn)

        self.session_hide_btn = QPushButton("Скрыть")
        self.session_hide_btn.setVisible(False)
        self.session_hide_btn.clicked.connect(self._hide_session_bar)
        session_row.addWidget(self.session_hide_btn)
        outer_layout.addLayout(session_row)

        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout, 1)

        main_splitter = Splitter(Qt.Orientation.Horizontal)
        self.main_splitter = main_splitter
        main_layout.addWidget(main_splitter)

        # Вид создаём до левой панели: на него ссылается мини-карта
        self.graphics_view = GraphicsView()
        self.graphics_view.setParent(self)
        self.graphics_view.mouse_moved.connect(self.update_mouse_coordinates)
        self.graphics_view.zoom_changed.connect(self.update_zoom_label)
        self.graphics_view.scene_clicked.connect(self.on_scene_clicked)

        # Панель в прокручиваемой области: содержимого в ней на добрую тысячу
        # пикселей по высоте, и на невысоком экране нижняя часть — дерево
        # устройств — сминалась до пары строк
        left_panel = self._create_left_panel()
        panel_scroll = QScrollArea()
        panel_scroll.setWidget(left_panel)
        panel_scroll.setWidgetResizable(True)
        panel_scroll.setFrameShape(QFrame.Shape.NoFrame)
        # Ширину выбирает человек: панель тянется от узкой полосы до сколько
        # угодно и сворачивается совсем. Раньше она была зажата между 240
        # и 420 пикселями — ни расширить, чтобы прочитать длинные имена,
        # ни убрать, чтобы посмотреть на схему
        panel_scroll.setMinimumWidth(self.PANEL_FOLD_WIDTH)
        self.panel_scroll = panel_scroll
        main_splitter.addWidget(panel_scroll)

        # Ширину берём от содержимого, а не назначаем числом: при другом
        # шрифте или масштабе экрана готовое число либо обрежет подписи,
        # либо оставит пустую полосу
        needed = left_panel.minimumSizeHint().width() + panel_scroll.frameWidth() * 2
        needed += self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
        self.panel_width = max(self.PANEL_MIN_WIDTH, min(self.PANEL_MAX_WIDTH, needed))

        # Схема и панель сведений — рядом. Панель не всплывающим окном:
        # её читают, глядя на схему, и окно пришлось бы отодвигать каждый раз.
        # И не третьей колонкой окна: ширину она берёт у схемы, а не у левой
        # панели, которой при узком окне и так впритык.
        #
        # Панель одна на всё: она показывает и устройство, и операцию. Раньше
        # у браузера операций внизу была своя, с теми же вкладками
        scene_row = Splitter(Qt.Orientation.Horizontal)
        self.scene_splitter = scene_row
        scene_row.addWidget(self.graphics_view)

        self.details_panel = DetailsPanel()
        self.details_panel.setMinimumWidth(self.DETAILS_MIN_WIDTH)
        self.details_panel.cleared.connect(self.clear_selection)
        scene_row.addWidget(self.details_panel)

        scene_row.setStretchFactor(0, 1)
        scene_row.setStretchFactor(1, 0)
        scene_row.setSizes([1000, self.DETAILS_WIDTH])
        # Схема не сворачивается: убрать с глаз можно всё, кроме неё
        scene_row.setCollapsible(0, False)

        right_splitter = Splitter(Qt.Orientation.Vertical)
        self.right_splitter = right_splitter
        right_splitter.addWidget(scene_row)

        self.operations_browser = OperationsBrowserWidget()
        self.operations_browser.operation_selected.connect(self.on_operation_selected_for_devices)
        right_splitter.addWidget(self.operations_browser)

        main_splitter.addWidget(right_splitter)

        # Лишняя ширина уходит схеме, а не панели. Без этого при разворачивании
        # окна свободное место делилось поровну, и на экране 3840 панель
        # разрасталась до 1260 пикселей — треть окна под кнопки
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([self.panel_width, 1400])
        main_splitter.setCollapsible(1, False)

        # Панель -> где она лежит: по этому и показывают, и прячут
        self.panes = {
            "panel": (main_splitter, 0, panel_scroll),
            "details": (scene_row, 1, self.details_panel),
            "operations": (right_splitter, 1, self.operations_browser),
        }

        # Так же по высоте: растёт вид схемы, а не список операций
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 0)
        right_splitter.setSizes([700, 300])
        right_splitter.setCollapsible(0, False)

        # Настройки читаем после сборки: они выставляются в готовые виджеты
        self._load_settings()
        self._refresh_recent_menus()
        self._offer_last_session()

    def _pane_action(self, title: str, shortcut: str, handler) -> QAction:
        # Переключатель панели: галочка в меню и горячая клавиша, как
        # в редакторах — Ctrl+B боковая панель, Ctrl+J нижняя
        item = QAction(title, self)
        item.setCheckable(True)
        item.setChecked(True)
        item.setShortcut(QKeySequence(shortcut))
        item.toggled.connect(handler)
        return item

    def _show_pane(self, name: str, visible: bool) -> None:
        """Показать или спрятать панель целиком.

        Не то же самое, что свернуть её разделителем: свёрнутую видно
        по границе и она разворачивается двойным щелчком, спрятанная уходит
        совсем — вместе со своей границей.
        """
        pane = self.panes.get(name)
        if pane is None:
            return
        pane[2].setVisible(visible)

    def _pane_actions(self) -> dict:
        return {"panel": self.act_show_panel, "details": self.act_show_details,
                "operations": self.act_show_operations}

    def _offer_last_session(self):
        # Каждый запуск начинался с трёх диалогов выбора файлов. Предложение
        # показываем полоской, а не модальным окном: молчание — тоже ответ,
        # и оно не должно ничего открывать
        session = app_settings.load_session()
        if not app_settings.has_session(session):
            return

        self._pending_session = session
        name = os.path.basename(session["pdf"]) if session["pdf"] else "прошлый набор Lua"
        page = session.get("page", 0)
        title = f"{name} (лист {page + 1})" if session["pdf"] and page else name

        self.session_bar.setText(f"Продолжить с «{title}»?")
        self.session_bar.setVisible(True)
        self.session_open_btn.setVisible(True)
        self.session_hide_btn.setVisible(True)

    def _restore_last_session(self):
        session = getattr(self, "_pending_session", None)
        self._hide_session_bar()
        if not session:
            return

        if session["lua"]:
            self._start_lua_parsing(session["lua"])
        if session["objects"]:
            self._start_objects_parsing(session["objects"])
        if session["pdf"]:
            self._open_pdf(session["pdf"], session.get("page", 0))

    def _hide_session_bar(self):
        self.session_bar.setVisible(False)
        self.session_open_btn.setVisible(False)
        self.session_hide_btn.setVisible(False)

    def _refresh_recent_menus(self):
        # Список последних файлов: пропавшие не показываем
        for menu, kind, opener in ((self.recent_pdf_menu, "pdf", self._open_recent_pdf),
                                   (self.recent_lua_menu, "lua", self._open_recent_lua)):
            menu.clear()
            files = app_settings.recent_files(kind)
            for path in files:
                act = QAction(os.path.basename(path), self)
                act.setStatusTip(path)
                # Обработчик привязываем значением, а не замыканием: внешний
                # цикл заканчивается раньше первого нажатия, и через замыкание
                # opener у всех пунктов оказывался последним — файл из списка
                # «Последние PDF» уходил в разбор Lua
                act.triggered.connect(
                    lambda checked=False, p=path, call=opener: call(p))
                menu.addAction(act)
            menu.setEnabled(bool(files))

    def _open_recent_pdf(self, path: str):
        self._open_pdf(path, 0)

    def _open_recent_lua(self, path: str):
        self._start_lua_parsing([path])

    def update_zoom_label(self, scale: float):
        self.zoom_label.setText(f"Масштаб: {scale * 100:.0f}%")

    def _scene_size(self) -> Tuple[float, float]:
        # Размер холста в координатах сцены: сначала подложка, иначе контуры
        if self.graphics_view.svg_item is not None:
            try:
                bounds = self.graphics_view.svg_item.boundingRect()
                if bounds.width() > 0 and bounds.height() > 0:
                    return bounds.width(), bounds.height()
            except RuntimeError:
                pass

        if self.contours:
            return (max((c.bounds[2] for c in self.contours), default=0),
                    max((c.bounds[3] for c in self.contours), default=0))
        return 0.0, 0.0

    def _device_at(self, x: float, y: float) -> Optional[DeviceMatch]:
        # Устройство под курсором. Допуск задаётся в пикселях экрана и
        # переводится в координаты сцены, иначе на большом увеличении
        # попасть в точку невозможно, а на общем виде ловится что попало
        scene = self.graphics_view._scene
        if scene is None:
            return None

        tolerance = 5.0 / max(self.graphics_view.current_scale(), 1e-6)
        area = QRectF(x - tolerance, y - tolerance, tolerance * 2, tolerance * 2)
        for item in scene.items(area):
            if isinstance(item, DeviceGraphicsItem):
                return item.device_data
        return None

    def update_mouse_coordinates(self, x: float, y: float):
        # Координаты курсора в процентах холста — в тех же единицах уходит
        # экспорт, поэтому по ним удобно сверяться с XML.
        #
        # Раньше этот метод всё считал и выбрасывал: ни одного вывода в теле
        # не было, и подпись навсегда оставалась «Координаты: --, --».
        if self._status_message_shown:
            return

        width, height = self._scene_size()
        if width <= 0 or height <= 0:
            self.coord_label.setText("Координаты: --, --")
            return

        percent_x = max(0.0, min(100.0, x / width * 100))
        percent_y = max(0.0, min(100.0, y / height * 100))
        text = f"X: {percent_x:.1f}%  Y: {percent_y:.1f}%"

        device = self._device_at(x, y)
        if device is not None:
            name = device.lua_name or device.pdf_name
            text += f"  ·  {name}"
            if device.tech_object and device.tech_object not in name:
                text += f" ({device.tech_object})"

        self.coord_label.setText(text)

    def show_coord_message(self, text: str, milliseconds: int = 1500):
        # Временное сообщение вместо координат. Раньше подпись перебивалась
        # обратно первым же движением мыши, и сообщение о копировании
        # исчезало, не успев прочитаться
        self._status_message_shown = True
        self.coord_label.setText(text)
        QTimer.singleShot(milliseconds, self._clear_coord_message)

    def _clear_coord_message(self):
        self._status_message_shown = False
        self.coord_label.setText("Координаты: --, --")

    def on_operation_selected_for_devices(self, operation: TechOperation):
        """Выбрана операция: панель показывает её, а схема — положение устройств.

        Панель одна на всё, и показывает она то, что выбрали последним:
        щёлкнули по устройству — устройство, щёлкнули по операции — операцию.
        Своей панели у списка операций больше нет.
        """
        self.current_selected_operation = operation
        self.select_operation(operation)
        if not self.matches:
            return

        for match in self.matches:
            self._update_device_graphics_item(match, {"status": "not_used"})

        devices_status = objects_data.get_devices_for_operation(operation.id)

        for match in self.matches:
            for name_variant in [match.lua_name, match.pdf_name, match.device_type]:
                if name_variant and name_variant in devices_status:
                    status = devices_status[name_variant]
                    details = objects_data.get_device_details_in_operation(operation.id, name_variant)
                    if details:
                        self._update_device_graphics_item(match, details)
                    else:
                        self._update_device_graphics_item(match, {"status": status})
                    break

        self._update_device_tree(operation)

        # Дерево перестроено — вернём в нём выбранное устройство. Подсветку
        # на схеме операция не снимает: она красит положение устройств,
        # а выбрано по-прежнему то же самое
        if self.selected_match is not None:
            self._select_tree_item(self.selected_match)

    def _update_device_graphics_item(self, match: DeviceMatch, status_info: dict):
        scene = self.graphics_view._scene
        for item in scene.items():
            if isinstance(item, DeviceGraphicsItem) and item.device_data == match:
                item.set_operation_state(
                    status_info.get("status", "not_used"),
                    status_info.get("state_name", ""),
                    status_info.get("step_name", ""),
                    status_info.get("step_number", -1)
                )
                break

    def _create_left_panel(self) -> QWidget:
        # Сборка вынесена в ui_panel: здесь она была на 256 строк подряд.
        # Создаваемые виджеты становятся полями окна — их гасят на время
        # работы, обновляют и читают из обработчиков
        return ui_panel.create_left_panel(self)

    def load_lua_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите Lua файлы (devices.lua, nodes.lua)",
            app_settings.last_directory("lua"),
            "Lua files (*.lua)"
        )

        if not files:
            return
        self._start_lua_parsing(files)

    def _start_lua_parsing(self, files: List[str]):
        # Отделено от диалога: тем же путём идут перетаскивание файла в окно,
        # список последних файлов и восстановление прошлого сеанса
        files = [path for path in files if os.path.exists(path)]
        if not files:
            return

        self.current_lua_files = list(files)
        app_settings.remember_directory("lua", files[0])
        for path in files:
            app_settings.remember_recent("lua", path)
        self._refresh_recent_menus()

        self.status_label.setText("Парсинг Lua файлов...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.lua_thread = LuaParsingThread(files)
        self.lua_thread.progress.connect(self._on_lua_progress)
        self.lua_thread.finished.connect(self._on_lua_finished)
        self.lua_thread.error.connect(self._on_lua_error)
        self.lua_thread.start()

    def _on_lua_progress(self, message: str):
        self.status_label.setText(message)

    def _on_lua_finished(self, success: bool, data: dict):
        self.progress_bar.setVisible(False)
        if success:
            self.current_lua_json = str(config.PARSED_LUA_JSON)
            self.status_label.setText(f"✅ Lua парсинг завершен: {len(data.get('devices', []))} устройств")
            self.status_label.setStyleSheet("color: green;")
            self._update_file_info()
            QMessageBox.information(
                self,
                "Успех",
                f"Lua файлы успешно обработаны\n"
                f"Устройств: {len(data.get('devices', []))}\n"
                f"IO узлов: {len(data.get('nodes', []))}"
            )
            # Чертёж мог быть загружен раньше Lua — тогда конвейер стоит
            # и без этого никогда не дойдёт до сопоставления
            self._continue_after_lua()
        else:
            self.status_label.setText("❌ Ошибка парсинга Lua")
            self.status_label.setStyleSheet("color: red;")

    def _on_lua_error(self, error: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Ошибка парсинга Lua")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Ошибка", error)

    def load_lua_objects_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите main.objects.lua файл",
            app_settings.last_directory("lua"),
            "Lua files (*.lua)"
        )

        if not file_path:
            return
        self._start_objects_parsing(file_path)

    def _start_objects_parsing(self, file_path: str):
        if not os.path.exists(file_path):
            return

        self.current_objects_file = file_path
        app_settings.remember_directory("lua", file_path)

        self.status_label.setText("Парсинг main.objects.lua...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.lua_objects_thread = LuaObjectsParsingThread(file_path)
        self.lua_objects_thread.progress.connect(self._on_lua_objects_progress)
        self.lua_objects_thread.finished.connect(self._on_lua_objects_finished)
        self.lua_objects_thread.error.connect(self._on_lua_objects_error)
        self.lua_objects_thread.start()

    def _on_lua_objects_progress(self, message: str):
        self.status_label.setText(message)

    def _on_lua_objects_finished(self, success: bool, data: dict):
        self.progress_bar.setVisible(False)
        if success:
            self.current_lua_objects_json = str(config.PARSED_LUA_OBJECTS_JSON)

            try:
                if hasattr(objects_data, 'load_from_json'):
                    objects_data.load_from_json(data)
                else:
                    config.ensure_output_dir()
                    with open(config.PARSED_LUA_OBJECTS_JSON, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                    objects_data.load()
            except Exception as e:
                print(f"Ошибка загрузки объектов: {e}")

            self.status_label.setText(f"✅ Парсинг объектов завершен: {len(data.get('tech_objects', []))} объектов")
            self.status_label.setStyleSheet("color: green;")

            self.operations_browser._load_operations()

            # Описание объектов сменилось — досье устройств устарело
            if self.matches:
                print(device_dossier.summary(device_dossier.attach(self.matches)))

            QMessageBox.information(
                self,
                "Успех",
                f"main.objects.lua успешно обработан\n"
                f"Тех. объектов: {len(data.get('tech_objects', []))}\n"
                f"Операций: {len(data.get('operations', []))}\n"
                f"Состояний: {len(data.get('states', []))}\n"
                f"Шагов: {len(data.get('steps', []))}"
            )
        else:
            self.status_label.setText("❌ Ошибка парсинга объектов")
            self.status_label.setStyleSheet("color: red;")

    def _on_lua_objects_error(self, error: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Ошибка парсинга объектов")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Ошибка", error)

    # ---------------------------------------------------- загруженные схемы

    def _remember_active_scheme(self):
        # Переносит текущее состояние окна в активную схему
        scheme = self.active_scheme
        if scheme is None:
            return
        scheme.contours = list(self.contours)
        scheme.matches = list(self.matches)
        scheme.svg_path = self.svg_background_path
        scheme.geometry_xml = self.current_geometry_xml
        scheme.match_context = self._last_match_context
        scheme.tech_colors = dict(self.tech_object_colors)

    def _apply_scheme(self, scheme: LoadedScheme):
        # Восстанавливает состояние окна из схемы и перерисовывает вид
        self.active_scheme = scheme
        self.current_pdf_path = scheme.pdf_path
        self.current_page = scheme.page
        self.contours = list(scheme.contours)
        self.matches = list(scheme.matches)
        self.svg_background_path = scheme.svg_path
        self.current_geometry_xml = scheme.geometry_xml
        self._last_match_context = scheme.match_context
        self.tech_object_colors = dict(scheme.tech_colors)

        # Фон снимаем всегда: иначе размеченный SVG предыдущей схемы
        # остаётся под контурами новой
        self.graphics_view.clear_svg_background()
        if scheme.svg_path and os.path.exists(scheme.svg_path):
            self.graphics_view.load_svg_background(scheme.svg_path)

        self._allow_markup(bool(scheme.pdf_path))
        self._allow_postgres(bool(scheme.svg_path))
        self._allow_report(scheme.match_context is not None)

        self._update_tech_filter()
        self._update_device_tree()
        self._update_file_info()
        self._refresh_page_controls()
        # Схема сменилась целиком — вписываем её заново
        self.draw_scene(fit=True)

    def _refresh_page_controls(self):
        scheme = self.active_scheme
        total = scheme.total_pages if scheme else 0
        page = scheme.page if scheme else 0

        multipage = bool(scheme and total > 1)
        self.prev_page_btn.setEnabled(multipage and page > 0)
        self.next_page_btn.setEnabled(multipage and page < total - 1)
        self.page_list_btn.setEnabled(multipage)
        self.page_label.setText(f"Лист {page + 1} из {total}" if scheme else "Лист —")

    def _step_page(self, delta: int):
        # Соседний лист того же файла. Раньше для этого надо было заново
        # выбрать файл в диалоге и ввести номер страницы
        scheme = self.active_scheme
        if not scheme:
            return

        target = scheme.page + delta
        if not (0 <= target < scheme.total_pages):
            return

        self._remember_active_scheme()
        self._open_pdf(scheme.pdf_path, target)

    def choose_page(self):
        scheme = self.active_scheme
        if not scheme or scheme.total_pages <= 1:
            return

        dialog = PageChooser(self, scheme.pdf_path, scheme.total_pages, scheme.page)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_page is not None:
            self._remember_active_scheme()
            self._open_pdf(scheme.pdf_path, dialog.selected_page)

    def _refresh_scheme_selector(self):
        # Перестраиваем список, не вызывая обработчик выбора
        self.scheme_selector.blockSignals(True)
        self.scheme_selector.clear()
        for scheme in self.schemes:
            self.scheme_selector.addItem(scheme.title)
        if self.active_scheme in self.schemes:
            self.scheme_selector.setCurrentIndex(self.schemes.index(self.active_scheme))
        self.scheme_selector.blockSignals(False)

        has_schemes = bool(self.schemes)
        self.scheme_selector.setEnabled(has_schemes)
        self.close_scheme_btn.setEnabled(has_schemes)

    def _on_scheme_selected(self, index: int):
        if not (0 <= index < len(self.schemes)):
            return
        scheme = self.schemes[index]
        if scheme is self.active_scheme:
            return

        self._remember_active_scheme()
        self._apply_scheme(scheme)
        self.status_label.setText(f"Схема: {scheme.title}")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")

    def close_current_scheme(self):
        # Убирает текущую схему из списка и показывает соседнюю
        if not self.active_scheme:
            return

        index = self.schemes.index(self.active_scheme)
        self.schemes.pop(index)

        if self.schemes:
            self._apply_scheme(self.schemes[min(index, len(self.schemes) - 1)])
        else:
            self.active_scheme = None
            self.current_pdf_path = None
            self.contours, self.matches = [], []
            self.svg_background_path = None
            self.current_geometry_xml = None
            self._last_match_context = None
            self.tech_object_colors = {}
            self.graphics_view.clear_svg_background()
            self._allow_markup(False)
            self._allow_postgres(False)
            self._allow_report(False)
            self._update_tech_filter()
            self._update_device_tree()
            self._update_file_info()
            self.draw_scene()

        self._refresh_scheme_selector()
        self._refresh_page_controls()

    def load_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите PDF файл с геометрией",
            app_settings.last_directory("pdf"),
            "PDF files (*.pdf)"
        )

        if not file_path:
            return
        self._open_pdf(file_path)

    def _open_pdf(self, file_path: str, page: Optional[int] = None):
        # Отделено от диалога: тем же путём идут перетаскивание файла в окно,
        # список последних файлов, восстановление сеанса и переход по страницам
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Файл не найден", file_path)
            return

        # Файл сначала читается, и только потом становится текущим. Раньше
        # current_pdf_path присваивался до проверки: после отказа окно
        # считало чертёж загруженным, и «Разметить схему» шла по битому пути
        try:
            total_pages = page_count(file_path)
        except Exception as e:
            app_log.write(f"не удалось открыть {file_path}: {e!r}")
            QMessageBox.critical(self, "Не удалось открыть чертёж",
                                 errors.describe(e, file_path))
            return

        if total_pages < 1:
            # Обрезанный PDF открывается без ошибки и показывает ноль страниц
            QMessageBox.critical(self, "Не удалось открыть чертёж",
                                 "В файле нет ни одной страницы — он повреждён "
                                 "или выгрузился не полностью."
                                 f"\n\nФайл: {os.path.basename(file_path)}")
            return

        app_settings.remember_directory("pdf", file_path)
        app_settings.remember_recent("pdf", file_path)
        self._refresh_recent_menus()

        self.current_pdf_path = file_path
        self.current_page = 0

        if page is not None:
            self.current_page = max(0, min(page, total_pages - 1))
        elif total_pages > 1:
            chosen, ok = QInputDialog.getInt(
                self, "Выбор страницы",
                f"В файле {total_pages} страниц. Какую обработать?",
                1, 1, total_pages, 1
            )
            if not ok:
                return
            self.current_page = chosen - 1

        # Заводим схему под этот лист. Если он уже загружен — просто
        # переключаемся, не обрабатывая заново
        scheme = LoadedScheme(pdf_path=file_path, page=self.current_page,
                              total_pages=total_pages)
        existing = next((s for s in self.schemes if s.key == scheme.key), None)

        self._remember_active_scheme()

        if existing is not None:
            self._apply_scheme(existing)
            self._refresh_scheme_selector()
            self.status_label.setText(f"Схема уже загружена: {existing.title}")
            self.status_label.setStyleSheet("color: gray; font-style: italic;")
            return

        self.schemes.append(scheme)
        self._apply_scheme(scheme)
        self._refresh_scheme_selector()

        self._allow_markup(True)
        page_info = f" (страница {self.current_page + 1} из {total_pages})" if total_pages > 1 else ""
        self.status_label.setText(f"PDF загружен: {os.path.basename(file_path)}{page_info}")

        if not self.current_lua_json and not os.path.exists(config.PARSED_LUA_JSON):
            reply = QMessageBox.question(
                self,
                "Lua данные не найдены",
                "Не найдены Lua данные. Сначала загрузить Lua файлы?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Разбор Lua продолжит конвейер сам — см. _continue_after_lua
                self.load_lua_files()
                return

        self._start_geometry_extraction()

    def _start_geometry_extraction(self):
        # Отделено от _open_pdf: сюда же возвращается конвейер, если Lua
        # догрузили после чертежа и геометрию так и не извлекли
        if not self.current_pdf_path:
            return

        self.status_label.setText("Извлечение геометрии из PDF...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.geometry_thread = GeometryExtractionThread(self.current_pdf_path,
                                                        self.current_page)
        self.geometry_thread.progress.connect(self._on_geometry_progress)
        self.geometry_thread.finished.connect(self._on_geometry_finished)
        self.geometry_thread.error.connect(self._on_geometry_error)
        self.geometry_thread.start()

    def _continue_after_lua(self):
        """Продолжает конвейер, если Lua загрузили после чертежа.

        Сопоставление вызывалось только из _on_geometry_finished, а геометрия —
        только из _open_pdf, поэтому порядок «сначала PDF, потом Lua» заходил
        в тупик: чертёж загружен, разметка идёт и красит устройства, а каталог
        пуст и выделять на схеме нечего — self.matches так и остаётся пустым.

        Два пути приводили сюда. Если Lua ещё нет, _open_pdf предлагает
        загрузить их и выходит, не начав геометрию, — а разбор Lua её не
        начинал. Если старый output/parsed_lua.json остался от прошлого
        проекта, вопроса не было вовсе: сопоставление отрабатывало по чужим
        данным, давало ноль и больше не пересчитывалось.
        """
        if not self.current_pdf_path:
            return
        if self.current_geometry_xml:
            self._start_device_matching()
        else:
            self._start_geometry_extraction()

    def rematch_devices(self):
        # Пункт меню: пересобрать каталог по текущим Lua, не открывая PDF заново
        if not self.current_pdf_path:
            QMessageBox.information(self, "Нечего сопоставлять",
                                    "Сначала загрузите чертёж (Ctrl+P).")
            return
        self._continue_after_lua()

    def _build_markup_thread(self) -> YOLOMarkingThread:
        # Передаём уже сопоставленные устройства: их имена выверены техобъектом
        # и точнее сырых подписей с чертежа
        matched = [(m.lua_name, m.coordinates[0], m.coordinates[1])
                   for m in self.matches if m.lua_name]
        return YOLOMarkingThread(self.current_pdf_path, self.current_page,
                                 self.detection_profile.currentData(),
                                 matched_devices=matched)

    def start_markup(self):
        # Путь по нажатию кнопки или пункта меню: о завершении сообщаем
        self._markup_started_by_user = True
        self.markup_pdf_with_yolo()

    def markup_pdf_with_yolo(self):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "Нет PDF", "Сначала загрузите входной PDF файл")
            return

        self._remember_idle_state()
        self._set_busy(True, cancellable=True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Запуск YOLO разметки...")
        self.status_label.setStyleSheet("color: orange;")

        self.yolo_thread = self._build_markup_thread()
        self.yolo_thread.progress.connect(self._on_yolo_progress)
        self.yolo_thread.progress_value.connect(self._on_yolo_progress_value)
        self.yolo_thread.finished.connect(self._on_yolo_finished)
        self.yolo_thread.error.connect(self._on_yolo_error)
        self.yolo_thread.cancelled.connect(self._on_yolo_cancelled)
        self.yolo_thread.start()

    def cancel_markup(self):
        # Поток сам проверяет запрос между пачками плиток и ничего не кладёт
        # в кэш, чтобы недосчитанная разметка не подменила настоящую
        if self.yolo_thread is not None and self.yolo_thread.isRunning():
            self.yolo_thread.requestInterruption()
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("Отмена разметки...")
            self.status_label.setStyleSheet("color: orange;")

    def _allow_markup(self, enabled: bool):
        # Кнопка и пункт меню включаются вместе, иначе меню позволяет то,
        # что кнопка уже запрещает
        self.markup_pdf_btn.setEnabled(enabled)
        self.act_markup.setEnabled(enabled)
        # Условие у сопоставления то же самое — загружен чертёж
        self.act_match.setEnabled(enabled)

    def _allow_report(self, enabled: bool):
        self.report_btn.setEnabled(enabled)
        self.act_report.setEnabled(enabled)

    def _allow_postgres(self, enabled: bool):
        self.export_pg_btn.setEnabled(enabled)
        self.act_export_pg.setEnabled(enabled)

    def _blockable(self) -> tuple:
        # Всё, что нельзя трогать во время обработки: потоки писали бы
        # в одно и то же состояние окна
        return (self.markup_pdf_btn, self.load_pdf_btn, self.load_lua_btn,
                self.load_objects_btn, self.export_pg_btn, self.report_btn,
                self.act_load_lua, self.act_load_objects, self.act_load_pdf,
                self.act_load_svg, self.act_load_xml, self.act_markup,
                self.act_match, self.act_report, self.act_export_file,
                self.act_export_pg)

    def _set_busy(self, busy: bool, cancellable: bool = False):
        for item in self._blockable():
            item.setEnabled(not busy and self._enabled_when_idle.get(item, True))

        self.act_cancel.setEnabled(busy and cancellable)
        self.progress_bar.setVisible(busy)
        self.cancel_btn.setVisible(busy and cancellable)
        self.cancel_btn.setEnabled(busy and cancellable)

        if not busy:
            self.progress_bar.setRange(0, 0)

    def _remember_idle_state(self):
        # Что было доступно до начала обработки — чтобы вернуть ровно это,
        # а не включить всё подряд
        self._enabled_when_idle = {item: item.isEnabled() for item in self._blockable()}

    def _on_yolo_progress(self, message: str):
        self.status_label.setText(message)

    def _on_yolo_progress_value(self, done: int, total: int):
        # Полоса была бесконечной: по ней нельзя было понять, идёт работа
        # минуту или десять
        if total <= 0:
            return
        if self.progress_bar.maximum() != total:
            self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)

    def _on_yolo_cancelled(self):
        self._set_busy(False)
        self._markup_started_by_user = True
        self.status_label.setText("Разметка отменена")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")

    def _on_yolo_finished(self, success: bool, svg_path: str):
        self._set_busy(False)

        if success:
            self.svg_background_path = svg_path
            self.status_label.setText("✅ YOLO разметка завершена успешно")
            self.status_label.setStyleSheet("color: green;")

            # После разметки известна геометрия устройств — переносим точки
            # с текстовых меток на сами устройства, чтобы вид совпадал с экспортом
            self._remember_active_scheme()
            refined = self._refine_device_positions(svg_path)
            self._attach_neighbours(svg_path)
            if refined.get("moved"):
                self._update_device_tree()
                if refined.get("class_conflict"):
                    self.status_label.setText(
                        f"✅ Разметка завершена. Класс модели противоречит подписи "
                        f"у {refined['class_conflict']} устройств — см. отчёт о расхождениях")

            if self.graphics_view.load_svg_background(svg_path):
                self.draw_scene()
                if not self._markup_started_by_user:
                    # Разметка пришла из кэша сама — сообщать не о чем
                    self._markup_started_by_user = True
                    self._allow_postgres(True)
                    return
                QMessageBox.information(
                    self,
                    "Успех",
                    f"PDF успешно размечен!\n"
                    f"Устройства выделены красным цветом\n"
                    f"Трубопроводы - синим\n\n"
                    f"SVG сохранен: {svg_path}"
                )
            else:
                QMessageBox.warning(self, "Предупреждение", "SVG создан, но не может быть отображен")
        else:
            self.status_label.setText("❌ Ошибка YOLO разметки")
            self.status_label.setStyleSheet("color: red;")

    def show_match_report(self):
        # Показывает, что не сошлось между чертежом и конфигурацией контроллера
        if not self._last_match_context:
            QMessageBox.information(self, "Нет данных",
                                    "Сначала загрузите Lua файлы и PDF со схемой")
            return

        lua_data, pdf_contours, device_texts = self._last_match_context
        report = build_match_report(lua_data, pdf_contours, device_texts, self.matches)
        text = format_match_report(report)

        # Если разметка есть — добавляем показатели её качества
        markup_text = self._markup_quality_text()
        if markup_text:
            text = f"{text}\n\n{markup_text}"

        dialog = QDialog(self)
        dialog.setWindowTitle("Отчёт о расхождениях")
        dialog.resize(700, 600)
        layout = QVBoxLayout(dialog)

        view = QTextEdit()
        view.setReadOnly(True)
        view.setFontFamily("Consolas")
        view.setPlainText(text)
        layout.addWidget(view)

        save_btn = QPushButton("Сохранить в файл")

        def save():
            path, _ = QFileDialog.getSaveFileName(
                dialog, "Сохранить отчёт", "отчёт_расхождений.txt", "Текст (*.txt)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(dialog, "Сохранено", path)

        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        dialog.exec()

    def _markup_quality_text(self) -> str:
        # Показатели качества разметки для отчёта
        if not self.svg_background_path or not os.path.exists(self.svg_background_path):
            return ""

        try:
            svg_root = ET.parse(self.svg_background_path).getroot()
            _, scale = detect_coordinate_system(
                svg_root, get_pdf_page_size(self.current_pdf_path, self.current_page))
            dimensions = get_svg_dimensions(svg_root, scale)
            segments = extract_line_segments(svg_root, scale, dimensions, verbose=False)
            geometry_scale = tolerance_scale(svg_root)
            junctions = find_junction_points(segments, verbose=False, scale=geometry_scale)
            pipelines = build_pipelines([s for s in segments if s.color == "blue"],
                                        junctions, verbose=False, scale=geometry_scale)
            return format_markup_report(markup_quality_report(
                segments, junctions, pipelines, detected_device_count(svg_root),
                named_device_count(svg_root)))
        except Exception as e:
            return f"Не удалось оценить качество разметки: {e}"

    def _attach_neighbours(self, svg_path: str) -> None:
        """Соседей по трубам — в досье устройства.

        Трубопроводы строит `scene.build_scene`, и звать его здесь
        дешевле, чем повторять этот же разбор своими руками: положение
        устройств уже уточнено, поэтому просим не трогать его второй раз.
        """
        if not self.matches:
            return
        try:
            build_scene(svg_path, self.matches, self.contours,
                        snap_to_geometry=False)
        except Exception as error:
            print(f"Соседей по трубам определить не удалось: {error}")

    def _refine_device_positions(self, svg_path: str) -> dict:
        # Уточняет координаты устройств по размеченному SVG.
        # Координаты приходят от текстовой метки, а она нарисована рядом
        # с устройством — для мнемосхемы нужнее геометрический центр.
        if not self.matches:
            return {}

        try:
            svg_root = ET.parse(svg_path).getroot()
            _, scale = detect_coordinate_system(
                svg_root, get_pdf_page_size(self.current_pdf_path, self.current_page))
            dimensions = get_svg_dimensions(svg_root, scale)
            segments = extract_line_segments(svg_root, scale, dimensions, verbose=False)
            geometry_scale = tolerance_scale(svg_root)
            return snap_devices_to_geometry(
                self.matches, device_centers(segments, scale=geometry_scale),
                verbose=False, scale=geometry_scale)
        except Exception as e:
            print(f"Не удалось уточнить положение устройств: {e}")
            return {}

    def _on_yolo_error(self, error: str):
        self._set_busy(False)
        self._markup_started_by_user = True
        self.status_label.setText("❌ Ошибка YOLO разметки")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Ошибка", error)

    def _on_geometry_progress(self, message: str):
        self.status_label.setText(message)

    def _on_geometry_finished(self, success: bool, xml_path: str, contours: list, texts: list):
        self.progress_bar.setVisible(False)

        if success:
            self.current_geometry_xml = xml_path
            self.status_label.setText(f"✅ Геометрия извлечена: {len(contours)} контуров")
            self.status_label.setStyleSheet("color: green;")

            self.contours = []
            for c in contours:
                self.contours.append(Contour(
                    name=c['name'],
                    bounds=c['bounds'],
                    center=c['center'],
                    tech_object=c['tech_object']
                ))
                if c['tech_object'] not in self.tech_object_colors:
                    self.tech_object_colors[c['tech_object']] = self._generate_color(c['tech_object'])

            self._remember_active_scheme()
            self._start_device_matching()
        else:
            self.status_label.setText("❌ Ошибка извлечения геометрии")
            self.status_label.setStyleSheet("color: red;")

    def _on_geometry_error(self, error: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Ошибка извлечения геометрии")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Ошибка", error)

    def _start_device_matching(self):
        if not self.current_pdf_path or not self.current_geometry_xml:
            return

        lua_path = self.current_lua_json or str(config.PARSED_LUA_JSON)
        if not os.path.exists(lua_path):
            QMessageBox.warning(
                self,
                "Lua данные не найдены",
                "Сначала загрузите Lua файлы"
            )
            return

        self.status_label.setText("Сопоставление устройств...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.matching_thread = DeviceMatchingThread(lua_path, self.current_pdf_path,
                                                    self.current_geometry_xml,
                                                    self.current_page)
        self.matching_thread.progress.connect(self._on_matching_progress)
        self.matching_thread.finished.connect(self._on_matching_finished)
        self.matching_thread.error.connect(self._on_matching_error)
        self.matching_thread.start()

    def _on_matching_progress(self, message: str):
        self.status_label.setText(message)

    def _on_matching_finished(self, success: bool, matches: List[DeviceMatch]):
        self.progress_bar.setVisible(False)

        if success:
            self.matches = matches
            # Досье: состояния и техобъект — при самом устройстве. Соседи
            # по трубам добавятся после разметки, когда появятся трубопроводы
            self.status_label.setText(
                device_dossier.summary(device_dossier.attach(self.matches)))

            thread = self.matching_thread
            if thread is not None and thread.lua_data is not None:
                self._last_match_context = (thread.lua_data, thread.pdf_contours,
                                            thread.device_texts)
                self._allow_report(True)

            for match in self.matches:
                if not hasattr(match, 'operation_status'):
                    match.operation_status = {"status": "not_used"}

            if matches:
                self.status_label.setText(f"✅ Сопоставлено устройств: {len(matches)}")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("⚠️ Не сопоставлено ни одного устройства")
                self.status_label.setStyleSheet("color: #b8860b;")

            self._remember_active_scheme()
            self._update_device_tree()
            self._update_tech_filter()
            self.draw_scene()
            self._save_matches_to_xml()

            if matches:
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Сопоставление завершено\n"
                    f"Найдено устройств: {len(matches)}"
                )
            else:
                # Ноль сопоставлений отчитывался зелёной галочкой «успех»,
                # и разобраться было можно только по журналу
                QMessageBox.warning(self, "Ничего не сопоставлено",
                                    self._explain_no_matches())
            self._markup_if_cached()
        else:
            self.status_label.setText("❌ Ошибка сопоставления")
            self.status_label.setStyleSheet("color: red;")

        self._allow_postgres(True)

    def _explain_no_matches(self) -> str:
        """Почему не сопоставилось ничего.

        Самая частая причина — чертёж одного проекта и Lua другого:
        техобъекты на листе просто отсутствуют в описании контроллера.
        Без объяснения это выглядит как поломка распознавания.
        """
        drawing = sorted({c.tech_object for c in self.contours if c.tech_object})
        lua_objects = sorted(self._lua_tech_objects())

        if not drawing:
            return ("На чертеже не найдено ни одного именованного контура.\n\n"
                    "Сопоставлять не с чем: имена техобъектов берутся "
                    "с самого чертежа.")

        if not lua_objects:
            return ("Файл Lua не загружен или в нём нет устройств.\n\n"
                    "Загрузите main.io.lua (Ctrl+O), при необходимости "
                    "вместе с main.wago.lua.")

        common = set(drawing) & set(lua_objects)
        message = [f"Техобъектов на чертеже: {len(drawing)}, в Lua: {len(lua_objects)}.",
                   f"Совпадает имён: {len(common)}."]

        if not common:
            message.append("")
            message.append("Похоже, загружены файлы разных проектов: ни одно имя "
                           "с чертежа не встречается в описании контроллера.")
            message.append("")
            message.append(f"На чертеже: {', '.join(drawing[:6])}")
            message.append(f"В Lua:      {', '.join(lua_objects[:6])}")
        else:
            message.append("")
            message.append("Имена совпадают, но подписи устройств на чертеже "
                           "не удалось привязать. Подробности — «Отчёт "
                           "о расхождениях» (Ctrl+R).")
        return "\n".join(message)

    def _lua_tech_objects(self) -> set:
        # Техобъект — приставка перед обозначением типа: LA_TANK1V101 -> LA_TANK1
        context = getattr(self, "_last_match_context", None)
        if not context or not context[0]:
            return set()

        pattern = re.compile(rf"^(.+?){config.device_types_pattern()}\d+$")
        found = set()
        for device in context[0].get("devices", []):
            name = device.get("name", "")
            match = pattern.match(name) if name else None
            if match:
                found.add(match.group(1))
        return found

    def _markup_if_cached(self):
        # Размеченный ранее лист достаётся из кэша за доли секунды — ждать
        # нажатия кнопки незачем. Новый лист по-прежнему ждёт: занимать
        # машину на полторы минуты без спроса нельзя.
        #
        # Ключ кэша учитывает число сопоставленных устройств, поэтому
        # спрашивать раньше сопоставления бессмысленно
        if not self.current_pdf_path:
            return

        try:
            key = self._build_markup_thread().cache_key()
        except Exception as e:
            print(f"Не удалось проверить кэш разметки: {e}")
            return

        if markup_cache.lookup(key):
            self.status_label.setText("Разметка этого листа уже посчитана — показываю")
            # Разметку показываем молча: окно «Успех» уместно после полутора
            # минут ожидания, но не после мгновенного чтения из кэша
            self._markup_started_by_user = False
            self.markup_pdf_with_yolo()

    def _on_matching_error(self, error: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Ошибка сопоставления")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Ошибка", error)

    def _save_matches_to_xml(self):
        if not self.matches:
            return

        try:
            contours_for_xml = []
            if self.current_geometry_xml:
                tree = ET.parse(self.current_geometry_xml)
                root = tree.getroot()
                for contour in root.findall('.//ClosedContours/Contour'):
                    bounds = contour.find('Bounds')
                    center = contour.find('Center')
                    name_elem = contour.find('Name')

                    contours_for_xml.append({
                        'id': contour.get('id'),
                        'bounds': (
                            float(bounds.get('min_x')),
                            float(bounds.get('min_y')),
                            float(bounds.get('max_x')),
                            float(bounds.get('max_y'))
                        ),
                        'center': (
                            float(center.get('x')),
                            float(center.get('y'))
                        ),
                        'name': name_elem.text if name_elem is not None else None
                    })

            lua_data = None
            if self.current_lua_json and os.path.exists(self.current_lua_json):
                with open(self.current_lua_json, 'r', encoding='utf-8') as f:
                    lua_data = json.load(f)

            output_path = generate_output_xml(self.matches, contours_for_xml, [], lua_data)
            self.file_info_label.setText(f"✅ Результат сохранен в {output_path}")

        except Exception as e:
            print(f"Ошибка сохранения XML: {e}")

    def load_svg_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите размеченный SVG файл",
            "",
            "SVG files (*.svg)"
        )

        if not file_path:
            return

        try:
            if self.graphics_view.load_svg_background(file_path):
                self.svg_background_path = file_path
                filename = os.path.basename(file_path)
                self.status_label.setText(f"SVG фон: {filename}")
                self.draw_scene(fit=True)

                QMessageBox.information(
                    self,
                    "Успех",
                    f"SVG файл успешно загружен:\n{filename}"
                )
            else:
                QMessageBox.warning(self, "Предупреждение", "Не удалось загрузить SVG файл")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить SVG:\n{e!s}")

    def load_xml_file(self, file_path: str | None = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите XML файл с результатами",
                "",
                "XML files (*.xml)"
            )

        if not file_path:
            return

        try:
            document = xml_io.load_document(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e!s}")
            return

        if document.needs_canvas:
            QMessageBox.warning(
                self, "Нет размеров холста",
                "Файл записан в процентах, но размеры холста в нём отсутствуют.\n"
                "Координаты устройств и контуров загрузить не удалось."
            )

        self.matches.clear()
        self.contours.clear()
        self.tech_object_colors.clear()

        self.contours.extend(document.contours)
        self.matches.extend(document.matches)

        # Цвета — оформление, а не данные: их назначает окно.
        # Устройствам цвет больше не раздаётся: они обводятся по габариту
        # своего символа одним цветом, а не красятся по типу
        tech_objects = ({contour.tech_object for contour in document.contours} |
                        {match.tech_object for match in document.matches})
        for name in tech_objects:
            self.tech_object_colors[name] = self._generate_color(name)

        self._update_file_info()
        self._update_tech_filter()
        self._update_device_tree()
        # Открыт другой файл — содержимое новое, вписываем целиком
        self.draw_scene(fit=True)

        message = (f"Загружено {len(self.contours)} контуров "
                   f"и {len(self.matches)} устройств")
        if document.problems:
            # Раньше о каждой такой записи сообщал print в консоль, которой
            # у собранного приложения нет
            for problem in document.problems:
                app_log.write(f"не разобрано при чтении {file_path}: {problem}")
            message += ("\nПропущено записей с некорректными координатами: "
                        f"{document.skipped}")
        QMessageBox.information(self, "Успех", message)

    def export_to_file(self):
        # Формат выбирается расширением в диалоге сохранения: XML или JSON.
        # Состав файла одинаков, разница только в записи
        if not self.svg_background_path:
            QMessageBox.warning(self, "Нет SVG", "Сначала загрузите SVG файл для экспорта")
            return

        if not self.matches and not self.contours:
            QMessageBox.warning(self, "Нет данных", "Нет устройств или контуров для экспорта")
            return

        default_name = "visualization_export.json"
        output_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл выгрузки",
            default_name,
            exporters.FILE_DIALOG_FILTER
        )

        if not output_path:
            return

        # Имя без расширения диалог отдаёт как есть, а формат берётся именно
        # из расширения — дописываем его по выбранному фильтру
        output_path = exporters.with_suffix(output_path, selected_filter)

        try:
            current_operation_id = None
            if hasattr(self, 'current_selected_operation') and self.current_selected_operation:
                current_operation_id = self.current_selected_operation.id

            success = exporters.export_visualization(
                svg_path=self.svg_background_path,
                output_path=output_path,
                matches=self.matches,
                contours=self.contours,
                current_operation_id=current_operation_id,
                pdf_size=get_pdf_page_size(self.current_pdf_path, self.current_page)
            )

            if success:
                QMessageBox.information(
                    self, "Успех",
                    f"Данные успешно экспортированы в {exporters.format_name(output_path)}:"
                    f"\n{output_path}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте:\n{e!s}")

    def export_to_postgresql(self):
        """Экспорт в PostgreSQL"""
        if not self.svg_background_path:
            QMessageBox.warning(self, "Нет SVG", "Сначала загрузите SVG файл")
            return

        if not self.matches and not self.contours:
            QMessageBox.warning(self, "Нет данных", "Нет устройств или контуров для экспорта")
            return

        # Одно окно вместо четырёх подряд: раньше хост, база, пользователь
        # и пароль спрашивались по очереди, и ошибка в первом означала
        # проход по всем заново
        dialog = PostgresDialog(self, self.db_settings)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.db_settings = dialog.saveable()

        self._remember_idle_state()
        self._set_busy(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Экспорт в PostgreSQL...")
        self.status_label.setStyleSheet("color: orange;")

        self.postgres_thread = PostgresExportThread(
            self.svg_background_path, self.matches, self.contours,
            dialog.db_config(),
            pdf_size=get_pdf_page_size(self.current_pdf_path, self.current_page),
            mode=dialog.mode())
        self.postgres_thread.progress.connect(self._on_matching_progress)
        self.postgres_thread.finished.connect(self._on_postgres_finished)
        self.postgres_thread.start()

    def _on_postgres_finished(self, success: bool, message: str):
        self._set_busy(False)

        if success:
            self.status_label.setText("✅ Экспорт в PostgreSQL завершён")
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, "Успех", message)
        else:
            self.status_label.setText("❌ Ошибка экспорта в PostgreSQL")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Ошибка", message)

    def _update_device_tree(self, operation: Optional[TechOperation] = None):
        """Строит дерево устройств; с операцией — с их состояниями в ней.

        Раньше это были два метода, совпадавшие на 16 значимых строк из 24:
        одно и то же построение дерева, а состояние в операции — всего лишь
        оформление поверх него. Расходиться они начали бы при первой же
        правке одного из них.
        """
        self.device_tree.clear()

        grouped: Dict[str, List[DeviceMatch]] = {}
        for match in self.matches:
            grouped.setdefault(match.tech_object, []).append(match)

        statuses = (objects_data.get_devices_for_operation(operation.id)
                    if operation is not None else {})

        for tech_obj in sorted(grouped):
            devices = grouped[tech_obj]
            tech_item = QTreeWidgetItem(self.device_tree)
            tech_item.setText(0, scene_painter.object_title(tech_obj))
            tech_item.setForeground(0, QBrush(
                self.tech_object_colors.get(tech_obj, Qt.GlobalColor.black)))

            if operation is None:
                tech_item.setText(1, f"({len(devices)})")
            else:
                counts = dict.fromkeys(self.OPERATION_STATUS_ICONS, 0)
                for match in devices:
                    counts[self._operation_status(match, statuses)[0]] += 1
                tech_item.setText(1, f"🔓{counts['opened']} 🔒{counts['closed']} "
                                     f"⚪{counts['not_used']}")

            for match in sorted(devices, key=lambda m: m.pdf_name):
                device_item = QTreeWidgetItem(tech_item)
                device_item.setText(1, match.device_type or "-")
                device_item.setText(2, match.article or "-")
                device_item.setData(0, Qt.ItemDataRole.UserRole, match)

                if operation is None:
                    device_item.setText(0, match.pdf_name)
                    device_item.setToolTip(0, self._create_tree_item_tooltip(match))
                else:
                    status, matched = self._operation_status(match, statuses)
                    device_item.setText(
                        0, self.OPERATION_STATUS_ICONS.get(status, "") + match.pdf_name)
                    device_item.setForeground(0, QBrush(
                        self.OPERATION_STATUS_COLORS.get(status, Qt.GlobalColor.black)))
                    device_item.setToolTip(
                        0, self._operation_tooltip(match, operation, status, matched))

            tech_item.setExpanded(True)

        # Дерево перестроено — введённый поиск нужно применить заново,
        # иначе после разметки в списке снова окажутся все устройства.
        # Вид с операцией этого не делал и терял введённый поиск.
        if self.device_search.text().strip():
            self._filter_device_tree(self.device_search.text())

        self._update_legend()

    @staticmethod
    def _operation_status(match: DeviceMatch,
                          statuses: Dict[str, str]) -> Tuple[str, Optional[str]]:
        # Состояние устройства в операции и имя, по которому оно нашлось:
        # искать надо и по имени из Lua, и по подписи с чертежа
        for name in (match.lua_name, match.pdf_name):
            if name and name in statuses:
                return statuses[name], name
        return "not_used", None

    def _operation_tooltip(self, match: DeviceMatch, operation: TechOperation,
                           status: str, matched_name: Optional[str]) -> str:
        lines = [f"<b>{match.lua_name}</b>",
                 f"<b>В операции '{operation.name}':</b> "
                 f"{self.OPERATION_STATUS_ICONS.get(status, '')}"
                 f"{self.OPERATION_STATUS_TEXT.get(status, status)}"]

        details = (objects_data.get_device_details_in_operation(operation.id, matched_name)
                   if matched_name else None)
        if details:
            if details.get("state_name"):
                lines.append(f"Состояние: {details['state_name']}")
            if details.get("step_name"):
                lines.append(f"Шаг: {details['step_name']} "
                             f"(№{details.get('step_number', '-')})")

        if match.descr:
            lines.append(f"Описание: {match.descr}")
        if match.article:
            lines.append(f"Артикул: {match.article}")
        if match.device_type:
            lines.append(f"Тип: {match.device_type}")
        return "<br>".join(lines)

    def _create_tree_item_tooltip(self, match: DeviceMatch) -> str:
        lines = [f"<b>{match.lua_name}</b>"]
        if match.descr:
            lines.append(f"Описание: {match.descr}")
        if match.article:
            lines.append(f"Артикул: {match.article}")
        if match.device_type:
            lines.append(f"Тип: {match.device_type}")
        if match.category:
            lines.append(f"Категория: {match.category}")
        return "<br>".join(lines)

    def _update_legend(self):
        # Сколько на листе устройств какого типа. Раньше это был единственный
        # способ прочитать цвет кружка; кружков больше нет — устройство
        # обводится по своему символу, — но разбивка по типам осталась
        # нужной, а цвета те же, что в выгрузке (config.device_color)
        types = {}
        for match in self.matches:
            if match.device_type:
                types[match.device_type] = types.get(match.device_type, 0) + 1

        if not types:
            self.legend_label.setVisible(False)
            return

        rows = []
        for device_type in sorted(types, key=lambda t: -types[t]):
            color = self.DEVICE_TYPE_COLORS.get(device_type, QColor(config.DEFAULT_DEVICE_COLOR))
            rows.append(f'<span style="color:{color.name()}">■</span> '
                        f'{device_type} — {types[device_type]}')

        self.legend_label.setText("<b>Типы устройств:</b><br>" + " &nbsp; ".join(rows))
        self.legend_label.setVisible(True)

    def _update_tech_filter(self):
        self.tech_filter.clear()
        self.tech_filter.addItem("Все объекты")
        tech_objects = {m.tech_object for m in self.matches}
        for tech_obj in sorted(tech_objects):
            # Пустой техобъект — у устройств, которых в Lua зовут просто «V1»
            self.tech_filter.addItem(scene_painter.object_title(tech_obj))

    def _update_file_info(self):
        info_lines = []
        if self.current_lua_json:
            info_lines.append(f"Lua: {os.path.basename(self.current_lua_json)}")
        if self.current_lua_objects_json:
            info_lines.append(f"Объекты: {os.path.basename(self.current_lua_objects_json)}")
        if self.current_pdf_path:
            info_lines.append(f"PDF: {os.path.basename(self.current_pdf_path)}")
        if self.svg_background_path:
            info_lines.append(f"SVG: {os.path.basename(self.svg_background_path)}")

        if info_lines:
            self.file_info_label.setText("\n".join(info_lines))
        else:
            self.file_info_label.setText("Файлы не загружены")

    def draw_scene(self, fit: bool = False):
        # fit=True — вписать схему целиком; так открывается новое содержимое.
        # По умолчанию положение и масштаб сохраняются: раньше перерисовка
        # заканчивалась reset_view(), и любая смена фильтра или настройки
        # отображения выбрасывала пользователя обратно к общему виду
        view = self.graphics_view
        keep_center = None if fit else view.mapToScene(view.viewport().rect().center())
        selected_before = self.selected_match

        # Каталог мог смениться целиком — другой лист, новое сопоставление,
        # открытый XML. Тогда выбранное устройство осталось от прошлых данных,
        # и панель показывала бы то, чего на схеме больше нет
        if selected_before is not None and not any(m is selected_before
                                                   for m in self.matches):
            self.clear_selection()
            selected_before = None

        options = scene_painter.options_from_window(self)
        scene_painter.preserve_background(view, self.svg_background_path)

        # Подложку можно снять, не выгружая её: удобно сверить разметку
        # с чистым чертежом
        if view.svg_item is not None:
            view.svg_item.setVisible(options.background)

        if not self.contours and not self.matches:
            self._restore_view(fit, keep_center)
            return

        scene_painter.draw_contours(view._scene, self.contours,
                                    self.tech_object_colors, options)
        scene_painter.draw_devices(view._scene, self.matches, options)

        # Элементы устройств пересозданы — подсветку выбранного возвращаем
        if selected_before is not None:
            self.selected_match = None
            self._highlight_device(selected_before)

        self._restore_view(fit, keep_center)

    def _restore_view(self, fit: bool, keep_center):
        # Границы схемы могли измениться — виду нужно новое поле вокруг неё,
        # а мини-карте новые границы
        self.graphics_view.refresh_scene_bounds()
        self.mini_map.refresh()
        # Очистка сцены сбрасывает её границы, а вместе с ними и полосы
        # прокрутки, поэтому центр возвращаем вручную
        if fit:
            self.graphics_view.fit_in_view()
        elif keep_center is not None:
            self.graphics_view.centerOn(keep_center)

    def _generate_color(self, tech_name: str) -> QColor:
        # Палитра и правило выбора — в config: выгрузка красит контуры так же
        return QColor(config.tech_object_color(tech_name))

    def _filter_device_tree(self, text: str):
        # Фильтр по любому из полей: имя в Lua, имя с чертежа, тип, артикул
        # и технологический объект — искать приходится по-разному
        needle = text.strip().lower()
        shown = 0

        for index in range(self.device_tree.topLevelItemCount()):
            group = self.device_tree.topLevelItem(index)
            group_matches = needle in group.text(0).lower()
            visible_children = 0

            for child_index in range(group.childCount()):
                child = group.child(child_index)
                match = child.data(0, Qt.ItemDataRole.UserRole)
                fields = [child.text(0), child.text(1), child.text(2), group.text(0)]
                if match is not None:
                    fields += [match.lua_name or "", match.pdf_name or "",
                               match.descr or ""]

                visible = (not needle or group_matches
                           or any(needle in field.lower() for field in fields))
                child.setHidden(not visible)
                visible_children += int(visible)

            group.setHidden(bool(needle) and visible_children == 0)
            if not group.isHidden():
                group.setExpanded(True)
            shown += visible_children

        if needle:
            self.search_result_label.setText(f"Найдено: {shown}")
        else:
            self.search_result_label.setText("")

    def focus_device_search(self):
        self.device_search.setFocus()
        self.device_search.selectAll()

    def _highlight_device(self, match: Optional[DeviceMatch]):
        # Раньше выбор в дереве только двигал вид, и какое устройство выбрано
        # было не видно — на чертеже сотни одинаковых кружков
        self.selected_match = match
        for item in self.graphics_view._scene.items():
            if isinstance(item, DeviceGraphicsItem):
                item.set_selected(item.device_data is match)

    def select_device(self, match: Optional[DeviceMatch]):
        """Выбрать устройство: подсветка на схеме, панель и место в каталоге.

        Единственный вход в выбор — щёлкают ли по схеме или по строке
        в каталоге. Панель при этом заполняется заново, а не дописывается:
        данные двух устройств наложиться не могут.
        """
        if match is None:
            self.clear_selection()
            return

        self._highlight_device(match)
        self.details_panel.show_device(match)
        self._select_tree_item(match)

    def select_operation(self, operation: Optional[TechOperation]):
        """Показать в панели операцию. Устройство с подсветки не снимается.

        Выбранная операция — это ещё и раскраска устройств по их положению
        в ней; она остаётся, даже когда в панели уже другое.
        """
        self.details_panel.show_operation(operation)

    def clear_selection(self):
        """Сбросить выбранное: пустая панель и снятая подсветка.

        Отдельным действием, а не «щелчком мимо»: щелчок мимо — это ещё
        и первая половина двойного, которым схему вписывают в окно,
        и выбор слетал бы сам собой.

        Выбранную операцию сброс не отменяет: она красит устройства
        по их положению, и это не то же самое, что показ в панели.
        """
        self._highlight_device(None)
        self.details_panel.clear()
        self.device_tree.setCurrentItem(None)

    def _select_tree_item(self, match: DeviceMatch):
        # Каталог показывает то же устройство, что и схема: иначе после
        # щелчка по чертежу в дереве оставалось подсвеченным предыдущее
        for index in range(self.device_tree.topLevelItemCount()):
            group = self.device_tree.topLevelItem(index)
            for child in range(group.childCount()):
                item = group.child(child)
                if item.data(0, Qt.ItemDataRole.UserRole) is match:
                    self.device_tree.setCurrentItem(item)
                    self.device_tree.scrollToItem(item)
                    return

    def on_scene_clicked(self, x: float, y: float):
        # Щелчок по устройству показывает его в панели. Мимо устройства —
        # ничего: выбор снимают кнопкой «Сбросить», а не промахом
        match = self._device_at(x, y)
        if match is not None:
            self.select_device(match)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        match = item.data(0, Qt.ItemDataRole.UserRole)
        if not match:
            return
        # Масштаб не трогаем: увеличение выбирает пользователь, а не дерево
        self.graphics_view.centerOn(match.coordinates[0], match.coordinates[1])
        self.select_device(match)

    def on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        # Двойной щелчок приближает — одиночный только показывает
        match = item.data(0, Qt.ItemDataRole.UserRole)
        if not match:
            return
        self.graphics_view.zoom_to_point(match.coordinates[0], match.coordinates[1])
        self.select_device(match)

    def update_display(self):
        self.draw_scene()

    def reset_view(self):
        self.graphics_view.fit_in_view()

    # Перетаскивание файлов: путь к чертежу проще бросить в окно,
    # чем искать его в диалоге через полдюжины папок
    DROP_HANDLERS: ClassVar[dict] = {
        ".pdf": "_open_pdf",
        ".svg": "_load_svg_path",
        ".xml": "load_xml_file",
    }

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            return
        if any(self._drop_kind(url.toLocalFile()) for url in event.mimeData().urls()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def _drop_kind(self, path: str) -> Optional[str]:
        suffix = os.path.splitext(path)[1].lower()
        if suffix == ".lua":
            return "lua"
        return suffix if suffix in self.DROP_HANDLERS else None

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        lua_files = [p for p in paths if self._drop_kind(p) == "lua"]

        # main.objects.lua разбирается отдельным разборщиком, остальные Lua —
        # общим; различаем по имени файла, как это делает и сам пользователь
        objects = [p for p in lua_files if "object" in os.path.basename(p).lower()]
        devices = [p for p in lua_files if p not in objects]

        if devices:
            self._start_lua_parsing(devices)
        for path in objects:
            self._start_objects_parsing(path)

        for path in paths:
            kind = self._drop_kind(path)
            if kind and kind != "lua":
                getattr(self, self.DROP_HANDLERS[kind])(path)

        event.acceptProposedAction()

    def _load_svg_path(self, path: str):
        if self.graphics_view.load_svg_background(path):
            self.svg_background_path = path
            self.status_label.setText(f"SVG фон: {os.path.basename(path)}")
            self._update_file_info()
            self.draw_scene(fit=True)
            self._allow_postgres(True)

    def _save_settings(self):
        # Раньше не сохранялось ничего: каждый запуск возвращал размеры окна,
        # положение разделителей и настройки отображения к исходным
        app_settings.save_geometry(self)
        app_settings.save_splitter("main", self.main_splitter)
        app_settings.save_splitter("right", self.right_splitter)
        app_settings.save_splitter("scene", self.scene_splitter)

        for name, item in self._pane_actions().items():
            app_settings.save_value(f"view/pane_{name}", item.isChecked())

        app_settings.save_value("markup/profile", self.detection_profile.currentData())
        app_settings.save_value("display/contour_alpha", self.contour_alpha.value())
        app_settings.save_value("display/contour_names", self.show_contour_names.isChecked())
        app_settings.save_value("display/device_names", self.show_device_names.isChecked())
        app_settings.save_value("display/tooltips", self.show_tooltips.isChecked())

        if self.db_settings:
            app_settings.save_db_settings(self.db_settings)

        app_settings.save_session(self.current_lua_files, self.current_objects_file,
                                  self.current_pdf_path, self.current_page)

    def _load_settings(self):
        profile = app_settings.load_value("markup/profile", config.YOLO_PROFILE)
        index = self.detection_profile.findData(profile)
        if index >= 0:
            self.detection_profile.setCurrentIndex(index)

        self.contour_alpha.setValue(app_settings.load_int("display/contour_alpha", 50))
        self.show_contour_names.setChecked(
            app_settings.load_bool("display/contour_names", True))
        self.show_device_names.setChecked(
            app_settings.load_bool("display/device_names", True))
        self.show_tooltips.setChecked(app_settings.load_bool("display/tooltips", True))

        self.db_settings = app_settings.load_db_settings()

        app_settings.restore_splitter("main", self.main_splitter)
        app_settings.restore_splitter("right", self.right_splitter)
        app_settings.restore_splitter("scene", self.scene_splitter)

        # Спрятанные панели остаются спрятанными между запусками: иначе
        # каждый запуск возвращал бы то, что человек только что убрал
        for name, item in self._pane_actions().items():
            shown = app_settings.load_bool(f"view/pane_{name}", True)
            item.setChecked(shown)
            self._show_pane(name, shown)

        self._unfold_lost_panes()

    def _unfold_lost_panes(self):
        """Возвращает панели, схлопнутые сохранённой раскладкой в ноль.

        Границу панели можно утащить до самого края — панель схлопывается
        в ноль и уезжает в настройки такой. Следующий запуск открывался уже
        без неё: место, где она была, ничем не отмечено, и выглядит это
        так, будто панель пропала из программы совсем. Именно так пропала
        панель сведений: в раскладке лежало `scene = [1596, 0]`.

        Спрятать панель осознанно по-прежнему можно — `Ctrl+B`, `Ctrl+I`,
        `Ctrl+J`, — но это помнится отдельным признаком, который видно
        галочкой в меню. Ноль в раскладке помнить нечего.
        """
        for splitter, index, widget in self.panes.values():
            if not widget.isVisibleTo(self):
                continue                      # спрятана осознанно — не трогаем
            sizes = splitter.sizes()
            if index < len(sizes) and sizes[index] == 0:
                splitter.toggle_pane(index)

    def _running_threads(self) -> List[Tuple[str, object]]:
        # Работающие сейчас фоновые потоки: (название для человека, поток)
        running = []
        for attribute, title in self.BACKGROUND_THREADS:
            thread = getattr(self, attribute, None)
            if thread is not None and thread.isRunning():
                running.append((title, thread))
        return running

    def _stop_threads(self) -> List[str]:
        """Просит все потоки остановиться. Возвращает не успевших.

        Запрос уходит сразу всем, и только потом начинается ожидание:
        иначе потоки останавливались бы по очереди, каждый в свой срок.
        """
        running = self._running_threads()
        for _, thread in running:
            thread.requestInterruption()

        deadline = time.monotonic() + self.THREAD_WAIT_MS / 1000
        stubborn = []
        for title, thread in running:
            left_ms = int(max(0.0, deadline - time.monotonic()) * 1000)
            if not thread.wait(left_ms):
                stubborn.append(title)
        return stubborn

    def closeEvent(self, event):
        self._save_settings()

        stubborn = self._stop_threads()
        if stubborn:
            # Бросать работающий поток нельзя: выгрузка в базу оборвётся
            # посреди записи, а Qt завершит процесс аварийно. Но и держать
            # окно взаперти тоже нельзя — решает пользователь, зная цену.
            answer = QMessageBox.question(
                self, "Работа не закончена",
                "Ещё выполняется: " + ", ".join(stubborn) + ".\n\n"
                "Закрыть окно всё равно? Незавершённая работа пропадёт.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        super().closeEvent(event)

    def clear_markup_cache(self):
        # Кэш держит по 470 КБ на лист и сам себя не чистит дальше предела
        # в markup_cache.MAX_SIZE_MB. Иногда его нужно сбросить целиком:
        # например, после переобучения модели
        # Пустоту определяем по наличию записей, а не по размеру: порог
        # в сотую мегабайта объявлял бы пустым кэш из нескольких килобайт
        size = markup_cache.size_bytes()
        if size == 0:
            QMessageBox.information(self, "Кэш разметки", "Кэш и так пуст.")
            return

        megabytes = size / 1048576
        answer = QMessageBox.question(
            self, "Очистить кэш разметки",
            f"Удалить сохранённую разметку? Сейчас она занимает "
            f"{megabytes:.1f} МБ.\n\n"
            "Разметка листов после этого будет считаться заново.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return

        removed = markup_cache.clear()
        app_log.write(f"кэш разметки очищен: файлов {removed}, {megabytes:.1f} МБ")
        QMessageBox.information(self, "Кэш разметки",
                                f"Удалено файлов: {removed} ({megabytes:.1f} МБ)")

    def open_settings_dialog(self):
        if not hasattr(self, '_settings_dialog') or self._settings_dialog is None:
            self._settings_dialog = SettingsDialog(self)

        if self._settings_dialog.isVisible():
            self._settings_dialog.raise_()
            self._settings_dialog.activateWindow()
        else:
            self._settings_dialog._load_settings()
            self._settings_dialog.show()


# Об одной и той же ошибке сообщаем один раз. Ошибка внутри отрисовки
# повторяется на каждой перерисовке, и без этого экран заполнился бы
# одинаковыми окнами, поверх которых уже ничего не нажать.
_reported_errors = set()


def _report_error(short: str, details: str) -> None:
    if QApplication.instance() is None or short in _reported_errors:
        return
    _reported_errors.add(short)

    box = QMessageBox()
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle("Ошибка")
    box.setText("Произошла ошибка, работа приложения могла нарушиться.\n\n" + short)
    box.setInformativeText(f"Подробности записаны в журнал:\n{app_log.log_path()}")
    box.setDetailedText(details)
    box.exec()


def _qt_message(mode, context, message):
    # Предупреждения Qt печатаются в поток, которого в собранном приложении
    # нет. Так теряется и «QThread: Destroyed while thread is still running» —
    # то самое сообщение, ради которого ждут остановки потоков при закрытии.
    app_log.write(f"Qt [{getattr(mode, 'name', mode)}]: {message}")


def main():
    app_log.start()
    app_log.install_excepthook(_report_error)

    app = QApplication(sys.argv)
    theme.apply(app)
    qInstallMessageHandler(_qt_message)

    window = DeviceVisualizer()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
