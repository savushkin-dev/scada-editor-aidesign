# tests/test_navigation.py
# Перемещение и масштабирование в окне просмотра схемы.
#
# Раньше двигаться по увеличенной схеме было нечем: колесо меняло масштаб,
# левая кнопка тянула рамку выделения, а обработчик средней кнопки был
# только на отпускание — нажатие никто не ловил, и перетаскивание
# не работало ни разу.
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QGraphicsRectItem


def _view():
    from widgets import GraphicsView
    QApplication.instance() or QApplication([])

    view = GraphicsView()
    view.resize(400, 300)
    # Сцена крупнее окна, иначе двигаться некуда
    view._scene.addItem(QGraphicsRectItem(0, 0, 4000, 3000))
    view.show()
    view.zoom_by(4.0)
    return view


def _mouse(view, kind, button, pos=(200.0, 150.0)):
    event = QMouseEvent(kind, QPointF(*pos), view.mapToGlobal(QPoint(*map(int, pos))),
                        button, button, Qt.KeyboardModifier.NoModifier)
    if kind == QEvent.Type.MouseButtonPress:
        view.mousePressEvent(event)
    elif kind == QEvent.Type.MouseMove:
        view.mouseMoveEvent(event)
    else:
        view.mouseReleaseEvent(event)
    return event


def _key(view, key, modifiers=Qt.KeyboardModifier.NoModifier, release=False):
    kind = QEvent.Type.KeyRelease if release else QEvent.Type.KeyPress
    event = QKeyEvent(kind, key, modifiers)
    (view.keyReleaseEvent if release else view.keyPressEvent)(event)
    return event


def test_middle_button_drag_pans():
    view = _view()
    before = (view.horizontalScrollBar().value(), view.verticalScrollBar().value())

    _mouse(view, QEvent.Type.MouseButtonPress, Qt.MouseButton.MiddleButton, (200.0, 150.0))
    assert view._panning, "нажатие средней кнопки не включило перетаскивание"
    _mouse(view, QEvent.Type.MouseMove, Qt.MouseButton.MiddleButton, (120.0, 90.0))
    after = (view.horizontalScrollBar().value(), view.verticalScrollBar().value())

    assert after != before, "схема не сдвинулась при перетаскивании"

    _mouse(view, QEvent.Type.MouseButtonRelease, Qt.MouseButton.MiddleButton, (120.0, 90.0))
    assert not view._panning, "перетаскивание не завершилось"


def test_space_with_left_button_pans():
    view = _view()
    _key(view, Qt.Key.Key_Space)
    assert view._space_held

    before = view.horizontalScrollBar().value()
    _mouse(view, QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, (200.0, 150.0))
    _mouse(view, QEvent.Type.MouseMove, Qt.MouseButton.LeftButton, (100.0, 150.0))
    assert view.horizontalScrollBar().value() != before

    _mouse(view, QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, (100.0, 150.0))
    _key(view, Qt.Key.Key_Space, release=True)
    assert not view._space_held


def test_arrows_pan_and_shift_moves_further():
    view = _view()

    start = view.horizontalScrollBar().value()
    _key(view, Qt.Key.Key_Right)
    normal = abs(view.horizontalScrollBar().value() - start)
    assert normal > 0, "стрелка не сдвинула вид"

    view.horizontalScrollBar().setValue(start)
    _key(view, Qt.Key.Key_Right, Qt.KeyboardModifier.ShiftModifier)
    fast = abs(view.horizontalScrollBar().value() - start)
    assert fast > normal, "Shift не увеличил шаг"


def test_vertical_arrows_pan():
    view = _view()
    start = view.verticalScrollBar().value()
    _key(view, Qt.Key.Key_Down)
    assert view.verticalScrollBar().value() != start


def test_zoom_is_limited():
    view = _view()

    for _ in range(60):
        view.zoom_by(view.ZOOM_STEP)
    assert view.current_scale() <= view.MAX_SCALE + 1e-6, "масштаб ушёл выше предела"

    for _ in range(200):
        view.zoom_by(1 / view.ZOOM_STEP)
    assert view.current_scale() >= view.MIN_SCALE - 1e-6, "масштаб ушёл ниже предела"


def test_zoom_keys():
    view = _view()
    before = view.current_scale()
    _key(view, Qt.Key.Key_Plus)
    assert view.current_scale() > before
    _key(view, Qt.Key.Key_Minus)
    assert abs(view.current_scale() - before) < 1e-6


def test_zoom_signal_reports_scale():
    view = _view()
    seen = []
    view.zoom_changed.connect(seen.append)
    view.zoom_by(2.0)
    assert seen and abs(seen[-1] - view.current_scale()) < 1e-9


def test_home_fits_view():
    view = _view()
    view.zoom_by(8.0)
    zoomed = view.current_scale()
    _key(view, Qt.Key.Key_Home)
    assert view.current_scale() != zoomed, "Home не вписал схему"


