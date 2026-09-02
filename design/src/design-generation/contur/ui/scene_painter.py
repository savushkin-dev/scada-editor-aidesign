# scene_painter.py
# Отрисовка схемы на сцене.
#
# draw_scene был на 125 строк и лез в восемь переключателей окна прямо
# посреди рисования: layer_contours, layer_device_names, show_tooltips,
# contour_alpha и прочие. Из-за этого нарисовать схему в стороне от окна
# было нельзя, а значит и проверить тоже.
#
# Здесь рисование знает не про виджеты, а про набор «что показывать»:
# окно собирает его один раз за отрисовку. Сцена, данные и настройки
# приходят доводами, состояние вида (масштаб, положение, подсветка
# выбранного) остаётся заботой окна.
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (QGraphicsRectItem,
                               QGraphicsScene, QGraphicsTextItem)

from contur.core import config
from contur.core.data_models import Contour, DeviceMatch
from contur.ui.widgets import DeviceGraphicsItem, TextItemWithBackground

# Значение фильтра, при котором показывают всё
ALL_OBJECTS = "Все объекты"

# Как называть устройства, у которых техобъекта нет вовсе. В проекте MCA1
# так названа общая обвязка станции мойки: имя устройства в Lua — просто
# `V1` или `LT2`, без объекта впереди. Пустая строка в списках выглядела бы
# как пустая строка, поэтому у неё есть подпись
NO_OBJECT = "Без объекта"


def object_title(tech_object: str) -> str:
    """Имя техобъекта для показа человеку."""
    return tech_object or NO_OBJECT

# Запасной полуразмер устройства и отступ подписи от него, пункты.
# Обводка идёт по габариту символа, а это остаётся для тех, у кого
# своей геометрии ещё нет
DEVICE_RADIUS = 5
LABEL_OFFSET = (8, -10)


@dataclass(frozen=True)
class ViewOptions:
    """Что показывать. Снимается с переключателей окна один раз за отрисовку."""

    background: bool = True
    contours: bool = True
    contour_names: bool = True
    devices: bool = True
    device_names: bool = True
    tooltips: bool = True
    contour_alpha: int = 50
    tech_filter: str = ALL_OBJECTS

    def shows(self, tech_object: str) -> bool:
        return self.tech_filter == ALL_OBJECTS or tech_object == self.tech_filter


def options_from_window(window) -> ViewOptions:
    # Единственное место, где рисование соприкасается с виджетами.
    # «Без объекта» в списке — это пустой техобъект у устройства
    tech_filter = window.tech_filter.currentText()
    if tech_filter == NO_OBJECT:
        tech_filter = ""

    return ViewOptions(
        background=window.layer_background.isChecked(),
        contours=window.layer_contours.isChecked(),
        contour_names=(window.show_contour_names.isChecked()
                       and window.layer_contour_names.isChecked()),
        devices=window.layer_devices.isChecked(),
        device_names=(window.show_device_names.isChecked()
                      and window.layer_device_names.isChecked()),
        tooltips=window.show_tooltips.isChecked(),
        contour_alpha=window.contour_alpha.value(),
        tech_filter=tech_filter,
    )


def preserve_background(view, svg_path: Optional[str]) -> None:
    """Переносит подложку через очистку сцены.

    scene.clear() удаляет объекты вместе с их C++ частью, и SVG после
    каждой перерисовки приходилось перечитывать с диска — на листе A0
    это полтора мегабайта. Поэтому подложку вынимают до очистки
    и возвращают после; если C++ часть всё же исчезла, читаем заново.
    """
    scene = view._scene
    svg_item = view.svg_item

    if svg_item is not None:
        try:
            scene.removeItem(svg_item)
        except RuntimeError:
            svg_item = None

    scene.clear()

    if svg_item is None:
        return

    try:
        scene.addItem(svg_item)
        view.svg_item = svg_item
    except RuntimeError:
        if svg_path and os.path.exists(svg_path):
            view.load_svg_background(svg_path)
        else:
            view.svg_item = None


def draw_contours(scene: QGraphicsScene, contours: List[Contour],
                  colors: Dict[str, QColor], options: ViewOptions) -> int:
    """Рисует рамки техобъектов. Возвращает число нарисованных."""
    if not options.contours:
        return 0

    drawn = 0
    for contour in contours:
        if not options.shows(contour.tech_object):
            continue

        minx, miny, maxx, maxy = contour.bounds
        color = colors.get(contour.tech_object, Qt.GlobalColor.blue)

        rect_item = QGraphicsRectItem(minx, miny, maxx - minx, maxy - miny)
        pen = QPen(color)
        pen.setWidth(2)
        rect_item.setPen(pen)

        fill = QColor(color)
        fill.setAlpha(options.contour_alpha)
        rect_item.setBrush(QBrush(fill))
        rect_item.setZValue(0)
        scene.addItem(rect_item)
        drawn += 1

        if options.contour_names and contour.name:
            text_item = QGraphicsTextItem(contour.name)
            text_item.setDefaultTextColor(color)
            text_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            text_item.setPos(contour.center[0] - 30, contour.center[1] - 15)
            text_item.setZValue(2)
            scene.addItem(text_item)

    return drawn


def _outline_size(match: DeviceMatch) -> tuple:
    """Площадь, которой устройство ловит курсор и щелчок.

    view_size приходит от разметки — это габарит кластера красных линий,
    то есть самого символа Eplan. До разметки его нет, и берётся запасной
    размер: иначе навести курсор на устройство было бы негде.

    Габарит ограничен снизу: у некоторых символов кластер вырождается
    в отрезок (нулевая высота у лежачего клапана), и площадь схлопнулась
    бы в линию, по которой не попасть курсором.
    """
    fallback = config.DEVICE_OUTLINE_FALLBACK
    width, height = getattr(match, "view_size", None) or (fallback, fallback)
    return max(float(width), fallback), max(float(height), fallback)


def draw_devices(scene: QGraphicsScene, matches: List[DeviceMatch],
                 options: ViewOptions) -> int:
    """Рисует устройства и их подписи. Возвращает число нарисованных.

    Устройство ничего не рисует поверх чертежа, пока его не тронули:
    обводка по линиям его символа появляется под курсором и у выбранного
    в каталоге (config.DEVICE_OUTLINE_COLOR). Палитру по типам метод
    поэтому не принимает — типы разобраны в легенде окна и в цветах выгрузки.
    """
    if not options.devices:
        return 0

    drawn = 0
    for match in matches:
        if not options.shows(match.tech_object):
            continue

        x, y = match.coordinates

        # Устройство всегда рисуется своим классом, даже без подсказки:
        # по нему работают подсветка выбранного и показ устройства под
        # курсором. Раньше при выключенных подсказках на сцену ложились
        # простые эллипсы, и вместе с подсказкой пропадал выбор устройств
        device_item = DeviceGraphicsItem(x, y, DEVICE_RADIUS, match,
                                         with_tooltip=options.tooltips,
                                         size=_outline_size(match),
                                         shape_segments=getattr(match, "view_shape", None))
        scene.addItem(device_item)
        drawn += 1

        if options.device_names:
            text = match.pdf_name
            if match.confidence < 1.0:
                text += f" ({match.confidence:.1f})"

            text_item = TextItemWithBackground(
                text, Qt.GlobalColor.black, QColor(255, 255, 255, 200),
                match if options.tooltips else None)
            text_item.setPos(x + LABEL_OFFSET[0], y + LABEL_OFFSET[1])
            text_item.setZValue(2)
            scene.addItem(text_item)

    return drawn
