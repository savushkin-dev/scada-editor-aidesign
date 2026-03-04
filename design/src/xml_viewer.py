# xml_viewer.py (обновленная версия)
import sys
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional, Set

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                               QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                               QGraphicsTextItem, QGraphicsEllipseItem, QSplitter,
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QComboBox, QSpinBox, QCheckBox, QGroupBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QTabWidget, QTextEdit,
                               QLineEdit)
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter

# Импортируем модели
from data_models import DeviceMatch, Contour, DeviceOperationState
from objects_loader import objects_data, TechObject, Operation as TechOperation, State, Step, Parameter


class DeviceGraphicsItem(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, radius: float, device_data: DeviceMatch, parent=None):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)
        self.device_data = device_data
        self.setAcceptHoverEvents(True)
        self.setToolTip(self._create_tooltip())
        self.base_color = Qt.GlobalColor.red

        # Настройки внешнего вида
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setBrush(QBrush(self.base_color))
        self.setZValue(3)

    def _create_tooltip(self) -> str:
        lines = []
        lines.append(f"<b>{self.device_data.lua_name}</b>")
        lines.append(f"PDF имя: {self.device_data.pdf_name}")
        lines.append(f"Объект: {self.device_data.tech_object}")
        lines.append(f"Координаты: ({self.device_data.coordinates[0]:.1f}, {self.device_data.coordinates[1]:.1f})")

        if self.device_data.descr:
            lines.append(f"Описание: {self.device_data.descr}")
        if self.device_data.article:
            lines.append(f"Артикул: {self.device_data.article}")
        if self.device_data.device_type:
            lines.append(f"Тип: {self.device_data.device_type}")
        if self.device_data.category:
            lines.append(f"Категория: {self.device_data.category}")

        # Добавляем информацию о состояниях в операциях (из объектов, если есть)
        if hasattr(self.device_data, 'operation_states') and self.device_data.operation_states:
            lines.append("")
            lines.append("<b>Состояния в операциях:</b>")
            for state in self.device_data.operation_states:
                state_text = f"  • {state.operation_name}: <b>{state.state}</b>"
                if state.state_id:
                    state_text += f" ({state.state_id})"
                lines.append(state_text)

        return "<br>".join(lines)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        lighter = self.base_color.lighter(150)
        self.setBrush(QBrush(lighter))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setBrush(QBrush(self.base_color))
        super().hoverLeaveEvent(event)


class TextItemWithBackground(QGraphicsTextItem):
    def __init__(self, text: str, color: QColor = Qt.GlobalColor.black,
                 bg_color: QColor = QColor(255, 255, 255, 200), device_data: DeviceMatch = None):
        super().__init__(text)
        self.device_data = device_data
        self.setDefaultTextColor(color)
        self.setFont(QFont("Arial", 8))

        # Сохраняем цвет фона
        self.bg_color = bg_color

        # Если есть данные устройства, добавляем всплывающую подсказку
        if device_data:
            self.setAcceptHoverEvents(True)
            self.setToolTip(self._create_tooltip())

    def _create_tooltip(self) -> str:
        if not self.device_data:
            return ""

        lines = []
        lines.append(f"<b>{self.device_data.lua_name}</b>")
        lines.append(f"PDF имя: {self.device_data.pdf_name}")
        lines.append(f"Объект: {self.device_data.tech_object}")

        if self.device_data.descr:
            lines.append(f"Описание: {self.device_data.descr}")
        if self.device_data.article:
            lines.append(f"Артикул: {self.device_data.article}")
        if self.device_data.device_type:
            lines.append(f"Тип: {self.device_data.device_type}")

        # Добавляем информацию о состояниях в операциях
        if hasattr(self.device_data, 'operation_states') and self.device_data.operation_states:
            lines.append("")
            lines.append("<b>Состояния в операциях:</b>")
            for state in self.device_data.operation_states:
                lines.append(f"  • {state.operation_name}: {state.state}")

        return "<br>".join(lines)

    def paint(self, painter: QPainter, option, widget=None):
        # Рисуем фон
        painter.save()
        painter.setBrush(QBrush(self.bg_color))
        painter.setPen(Qt.PenStyle.NoPen)

        # Получаем прямоугольник текста
        rect = self.boundingRect()
        # Добавляем отступы
        rect = QRectF(rect.x() - 2, rect.y() - 1, rect.width() + 4, rect.height() + 2)
        painter.drawRect(rect)
        painter.restore()

        # Рисуем текст
        super().paint(painter, option, widget)


