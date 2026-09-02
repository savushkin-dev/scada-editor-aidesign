# details_panel.py
# Панель сведений: всё, что известно о выбранном — об устройстве или об операции.
#
# Зачем одна на двоих. Панели было две, и обе с одними и теми же вкладками —
# «Параметры», «Состояния и шаги», «Свойства», «Информация»: одна внизу,
# в браузере операций, другая справа от схемы. Половина данных при этом
# не показывалась нигде, а человеку приходилось помнить, в какой из двух
# одинаковых панелей искать. Теперь панель одна: она показывает то, что
# выбрали последним, — устройство щелчком по схеме или каталогу, операцию
# щелчком по списку операций. Браузер операций остался списком, своих
# вкладок у него больше нет.
#
# Про устройство в окне до этого было видно ровно столько, сколько помещалось
# в подсказку под курсором: имя, объект, описание, артикул. Каналы контроллера
# с адресом, уставки техобъекта, шаги операций, где клапан открывается
# и закрывается, лежали в данных и уезжали в выгрузку, но посмотреть на них
# самим было негде.
#
# Панель — инструмент окна: она ничего не добавляет ни в одну выгрузку
# и ничего не меняет в данных. Она читает те же поля, что уезжают редактору
# (`export_scene`, `objects_loader`), и показывает их человеку.
#
# Показываемое всегда одно. `show_device` и `show_operation` очищают
# содержимое перед заполнением, поэтому данные двух устройств (или устройства
# и операции) не могут наложиться, даже если выбирать их подряд без сброса.
# Сброс — `clear()`: панель возвращается к пустому виду, а окно снимает
# подсветку со схемы.
#
# Сбор данных вынесен в обычные функции (`device_sections`, `parameter_groups`,
# `signal_rows`, `property_rows`, `operation_sections`): они не знают про Qt,
# и проверить, что попадает в панель, можно без окна.
import html
import json
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QPushButton,
                               QTableWidget, QTableWidgetItem, QTabWidget,
                               QTextEdit, QTreeWidget, QTreeWidgetItem,
                               QVBoxLayout, QWidget)

from contur.core import config
from contur.core.data_models import DeviceMatch
from contur.export.export_scene import state_text
from contur.matching import device_dossier
from contur.lua.objects_loader import Operation, TechObject, objects_data

# Каналы ввода-вывода в порядке показа
CHANNELS = ("DI", "DO", "AI", "AO")

# Положение устройства в операции: те же значки, что в каталоге устройств
STATUS_ICONS = {"opened": "🔓", "closed": "🔒", "not_used": "⚪"}
STATUS_COLORS = {"opened": "#2e7d32", "closed": "#c62828"}

EMPTY_TITLE = "Ничего не выбрано"
EMPTY_HINT = ("Щёлкните по устройству на схеме, по строке в каталоге "
              "или по операции в списке внизу.<br>"
              "Здесь появится всё, что о нём известно.")


# ---------------------------------------------------------------- общее