def test_view_takes_focus_for_arrows():
    # Без фокуса вид не получает нажатия стрелок
    view = _view()
    assert view.focusPolicy() != Qt.FocusPolicy.NoFocus


# --------------------------------------------- увеличение туда, куда смотрю

def test_zoom_holds_the_point_under_the_cursor():
    # Увеличение уезжало к центру схемы: точку под курсором возвращали
    # переносом в матрице вида, а QGraphicsView считает перенос делом полос
    # прокрутки и матричный не применяет вовсе
    view = _view()
    anchor = QPoint(60, 40)
    before = view.mapToScene(anchor)

    view.zoom_by(2.0, anchor)

    after = view.mapToScene(anchor)
    drift = view.mapFromScene(after) - view.mapFromScene(before)
    assert abs(drift.x()) <= 2 and abs(drift.y()) <= 2, \
        f"точка под курсором уехала на ({drift.x()}, {drift.y()}) px"


def test_zoom_without_anchor_holds_the_centre():
    view = _view()
    before = view.mapToScene(view.viewport().rect().center())

    view.zoom_by(2.0)

    after = view.mapToScene(view.viewport().rect().center())
    assert abs(after.x() - before.x()) < 2 and abs(after.y() - before.y()) < 2, \
        "увеличение с клавиатуры увело вид с места"


def test_wheel_zooms_at_the_cursor():
    # Тот же путь, но целиком: колесо -> zoom_by
    from PySide6.QtGui import QWheelEvent

    view = _view()
    anchor = QPoint(320, 240)
    before = view.mapToScene(anchor)
    view.wheelEvent(QWheelEvent(QPointF(anchor), view.mapToGlobal(anchor), QPoint(0, 0),
                                QPoint(0, 120), Qt.MouseButton.NoButton,
                                Qt.KeyboardModifier.NoModifier,
                                Qt.ScrollPhase.NoScrollPhase, False))

    after = view.mapToScene(anchor)
    drift = view.mapFromScene(after) - view.mapFromScene(before)
    assert abs(drift.x()) <= 2 and abs(drift.y()) <= 2, \
        f"колесо увеличивает не туда: снос ({drift.x()}, {drift.y()}) px"


# ------------------------------------------------- поле вокруг схемы и тяга

def test_view_can_be_dragged_even_when_everything_fits():
    # Пока лист помещался в окно, sceneRect был равен рамке содержимого:
    # полос прокрутки нет, вид намертво стоит по центру, двигать нечем
    from widgets import GraphicsView
    QApplication.instance() or QApplication([])

    view = GraphicsView()
    view.resize(800, 600)
    view._scene.addItem(QGraphicsRectItem(0, 0, 400, 300))
    view.show()
    view.fit_in_view()

    horizontal = view.horizontalScrollBar()
    assert horizontal.maximum() > horizontal.minimum(), \
        "вписанную схему невозможно сдвинуть: прокручивать нечего"


def test_scene_margin_grows_with_the_drawing():
    from widgets import GraphicsView
    QApplication.instance() or QApplication([])

    view = GraphicsView()
    view._scene.addItem(QGraphicsRectItem(0, 0, 1000, 500))
    view.refresh_scene_bounds()

    rect = view._scene.sceneRect()
    assert rect.width() > 1000 and rect.height() > 500, "поля вокруг схемы нет"
    assert abs(rect.center().x() - 500) < 1 and abs(rect.center().y() - 250) < 1, \
        "поле легло не вокруг схемы"


def test_left_drag_pans_the_view():
    # Левая кнопка тянула рамку выделения, хотя выделять на сцене нечего
    view = _view()
    before = (view.horizontalScrollBar().value(), view.verticalScrollBar().value())

    _mouse(view, QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, (200.0, 150.0))
    _mouse(view, QEvent.Type.MouseMove, Qt.MouseButton.LeftButton, (120.0, 90.0))
    after = (view.horizontalScrollBar().value(), view.verticalScrollBar().value())
    _mouse(view, QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, (120.0, 90.0))

    assert view._panning is False, "перетаскивание не закончилось на отпускании"
    assert after != before, "схема не поехала за левой кнопкой"


def test_click_without_drag_is_a_click():
    view = _view()
    clicks = []
    view.scene_clicked.connect(lambda x, y: clicks.append((x, y)))

    _mouse(view, QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, (200.0, 150.0))
    _mouse(view, QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, (200.0, 150.0))

    assert len(clicks) == 1, f"щелчок по сцене не дошёл: {clicks}"


def test_drag_is_not_a_click():
    # Иначе каждое перетаскивание открывало бы устройство под пальцем
    view = _view()
    clicks = []
    view.scene_clicked.connect(lambda x, y: clicks.append((x, y)))

    _mouse(view, QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, (200.0, 150.0))
    _mouse(view, QEvent.Type.MouseMove, Qt.MouseButton.LeftButton, (140.0, 110.0))
    _mouse(view, QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, (140.0, 110.0))

    assert not clicks, "перетаскивание сработало как щелчок"


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
