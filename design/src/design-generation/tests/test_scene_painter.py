# tests/test_scene_painter.py
# Отрисовка схемы.
#
# draw_scene был на 125 строк и лез в восемь переключателей окна прямо
# посреди рисования. Нарисовать схему в стороне от окна было нельзя,
# а значит и проверить: числовые проверки один раз уже пропустили
# регрессию, при которой символы устройств исчезли с чертежа полностью.
#
# Здесь рисование получает набор «что показывать» доводом, и каждый
# переключатель проверяется отдельно.
#
# Запуск из папки CONTUR:
#     python tests/test_scene_painter.py
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QGraphicsRectItem,
                               QGraphicsScene, QGraphicsTextItem)

from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.ui import scene_painter
from contur.core.data_models import Contour, DeviceMatch
from contur.ui.widgets import DeviceGraphicsItem, TextItemWithBackground

CONTOURS = [
    Contour(name="LA_TANK1", bounds=(0.0, 0.0, 100.0, 80.0),
            center=(50.0, 40.0), tech_object="LA_TANK1"),
    Contour(name="LINE_M1", bounds=(200.0, 0.0, 300.0, 80.0),
            center=(250.0, 40.0), tech_object="LINE_M1"),
]

MATCHES = [
    DeviceMatch(lua_name="LA_TANK1V1", pdf_name="V1", tech_object="LA_TANK1",
                coordinates=(20.0, 20.0), confidence=1.0, device_type="V"),
    DeviceMatch(lua_name="LA_TANK1V2", pdf_name="V2", tech_object="LA_TANK1",
                coordinates=(40.0, 20.0), confidence=0.7, device_type="V"),
    DeviceMatch(lua_name="LINE_M1LS1", pdf_name="LS1", tech_object="LINE_M1",
                coordinates=(220.0, 20.0), confidence=1.0, device_type="LS"),
]

COLORS = {"LA_TANK1": QColor("red"), "LINE_M1": QColor("green")}


def _scene() -> QGraphicsScene:
    QApplication.instance() or QApplication([])
    return QGraphicsScene()


def _count(scene, kind) -> int:
    return sum(1 for item in scene.items() if type(item) is kind)


# ---------------------------------------------------------------- контуры

def test_contours_are_drawn_with_names():
    scene = _scene()
    drawn = scene_painter.draw_contours(scene, CONTOURS, COLORS,
                                        scene_painter.ViewOptions())

    assert drawn == 2, f"нарисовано контуров: {drawn}"
    assert _count(scene, QGraphicsRectItem) == 2, "рамки контуров не нарисованы"
    assert _count(scene, QGraphicsTextItem) == 2, "имена контуров не нарисованы"


def test_contour_layer_can_be_switched_off():
    scene = _scene()
    drawn = scene_painter.draw_contours(
        scene, CONTOURS, COLORS, scene_painter.ViewOptions(contours=False))

    assert drawn == 0 and not scene.items(), "выключенный слой всё равно нарисован"


def test_contour_names_can_be_switched_off():
    scene = _scene()
    scene_painter.draw_contours(
        scene, CONTOURS, COLORS, scene_painter.ViewOptions(contour_names=False))

    assert _count(scene, QGraphicsRectItem) == 2, "рамки пропали вместе с именами"
    assert _count(scene, QGraphicsTextItem) == 0, "имена нарисованы вопреки настройке"


def test_filter_leaves_one_object():
    scene = _scene()
    drawn = scene_painter.draw_contours(
        scene, CONTOURS, COLORS, scene_painter.ViewOptions(tech_filter="LINE_M1"))

    assert drawn == 1, f"фильтр оставил контуров: {drawn}"


def test_contour_fill_uses_given_transparency():
    scene = _scene()
    scene_painter.draw_contours(scene, CONTOURS[:1], COLORS,
                                scene_painter.ViewOptions(contour_alpha=120))

    rect = next(item for item in scene.items() if type(item) is QGraphicsRectItem)
    assert rect.brush().color().alpha() == 120, \
        f"прозрачность заливки: {rect.brush().color().alpha()}"


# ---------------------------------------------------------------- устройства

def test_devices_are_drawn_with_labels():
    scene = _scene()
    drawn = scene_painter.draw_devices(scene, MATCHES,
                                       scene_painter.ViewOptions())

    assert drawn == 3, f"нарисовано устройств: {drawn}"
    assert _count(scene, DeviceGraphicsItem) == 3, "устройства без подсказок"
    assert _count(scene, TextItemWithBackground) == 3, "подписи не нарисованы"


def test_devices_disappear_only_when_asked():
    # Числовые проверки один раз уже пропустили регрессию, при которой
    # символы устройств исчезли с чертежа полностью
    scene = _scene()
    drawn = scene_painter.draw_devices(scene, MATCHES,
                                       scene_painter.ViewOptions(devices=False))

    assert drawn == 0 and not scene.items(), "выключенный слой всё равно нарисован"


