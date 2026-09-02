# widgets.py
# Виджеты и графические элементы интерфейса.
#
# Вынесены из main_window.py, где лежали вперемешку с потоками и главным окном.
# Здесь нет логики конвейера — только отображение.
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)

import os
from typing import Optional

from PySide6.QtCore import Qt, QRectF, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                               QFormLayout, QGraphicsEllipseItem, QGraphicsPathItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsTextItem, QGraphicsView, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QSpinBox,
                               QSplitter, QSplitterHandle, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from contur.core import config
from contur.core.data_models import DeviceMatch
from contur.lua.objects_loader import Operation as TechOperation, State, Step, objects_data


class DeviceGraphicsItem(QGraphicsRectItem):
    """Устройство на схеме: выбирается, подсвечивается, знает о себе всё.

    Сам прямоугольник не рисуется — он только ловит курсор и щелчок по
    габариту устройства. Видимая часть это обводка-ребёнок, повторяющая
    линии символа с чертежа, и показывается она лишь тогда, когда человек
    об этом попросил: навёл курсор или выбрал устройство в каталоге.
    Постоянная обводка (а до неё — закрашенный кружок) ложилась поверх
    символа Eplan и прятала ровно то, на что человек смотрит.

    Заливка прямоугольника прозрачная, но она есть: с `Qt.NoBrush` shape()
    сжимается до штриха пера, и попасть по устройству щелчком или навести
    на него курсор стало бы можно только точно по линии.

    with_tooltip выключает только подсказку. Раньше настройка «показывать
    подсказки» решала заодно, каким объектом рисовать устройство, и при
    выключенных подсказках на сцену ложились простые эллипсы. Вместе
    с подсказкой пропадали подсветка выбранного и показ устройства под
    курсором — они ищут именно этот класс. Связь была неочевидной:
    человек выключал подсказки, а терял выбор устройств.
    """

    def __init__(self, x: float, y: float, radius: float, device_data: DeviceMatch,
                 parent=None, with_tooltip: bool = True,
                 size: Optional[tuple] = None,
                 shape_segments: Optional[list] = None):
        width, height = size if size else (radius * 2, radius * 2)
        super().__init__(x - width / 2, y - height / 2, width, height, parent)
        self.device_data = device_data
        self.operation_state = None
        self.with_tooltip = with_tooltip
        self.setAcceptHoverEvents(True)
        self.base_color = QColor(config.DEVICE_OUTLINE_COLOR)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setZValue(3)
        self.selected = False
        self.hovered = False
        self._halo = None
        # Для ореола выбранного: половина большей стороны
        self._radius = max(width, height) / 2
        self._outline = self._build_outline(x, y, shape_segments)
        self._update_tooltip()

    @staticmethod
    def _outline_pen(color) -> QPen:
        pen = QPen(QColor(color), config.DEVICE_OUTLINE_WIDTH)
        # Толщина в пикселях экрана: на общем виде обводка иначе исчезает,
        # а на большом увеличении разрастается в полосу
        pen.setCosmetic(True)
        return pen

    def _build_outline(self, x: float, y: float,
                       segments: Optional[list]) -> QGraphicsPathItem:
        # Обводка повторяет рисунок устройства: линии его символа приходят
        # от разметки в координатах относительно центра. Своей геометрии
        # нет только до разметки — тогда обводится габарит, иначе показывать
        # под курсором было бы нечего
        path = QPainterPath()
        for x1, y1, x2, y2 in segments or ():
            path.moveTo(x + x1, y + y1)
            path.lineTo(x + x2, y + y2)

        if path.isEmpty():
            path.addRect(self.rect())

        outline = QGraphicsPathItem(path, self)
        outline.setPen(self._outline_pen(self.base_color))
        outline.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        outline.setVisible(False)
        return outline

    def _refresh_outline(self):
        # Подсветка появляется только там, где её попросили: под курсором
        # или у выбранного в каталоге устройства
        self._outline.setVisible(self.hovered or self.selected)

    @property
    def outline_visible(self) -> bool:
        return self._outline.isVisible()

    def set_selected(self, selected: bool):
        # Выбор в дереве раньше только двигал вид, и какое устройство выбрано,
        # было не понять: на чертеже сотни одинаковых кружков
        if selected == self.selected:
            return
        self.selected = selected
        self._refresh_outline()

        if selected:
            size = self._radius * 3
            self._halo = QGraphicsEllipseItem(
                self.rect().center().x() - size, self.rect().center().y() - size,
                size * 2, size * 2, self)
            pen = QPen(QColor(255, 235, 59), 3)
            pen.setCosmetic(True)  # толщина в пикселях экрана, а не сцены
            self._halo.setPen(pen)
            self._halo.setBrush(QBrush(QColor(255, 235, 59, 60)))
            self._halo.setZValue(-1)
        elif self._halo is not None:
            self._halo.setParentItem(None)
            if self._halo.scene() is not None:
                self._halo.scene().removeItem(self._halo)
            self._halo = None

    def _update_tooltip(self):
        if not self.with_tooltip:
            return

        lines = []
        lines.append(f"<b>{self.device_data.lua_name}</b>")
        lines.append(f"PDF имя: {self.device_data.pdf_name}")
        lines.append(f"Объект: {self.device_data.tech_object}")

        if hasattr(self.device_data, 'operation_status') and self.device_data.operation_status:
            status = self.device_data.operation_status
            status_text = {
                "opened": "🔓 ОТКРЫТО",
                "closed": "🔒 ЗАКРЫТО",
                "not_used": "⚪ Не используется"
            }.get(status.get("status", ""), status.get("status", ""))

            lines.append("")
            lines.append("<b>В выбранной операции:</b>")
            lines.append(f"  • Состояние: {status_text}")
            if status.get("state_name"):
                lines.append(f"  • Шаг/состояние: {status['state_name']}")
            if status.get("step_name"):
                lines.append(f"  • Детальный шаг: {status['step_name']} (№{status.get('step_number', '-')})")

        if self.device_data.descr:
            lines.append(f"Описание: {self.device_data.descr}")
        if self.device_data.article:
            lines.append(f"Артикул: {self.device_data.article}")
        if self.device_data.device_type:
            lines.append(f"Тип: {self.device_data.device_type}")

        self.setToolTip("<br>".join(lines))

    def set_operation_state(self, status: str, state_name: str = "", step_name: str = "", step_number: int = -1):
        self.operation_state = status

        if status == "opened":
            color = QColor(76, 175, 80)
        elif status == "closed":
            color = QColor(244, 67, 54)
        else:
            color = QColor(158, 158, 158)

        # Положение в операции красит обводку — ту самую, что появляется
        # под курсором и у выбранного устройства
        self.base_color = color
        self._outline.setPen(self._outline_pen(color))

        if not hasattr(self.device_data, 'operation_status'):
            self.device_data.operation_status = {}
        self.device_data.operation_status = {
            "status": status,
            "state_name": state_name,
            "step_name": step_name,
            "step_number": step_number
        }
        self._update_tooltip()

    def hoverEnterEvent(self, event):
        self.hovered = True
        self._refresh_outline()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self._refresh_outline()
        super().hoverLeaveEvent(event)


