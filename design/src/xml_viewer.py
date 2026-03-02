# visualize_matches_pyside.py
import sys
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                               QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                               QGraphicsTextItem, QGraphicsEllipseItem, QSplitter,
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QComboBox, QSpinBox, QCheckBox, QToolTip, QGraphicsItem)
from PySide6.QtCore import Qt, QRectF, QPointF, QEvent
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QTransform, QHelpEvent


@dataclass
class DeviceMatch:
    lua_name: str
    pdf_name: str
    tech_object: str
    coordinates: Tuple[float, float]
    confidence: float
    # Дополнительные поля из Lua
    descr: str = ""
    article: str = ""
    device_type: str = ""
    category: str = ""
    extra_data: Dict[str, str] = None


@dataclass
class Contour:
    name: str
    bounds: Tuple[float, float, float, float]
    center: Tuple[float, float]
    tech_object: Optional[str] = None


class DeviceGraphicsItem(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, radius: float, device_data: DeviceMatch, parent=None):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)
        self.device_data = device_data
        self.setAcceptHoverEvents(True)
        self.setToolTip(self._create_tooltip())

        # Настройки внешнего вида
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.base_color = Qt.GlobalColor.red  # временно
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

        # Добавляем дополнительные данные
        if self.device_data.extra_data:
            for key, value in self.device_data.extra_data.items():
                if value:  # Только непустые значения
                    lines.append(f"{key}: {value}")

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
        "M": QColor("#34495e"), # насосы - серый
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация сопоставленных устройств")
        self.setGeometry(100, 100, 1400, 900)

        # Данные
        self.matches: List[DeviceMatch] = []
        self.contours: List[Contour] = []
        self.tech_object_colors: Dict[str, QColor] = {}

        # Инициализация интерфейса
        self._init_ui()

    def _init_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout(central_widget)

        # Создаем сплиттер для разделения панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

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

        # Настройки отображения
        left_layout.addWidget(QLabel("Настройки отображения:"))

        # Выбор технологического объекта
        self.tech_filter = QComboBox()
        self.tech_filter.addItem("Все объекты")
        self.tech_filter.currentTextChanged.connect(self.update_display)
        left_layout.addWidget(QLabel("Фильтр по объекту:"))
        left_layout.addWidget(self.tech_filter)

        # Прозрачность контуров
        self.contour_alpha = QSpinBox()
        self.contour_alpha.setRange(0, 255)
        self.contour_alpha.setValue(50)
        self.contour_alpha.setSingleStep(10)
        self.contour_alpha.valueChanged.connect(self.update_display)
        left_layout.addWidget(QLabel("Прозрачность контуров:"))
        left_layout.addWidget(self.contour_alpha)

        # Показать имена контуров
        self.show_contour_names = QCheckBox("Показать имена контуров")
        self.show_contour_names.setChecked(True)
        self.show_contour_names.stateChanged.connect(self.update_display)
        left_layout.addWidget(self.show_contour_names)

        # Показать имена устройств
        self.show_device_names = QCheckBox("Показать имена устройств")
        self.show_device_names.setChecked(True)
        self.show_device_names.stateChanged.connect(self.update_display)
        left_layout.addWidget(self.show_device_names)

        # Показывать всплывающие подсказки
        self.show_tooltips = QCheckBox("Показывать всплывающие подсказки")
        self.show_tooltips.setChecked(True)
        self.show_tooltips.stateChanged.connect(self.update_display)
        left_layout.addWidget(self.show_tooltips)

        # Кнопка сброса масштаба
        reset_view_btn = QPushButton("Сбросить масштаб")
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

        # Добавляем левую панель в сплиттер
        splitter.addWidget(left_panel)

        # Правая панель - графика
        self.graphics_view = GraphicsView()
        splitter.addWidget(self.graphics_view)

        # Устанавливаем пропорции сплиттера (20% - левая панель, 80% - графика)
        splitter.setSizes([280, 1120])

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

                # Цвет технологического объекта (если нужен)
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

                        # 🔹 Берем device_type именно из XML
                        device_type = device.get("device_type", "")

                        # 🔹 Цвет по классу устройства
                        color = self.DEVICE_TYPE_COLORS.get(
                            device_type,
                            QColor("black")
                        )

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

                        # можно сохранить цвет прямо в объект (если нужно)
                        match.color = color

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
    def _generate_color(self, tech_name: str) -> QColor:
        # Используем простой хеш для генерации цвета
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

        # Используем хеш имени для выбора цвета
        hash_val = hash(tech_name) % len(colors)
        return colors[hash_val]

    def _update_file_info(self, file_path: str):
        import os
        filename = os.path.basename(file_path)
        self.file_info_label.setText(f"Файл: {filename}\n"
                                     f"Контуров: {len(self.contours)}\n"
                                     f"Устройств: {len(self.matches)}")

    def _update_tech_filter(self):
        self.tech_filter.clear()
        self.tech_filter.addItem("Все объекты")

        tech_objects = set(m.tech_object for m in self.matches)
        for tech_obj in sorted(tech_objects):
            self.tech_filter.addItem(tech_obj)

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

            for match in sorted(devices_by_tech[tech_obj], key=lambda x: x.pdf_name):
                device_item = QTreeWidgetItem(tech_item)
                device_item.setText(0, match.pdf_name)
                device_item.setText(1, match.device_type or match.lua_name)
                device_item.setText(2, match.article or "-")
                device_item.setText(3, f"{match.confidence:.2f}")

                # Сохраняем данные устройства для доступа при клике
                device_item.setData(0, Qt.ItemDataRole.UserRole, match)

                # Добавляем всплывающую подсказку для элемента дерева
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

        if match.extra_data:
            for key, value in match.extra_data.items():
                if value:
                    lines.append(f"{key}: {value}")

        return "<br>".join(lines)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        match = item.data(0, Qt.ItemDataRole.UserRole)
        if match:
            # Центрируем вид на устройстве
            self.center_on_point(match.coordinates)

    def center_on_point(self, point: Tuple[float, float]):
        self.graphics_view.centerOn(point[0], point[1])

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

            # Цвет по типу устройства
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