def _text(value: Any) -> str:
    """Значение строкой. Списки и словари — как в JSON, а не как repr Python."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def type_title(device_type: str) -> str:
    """Тип устройства словами: «V — Клапан: отсечной, донный, дренажный, CIP»."""
    device_type = (device_type or "").strip()
    if not device_type:
        return "не разобран"
    name = config.device_type_name(device_type)
    return f"{device_type} — {name}" if name else device_type


def tech_object_of(match: Optional[DeviceMatch]) -> Optional[TechObject]:
    """Техобъект устройства из описания объектов, если оно загружено.

    Поиск живёт в `device_dossier`: им же закрепляется досье устройства,
    и расходиться этим двум нельзя — панель показывала бы один объект,
    а выгрузка уносила другой.
    """
    if match is None:
        return None
    return device_dossier.find_tech_object(match.tech_object)


def object_parameters(tech_object: Optional[TechObject]
                      ) -> List[Tuple[str, List[Tuple[str, str, str, str]]]]:
    """Уставки техобъекта одной группой. Общее у устройства и у операции."""
    if tech_object is None:
        return []

    rows = [(parameter.name or parameter.id, _text(parameter.value),
             parameter.meter or "", parameter.nameLua or "")
            for parameter in objects_data.get_parameters_for_object(tech_object.id)]
    return [(f"Уставки объекта «{tech_object.name}»", rows)] if rows else []


def object_properties(tech_object: Optional[TechObject]) -> List[Tuple[str, str]]:
    """Свойства, состав оборудования и системные параметры объекта."""
    if tech_object is None:
        return []

    rows = []
    for title, values in (("Свойство объекта", tech_object.properties),
                          ("Оборудование объекта", tech_object.equipment),
                          ("Системный параметр", tech_object.system_parameters)):
        if isinstance(values, dict):
            rows += [(f"{title}: {key}", _text(value)) for key, value in values.items()]
    return rows


def sections_html(sections: List[Tuple[str, List[Tuple[str, str]]]]) -> str:
    """Разделы сводки — таблицей, читаемой в QTextEdit."""
    parts = []
    for title, rows in sections:
        if not rows:
            continue
        parts.append(f'<p style="margin:8px 0 2px 0"><b>{html.escape(title)}</b></p>')
        parts.append('<table cellspacing="0" cellpadding="2" width="100%">')
        for name, value in rows:
            # Значения приходят из чужих файлов: описание с «<» или «&» иначе
            # съело бы разметку вместе с остатком таблицы
            parts.append(f'<tr><td width="45%" style="color:#666">{html.escape(name)}</td>'
                         f'<td><b>{html.escape(value)}</b></td></tr>')
        parts.append("</table>")
    return "".join(parts)


def _filled(sections: List[Tuple[str, List[Tuple[str, str]]]]
            ) -> List[Tuple[str, List[Tuple[str, str]]]]:
    # Пустые поля не показываются: у сигнала нет ни артикула, ни описания,
    # и строки «Артикул: —» только мешали бы читать
    return [(title, [(name, value) for name, value in rows if value])
            for title, rows in sections]


# ---------------------------------------------------------------- устройство

def parameter_groups(match: DeviceMatch,
                     tech_object: Optional[TechObject] = None
                     ) -> List[Tuple[str, List[Tuple[str, str, str, str]]]]:
    """Параметры устройства и уставки его объекта, по группам.

    Возвращает `[(название группы, [(параметр, значение, ед. изм., имя в Lua)])]`.
    Параметры устройства приходят из main.io.lua списком чисел без имён —
    показываем их с номером, как они там и лежат.
    """
    groups = []
    tags = match.tags or {}

    for key, title in (("par", "Параметры устройства (par)"),
                       ("rt_par", "Рабочие параметры (rt_par)")):
        values = tags.get(key)
        rows: List[Tuple[str, str, str, str]] = []
        if isinstance(values, dict):
            rows = [(str(name), _text(value), "", f"{key}.{name}")
                    for name, value in values.items()]
        elif isinstance(values, (list, tuple)):
            # Нумерация с единицы: столько же, сколько в самом Lua
            rows = [(f"№ {number}", _text(value), "", f"{key}[{number}]")
                    for number, value in enumerate(values, 1)]
        if rows:
            groups.append((title, rows))

    return groups + object_parameters(tech_object)


def signal_rows(match: DeviceMatch) -> List[Tuple[str, str, str, str, str, str]]:
    """Каналы ввода-вывода с адресом в контроллере.

    Это и есть привязка картинки к живому сигналу: узел, модуль и порт.
    """
    rows = []
    tags = match.tags or {}
    for channel in CHANNELS:
        for entry in tags.get(channel) or ():
            if isinstance(entry, dict):
                rows.append((channel,
                             _text(entry.get("node", "")),
                             _text(entry.get("module_offset", "")),
                             _text(entry.get("logical_port", "")),
                             _text(entry.get("physical_port", "")),
                             _text(entry.get("offset", ""))))
            else:
                rows.append((channel, _text(entry), "", "", "", ""))
    return rows


def state_entries(match: DeviceMatch) -> List[Dict[str, Any]]:
    """Где устройство открывается и закрывается — по всем операциям проекта.

    Сначала смотрим досье: после сопоставления состояния закреплены за самим
    устройством (`device_dossier.attach`), и панель обязана показывать
    ровно то, что уедет в выгрузку. Досье пустое — спрашиваем описание
    операций сами: панель открывают и до разметки.
    """
    return match.states or device_dossier.device_states(match)


def property_rows(match: DeviceMatch,
                  tech_object: Optional[TechObject] = None) -> List[Tuple[str, str]]:
    """Всё остальное, что известно об устройстве и его объекте.

    Сюда попадает то, чему нет своего места: свойства из Lua (`prop`, вроде
    IP-адреса привода), поля, пришедшие мимо модели (`extra_data` — их же
    целиком перебирают экспортёры), и настройки объекта.
    """
    rows: List[Tuple[str, str]] = []

    prop = (match.tags or {}).get("prop")
    if isinstance(prop, dict):
        rows += [(str(key), _text(value)) for key, value in prop.items()]
    elif prop:
        rows.append(("prop", _text(prop)))

    rows += [(str(key), _text(value)) for key, value in (match.extra_data or {}).items()]

    # Геометрия символа: её видно на схеме обводкой, но числа полезны, когда
    # обводка встала не туда. В выгрузки эти поля не уходят
    if match.view_size:
        rows.append(("Габарит символа, пт",
                     f"{match.view_size[0]:.1f} × {match.view_size[1]:.1f}"))
    if match.view_shape:
        rows.append(("Линий символа", str(len(match.view_shape))))

    rows += object_properties(tech_object)

    # Пустое значение — это «не задано», и строкой оно только шумит: у объекта
    # незаполнена половина состава оборудования
    return [(name, value) for name, value in rows if value != ""]


def device_sections(match: DeviceMatch, tech_object: Optional[TechObject] = None,
                    counts: Optional[Dict[str, int]] = None
                    ) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """Сводка об устройстве разделами: `[(заголовок, [(поле, значение)])]`."""
    device: List[Tuple[str, str]] = [
        ("Имя в Lua", match.lua_name),
        ("Подпись на чертеже", match.pdf_name),
        ("Тип устройства", type_title(match.device_type)),
        ("Описание", match.descr),
        ("Артикул", match.article),
        ("Категория", match.category),
        ("Подтип", _text(match.subtype)),
        ("dtype", _text(match.dtype)),
        ("Уверенность сопоставления", f"{match.confidence:.2f}"),
        ("Координаты на листе, пт",
         f"{match.coordinates[0]:.1f}, {match.coordinates[1]:.1f}"),
    ]

    obj: List[Tuple[str, str]] = [("Обозначение на чертеже", match.tech_object)]
    if tech_object is not None:
        obj += _object_rows(tech_object)
    else:
        obj.append(("В описании объектов", "не найден — main.objects.lua "
                                           "не загружен или объекта в нём нет"))

    sections = [("Устройство", device), ("Технологический объект", obj)]

    # Сигнал обмена: не датчик проекта, а строка к соседнему контроллеру.
    # Написано в shared.lua проекта, а не выведено по имени
    exchange = (match.tags or {}).get("exchange") or {}
    if exchange:
        sections.append(("Обмен с соседним контроллером", [
            ("Контроллер", _text(exchange.get("gateway"))),
            ("Направление", _text(exchange.get("direction"))),
            ("Адрес", _text(exchange.get("ip"))),
            ("Станция Modbus", _text(exchange.get("station"))),
        ]))

    # Положение в операции, выбранной в списке операций: его же показывает
    # цвет обводки на схеме
    status_info = getattr(match, "operation_status", None) or {}
    status = status_info.get("status")
    if status:
        operation: List[Tuple[str, str]] = [
            ("Положение", f"{STATUS_ICONS.get(status, '')} {state_text(status)}".strip()),
            ("Состояние", status_info.get("state_name", "")),
            ("Шаг", status_info.get("step_name", "")),
        ]
        number = status_info.get("step_number", -1)
        if isinstance(number, int) and number >= 0:
            operation.append(("Номер шага", str(number)))
        sections.append(("В выбранной операции", operation))

    if counts:
        sections.append(("Что есть в панели", [
            ("Параметров", str(counts.get("params", 0))),
            ("Сигналов", str(counts.get("signals", 0))),
            ("Состояний и шагов", str(counts.get("states", 0))),
            ("Свойств", str(counts.get("props", 0))),
        ]))

    return _filled(sections)


# ---------------------------------------------------------------- операция

def operation_entries(operation: Operation) -> List[Dict[str, Any]]:
    """Что операция делает с устройствами: состояние, шаг, положение.

    Тем же индексом, которым устройство отвечает, где оно участвует, —
    поэтому панель не может рассказать про операцию и про устройство разное.
    """
    return objects_data.get_operation_device_states(operation.id)


def operation_structure(operation: Operation) -> List[Tuple[Any, List[Any]]]:
    """Состояния операции со своими шагами, шаги — по номеру.

    Структура берётся у самой операции, а не выводится из устройств:
    шаг без устройств — это тоже шаг, и в списке он должен быть виден.
    """
    return [(state, sorted(objects_data.get_steps_for_state(state.id),
                           key=lambda step: step.step_number))
            for state in objects_data.get_states_for_operation(operation.id)]


def entries_by_place(entries: List[Dict[str, Any]]
                     ) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
    """Записи об устройствах, разложенные по «состояние + шаг».

    Ключ с пустым шагом — устройства, положение которых задано самим
    состоянием, без шага.
    """
    places: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for entry in entries:
        places.setdefault((entry["state_id"], entry["step_id"]), []).append(entry)
    return places


def operation_properties(operation: Operation,
                         tech_object: Optional[TechObject] = None
                         ) -> List[Tuple[str, str]]:
    """Свойства самой операции и настройки её объекта."""
    rows = [(str(key), _text(value)) for key, value in (operation.props or {}).items()]
    rows += object_properties(tech_object)
    return [(name, value) for name, value in rows if value != ""]


def operation_sections(operation: Operation,
                       tech_object: Optional[TechObject] = None,
                       counts: Optional[Dict[str, int]] = None
                       ) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """Сводка об операции разделами — тем же видом, что и об устройстве."""
    states = objects_data.get_states_for_operation(operation.id)
    steps = sum(len(objects_data.get_steps_for_state(state.id)) for state in states)

    about: List[Tuple[str, str]] = [
        ("Операция", operation.name),
        ("Идентификатор", operation.id),
        ("Базовая операция", operation.base_operation or ""),
        ("Состояний", str(len(states))),
        ("Шагов", str(steps)),
    ]

    obj: List[Tuple[str, str]] = [("Объект операции", operation.obj_name)]
    if tech_object is not None:
        obj += _object_rows(tech_object)

    sections = [("Операция", about), ("Технологический объект", obj)]

    if counts:
        sections.append(("Что есть в панели", [
            ("Параметров", str(counts.get("params", 0))),
            ("Устройств в операции", str(counts.get("devices", 0))),
            ("Состояний и шагов", str(counts.get("states", 0))),
            ("Свойств", str(counts.get("props", 0))),
        ]))

    return _filled(sections)


def _object_rows(tech_object: TechObject) -> List[Tuple[str, str]]:
    return [
        ("Имя в описании", tech_object.name),
        ("Имя Eplan", tech_object.name_eplan),
        ("Имя BC", tech_object.name_BC),
        ("Базовый объект", tech_object.base_tech_object),
        ("Тип объекта (tech_type)", _text(tech_object.tech_type)),
        ("Номер объекта", _text(tech_object.n)),
        ("Операций у объекта", str(len(tech_object.operations))),
    ]


# ---------------------------------------------------------------- сама панель

class DetailsPanel(QWidget):
    """Единственная панель сведений: показывает устройство или операцию.

    Сигнал `cleared` — человек нажал «Сбросить»; окно по нему снимает
    подсветку со схемы. Сама панель про сцену ничего не знает.
    """

    cleared = Signal()

    # Порядок вкладок и их заголовки без счётчиков. Коротко: к заголовку
    # приписывается число строк, а пять длинных подписей со счётчиками
    # не помещались в панель — вместо вкладок появлялись стрелки прокрутки
    TAB_TITLES = ("Сводка", "Параметры", "Состояния", "Сигналы", "Свойства")
    TAB_HINTS = ("Что это за устройство или операция",
                 "Параметры выбранного и уставки его объекта",
                 "Состояния и шаги: где что открывается и закрывается",
                 "Каналы ввода-вывода с адресом в контроллере",
                 "Всё остальное, что о нём известно")
    INFO, PARAMS, STATES, SIGNALS, PROPS = range(5)

    DEVICE_STATE_HEADERS = ("Операция · состояние · шаг", "Положение", "№")
    OPERATION_STATE_HEADERS = ("Состояние · шаг · устройство", "Положение", "№")

    def __init__(self, parent=None):
        super().__init__(parent)
        # Показываемое всегда одно: заполнено ровно одно из двух полей
        self.device: Optional[DeviceMatch] = None
        self.operation: Optional[Operation] = None
        self._init_ui()
        self.clear()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        header = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        header.addWidget(self.title_label, 1)

        self.clear_btn = QPushButton("Сбросить")
        self.clear_btn.setToolTip(
            "Очистить панель и снять подсветку со схемы (Ctrl+Shift+D)")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        header.addWidget(self.clear_btn, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        # Панель узкая, и подписи должны ужиматься, а не прятаться за стрелки
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.tabBar().setExpanding(False)
        for index, page in enumerate((self._info_tab(), self._params_tab(),
                                      self._states_tab(), self._signals_tab(),
                                      self._props_tab())):
            self.tabs.addTab(page, self.TAB_TITLES[index])
            self.tabs.setTabToolTip(index, self.TAB_HINTS[index])
        layout.addWidget(self.tabs, 1)

    # ------------------------------------------------------------- вкладки

    def _info_tab(self) -> QWidget:
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        return self.info_text

    def _params_tab(self) -> QWidget:
        self.params_tree = QTreeWidget()
        self.params_tree.setHeaderLabels(["Параметр", "Значение", "Ед. изм.", "Имя в Lua"])
        self.params_tree.setAlternatingRowColors(True)
        return self.params_tree

    def _states_tab(self) -> QWidget:
        self.states_tree = QTreeWidget()
        self.states_tree.setHeaderLabels(list(self.DEVICE_STATE_HEADERS))
        self.states_tree.setAlternatingRowColors(True)
        return self.states_tree

    def _signals_tab(self) -> QWidget:
        self.signals_table = self._table(
            ["Канал", "Узел", "Модуль", "Лог. порт", "Физ. порт", "Смещение"])
        return self.signals_table

    def _props_tab(self) -> QWidget:
        self.props_table = self._table(["Свойство", "Значение"])
        return self.props_table

    @staticmethod
    def _table(headers: List[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        return table

    # ---------------------------------------------------------- заполнение

    def show_device(self, match: Optional[DeviceMatch]):
        """Показать устройство. Прежнее содержимое стирается целиком."""
        if match is None:
            self.clear()
            return

        # Сначала очистка, потом заполнение: иначе выбор второго устройства
        # без сброса дописывал бы его строки к строкам первого
        self._clear_contents()
        self.device = match

        tech_object = tech_object_of(match)
        groups = parameter_groups(match, tech_object)
        signals = signal_rows(match)
        states = state_entries(match)
        properties = property_rows(match, tech_object)
        counts = {"params": sum(len(rows) for _, rows in groups),
                  "signals": len(signals), "states": len(states),
                  "props": len(properties)}

        self._fill_header(
            match.lua_name or match.pdf_name,
            (match.device_type,
             (tech_object.name if tech_object is not None else "") or match.tech_object,
             match.descr),
            config.device_color(match.device_type),
            type_title(match.device_type))
        self.info_text.setHtml(sections_html(device_sections(match, tech_object, counts)))
        self._fill_params(groups)
        self._fill_device_states(states)
        self._fill_table(self.signals_table, signals)
        self._fill_table(self.props_table, properties)
        self._set_counts(counts, ("params", "states", "signals", "props"))
        self.tabs.setTabVisible(self.SIGNALS, True)
        self.clear_btn.setEnabled(True)

    def show_operation(self, operation: Optional[Operation]):
        """Показать операцию. Прежнее содержимое стирается целиком."""
        if operation is None:
            self.clear()
            return

        self._clear_contents()
        self.operation = operation

        tech_object = objects_data.get_object_for_operation(operation)
        groups = object_parameters(tech_object)
        entries = operation_entries(operation)
        structure = operation_structure(operation)
        properties = operation_properties(operation, tech_object)
        counts = {"params": sum(len(rows) for _, rows in groups),
                  # Счётчик вкладки — про структуру: сколько состояний и шагов.
                  # Сколько там устройств, сказано отдельной строкой в сводке
                  "states": len(structure) + sum(len(steps) for _, steps in structure),
                  "props": len(properties),
                  "devices": len({entry["device"] for entry in entries})}

        self._fill_header(
            operation.name,
            ("Операция", operation.obj_name,
             f"базовая: {operation.base_operation}" if operation.base_operation else ""),
            "#0064B1", f"Операция объекта «{operation.obj_name}»")
        self.info_text.setHtml(
            sections_html(operation_sections(operation, tech_object, counts)))
        self._fill_params(groups)
        self._fill_operation_states(structure, entries)
        self._fill_table(self.props_table, properties)
        self._set_counts(counts, ("params", "states", None, "props"))
        # Каналы ввода-вывода есть у устройства, а не у операции: пустая
        # вкладка выглядела бы потерянными данными
        self.tabs.setTabVisible(self.SIGNALS, False)
        self.clear_btn.setEnabled(True)

    def clear(self):
        """Вернуть панель к пустому виду. Сигнал `cleared` не шлётся."""
        self._clear_contents()
        self.device = None
        self.operation = None
        self.title_label.setText(
            f'<span style="font-size:12pt; color:#888">{EMPTY_TITLE}</span>')
        self.title_label.setToolTip("")
        self.info_text.setHtml(f'<p style="color:#888">{EMPTY_HINT}</p>')
        for index, title in enumerate(self.TAB_TITLES):
            self.tabs.setTabText(index, title)
        self.tabs.setTabVisible(self.SIGNALS, True)
        self.clear_btn.setEnabled(False)

    def _clear_contents(self):
        self.device = None
        self.operation = None
        self.info_text.clear()
        self.params_tree.clear()
        self.states_tree.clear()
        self.signals_table.setRowCount(0)
        self.props_table.setRowCount(0)

    def _on_clear_clicked(self):
        self.clear()
        self.cleared.emit()

    def _set_counts(self, counts: Dict[str, int], keys) -> None:
        # Счётчик в заголовке вкладки: сколько там строк, видно не открывая
        for index, key in enumerate(keys, start=self.PARAMS):
            if key is None:
                continue
            self.tabs.setTabText(index, f"{self.TAB_TITLES[index]} ({counts[key]})")

    def _fill_header(self, name: str, subtitle_parts, color: str, tooltip: str):
        # В заголовке — короткое: обозначение, объект и описание. Тип словами
        # длиной со строку («Клапан: отсечной, донный, дренажный, CIP»),
        # и здесь он отнимал бы у панели четыре строки высоты; его место —
        # во вкладке «Информация» и в подсказке
        subtitle = " · ".join(part for part in subtitle_parts if part)
        self.title_label.setText(
            f'<span style="font-size:12pt"><b>{html.escape(name)}</b></span><br>'
            f'<span style="color:{color}">■</span> '
            f'<span style="color:#666">{html.escape(subtitle)}</span>')
        self.title_label.setToolTip(tooltip)

    def _fill_params(self, groups):
        if not groups:
            self._empty_row(self.params_tree,
                            "Параметров нет: ни у самого выбранного, "
                            "ни в уставках его объекта")
            return

        for title, rows in groups:
            group_item = QTreeWidgetItem(self.params_tree)
            group_item.setText(0, title)
            group_item.setFont(0, self._bold(group_item.font(0)))
            for name, value, meter, lua_name in rows:
                item = QTreeWidgetItem(group_item)
                item.setText(0, name)
                item.setText(1, value)
                item.setText(2, meter)
                item.setText(3, lua_name)
            group_item.setExpanded(True)

    def _fill_device_states(self, entries):
        """Дерево «операция → состояние → шаг» для устройства.

        Плоский список из описания объектов группируется здесь, а не в данных:
        выгрузке нужен именно список, а человеку — вложенность.
        """
        self.states_tree.setHeaderLabels(list(self.DEVICE_STATE_HEADERS))
        if not entries:
            self._empty_row(self.states_tree,
                            "Устройство не участвует ни в одной операции "
                            "или main.objects.lua не загружен")
            return

        operations: Dict[str, QTreeWidgetItem] = {}
        states: Dict[Tuple[str, str], QTreeWidgetItem] = {}

        for entry in entries:
            operation_key = entry["operation_id"]
            operation_item = operations.get(operation_key)
            if operation_item is None:
                operation_item = self._group_item(
                    self.states_tree, f"⚙ {entry['operation']} · {entry['tech_object']}")
                operations[operation_key] = operation_item

            state_key = (operation_key, entry["state_id"])
            state_item = states.get(state_key)
            if state_item is None:
                state_item = self._state_item(operation_item, entry["state"])
                states[state_key] = state_item

            # Положение бывает задано самим состоянием, без шага: строка
            # всё равно нужна — иначе состояние выглядело бы пустым
            step_item = QTreeWidgetItem(state_item)
            step_item.setText(0, f"▶ {entry['step']}" if entry["step"]
                              else "▶ задано состоянием")
            self._set_status(step_item, entry["status"])
            if entry["step_number"] >= 0:
                step_item.setText(2, str(entry["step_number"]))

    def _fill_operation_states(self, structure, entries):
        """Дерево «состояние → шаг → устройство» для операции.

        Скелет — состояния и шаги самой операции: шаг без устройств тоже
        должен быть виден, а раньше пустая операция выглядела бы вовсе
        без состояний. Устройства навешиваются на шаги теми же записями,
        которыми устройство отвечает, где оно участвует, — рассказать разное
        про одно и то же панель не может.

        Шаги свёрнуты: в них бывает по десятку устройств, а видеть надо
        прежде всего порядок шагов.
        """
        self.states_tree.setHeaderLabels(list(self.OPERATION_STATE_HEADERS))
        if not structure:
            self._empty_row(self.states_tree,
                            "У операции нет состояний "
                            "или main.objects.lua не загружен")
            return

        places = entries_by_place(entries)
        for state, steps in structure:
            state_item = self._state_item(self.states_tree, state.name)

            # Положение, заданное самим состоянием, без шага
            self._place_item(state_item, "▶ задано состоянием", -1,
                             places.get((state.id, ""), []), skip_empty=True)
            for step in steps:
                self._place_item(state_item, f"▶ {step.name}", step.step_number,
                                 places.get((state.id, step.id), []))

    def _place_item(self, parent: QTreeWidgetItem, title: str, number: int,
                    entries, skip_empty: bool = False) -> None:
        # Шаг (или само состояние) со своими устройствами. Сколько устройств
        # он открывает и закрывает — видно не разворачивая
        if skip_empty and not entries:
            return

        item = QTreeWidgetItem(parent)
        item.setText(0, title)
        if number >= 0:
            item.setText(2, str(number))

        counts = {"opened": 0, "closed": 0}
        for entry in entries:
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
            device_item = QTreeWidgetItem(item)
            device_item.setText(0, entry["device"])
            self._set_status(device_item, entry["status"])

        item.setText(1, f"🔓 {counts['opened']} · 🔒 {counts['closed']}"
                     if entries else "устройств нет")

    def _fill_table(self, table: QTableWidget, rows):
        if not rows:
            return
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))
        table.resizeRowsToContents()

    @staticmethod
    def _group_item(parent, text: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent)
        item.setText(0, text)
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)
        item.setExpanded(True)
        return item

    @staticmethod
    def _state_item(parent, name: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent)
        item.setText(0, f"📌 {name}")
        item.setForeground(0, QBrush(QColor(0, 100, 200)))
        item.setExpanded(True)
        return item

    @staticmethod
    def _set_status(item: QTreeWidgetItem, status: str) -> None:
        item.setText(1, f"{STATUS_ICONS.get(status, '')} {state_text(status)}")
        color = STATUS_COLORS.get(status)
        if color:
            item.setForeground(1, QBrush(QColor(color)))

    @staticmethod
    def _empty_row(tree: QTreeWidget, text: str):
        item = QTreeWidgetItem(tree)
        item.setText(0, text)
        item.setForeground(0, QBrush(QColor(136, 136, 136)))

    @staticmethod
    def _bold(font: QFont) -> QFont:
        font.setBold(True)
        return font