def test_without_tooltips_devices_stay_selectable():
    # Настройка «показывать подсказки» решала заодно, каким объектом рисовать
    # устройство: без неё на сцену ложились простые эллипсы, и вместе
    # с подсказкой пропадали подсветка выбранного и показ устройства под
    # курсором — они ищут именно DeviceGraphicsItem
    scene = _scene()
    scene_painter.draw_devices(scene, MATCHES,
                               scene_painter.ViewOptions(tooltips=False))

    devices = [item for item in scene.items() if isinstance(item, DeviceGraphicsItem)]
    assert len(devices) == 3, "устройства перестали быть выбираемыми"
    assert all(not item.toolTip() for item in devices), \
        "подсказка показана вопреки настройке"
    assert all(item.device_data is not None for item in devices), \
        "в элементе не осталось самого устройства"


def test_tooltip_appears_when_asked():
    scene = _scene()
    scene_painter.draw_devices(scene, MATCHES,
                               scene_painter.ViewOptions())

    devices = [item for item in scene.items() if isinstance(item, DeviceGraphicsItem)]
    assert all(item.toolTip() for item in devices), "подсказки не заполнены"
    assert any("LA_TANK1V1" in item.toolTip() for item in devices), \
        "в подсказке нет имени устройства"


def test_selection_works_without_tooltips():
    # Щелчок по дереву подсвечивает устройство на схеме — это не должно
    # зависеть от настройки подсказок
    scene = _scene()
    scene_painter.draw_devices(scene, MATCHES,
                               scene_painter.ViewOptions(tooltips=False))

    device = next(item for item in scene.items()
                  if isinstance(item, DeviceGraphicsItem))
    device.set_selected(True)
    assert device.selected, "устройство не выбирается без подсказок"


def test_uncertain_detection_shows_its_confidence():
    scene = _scene()
    scene_painter.draw_devices(scene, MATCHES,
                               scene_painter.ViewOptions())

    labels = [item.toPlainText() for item in scene.items()
              if isinstance(item, TextItemWithBackground)]
    assert "V2 (0.7)" in labels, f"уверенность не показана: {labels}"
    assert "V1" in labels, f"у надёжного устройства лишняя приписка: {labels}"


def _hover(device, entering: bool):
    """Наводит и уводит курсор — настоящими событиями Qt, не флагом."""
    from PySide6.QtWidgets import QGraphicsSceneHoverEvent

    kind = (QEvent.Type.GraphicsSceneHoverEnter if entering
            else QEvent.Type.GraphicsSceneHoverLeave)
    event = QGraphicsSceneHoverEvent(kind)
    if entering:
        device.hoverEnterEvent(event)
    else:
        device.hoverLeaveEvent(event)


def test_device_draws_nothing_until_it_is_touched():
    # Постоянная обводка (а до неё закрашенный кружок) ложилась поверх
    # символа Eplan и прятала ровно то, на что человек смотрит
    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(10.0, 10.0), confidence=1.0, device_type="V")

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))

    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))
    assert device.brush().color().alpha() == 0, "устройство закрашено — символ под ним не виден"
    assert device.pen().style() == Qt.PenStyle.NoPen, "габарит устройства нарисован поверх чертежа"
    assert not device.outline_visible, "обводка показана, хотя устройство не трогали"


def test_outline_appears_under_the_cursor():
    from contur.core import config

    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(10.0, 10.0), confidence=1.0, device_type="V")

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))
    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))

    _hover(device, True)
    assert device.outline_visible, "под курсором устройство никак не отзывается"

    outline = device._outline
    assert outline.pen().color().name() == QColor(config.DEVICE_OUTLINE_COLOR).name(), \
        f"обводка не того цвета: {outline.pen().color().name()}"
    assert outline.pen().isCosmetic(), "толщина обводки поедет вместе с масштабом"
    assert outline.brush().style() == Qt.BrushStyle.NoBrush, \
        "обводка залита — символ под ней снова не виден"

    _hover(device, False)
    assert not device.outline_visible, "обводка осталась после ухода курсора"


def test_outline_appears_for_the_device_chosen_in_the_tree():
    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(10.0, 10.0), confidence=1.0, device_type="V")

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))
    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))

    device.set_selected(True)
    assert device.outline_visible, "выбранное в каталоге устройство не подсвечено"

    device.set_selected(False)
    assert not device.outline_visible, "подсветка осталась после снятия выбора"


def test_outline_repeats_the_symbol():
    # Обводка идёт по линиям символа с чертежа, а не по описанному вокруг
    # него прямоугольнику: у клапана это две сходящиеся «бабочкой» пары
    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(100.0, 100.0), confidence=1.0, device_type="V")
    match.view_size = (20.0, 20.0)
    match.view_shape = [(-10.0, -10.0, 10.0, 10.0), (-10.0, 10.0, 10.0, -10.0)]

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))
    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))

    path = device._outline.path()
    assert path.elementCount() == 4, \
        f"обводка не повторяет символ: элементов {path.elementCount()}"

    points = {(round(path.elementAt(i).x), round(path.elementAt(i).y))
              for i in range(path.elementCount())}
    assert points == {(90, 90), (110, 110), (90, 110), (110, 90)}, \
        f"линии символа встали не на своё место: {sorted(points)}"