class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Включаем всплывающие подсказки
        self.setMouseTracking(True)

        # Настройки масштабирования
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Сохраняем позицию под мышью
        old_pos = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        self.scale(zoom_factor, zoom_factor)

        # Возвращаем позицию под мышью
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MidButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MidButton:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def fit_in_view(self):
        if self._scene.items():
            self.fitInView(self._scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = 0


class OperationDetailsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_operation = None
        self.current_object = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Вкладки для разных аспектов операции
        self.tab_widget = QTabWidget()

        # Вкладка с основной информацией
        self.info_widget = QWidget()
        info_layout = QVBoxLayout(self.info_widget)

        # Текстовое поле для детальной информации
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)

        self.tab_widget.addTab(self.info_widget, "Основная информация")

        # Вкладка с параметрами
        self.params_widget = QWidget()
        params_layout = QVBoxLayout(self.params_widget)

        self.params_table = QTableWidget()
        self.params_table.setColumnCount(4)
        self.params_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Ед. изм.", "Lua имя"])
        self.params_table.horizontalHeader().setStretchLastSection(True)
        self.params_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        params_layout.addWidget(self.params_table)

        self.tab_widget.addTab(self.params_widget, "Параметры")

        # Вкладка с состояниями и шагами
        self.states_widget = QWidget()
        states_layout = QVBoxLayout(self.states_widget)

        # Дерево состояний и шагов
        self.states_tree = QTreeWidget()
        self.states_tree.setHeaderLabels(["Состояния и шаги операции"])
        self.states_tree.itemClicked.connect(self.on_state_or_step_clicked)
        states_layout.addWidget(self.states_tree)

        self.tab_widget.addTab(self.states_widget, "Состояния и шаги")

        # Вкладка с пропертями
        self.props_widget = QWidget()
        props_layout = QVBoxLayout(self.props_widget)

        self.props_table = QTableWidget()
        self.props_table.setColumnCount(2)
        self.props_table.setHorizontalHeaderLabels(["Свойство", "Значение"])
        self.props_table.horizontalHeader().setStretchLastSection(True)
        self.props_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        props_layout.addWidget(self.props_table)

        self.tab_widget.addTab(self.props_widget, "Свойства")

        layout.addWidget(self.tab_widget)

    def clear(self):
        self.current_operation = None
        self.current_object = None
        self.info_text.clear()
        self.params_table.setRowCount(0)
        self.states_tree.clear()
        self.props_table.setRowCount(0)

    def display_operation(self, operation: TechOperation):
        self.current_operation = operation
        self.current_object = objects_data.get_object_for_operation(operation)

        if not operation:
            self.clear()
            return

        # Основная информация
        info_lines = []
        info_lines.append(f"<b>Операция:</b> {operation.name}")
        info_lines.append(f"<b>ID:</b> {operation.id}")
        info_lines.append(f"<b>Тех. объект:</b> {operation.obj_name}")
        info_lines.append(f"<b>Базовая операция:</b> {operation.base_operation or 'Нет'}")

        if self.current_object:
            info_lines.append("")
            info_lines.append(f"<b>Тех. объект детально:</b>")
            info_lines.append(f"  • Тип: {self.current_object.tech_type}")
            info_lines.append(f"  • Eplan имя: {self.current_object.name_eplan}")
            info_lines.append(f"  • BC имя: {self.current_object.name_BC}")
            info_lines.append(f"  • Базовый объект: {self.current_object.base_tech_object}")

        self.info_text.setHtml("<br>".join(info_lines))

        # Параметры операции (из props)
        props = operation.props
        self.props_table.setRowCount(len(props))
        for i, (key, value) in enumerate(props.items()):
            self.props_table.setItem(i, 0, QTableWidgetItem(key))
            self.props_table.setItem(i, 1, QTableWidgetItem(str(value)))

        # Параметры тех. объекта
        if self.current_object:
            params = objects_data.get_parameters_for_object(self.current_object.id)
            self.params_table.setRowCount(len(params))
            for i, param in enumerate(params):
                self.params_table.setItem(i, 0, QTableWidgetItem(param.name))
                self.params_table.setItem(i, 1, QTableWidgetItem(str(param.value)))
                self.params_table.setItem(i, 2, QTableWidgetItem(param.meter))
                self.params_table.setItem(i, 3, QTableWidgetItem(param.nameLua))

        # Состояния и шаги
        self._populate_states_tree(operation)

    def _populate_states_tree(self, operation: TechOperation):
        self.states_tree.clear()

        states = objects_data.get_states_for_operation(operation.id)
        if not states:
            empty_item = QTreeWidgetItem(self.states_tree)
            empty_item.setText(0, "Нет состояний")
            return

        for state in states:
            # Элемент состояния
            state_item = QTreeWidgetItem(self.states_tree)
            state_item.setText(0, f"📌 {state.name}")
            state_item.setForeground(0, QBrush(QColor(0, 100, 200)))
            state_item.setData(0, Qt.ItemDataRole.UserRole, state)

            # Добавляем шаги
            steps = objects_data.get_steps_for_state(state.id)
            if steps:
                for step in steps:
                    step_item = QTreeWidgetItem(state_item)
                    step_item.setText(0, f"  ▶ {step.name}")
                    step_item.setForeground(0, QBrush(QColor(100, 100, 100)))
                    step_item.setData(0, Qt.ItemDataRole.UserRole, step)

                    # Добавляем информацию об устройствах
                    devices_text = []
                    if step.opened_devices:
                        devices_text.append(f"Открыть: {', '.join(step.opened_devices[:3])}")
                    if step.closed_devices:
                        devices_text.append(f"Закрыть: {', '.join(step.closed_devices[:3])}")
                    if devices_text:
                        info_item = QTreeWidgetItem(step_item)
                        info_item.setText(0, "    " + " | ".join(devices_text))
                        info_item.setForeground(0, QBrush(QColor(150, 150, 150)))
            else:
                no_step_item = QTreeWidgetItem(state_item)
                no_step_item.setText(0, "  (нет шагов)")

            state_item.setExpanded(True)

    def on_state_or_step_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(data, State):
            # Клик по состоянию
            self._show_state_info(data)
        elif isinstance(data, Step):
            # Клик по шагу - показываем только открытые и закрытые устройства
            self._show_step_info(data)

    def _show_state_info(self, state: State):
        # Собираем информацию об устройствах из состояния
        opened_devices = []
        closed_devices = []
        checked_devices = []

        state_data = state.state_data
        if "opened_devices" in state_data:
            opened_devices = state_data["opened_devices"]
        if "closed_devices" in state_data:
            closed_devices = state_data["closed_devices"]
        if "checked_devices" in state_data:
            checked_devices = state_data["checked_devices"]

        # Формируем сообщение
        msg_lines = [f"<b>Состояние: {state.name}</b>", ""]

        if opened_devices:
            msg_lines.append("<b>Открываемые устройства:</b>")
            msg_lines.extend([f"  • {dev}" for dev in opened_devices[:10]])
            if len(opened_devices) > 10:
                msg_lines.append(f"  ... и еще {len(opened_devices) - 10}")

        if closed_devices:
            if opened_devices:
                msg_lines.append("")
            msg_lines.append("<b>Закрываемые устройства:</b>")
            msg_lines.extend([f"  • {dev}" for dev in closed_devices[:10]])
            if len(closed_devices) > 10:
                msg_lines.append(f"  ... и еще {len(closed_devices) - 10}")

        if checked_devices:
            if opened_devices or closed_devices:
                msg_lines.append("")
            msg_lines.append("<b>Проверяемые устройства:</b>")
            msg_lines.extend([f"  • {dev}" for dev in checked_devices[:10]])
            if len(checked_devices) > 10:
                msg_lines.append(f"  ... и еще {len(checked_devices) - 10}")

        if not (opened_devices or closed_devices or checked_devices):
            msg_lines.append("Нет информации об устройствах")

        QMessageBox.information(
            self,
            f"Состояние: {state.name}",
            "<br>".join(msg_lines)
        )

    def _show_step_info(self, step: Step):
        msg_lines = [f"<b>Шаг: {step.name}</b>", ""]

        if step.opened_devices:
            msg_lines.append("<b>Открываемые устройства:</b>")
            msg_lines.extend([f"  • {dev}" for dev in step.opened_devices])

        if step.closed_devices:
            if step.opened_devices:
                msg_lines.append("")
            msg_lines.append("<b>Закрываемые устройства:</b>")
            msg_lines.extend([f"  • {dev}" for dev in step.closed_devices])

        if not step.opened_devices and not step.closed_devices:
            msg_lines.append("Нет информации об устройствах")

        QMessageBox.information(
            self,
            f"Шаг: {step.name}",
            "<br>".join(msg_lines)
        )


class OperationsBrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        # Загружаем операции после инициализации UI
        QTimer.singleShot(100, self._load_operations)  # Небольшая задержка для гарантии загрузки

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Фильтры
        filter_layout = QHBoxLayout()

        self.object_filter = QComboBox()
        self.object_filter.addItem("Все тех. объекты")
        self.object_filter.currentTextChanged.connect(self.filter_operations)
        filter_layout.addWidget(QLabel("Тех. объект:"))
        filter_layout.addWidget(self.object_filter)

        self.operation_filter = QLineEdit()
        self.operation_filter.setPlaceholderText("Поиск операций...")
        self.operation_filter.textChanged.connect(self.filter_operations)
        filter_layout.addWidget(self.operation_filter)

        # Кнопка обновления
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self._load_operations)
        filter_layout.addWidget(self.refresh_btn)

        layout.addLayout(filter_layout)

        # Информационная метка
        self.info_label = QLabel("Загрузка данных...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Сплиттер для дерева операций и деталей
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - дерево операций
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.operations_tree = QTreeWidget()
        self.operations_tree.setHeaderLabels(["Операции технологических объектов"])
        self.operations_tree.itemClicked.connect(self.on_operation_selected)
        left_layout.addWidget(self.operations_tree)

        splitter.addWidget(left_widget)

        # Правая панель - детали операции
        self.operation_details = OperationDetailsWidget()
        splitter.addWidget(self.operation_details)

        # Устанавливаем пропорции
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def _load_operations(self):
        print("\n=== Загрузка операций в дерево ===")
        self.operations_tree.clear()

        # Проверяем наличие данных
        if not objects_data.objects:
            print("objects_data.objects пуст, пробуем загрузить...")
            objects_data.load()

        print(f"Всего тех. объектов: {len(objects_data.objects)}")

        if not objects_data.objects:
            self.info_label.setText("❌ Нет данных о технологических объектах")
            self.info_label.setStyleSheet("color: red;")
            return

        # Считаем общее количество операций
        total_operations = 0
        objects_with_ops = 0

        # Группируем операции по тех. объектам
        for tech_obj in objects_data.objects:
            if not tech_obj.operations:
                print(f"  {tech_obj.name}: нет операций")
                continue

            objects_with_ops += 1
            total_operations += len(tech_obj.operations)

            print(f"  {tech_obj.name}: {len(tech_obj.operations)} операций")

            obj_item = QTreeWidgetItem(self.operations_tree)
            obj_item.setText(0, f"{tech_obj.name} [{len(tech_obj.operations)}]")
            obj_item.setForeground(0, QBrush(QColor(0, 100, 200)))

            # Сортируем операции
            for operation in sorted(tech_obj.operations, key=lambda x: x.name):
                op_item = QTreeWidgetItem(obj_item)
                op_item.setText(0, operation.name)

                # Добавляем информацию о базовой операции
                if operation.base_operation:
                    op_item.setText(0, f"{operation.name} (base: {operation.base_operation})")

                # Сохраняем данные операции
                op_item.setData(0, Qt.ItemDataRole.UserRole, operation)

                # Добавляем состояния и шаги
                states = objects_data.get_states_for_operation(operation.id)
                if states:
                    for state in states[:2]:  # Показываем первые 2 состояния
                        state_item = QTreeWidgetItem(op_item)
                        state_item.setText(0, f"  📌 {state.name}")
                        state_item.setForeground(0, QBrush(QColor(100, 100, 100)))
                        state_item.setData(0, Qt.ItemDataRole.UserRole, state)

                        # Добавляем шаги
                        steps = objects_data.get_steps_for_state(state.id)
                        if steps:
                            for step in steps[:2]:  # Показываем первые 2 шага
                                step_item = QTreeWidgetItem(state_item)
                                step_item.setText(0, f"    ▶ {step.name}")
                                step_item.setForeground(0, QBrush(QColor(150, 150, 150)))
                                step_item.setData(0, Qt.ItemDataRole.UserRole, step)

                            if len(steps) > 2:
                                more_item = QTreeWidgetItem(state_item)
                                more_item.setText(0, f"    ... и еще {len(steps) - 2} шагов")
                                more_item.setForeground(0, QBrush(QColor(180, 180, 180)))

                    if len(states) > 2:
                        more_item = QTreeWidgetItem(op_item)
                        more_item.setText(0, f"  ... и еще {len(states) - 2} состояний")
                        more_item.setForeground(0, QBrush(QColor(150, 150, 150)))

                obj_item.setExpanded(False)

        print(f"\nИтого: {objects_with_ops} объектов с операциями, всего {total_operations} операций")

        # Обновляем информацию
        if total_operations > 0:
            self.info_label.setText(f"✅ Загружено {total_operations} операций из {objects_with_ops} объектов")
            self.info_label.setStyleSheet("color: green;")
        else:
            self.info_label.setText("⚠️ Операции не найдены")
            self.info_label.setStyleSheet("color: orange;")

        # Добавляем фильтр тех. объектов
        self._update_object_filter()

        # Если есть объекты, разворачиваем первый для наглядности
        if self.operations_tree.topLevelItemCount() > 0:
            self.operations_tree.topLevelItem(0).setExpanded(True)

    def _update_object_filter(self):
        self.object_filter.clear()
        self.object_filter.addItem("Все тех. объекты")

        for tech_obj in objects_data.objects:
            if tech_obj.operations:
                self.object_filter.addItem(tech_obj.name)

    def filter_operations(self):
        tech_filter = self.object_filter.currentText()
        text_filter = self.operation_filter.text().lower()

        visible_count = 0

        for i in range(self.operations_tree.topLevelItemCount()):
            obj_item = self.operations_tree.topLevelItem(i)

            # Проверяем фильтр по тех. объекту
            obj_name = obj_item.text(0).split(" [")[0]
            if tech_filter != "Все тех. объекты" and obj_name != tech_filter:
                obj_item.setHidden(True)
                continue

            # Проверяем текстовый фильтр
            if text_filter:
                has_visible = False
                for j in range(obj_item.childCount()):
                    op_item = obj_item.child(j)
                    op_name = op_item.text(0).lower()
                    visible = text_filter in op_name
                    op_item.setHidden(not visible)
                    if visible:
                        has_visible = True
                        visible_count += 1

                obj_item.setHidden(not has_visible)
                if has_visible:
                    obj_item.setExpanded(True)
            else:
                # Сбрасываем фильтр
                obj_item.setHidden(False)
                for j in range(obj_item.childCount()):
                    obj_item.child(j).setHidden(False)
                    visible_count += 1
                obj_item.setExpanded(False)

        # Обновляем информацию
        if text_filter:
            self.info_label.setText(f"Найдено {visible_count} операций")

    def on_operation_selected(self, item: QTreeWidgetItem, column: int):
        operation = item.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(operation, TechOperation):
            print(f"Выбрана операция: {operation.name}")
            self.operation_details.display_operation(operation)
        elif isinstance(operation, State):
            # Если выбрано состояние, показываем его операцию
            print(f"Выбрано состояние: {operation.name}")
            parent_op = objects_data.get_operation_by_id(operation.operation_id)
            if parent_op:
                self.operation_details.display_operation(parent_op)
        elif isinstance(operation, Step):
            # Если выбран шаг, показываем операцию
            print(f"Выбран шаг: {operation.name}")
            parent_op = objects_data.get_operation_by_id(operation.operation_id)
            if parent_op:
                self.operation_details.display_operation(parent_op)


class DeviceVisualizer(QMainWindow):
    DEVICE_TYPE_COLORS = {
        "V": QColor("#e74c3c"),  # клапаны - красный
        "DI": QColor("#3498db"),  # дискретные входы - синий
        "DO": QColor("#2980b9"),
        "AI": QColor("#2ecc71"),  # аналоговые входы - зеленый
        "AO": QColor("#27ae60"),
        "PT": QColor("#f39c12"),  # давление - оранжевый
        "LT": QColor("#9b59b6"),  # уровень - фиолетовый
        "TE": QColor("#1abc9c"),  # температура - бирюза
        "LS": QColor("#8e44ad"),
        "QT": QColor("#d35400"),
        "FQT": QColor("#c0392b"),
        "PC": QColor("#7f8c8d"),
        "M": QColor("#34495e"),  # насосы - серый
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация сопоставленных устройств")
        self.setGeometry(100, 100, 1800, 1000)

        # Данные
        self.matches: List[DeviceMatch] = []
        self.contours: List[Contour] = []
        self.tech_object_colors: Dict[str, QColor] = {}

        # Инициализация интерфейса
        self._init_ui()

        # Загружаем данные о технологических объектах
        self._load_objects_data()

    def _load_objects_data(self):
        if objects_data.load():
            print(f"✅ Загружено тех. объектов: {len(objects_data.objects)}")
            print(f"✅ Загружено операций: {len(objects_data.operations)}")
            print(f"✅ Загружено состояний: {len(objects_data.states)}")
            print(f"✅ Загружено шагов: {len(objects_data.steps)}")
        else:
            print("⚠️ Не удалось загрузить данные о тех. объектах")

    def _init_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout(central_widget)

        # Создаем главный сплиттер
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # Левая панель - управление и дерево
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Кнопки загрузки
        load_btn = QPushButton("Загрузить XML файл")
        load_btn.clicked.connect(self.load_xml_file)
        left_layout.addWidget(load_btn)

        # Информация о файле
        self.file_info_label = QLabel("Файл не загружен")
        self.file_info_label.setWordWrap(True)
        left_layout.addWidget(self.file_info_label)

        # Разделитель
        left_layout.addWidget(QLabel(""))

        # Группа фильтров
        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout(filter_group)

        # Выбор технологического объекта
        self.tech_filter = QComboBox()
        self.tech_filter.addItem("Все объекты")
        self.tech_filter.currentTextChanged.connect(self.update_display)
        filter_layout.addWidget(QLabel("Тех. объект:"))
        filter_layout.addWidget(self.tech_filter)

        left_layout.addWidget(filter_group)

        # Группа настроек отображения
        display_group = QGroupBox("Настройки отображения")
        display_layout = QVBoxLayout(display_group)

        # Прозрачность контуров
        self.contour_alpha = QSpinBox()
        self.contour_alpha.setRange(0, 255)
        self.contour_alpha.setValue(50)
        self.contour_alpha.setSingleStep(10)
        self.contour_alpha.valueChanged.connect(self.update_display)
        display_layout.addWidget(QLabel("Прозрачность контуров:"))
        display_layout.addWidget(self.contour_alpha)

        # Показать имена контуров
        self.show_contour_names = QCheckBox("Показать имена контуров")
        self.show_contour_names.setChecked(True)
        self.show_contour_names.stateChanged.connect(self.update_display)
        display_layout.addWidget(self.show_contour_names)

        # Показать имена устройств
        self.show_device_names = QCheckBox("Показать имена устройств")
        self.show_device_names.setChecked(True)
        self.show_device_names.stateChanged.connect(self.update_display)
        display_layout.addWidget(self.show_device_names)

        # Показывать всплывающие подсказки
        self.show_tooltips = QCheckBox("Показывать всплывающие подсказки")
        self.show_tooltips.setChecked(True)
        self.show_tooltips.stateChanged.connect(self.update_display)
        display_layout.addWidget(self.show_tooltips)

        left_layout.addWidget(display_group)

        # Кнопка сброса масштаба
        reset_view_btn = QPushButton("Сбросить масштаб (F)")
        reset_view_btn.clicked.connect(self.reset_view)
        left_layout.addWidget(reset_view_btn)

        # Разделитель
        left_layout.addWidget(QLabel(""))

        # Дерево устройств
        left_layout.addWidget(QLabel("Сопоставленные устройства:"))
        self.device_tree = QTreeWidget()
        self.device_tree.setHeaderLabels(["Устройство", "Тип", "Артикул"])
        self.device_tree.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.device_tree)

        # Добавляем левую панель в главный сплиттер
        main_splitter.addWidget(left_panel)

        # Правая часть - сплиттер для графики и операций
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Верхняя панель - графика
        self.graphics_view = GraphicsView()
        right_splitter.addWidget(self.graphics_view)

        # Нижняя панель - операции тех. объектов
        self.operations_browser = OperationsBrowserWidget()
        right_splitter.addWidget(self.operations_browser)

        # Устанавливаем пропорции для вертикального сплиттера
        right_splitter.setSizes([700, 300])

        main_splitter.addWidget(right_splitter)

        # Устанавливаем пропорции главного сплиттера
        main_splitter.setSizes([400, 1400])

    def load_xml_file(self, file_path: str = None):
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
            # Очистка текущих данных
            self.matches.clear()
            self.contours.clear()
            self.tech_object_colors.clear()
            self.device_tree.clear()
            self.tech_filter.clear()

            tree = ET.parse(file_path)
            root = tree.getroot()

            # Парсинг XML
            for tech_obj in root.findall(".//TechnologicalObject"):
                tech_name = tech_obj.get("name", "")

                if not tech_name:
                    continue

                # Цвет технологического объекта
                if tech_name not in self.tech_object_colors:
                    self.tech_object_colors[tech_name] = self._generate_color(tech_name)

                # Контур
                contour_elem = tech_obj.find("Contour")
                if contour_elem is not None:
                    bounds_str = contour_elem.get("bounds", "")
                    center_str = contour_elem.get("center", "")

                    if bounds_str and center_str:
                        try:
                            bounds = tuple(map(float, bounds_str.split(',')))
                            center = tuple(map(float, center_str.split(',')))

                            contour = Contour(
                                name=tech_name,
                                bounds=bounds,
                                center=center,
                                tech_object=tech_name
                            )
                            self.contours.append(contour)

                        except ValueError:
                            print(f"Ошибка парсинга контура для {tech_name}")

                # Устройства
                devices_elem = tech_obj.find("Devices")
                if devices_elem is None:
                    continue

                for device in devices_elem.findall("Device"):
                    try:
                        lua_name = device.get("lua_name", "")
                        pdf_name = device.get("pdf_name", "")
                        x = float(device.get("x", 0))
                        y = float(device.get("y", 0))
                        confidence = float(device.get("confidence", 0))
                        device_type = device.get("device_type", "")

                        # Собираем дополнительные данные
                        extra_data = {}
                        for key, value in device.attrib.items():
                            if key not in [
                                "lua_name", "pdf_name", "x", "y", "confidence",
                                "descr", "article", "type", "category", "device_type"
                            ]:
                                extra_data[key] = value

                        match = DeviceMatch(
                            lua_name=lua_name,
                            pdf_name=pdf_name,
                            tech_object=tech_name,
                            coordinates=(x, y),
                            confidence=confidence,
                            descr=device.get("descr", ""),
                            article=device.get("article", ""),
                            device_type=device_type,
                            category=device.get("category", ""),
                            extra_data=extra_data
                        )

                        # Сохраняем цвет
                        match.color = self.DEVICE_TYPE_COLORS.get(
                            device_type,
                            QColor("black")
                        )

                        self.matches.append(match)

                    except (ValueError, TypeError) as e:
                        print(f"Ошибка парсинга устройства {device.get('lua_name')}: {e}")

            # Обновление интерфейса
            self._update_file_info(file_path)
            self._update_tech_filter()
            self._update_device_tree()
            self.draw_scene()

            QMessageBox.information(
                self,
                "Успех",
                f"Загружено {len(self.contours)} контуров и {len(self.matches)} устройств"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить файл:\n{str(e)}"
            )

    def _update_device_tree(self):
        self.device_tree.clear()

        # Группируем по технологическим объектам
        devices_by_tech = {}
        for match in self.matches:
            if match.tech_object not in devices_by_tech:
                devices_by_tech[match.tech_object] = []
            devices_by_tech[match.tech_object].append(match)

        # Добавляем элементы в дерево
        for tech_obj in sorted(devices_by_tech.keys()):
            tech_item = QTreeWidgetItem(self.device_tree)
            tech_item.setText(0, tech_obj)
            tech_item.setForeground(0, QBrush(self.tech_object_colors.get(tech_obj, Qt.GlobalColor.black)))
            tech_item.setText(1, f"({len(devices_by_tech[tech_obj])})")

            for match in sorted(devices_by_tech[tech_obj], key=lambda x: x.pdf_name):
                device_item = QTreeWidgetItem(tech_item)
                device_item.setText(0, match.pdf_name)
                device_item.setText(1, match.device_type or "-")
                device_item.setText(2, match.article or "-")

                device_item.setData(0, Qt.ItemDataRole.UserRole, match)

                tooltip = self._create_tree_item_tooltip(match)
                device_item.setToolTip(0, tooltip)

            tech_item.setExpanded(True)

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

        lines.append(f"Координаты: ({match.coordinates[0]:.1f}, {match.coordinates[1]:.1f})")

        return "<br>".join(lines)

    def draw_scene(self):
        scene = self.graphics_view._scene
        scene.clear()

        if not self.contours:
            return

        current_filter = self.tech_filter.currentText()

        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        contour_alpha = self.contour_alpha.value()

        # Рисуем контуры
        for contour in self.contours:
            if current_filter != "Все объекты" and contour.tech_object != current_filter:
                continue

            minx, miny, maxx, maxy = contour.bounds
            width = maxx - minx
            height = maxy - miny

            min_x = min(min_x, minx)
            min_y = min(min_y, miny)
            max_x = max(max_x, maxx)
            max_y = max(max_y, maxy)

            color = self.tech_object_colors.get(contour.tech_object, Qt.GlobalColor.blue)

            rect_item = QGraphicsRectItem(minx, miny, width, height)
            rect_pen = QPen(color)
            rect_pen.setWidth(2)
            rect_item.setPen(rect_pen)

            fill_color = QColor(color)
            fill_color.setAlpha(contour_alpha)
            rect_item.setBrush(QBrush(fill_color))

            scene.addItem(rect_item)

            if self.show_contour_names.isChecked() and contour.name:
                text_item = QGraphicsTextItem(contour.name)
                text_item.setDefaultTextColor(color)
                text_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                text_item.setPos(contour.center[0] - 30, contour.center[1] - 15)
                text_item.setZValue(2)
                scene.addItem(text_item)

        # Рисуем устройства
        for match in self.matches:
            if current_filter != "Все объекты" and match.tech_object != current_filter:
                continue

            # Определяем цвет устройства
            device_color = getattr(match, "color", None)
            if not device_color:
                device_color = self.DEVICE_TYPE_COLORS.get(
                    match.device_type,
                    QColor("black")
                )

            # Точка устройства
            if self.show_tooltips.isChecked():
                device_item = DeviceGraphicsItem(
                    match.coordinates[0],
                    match.coordinates[1],
                    5,
                    match
                )
                device_item.base_color = device_color
                device_item.setBrush(QBrush(device_color))
                scene.addItem(device_item)
            else:
                ellipse_item = QGraphicsEllipseItem(
                    match.coordinates[0] - 5,
                    match.coordinates[1] - 5,
                    10,
                    10
                )
                ellipse_item.setPen(QPen(Qt.GlobalColor.black, 1))
                ellipse_item.setBrush(QBrush(device_color))
                ellipse_item.setZValue(3)
                scene.addItem(ellipse_item)

            # Имя устройства
            if self.show_device_names.isChecked():
                text = f"{match.pdf_name}"
                if match.confidence < 1.0:
                    text += f" ({match.confidence:.1f})"

                if self.show_tooltips.isChecked():
                    text_item = TextItemWithBackground(
                        text,
                        Qt.GlobalColor.black,
                        QColor(255, 255, 255, 200),
                        match
                    )
                else:
                    text_item = TextItemWithBackground(
                        text,
                        Qt.GlobalColor.black,
                        QColor(255, 255, 255, 200)
                    )

                text_item.setPos(match.coordinates[0] + 8, match.coordinates[1] - 10)
                text_item.setZValue(2)
                scene.addItem(text_item)

        if min_x != float('inf'):
            margin = 50
            scene.setSceneRect(
                min_x - margin,
                min_y - margin,
                (max_x - min_x) + 2 * margin,
                (max_y - min_y) + 2 * margin
            )

        self.reset_view()

    def _generate_color(self, tech_name: str) -> QColor:
        colors = [
            QColor(255, 0, 0),  # Красный
            QColor(0, 150, 0),  # Зеленый
            QColor(0, 0, 255),  # Синий
            QColor(255, 165, 0),  # Оранжевый
            QColor(128, 0, 128),  # Фиолетовый
            QColor(255, 192, 203),  # Розовый
            QColor(165, 42, 42),  # Коричневый
            QColor(0, 128, 128),  # Бирюзовый
            QColor(255, 255, 0),  # Желтый
            QColor(128, 128, 0),  # Оливковый
        ]
        hash_val = hash(tech_name) % len(colors)
        return colors[hash_val]

    def _update_file_info(self, file_path: str):
        import os
        filename = os.path.basename(file_path)
        self.file_info_label.setText(
            f"Файл: {filename}\n"
            f"Контуров: {len(self.contours)}\n"
            f"Устройств: {len(self.matches)}"
        )

    def _update_tech_filter(self):
        self.tech_filter.clear()
        self.tech_filter.addItem("Все объекты")

        tech_objects = set(m.tech_object for m in self.matches)
        for tech_obj in sorted(tech_objects):
            self.tech_filter.addItem(tech_obj)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        match = item.data(0, Qt.ItemDataRole.UserRole)
        if match:
            self.center_on_point(match.coordinates)

    def center_on_point(self, point: Tuple[float, float]):
        self.graphics_view.centerOn(point[0], point[1])

    def update_display(self):
        self.draw_scene()

    def reset_view(self):
        self.graphics_view.fit_in_view()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F:
            self.reset_view()
        elif event.key() == Qt.Key.Key_O:
            self.load_xml_file()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)

    # Устанавливаем стиль
    app.setStyle('Fusion')

    # Создаем и показываем окно
    window = DeviceVisualizer()
    window.show()

    # Загружаем файл по умолчанию, если он существует
    import os
    if os.path.exists("output/matched_devices.xml"):
        window.load_xml_file("output/matched_devices.xml")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()