class TextItemWithBackground(QGraphicsTextItem):
    # Текстовый элемент с фоном
    # Цвет по умолчанию — один объект на все подписи; создавать его
    # в списке аргументов нельзя: он вычисляется один раз при импорте
    # и оказывается общим для всех, изменение задело бы каждую подпись
    DEFAULT_BACKGROUND = (255, 255, 255, 200)

    def __init__(self, text: str, color: QColor = Qt.GlobalColor.black,
                 bg_color: Optional[QColor] = None, device_data: DeviceMatch = None):
        super().__init__(text)
        self.device_data = device_data
        self.setDefaultTextColor(color)
        self.setFont(QFont("Arial", 8))
        self.bg_color = bg_color if bg_color is not None else QColor(*self.DEFAULT_BACKGROUND)
        if device_data:
            self.setAcceptHoverEvents(True)
            self.setToolTip(self._create_tooltip())

    def _create_tooltip(self) -> str:
        if not self.device_data:
            return ""
        lines = [f"<b>{self.device_data.lua_name}</b>"]
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
        painter.save()
        painter.setBrush(QBrush(self.bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        rect = self.boundingRect()
        rect = QRectF(rect.x() - 2, rect.y() - 1, rect.width() + 4, rect.height() + 2)
        painter.drawRect(rect)
        painter.restore()
        super().paint(painter, option, widget)


class GraphicsView(QGraphicsView):
    """Просмотр схемы: масштабирование и перемещение.

    Раньше двигаться по увеличенной схеме было нечем: колесо только меняло
    масштаб, левая кнопка тянула рамку выделения, а обработчик средней кнопки
    существовал только на отпускание — нажатие никто не ловил, поэтому
    перетаскивание не работало ни разу.

    Схему таскают как в любом редакторе: зажатой левой кнопкой по пустому
    месту, средней кнопкой или пробелом с левой. Рамку выделения левая кнопка
    больше не тянет — выделять на сцене нечего, устройства выбираются
    щелчком, — а щелчком считается нажатие без перетаскивания.

    Увеличение идёт туда, куда показывает курсор, и держит точку под ним
    прокруткой, а не переносом в матрице вида: у QGraphicsView перенос
    в матрице перебивается полосами прокрутки, и вместо «увеличить вот это»
    вид уезжал к центру. Вокруг схемы оставлено поле (`SCENE_MARGIN`), иначе
    пока лист помещается в окно, полос прокрутки нет вовсе, двигать вид
    нечем и увеличение упирается в один и тот же центр.
    """

    mouse_moved = Signal(float, float)
    zoom_changed = Signal(float)
    # Вид сместился или изменил масштаб — мини-карте пора перерисовать рамку
    view_changed = Signal()
    # Щелчок левой кнопкой по точке сцены. Что под этой точкой — решает окно:
    # вид знает про масштаб и перетаскивание, но не про устройства
    scene_clicked = Signal(float, float)

    ZOOM_STEP = 1.25
    MIN_SCALE = 0.02
    MAX_SCALE = 60.0
    # Шаг перемещения стрелками, доля видимой области
    ARROW_STEP = 0.15
    FAST_ARROW_STEP = 0.5
    # Насколько сдвинуть зажатую левую кнопку, чтобы это считалось
    # перетаскиванием, а не щелчком по устройству (пиксели экрана)
    DRAG_THRESHOLD = 4
    # Поле вокруг схемы, доля её размера: запас, за который можно утащить вид
    SCENE_MARGIN = 0.5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Перетаскивание вид ведёт сам: рамка выделения ничего не выделяла
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # Точку под курсором держим сами, прокруткой; при изменении размеров
        # окна (или ширины панелей) остаёмся на том же месте схемы
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMouseTracking(True)
        # Без фокуса вид не получает нажатия стрелок
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.svg_item = None

        self._panning = False
        self._pan_origin = None
        self._space_held = False
        # Где нажали левую кнопку: пока не сдвинули — это ещё щелчок
        self._press_at = None
        self._press_scene = None

    # ------------------------------------------------------------ масштаб

    def current_scale(self) -> float:
        return self.transform().m11()

    def zoom_by(self, factor: float, anchor=None):
        """Масштабирует вокруг точки: без anchor — вокруг центра вида.

        Точка под курсором возвращается на место прокруткой. Через
        `translate`, то есть перенос в матрице вида, не выходит: QGraphicsView
        считает перенос делом полос прокрутки и матричный попросту не
        применяет — увеличение уезжало к центру схемы вместо места, куда
        показывает курсор.
        """
        # Ограничение, чтобы схема не улетала в бесконечность
        target = self.current_scale() * factor
        if target < self.MIN_SCALE:
            factor = self.MIN_SCALE / self.current_scale()
        elif target > self.MAX_SCALE:
            factor = self.MAX_SCALE / self.current_scale()
        if abs(factor - 1.0) < 1e-9:
            return

        if anchor is None:
            anchor = self.viewport().rect().center()

        before = self.mapToScene(anchor)
        self.scale(factor, factor)
        after = self.mapToScene(anchor)
        center = self.mapToScene(self.viewport().rect().center())
        self.centerOn(center + (before - after))

        self.zoom_changed.emit(self.current_scale())
        self.view_changed.emit()

    def refresh_scene_bounds(self):
        """Поле вокруг схемы, за которое можно утащить вид.

        Без него sceneRect равен рамке содержимого: пока лист помещается
        в окно, полос прокрутки нет вовсе — вид намертво стоит по центру,
        двигать его нечем, и увеличение всегда идёт в одну и ту же точку.
        Поле считается от размера схемы, а не от размера окна: иначе
        появление полосы прокрутки меняло бы размер окна, а тот — поле.
        """
        content = self._scene.itemsBoundingRect()
        if content.isEmpty():
            self._scene.setSceneRect(QRectF())
            return

        margin_x = content.width() * self.SCENE_MARGIN
        margin_y = content.height() * self.SCENE_MARGIN
        self._scene.setSceneRect(
            content.adjusted(-margin_x, -margin_y, margin_x, margin_y))

    def wheelEvent(self, event):
        anchor = event.position().toPoint()
        self.zoom_by(self.ZOOM_STEP if event.angleDelta().y() > 0
                     else 1 / self.ZOOM_STEP, anchor)

    # --------------------------------------------------------- перемещение

    def _pan_by(self, dx: float, dy: float):
        horizontal, vertical = self.horizontalScrollBar(), self.verticalScrollBar()
        horizontal.setValue(horizontal.value() - int(dx))
        vertical.setValue(vertical.value() - int(dy))
        self.view_changed.emit()

    def _start_pan(self, position):
        self._panning = True
        self._pan_origin = position
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _stop_pan(self):
        self._panning = False
        self._pan_origin = None
        self.setCursor(Qt.CursorShape.OpenHandCursor if self._space_held
                       else Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        # Средняя кнопка (или пробел с левой) — перетаскивание сразу
        if (event.button() == Qt.MouseButton.MiddleButton
                or (self._space_held and event.button() == Qt.MouseButton.LeftButton)):
            self._start_pan(event.position())
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            # Ctrl+клик копирует координаты точки
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                QApplication.clipboard().setText(f"{scene_pos.x():.1f}, {scene_pos.y():.1f}")
                # Сообщение показывает окно: раньше вид сам писал в его подпись,
                # и первое же движение мыши стирало сообщение о копировании.
                # Спрашиваем окно, а не родителя: родитель вида — разделитель
                show = getattr(self.window(), "show_coord_message", None)
                if callable(show):
                    show(f"📋 Скопировано: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
                event.accept()
                return

            # Щелчок это или перетаскивание — решится по первому движению
            self._press_at = event.position()
            self._press_scene = scene_pos
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_origin is not None:
            delta = event.position() - self._pan_origin
            self._pan_origin = event.position()
            self._pan_by(delta.x(), delta.y())
            event.accept()
            return

        # Зажатую левую кнопку сдвинули — значит, тащат схему, а не выбирают
        if (self._press_at is not None
                and event.buttons() & Qt.MouseButton.LeftButton):
            shift = event.position() - self._press_at
            if abs(shift.x()) + abs(shift.y()) >= self.DRAG_THRESHOLD:
                self._start_pan(event.position())
                self._press_at = None
                self._press_scene = None
                self._pan_by(shift.x(), shift.y())
                event.accept()
                return

        scene_pos = self.mapToScene(event.position().toPoint())
        self.mouse_moved.emit(scene_pos.x(), scene_pos.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning and event.button() in (Qt.MouseButton.MiddleButton,
                                                Qt.MouseButton.LeftButton):
            self._stop_pan()
            event.accept()
            return

        # Отпустили, не сдвинув, — это щелчок по точке сцены
        if event.button() == Qt.MouseButton.LeftButton and self._press_at is not None:
            scene_pos = self._press_scene
            self._press_at = None
            self._press_scene = None
            if scene_pos is not None:
                self.scene_clicked.emit(scene_pos.x(), scene_pos.y())
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Двойной щелчок вписывает схему целиком
        if event.button() == Qt.MouseButton.LeftButton:
            self.fit_in_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------ клавиши

    def keyPressEvent(self, event):
        key = event.key()
        fast = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        step = (self.FAST_ARROW_STEP if fast else self.ARROW_STEP)
        dx = self.viewport().width() * step
        dy = self.viewport().height() * step

        if key == Qt.Key.Key_Left:
            self._pan_by(dx, 0)
        elif key == Qt.Key.Key_Right:
            self._pan_by(-dx, 0)
        elif key == Qt.Key.Key_Up:
            self._pan_by(0, dy)
        elif key == Qt.Key.Key_Down:
            self._pan_by(0, -dy)
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.zoom_by(self.ZOOM_STEP)
        elif key == Qt.Key.Key_Minus:
            self.zoom_by(1 / self.ZOOM_STEP)
        elif key == Qt.Key.Key_Home:
            self.fit_in_view()
        elif key == Qt.Key.Key_Space and not event.isAutoRepeat():
            # Пробел удерживается — левая кнопка временно перетаскивает
            self._space_held = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            super().keyPressEvent(event)
            return

        event.accept()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_held = False
            if not self._panning:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().keyReleaseEvent(event)

    def zoom_to_point(self, x: float, y: float, scale: float = 4.0):
        # Приблизиться к устройству, выбранному в дереве. Масштаб задаётся,
        # а не умножается: иначе двойной щелчок по второму устройству
        # уводил бы всё глубже и глубже
        target = max(self.MIN_SCALE, min(self.MAX_SCALE, scale))
        current = self.current_scale()
        if current > 0:
            self.scale(target / current, target / current)
        self.centerOn(x, y)
        self.zoom_changed.emit(self.current_scale())
        self.view_changed.emit()

    def fit_in_view(self):
        if self._scene.items():
            self.refresh_scene_bounds()
            self.fitInView(self._scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = 0
            self.zoom_changed.emit(self.current_scale())
            self.view_changed.emit()

    def clear_svg_background(self):
        # Снимает подложку. Нужно при переключении схем: иначе размеченный
        # SVG предыдущей остаётся под контурами следующей
        if self.svg_item is None:
            return
        try:
            self._scene.removeItem(self.svg_item)
        except RuntimeError:
            pass
        self.svg_item = None

    def load_svg_background(self, svg_path: str) -> bool:
        if self.svg_item is not None:
            try:
                self._scene.removeItem(self.svg_item)
                self.svg_item = None
            except RuntimeError:
                self.svg_item = None
        try:
            if not os.path.exists(svg_path):
                return False
            self.svg_item = QGraphicsSvgItem(svg_path)
            self._scene.addItem(self.svg_item)
            self.svg_item.setZValue(-1)
            return True
        except Exception as e:
            print(f"Ошибка загрузки SVG: {e}")
            self.svg_item = None
            return False


class SplitterHandle(QSplitterHandle):
    """Граница между панелями. Двойной щелчок сворачивает панель и возвращает."""

    def mouseDoubleClickEvent(self, event):
        self.splitter().toggle_pane_at(self)
        event.accept()


class Splitter(QSplitter):
    """Разделитель панелей, каким его ждут от редактора.

    Границу видно и за неё можно взяться (ширина ручки, подсветка под
    курсором — в `theme.py`), панель тянется от нуля до сколько угодно,
    а двойной щелчок по границе сворачивает её и возвращает обратно
    в прежний размер. Раньше границы были в один пиксель, панель упиралась
    в свою минимальную ширину и убрать её с глаз было нечем.

    Какую панель считать боковой, разделитель не решает за человека:
    сворачивается та из двух соседних, которой это разрешено
    (`setCollapsible`), а если обеим — меньшая.
    """

    #: Ширина, до которой разворачивается свёрнутая панель, если прежней нет
    DEFAULT_PANE = 260

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(6)
        self.setChildrenCollapsible(True)
        # Панель -> её размер до сворачивания
        self._folded = {}

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)

    def toggle_pane_at(self, handle) -> None:
        """Свернуть или развернуть панель у этой границы."""
        index = next((i for i in range(1, self.count())
                      if self.handle(i) is handle), None)
        if index is None:
            return

        sizes = self.sizes()
        candidates = [i for i in (index, index - 1) if self.isCollapsible(i)]
        if not candidates:
            return
        # Свёрнутую разворачиваем, иначе сворачиваем меньшую из соседних
        pane = next((i for i in candidates if sizes[i] == 0),
                    min(candidates, key=lambda i: sizes[i]))
        self.toggle_pane(pane)

    def toggle_pane(self, index: int) -> None:
        sizes = self.sizes()
        if not 0 <= index < len(sizes):
            return

        if sizes[index] > 0:
            self._folded[index] = sizes[index]
            room = index - 1 if index else 1
            sizes[room] += sizes[index]
            sizes[index] = 0
        else:
            restored = self._folded.get(index, self.DEFAULT_PANE)
            room = index - 1 if index else 1
            restored = min(restored, max(0, sizes[room] - self.DEFAULT_PANE // 2))
            sizes[room] -= restored
            sizes[index] = restored

        self.setSizes(sizes)


class MiniMap(QWidget):
    """Вся схема целиком с рамкой видимой области.

    На листе A0 при увеличении в четыре раза на экране помещается около
    процента чертежа, и понять, в каком его углу находишься, было нельзя.
    Щелчок по карте переносит вид в это место.
    """

    MAX_SIDE = 220

    def __init__(self, view: "GraphicsView", parent=None):
        super().__init__(parent)
        self.view = view
        self.setFixedSize(self.MAX_SIDE, self.MAX_SIDE // 2)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Мини-карта: щелчок переносит вид")
        self._scene_rect = QRectF()

    def refresh(self):
        # Границы схемы меняются при загрузке и разметке
        rect = self.view._scene.itemsBoundingRect()
        if rect.isEmpty():
            self._scene_rect = QRectF()
            self.update()
            return

        self._scene_rect = rect
        # Подгоняем пропорции под чертёж, чтобы карта не врала о форме листа
        ratio = rect.height() / rect.width() if rect.width() else 0.5
        height = max(60, min(self.MAX_SIDE, int(self.MAX_SIDE * ratio)))
        self.setFixedSize(self.MAX_SIDE, height)
        self.update()

    def _mapping(self):
        # Коэффициент перевода координат сцены в пиксели карты
        if self._scene_rect.isEmpty():
            return None
        scale = min(self.width() / self._scene_rect.width(),
                    self.height() / self._scene_rect.height())
        return scale

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(250, 250, 250))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        scale = self._mapping()
        if scale is None:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "нет схемы")
            return

        # Видимая область в координатах сцены
        visible = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        left = (visible.left() - self._scene_rect.left()) * scale
        top = (visible.top() - self._scene_rect.top()) * scale
        width = max(2.0, visible.width() * scale)
        height = max(2.0, visible.height() * scale)

        painter.setPen(QPen(QColor(33, 150, 243), 2))
        painter.setBrush(QBrush(QColor(33, 150, 243, 40)))
        painter.drawRect(QRectF(left, top, width, height))

    def mousePressEvent(self, event):
        scale = self._mapping()
        if scale is None:
            return
        point = event.position()
        self.view.centerOn(self._scene_rect.left() + point.x() / scale,
                           self._scene_rect.top() + point.y() / scale)
        self.update()


class OperationsBrowserWidget(QWidget):
    """Список операций технологических объектов.

    Только список: выбранную операцию показывает общая панель сведений
    (`details_panel.DetailsPanel`), та же, что показывает устройство.
    Своя вкладочная панель здесь была — с теми же «Параметрами»,
    «Состояниями и шагами», «Свойствами» и «Информацией», — и рядом с общей
    получались две панели об одном и том же, причём половина данных
    не показывалась ни в одной.
    """

    operation_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        QTimer.singleShot(100, self._load_operations)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

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

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self._load_operations)
        filter_layout.addWidget(self.refresh_btn)

        layout.addLayout(filter_layout)

        self.info_label = QLabel("Загрузка данных...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.operations_tree = QTreeWidget()
        self.operations_tree.setHeaderLabels(["Операции технологических объектов"])
        self.operations_tree.itemClicked.connect(self.on_operation_selected)
        layout.addWidget(self.operations_tree)

    def _load_operations(self):
        self.operations_tree.clear()
        if not objects_data.objects:
            objects_data.load()
        if not objects_data.objects:
            self.info_label.setText("❌ Нет данных о технологических объектах")
            self.info_label.setStyleSheet("color: red;")
            return

        total_operations = 0
        objects_with_ops = 0

        for tech_obj in objects_data.objects:
            if not tech_obj.operations:
                continue
            objects_with_ops += 1
            total_operations += len(tech_obj.operations)

            obj_item = QTreeWidgetItem(self.operations_tree)
            obj_item.setText(0, f"{tech_obj.name} [{len(tech_obj.operations)}]")
            obj_item.setForeground(0, QBrush(QColor(0, 100, 200)))

            for operation in sorted(tech_obj.operations, key=lambda x: x.name):
                op_item = QTreeWidgetItem(obj_item)
                op_item.setText(0, operation.name)
                op_item.setData(0, Qt.ItemDataRole.UserRole, operation)

                states = objects_data.get_states_for_operation(operation.id)
                if states:
                    for state in states[:2]:
                        state_item = QTreeWidgetItem(op_item)
                        state_item.setText(0, f"  📌 {state.name}")
                        state_item.setForeground(0, QBrush(QColor(100, 100, 100)))
                        state_item.setData(0, Qt.ItemDataRole.UserRole, state)

                        steps = objects_data.get_steps_for_state(state.id)
                        if steps:
                            for step in steps[:2]:
                                step_item = QTreeWidgetItem(state_item)
                                step_item.setText(0, f"    ▶ {step.name}")
                                step_item.setForeground(0, QBrush(QColor(150, 150, 150)))
                                step_item.setData(0, Qt.ItemDataRole.UserRole, step)

            obj_item.setExpanded(False)

        if total_operations > 0:
            self.info_label.setText(f"✅ Загружено {total_operations} операций из {objects_with_ops} объектов")
            self.info_label.setStyleSheet("color: green;")
        else:
            self.info_label.setText("⚠️ Операции не найдены")
            self.info_label.setStyleSheet("color: orange;")

        self._update_object_filter()

    def _update_object_filter(self):
        self.object_filter.clear()
        self.object_filter.addItem("Все тех. объекты")
        for tech_obj in objects_data.objects:
            if tech_obj.operations:
                self.object_filter.addItem(tech_obj.name)

    def filter_operations(self):
        tech_filter = self.object_filter.currentText()
        text_filter = self.operation_filter.text().lower()

        for i in range(self.operations_tree.topLevelItemCount()):
            obj_item = self.operations_tree.topLevelItem(i)
            obj_name = obj_item.text(0).split(" [")[0]

            if tech_filter != "Все тех. объекты" and obj_name != tech_filter:
                obj_item.setHidden(True)
                continue

            if text_filter:
                has_visible = False
                for j in range(obj_item.childCount()):
                    op_item = obj_item.child(j)
                    op_name = op_item.text(0).lower()
                    visible = text_filter in op_name
                    op_item.setHidden(not visible)
                    if visible:
                        has_visible = True
                obj_item.setHidden(not has_visible)
                if has_visible:
                    obj_item.setExpanded(True)
            else:
                obj_item.setHidden(False)
                for j in range(obj_item.childCount()):
                    obj_item.child(j).setHidden(False)
                obj_item.setExpanded(False)

    def on_operation_selected(self, item: QTreeWidgetItem, column: int):
        # Показывает выбранное общая панель сведений — по этому сигналу.
        # Щелчок по состоянию или шагу в списке считается выбором их операции:
        # состояния и шаги эта панель показывает целиком
        selected = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(selected, TechOperation):
            self.operation_selected.emit(selected)
        elif isinstance(selected, (State, Step)):
            parent_operation = objects_data.get_operation_by_id(selected.operation_id)
            if parent_operation:
                self.operation_selected.emit(parent_operation)


class PageChooser(QDialog):
    """Выбор листа многостраничного файла.

    Раньше страницу спрашивали числом: в файле на 265 листов надо было
    помнить, что именно на каком. Номера показываются сразу, названия
    из штампа дочитываются в фоне — вычитывать текст со всех страниц
    синхронно нельзя, окно замерло бы на несколько секунд.
    """

    def __init__(self, parent, pdf_path: str, total_pages: int, current: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Выбор листа")
        self.resize(460, 520)
        self.selected_page = None
        self._reader = None

        layout = QVBoxLayout(self)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по названию или номеру листа")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        self.list = QTreeWidget()
        self.list.setHeaderLabels(["Лист", "Название"])
        self.list.setRootIsDecorated(False)
        self.list.itemDoubleClicked.connect(lambda *_: self._accept_current())
        layout.addWidget(self.list)

        self.items = []
        for number in range(total_pages):
            item = QTreeWidgetItem(self.list)
            item.setText(0, str(number + 1))
            item.setText(1, "…")
            item.setData(0, Qt.ItemDataRole.UserRole, number)
            self.items.append(item)
            if number == current:
                self.list.setCurrentItem(item)

        self.status = QLabel("Читаю названия листов…")
        self.status.setStyleSheet("color: gray;")
        layout.addWidget(self.status)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        open_btn = QPushButton("Открыть")
        open_btn.setDefault(True)
        open_btn.clicked.connect(self._accept_current)
        buttons.addWidget(open_btn)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self._start_reading(pdf_path, total_pages)

    def _start_reading(self, pdf_path: str, total_pages: int):
        from contur.ui.workers import PageTitlesThread

        self._reader = PageTitlesThread(pdf_path, total_pages)
        self._reader.titles.connect(self._set_title)
        self._reader.finished_reading.connect(
            lambda: self.status.setText("Названия прочитаны"))
        self._reader.start()

    def _set_title(self, number: int, title: str):
        if 0 <= number < len(self.items):
            self.items[number].setText(1, title or "—")

    def _filter(self, text: str):
        needle = text.strip().lower()
        for item in self.items:
            item.setHidden(bool(needle) and needle not in item.text(0).lower()
                           and needle not in item.text(1).lower())

    def _accept_current(self):
        item = self.list.currentItem()
        if item is not None:
            self.selected_page = item.data(0, Qt.ItemDataRole.UserRole)
            self.accept()

    def closeEvent(self, event):
        # Чтение переживало закрытие окна и держало файл открытым
        if self._reader is not None and self._reader.isRunning():
            self._reader.requestInterruption()
            self._reader.wait(3000)
        super().closeEvent(event)

    def done(self, result):
        if self._reader is not None and self._reader.isRunning():
            self._reader.requestInterruption()
            self._reader.wait(3000)
        super().done(result)


class PostgresDialog(QDialog):
    """Параметры подключения к базе — одним окном.

    Раньше экспорт спрашивал хост, базу, пользователя и пароль четырьмя
    модальными окнами подряд: ошибся в первом — проходи все заново. Порт
    был зашит числом 5432 и задать другой было нельзя.
    """

    def __init__(self, parent=None, settings: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Экспорт в PostgreSQL")
        self.setMinimumWidth(360)

        defaults = dict(config.DB_CONFIG)
        defaults.update(settings or {})

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.host = QLineEdit(str(defaults.get("host", "localhost")))
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(int(defaults.get("port", 5432)))
        self.database = QLineEdit(str(defaults.get("database", "hmi_design")))
        self.user = QLineEdit(str(defaults.get("user", "postgres")))
        self.password = QLineEdit(str(defaults.get("password", "")))
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        # Что делать с тем, что уже лежит в базе.
        #
        # Контуры и устройства обновляются по имени и повтора не боятся,
        # а связи и точки сопряжения ложатся вторым комплектом: колонки
        # листа в схеме нет, и отличить одну выгрузку от другой база
        # не может. Догадаться за пользователя нельзя — спрашиваем.
        self.mode_choice = QComboBox()
        self.mode_choice.addItem("Дописать к имеющемуся", "append")
        self.mode_choice.addItem("Заменить связи и точки сопряжения", "replace")

        form.addRow("Хост:", self.host)
        form.addRow("Порт:", self.port)
        form.addRow("База данных:", self.database)
        form.addRow("Пользователь:", self.user)
        form.addRow("Пароль:", self.password)
        form.addRow("Повторная выгрузка:", self.mode_choice)
        layout.addLayout(form)

        self.mode_hint = QLabel()
        self.mode_hint.setWordWrap(True)
        self.mode_hint.setStyleSheet("color: gray;")
        self.mode_choice.currentIndexChanged.connect(self._update_mode_hint)
        self._update_mode_hint()
        layout.addWidget(self.mode_hint)

        self.check_result = QLabel("")
        self.check_result.setWordWrap(True)
        layout.addWidget(self.check_result)

        buttons = QHBoxLayout()
        check_btn = QPushButton("Проверить подключение")
        check_btn.clicked.connect(self._check_connection)
        buttons.addWidget(check_btn)
        buttons.addStretch(1)

        ok_btn = QPushButton("Выгрузить")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def db_config(self) -> dict:
        return {
            "host": self.host.text().strip() or "localhost",
            "port": self.port.value(),
            "database": self.database.text().strip() or "hmi_design",
            "user": self.user.text().strip() or "postgres",
            "password": self.password.text(),
        }

    def saveable(self) -> dict:
        # Пароль не сохраняем: класть его в реестр Windows открытым текстом
        # нельзя, а шифровать здесь нечем
        settings = self.db_config()
        settings.pop("password", None)
        return settings

    def mode(self) -> str:
        return self.mode_choice.currentData()

    def _update_mode_hint(self):
        if self.mode() == "replace":
            self.mode_hint.setText(
                "Прежние связи и точки сопряжения будут удалены целиком — "
                "включая пришедшие с других листов. Контуры и устройства "
                "обновятся по имени.")
        else:
            self.mode_hint.setText(
                "Связи и точки сопряжения добавятся к имеющимся. Если этот "
                "лист уже выгружали, в базе окажется два комплекта.")

    def _check_connection(self):
        # Проверка до выгрузки: раньше ошибку в пароле показывал только
        # сам экспорт, уже после разбора всей схемы
        self.check_result.setText("Проверяю...")
        QApplication.processEvents()
        try:
            import psycopg2
            connection = psycopg2.connect(connect_timeout=5, **self.db_config())
            try:
                self.check_result.setText("✅ Подключение есть. " + self._existing(connection))
            finally:
                connection.close()
            self.check_result.setStyleSheet("color: green;")
        except ImportError:
            self.check_result.setText("❌ Не установлен psycopg2")
            self.check_result.setStyleSheet("color: red;")
        except Exception as e:
            self.check_result.setText(f"❌ {e}")
            self.check_result.setStyleSheet("color: red;")

    @staticmethod
    def _existing(connection) -> str:
        # Выбор «дописать или заменить» имеет смысл, только когда видно,
        # что уже лежит в базе
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM connections")
                connections = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM junction_points")
                junctions = cursor.fetchone()[0]
        except Exception:
            # Таблиц ещё нет — это нормально при первой выгрузке
            return "Таблицы будут созданы."

        if not connections and not junctions:
            return "База пуста."
        return f"Уже есть: связей {connections}, точек сопряжения {junctions}."


class SettingsDialog(QDialog):
    # Диалоговое окно настроек отображения
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки отображения")
        self.setWindowFlags(Qt.WindowType.Window)
        self.setMinimumWidth(300)

        self.main_window = parent
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Прозрачность контуров:"))
        self.contour_alpha = QSpinBox()
        self.contour_alpha.setRange(0, 255)
        self.contour_alpha.setSingleStep(10)
        self.contour_alpha.valueChanged.connect(self._on_contour_alpha_changed)
        layout.addWidget(self.contour_alpha)

        layout.addSpacing(10)

        self.show_contour_names = QCheckBox("Показать имена контуров")
        self.show_contour_names.stateChanged.connect(self._on_show_contour_names_changed)
        layout.addWidget(self.show_contour_names)

        self.show_device_names = QCheckBox("Показать имена устройств")
        self.show_device_names.stateChanged.connect(self._on_show_device_names_changed)
        layout.addWidget(self.show_device_names)

        self.show_tooltips = QCheckBox("Показывать всплывающие подсказки")
        self.show_tooltips.stateChanged.connect(self._on_show_tooltips_changed)
        layout.addWidget(self.show_tooltips)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._apply_settings)
        btn_layout.addWidget(apply_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _load_settings(self):
        self.contour_alpha.setValue(self.main_window.contour_alpha.value())
        self.show_contour_names.setChecked(self.main_window.show_contour_names.isChecked())
        self.show_device_names.setChecked(self.main_window.show_device_names.isChecked())
        self.show_tooltips.setChecked(self.main_window.show_tooltips.isChecked())

    def _apply_settings(self):
        self._on_contour_alpha_changed(self.contour_alpha.value())
        self._on_show_contour_names_changed(self.show_contour_names.checkState())
        self._on_show_device_names_changed(self.show_device_names.checkState())
        self._on_show_tooltips_changed(self.show_tooltips.checkState())

    def _on_contour_alpha_changed(self, value):
        self.main_window.contour_alpha.setValue(value)
        self.main_window.update_display()

    def _on_show_contour_names_changed(self, state):
        is_checked = (state == Qt.CheckState.Checked)
        self.main_window.show_contour_names.setChecked(is_checked)
        self.main_window.update_display()

    def _on_show_device_names_changed(self, state):
        is_checked = (state == Qt.CheckState.Checked)
        self.main_window.show_device_names.setChecked(is_checked)
        self.main_window.update_display()

    def _on_show_tooltips_changed(self, state):
        is_checked = (state == Qt.CheckState.Checked)
        self.main_window.show_tooltips.setChecked(is_checked)
        self.main_window.update_display()

    def showEvent(self, event):
        self._load_settings()
        super().showEvent(event)