def test_without_geometry_the_outline_falls_back_to_the_box():
    # До разметки линий символа нет — показывать под курсором было бы нечего
    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(100.0, 100.0), confidence=1.0, device_type="V")

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))
    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))

    assert not device._outline.path().isEmpty(), "обводка пустая — наводить не на что"
    assert device._outline.path().boundingRect() == device.rect(), \
        "запасная обводка не совпала с габаритом устройства"


def test_flat_symbol_does_not_collapse_the_hit_area():
    # У лежачего клапана кластер вырождается в отрезок: без нижней границы
    # площадь устройства стала бы линией, по которой не попасть курсором
    from contur.core import config

    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(10.0, 10.0), confidence=1.0, device_type="V")
    match.view_size = (40.0, 0.0)

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))

    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))
    assert device.rect().height() >= config.DEVICE_OUTLINE_FALLBACK, \
        f"площадь устройства схлопнулась: {device.rect()}"


def test_outline_is_still_clickable():
    # shape() у незакрашенного элемента сжимается до штриха пера, и попасть
    # по устройству можно было бы только точно по линии обводки
    scene = _scene()
    match = DeviceMatch(lua_name="X", pdf_name="X", tech_object="LA_TANK1",
                        coordinates=(100.0, 100.0), confidence=1.0, device_type="V")
    match.view_size = (40.0, 40.0)

    scene_painter.draw_devices(scene, [match],
                               scene_painter.ViewOptions(device_names=False))

    device = next(item for item in scene.items() if isinstance(item, DeviceGraphicsItem))
    assert device.contains(device.rect().center()), \
        "по середине устройства не попасть — выбирается только сама линия"


# ---------------------------------------------------------------- подложка

def test_background_survives_redraw():
    # scene.clear() удаляет объекты вместе с их C++ частью, и SVG после
    # каждой перерисовки перечитывался с диска — на листе A0 это полтора
    # мегабайта на каждую смену фильтра
    from contur.core import config
    from contur.ui.widgets import GraphicsView

    QApplication.instance() or QApplication([])
    svg = config.ensure_output_dir() / "_painter_test.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
                   '<line x1="10" y1="10" x2="90" y2="90" stroke="blue"/></svg>',
                   encoding="utf-8")
    try:
        view = GraphicsView()
        view.load_svg_background(str(svg))
        assert view.svg_item is not None, "подложка не загрузилась"
        was = view.svg_item

        scene_painter.preserve_background(view, str(svg))

        assert view.svg_item is not None, "подложка исчезла при перерисовке"
        assert view.svg_item is was, "подложка перечитана с диска вместо переноса"
        assert view.svg_item.scene() is view._scene, "подложка не вернулась на сцену"
    finally:
        svg.unlink(missing_ok=True)


def test_redraw_without_background_does_not_break():
    from contur.ui.widgets import GraphicsView

    QApplication.instance() or QApplication([])
    view = GraphicsView()
    assert view.svg_item is None, "подложка взялась ниоткуда"

    scene_painter.preserve_background(view, None)
    assert view.svg_item is None, "подложка появилась из ничего"


# ---------------------------------------------------------------- набор настроек

def test_options_are_taken_from_the_window():
    # Единственное место, где рисование соприкасается с виджетами
    from contur.ui import main_window

    QApplication.instance() or QApplication([])
    window = main_window.DeviceVisualizer()

    options = scene_painter.options_from_window(window)
    assert options.contours and options.devices, "слои выключены при запуске"
    assert options.tech_filter == scene_painter.ALL_OBJECTS, \
        f"фильтр при запуске: {options.tech_filter!r}"

    window.layer_devices.setChecked(False)
    window.contour_alpha.setValue(200)
    changed = scene_painter.options_from_window(window)
    assert not changed.devices, "переключатель слоя не доходит до отрисовки"
    assert changed.contour_alpha == 200, "прозрачность не доходит до отрисовки"

    # Подписи гасятся двумя разными переключателями, и любой из них
    # должен срабатывать
    window.layer_devices.setChecked(True)
    window.show_device_names.setChecked(False)
    assert not scene_painter.options_from_window(window).device_names, \
        "настройка отображения подписей не действует"
    window.show_device_names.setChecked(True)
    window.layer_device_names.setChecked(False)
    assert not scene_painter.options_from_window(window).device_names, \
        "слой подписей не действует"


if __name__ == "__main__":
    failures = 0
    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]

    for name, test in tests:
        try:
            test()
            print(f"  OK    {name}")
        except AssertionError as e:
            failures += 1
            print(f"  СБОЙ  {name}: {e or 'проверка не прошла'}")
        except Exception as e:
            failures += 1
            print(f"  СБОЙ  {name}: {type(e).__name__}: {e}")

    print(f"\nВсего: {len(tests)}, сбоев: {failures}")
    sys.exit(1 if failures else 0)
