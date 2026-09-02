# tests/test_ui_state.py
# Состояние окна: что переживает перерисовку и что доходит до пользователя.
#
# Перерисовка сцены заканчивалась вызовом reset_view(), поэтому смена фильтра,
# настройки отображения или выбор операции выбрасывали пользователя обратно
# к общему виду — увеличенный участок приходилось искать заново.
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from contur.ui import app_settings
from contur.core import config
from contur.core.data_models import Contour, DeviceMatch

# Настройки пользователя проверки трогать не должны: уводим хранилище
# в отдельное имя до создания первого окна — окно читает их в конструкторе
app_settings.APPLICATION = "ViewerTests"


def _window():
    from PySide6.QtWidgets import QApplication
    from contur.ui import main_window
    QApplication.instance() or QApplication([])
    window = main_window.DeviceVisualizer()
    window.resize(800, 600)
    window.show()
    return window


def _fill(window, devices: int = 4):
    window.contours = [Contour(name="LA_TANK1", bounds=(0, 0, 2000, 1500),
                               center=(1000, 750), tech_object="LA_TANK1")]
    window.matches = [DeviceMatch(lua_name=f"LA_TANK1V{i}", pdf_name=f"V{i}",
                                  tech_object="LA_TANK1",
                                  coordinates=(100.0 * i + 50, 200.0),
                                  confidence=0.9, device_type="V")
                      for i in range(devices)]
    window._update_tech_filter()
    window._update_device_tree()
    # Намеренно без fit=True: подготовка должна работать и на прежнем коде,
    # иначе проверки падали бы на подписи метода, а не на поведении
    window.draw_scene()
    window.graphics_view.fit_in_view()
    return window


def test_redraw_keeps_zoom():
    window = _fill(_window())
    view = window.graphics_view

    view.zoom_by(6.0)
    zoomed = view.current_scale()

    window.draw_scene()
    assert abs(view.current_scale() - zoomed) < 1e-6, \
        f"масштаб сбросился: было {zoomed:.3f}, стало {view.current_scale():.3f}"


def test_redraw_keeps_position():
    window = _fill(_window())
    view = window.graphics_view

    view.zoom_by(6.0)
    view.centerOn(350.0, 200.0)
    before = view.mapToScene(view.viewport().rect().center())

    window.draw_scene()
    after = view.mapToScene(view.viewport().rect().center())

    # Допуск в пикселях экрана, а не в пунктах листа. Центр возвращают полосы
    # прокрутки, а их значение целое: остаётся пиксель округления, и в пунктах
    # он тем крупнее, чем мельче масштаб. Порог в пунктах поэтому зависел бы
    # от ширины окна — а смещение всё то же, в один пиксель
    drift = view.mapFromScene(after) - view.mapFromScene(before)
    assert abs(drift.x()) <= 2 and abs(drift.y()) <= 2, \
        f"вид уехал на ({drift.x()}, {drift.y()}) px: " \
        f"было ({before.x():.1f}, {before.y():.1f}), " \
        f"стало ({after.x():.1f}, {after.y():.1f})"


def test_filter_change_keeps_zoom():
    # Смена фильтра идёт через update_display — самый частый путь перерисовки
    window = _fill(_window())
    view = window.graphics_view

    view.zoom_by(5.0)
    zoomed = view.current_scale()
    window.update_display()

    assert abs(view.current_scale() - zoomed) < 1e-6, "фильтр сбросил масштаб"


def test_fit_still_works_for_new_content():
    # Новая схема должна вписываться целиком, иначе после переключения
    # окажешься в случайном углу чужого чертежа
    window = _fill(_window())
    view = window.graphics_view

    view.zoom_by(8.0)
    window.draw_scene(fit=True)

    assert view.current_scale() < 8.0, "схема не вписалась при новом содержимом"


def test_coordinates_reach_the_label():
    # Метод считал проценты и искал устройство под курсором, но ничего
    # не выводил — в теле не было ни одного setText, и подпись навсегда
    # оставалась «Координаты: --, --»
    window = _fill(_window())
    window.update_mouse_coordinates(1000.0, 750.0)

    text = window.coord_label.text()
    assert "--" not in text, f"координаты не дошли до подписи: {text!r}"
    assert "50" in text, f"половина холста должна давать 50%: {text!r}"


def test_coordinates_are_clamped():
    # Точка за пределами холста не должна давать 137%
    window = _fill(_window())
    window.update_mouse_coordinates(999999.0, 999999.0)
    assert "100.0%" in window.coord_label.text()


def test_device_under_cursor_is_named():
    window = _fill(_window())
    device = window.matches[1]
    window.update_mouse_coordinates(*device.coordinates)

    text = window.coord_label.text()
    assert device.lua_name in text, f"устройство под курсором не показано: {text!r}"


# ---------------------------------------------------------- панель сведений

def _operation():
    # Описание объектов — общее на процесс, поэтому проверка загружает своё
    from contur.lua.objects_loader import objects_data
    objects_data.load_from_json({
        "tech_objects": [{"id": "1", "n": 1, "name": "Танк",
                          "name_eplan": "LA_TANK1", "name_BC": "TANK1",
                          "operations": [{"id": "оп1", "name": "Мойка",
                                          "base_operation": "wash"}]}],
        "states": [{"state_id": "с1", "operation_id": "оп1",
                    "operation_name": "Мойка", "obj_id": "1", "obj_name": "Танк",
                    "state_data": {"name": "Наполнение",
                                   "opened_devices": ["LA_TANK1V1"]}}],
    })
    return objects_data.get_operation_by_id("оп1")


def _selected_on_scene(window):
    from contur.ui.widgets import DeviceGraphicsItem
    return [item.device_data for item in window.graphics_view._scene.items()
            if isinstance(item, DeviceGraphicsItem) and item.selected]


def test_click_on_device_opens_its_details():
    # Щелчок по устройству — единственный способ добраться до его данных,
    # не разыскивая устройство в каталоге
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    window = _fill(_window())
    device = window.matches[1]
    view = window.graphics_view
    point = view.mapFromScene(*device.coordinates)

    # Щелчок это нажатие и отпускание на месте: сдвинутая кнопка тащит схему
    view.mousePressEvent(QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(point), view.mapToGlobal(point),
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier))
    view.mouseReleaseEvent(QMouseEvent(
        QEvent.Type.MouseButtonRelease, QPointF(point), view.mapToGlobal(point),
        Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier))

    assert window.details_panel.device is device, "панель не открылась по щелчку"
    assert window.selected_match is device, "устройство не подсвечено на схеме"


def test_dragging_the_scheme_does_not_select():
    # Тащить схему левой кнопкой и выбирать ею устройства — разные жесты:
    # иначе каждое перетаскивание открывало бы устройство под пальцем
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    window = _fill(_window())
    device = window.matches[1]
    view = window.graphics_view
    point = view.mapFromScene(*device.coordinates)
    away = QPointF(point.x() - 60, point.y() - 40)

    view.mousePressEvent(QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(point), view.mapToGlobal(point),
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier))
    view.mouseMoveEvent(QMouseEvent(
        QEvent.Type.MouseMove, away, view.mapToGlobal(away.toPoint()),
        Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier))
    view.mouseReleaseEvent(QMouseEvent(
        QEvent.Type.MouseButtonRelease, away, view.mapToGlobal(away.toPoint()),
        Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier))

    assert window.details_panel.device is None, "перетаскивание выбрало устройство"


def test_ctrl_click_copies_and_does_not_select():
    # Ctrl+клик копирует координаты точки — выбирать при этом нечего
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    window = _fill(_window())
    device = window.matches[1]
    view = window.graphics_view
    point = view.mapFromScene(*device.coordinates)

    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(point),
                        view.mapToGlobal(point), Qt.MouseButton.LeftButton,
                        Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ControlModifier)
    view.mousePressEvent(event)

    assert window.details_panel.device is None, "Ctrl+клик открыл панель"


def test_click_past_devices_keeps_the_panel():
    # Промах не должен сбрасывать выбор: первый щелчок двойного, которым
    # схему вписывают в окно, попадает как раз мимо устройств
    window = _fill(_window())
    window.select_device(window.matches[0])
    window.on_scene_clicked(1500.0, 1200.0)

    assert window.details_panel.device is window.matches[0], "промах сбросил панель"


def test_next_device_replaces_the_previous():
    # Ради этого панель и заполняется заново: без сброса данные двух
    # устройств легли бы друг на друга
    window = _fill(_window())
    window.on_scene_clicked(*window.matches[0].coordinates)
    window.on_scene_clicked(*window.matches[2].coordinates)

    assert window.details_panel.device is window.matches[2], "панель осталась на первом"
    assert _selected_on_scene(window) == [window.matches[2]], \
        "на схеме подсвечены оба устройства сразу"


def test_reset_clears_panel_and_highlight():
    window = _fill(_window())
    window.select_device(window.matches[1])
    window.clear_selection()

    assert window.details_panel.device is None, "панель не очистилась"
    assert window.selected_match is None, "выбранное устройство осталось"
    assert not _selected_on_scene(window), "подсветка на схеме осталась"


def test_reset_button_of_the_panel_reaches_the_window():
    window = _fill(_window())
    window.select_device(window.matches[1])
    window.details_panel.clear_btn.click()

    assert window.selected_match is None, "кнопка панели не сняла подсветку"
    assert not _selected_on_scene(window), "подсветка на схеме осталась"


def test_selection_survives_redraw():
    window = _fill(_window())
    window.select_device(window.matches[1])
    window.draw_scene()

    assert window.details_panel.device is window.matches[1], "перерисовка закрыла панель"
    assert _selected_on_scene(window) == [window.matches[1]], \
        "перерисовка потеряла подсветку"


def test_new_catalog_closes_the_panel():
    # Устройство осталось бы от прошлого листа: на схеме его больше нет,
    # а карточка показывала бы его данные
    window = _fill(_window())
    window.select_device(window.matches[1])

    window.matches = [DeviceMatch(lua_name="LINE_M1V9", pdf_name="V9",
                                  tech_object="LINE_M1", coordinates=(700.0, 300.0),
                                  confidence=1.0, device_type="V")]
    window.draw_scene()

    assert window.details_panel.device is None, "панель от прошлого каталога осталась"
    assert window.selected_match is None, "подсветка от прошлого каталога осталась"


def test_tree_click_opens_the_same_panel():
    window = _fill(_window())
    group = window.device_tree.topLevelItem(0)
    item = group.child(0)
    window.on_tree_item_clicked(item, 0)

    from PySide6.QtCore import Qt as QtCore
    match = item.data(0, QtCore.ItemDataRole.UserRole)
    assert window.details_panel.device is match, "выбор в каталоге не открыл панель"


def test_scene_click_marks_device_in_the_tree():
    # Иначе после щелчка по чертежу в каталоге подсвечено предыдущее
    window = _fill(_window())
    device = window.matches[2]
    window.on_scene_clicked(*device.coordinates)

    from PySide6.QtCore import Qt as QtCore
    current = window.device_tree.currentItem()
    assert current is not None, "в каталоге ничего не выбрано"
    assert current.data(0, QtCore.ItemDataRole.UserRole) is device, \
        "в каталоге выбрано не то устройство"


def test_panes_can_be_hidden_and_returned():
    # Убрать панель с глаз было нечем: она занимала своё место всегда
    window = _window()
    for name, item in (("panel", window.act_show_panel),
                       ("details", window.act_show_details),
                       ("operations", window.act_show_operations)):
        widget = window.panes[name][2]
        assert widget.isVisible(), f"панель {name} не видна с самого начала"

        item.setChecked(False)
        assert not widget.isVisible(), f"панель {name} не спряталась"

        item.setChecked(True)
        assert widget.isVisible(), f"панель {name} не вернулась"


def test_hidden_panes_are_remembered():
    # Иначе каждый запуск возвращал бы то, что человек только что убрал
    window = _window()
    try:
        window.act_show_details.setChecked(False)
        window._save_settings()

        again = _window()
        assert not again.act_show_details.isChecked(), "панель вернулась после запуска"
        assert not again.panes["details"][2].isVisible(), "спрятанная панель показана"
    finally:
        window.act_show_details.setChecked(True)
        window._save_settings()


def test_side_pane_folds_by_its_border():
    # Двойной щелчок по границе сворачивает панель и возвращает её
    # в прежний размер — как в редакторах
    window = _window()
    splitter = window.main_splitter
    before = splitter.sizes()

    splitter.toggle_pane_at(splitter.handle(1))
    folded = splitter.sizes()
    assert folded[0] == 0, f"панель не свернулась: {folded}"
    assert folded[1] > before[1], "освободившееся место не досталось схеме"

    splitter.toggle_pane_at(splitter.handle(1))
    assert splitter.sizes() == before, \
        f"панель вернулась не в свой размер: {splitter.sizes()} вместо {before}"


def test_pane_folded_to_nothing_comes_back_on_start():
    # Так пропала панель сведений: границу утащили до края, ноль уехал
    # в настройки (`scene = [1596, 0]`), и следующий запуск открывался
    # без панели — место, где она была, ничем не отмечено, и выглядит это
    # так, будто панель убрали из программы совсем
    window = _window()
    window.scene_splitter.setSizes([window.scene_splitter.sizes()[0]
                                    + window.scene_splitter.sizes()[1], 0])
    assert window.scene_splitter.sizes()[1] == 0, "подготовка не схлопнула панель"

    window._unfold_lost_panes()

    assert window.scene_splitter.sizes()[1] > 0, "схлопнутая панель не вернулась"
    assert window.details_panel.isVisibleTo(window), "панель осталась невидимой"


def test_deliberately_hidden_pane_is_not_unfolded():
    # Спрятанное осознанно — Ctrl+B, Ctrl+I, Ctrl+J — возвращать не надо:
    # это помнится отдельным признаком, и галочку в меню видно
    window = _window()
    window.act_show_details.setChecked(False)
    window.scene_splitter.setSizes([window.scene_splitter.sizes()[0], 0])

    window._unfold_lost_panes()

    assert not window.details_panel.isVisibleTo(window), \
        "спрятанная панель вернулась сама"


def test_scheme_pane_cannot_be_folded():
    # Убрать с глаз можно всё, кроме самой схемы
    window = _window()
    assert not window.scene_splitter.isCollapsible(0), "схему можно свернуть вбок"
    assert not window.right_splitter.isCollapsible(0), "схему можно свернуть вниз"
    assert not window.main_splitter.isCollapsible(1), "схему можно свернуть влево"


def test_left_panel_can_be_widened():
    # Раньше ширина панели была зажата между 240 и 420 пикселями: длинные
    # имена устройств прочитать было нельзя, как ни тяни
    window = _window()
    window.resize(1600, 900)
    QApplication.processEvents()
    window.main_splitter.setSizes([700, 900])
    QApplication.processEvents()

    assert window.main_splitter.sizes()[0] > window.PANEL_MAX_WIDTH, \
        f"панель не растягивается шире стартовой: {window.main_splitter.sizes()}"

    # И сжимается заметно уже стартовой ширины
    window.main_splitter.setSizes([window.PANEL_FOLD_WIDTH, 1400])
    QApplication.processEvents()
    assert window.main_splitter.sizes()[0] < window.PANEL_MIN_WIDTH, \
        f"панель не сжимается: {window.main_splitter.sizes()}"


def test_panel_is_the_only_one():
    # Панелей с вкладками «Параметры / Состояния и шаги / Свойства /
    # Информация» было две: своя у браузера операций и общая справа.
    # Половина данных не показывалась ни в одной, а искать приходилось
    # в обеих
    from contur.ui.details_panel import DetailsPanel

    window = _window()
    panels = window.findChildren(DetailsPanel)
    assert len(panels) == 1, f"панелей сведений в окне: {len(panels)}"
    assert panels[0] is window.details_panel, "панель окна — не та, что на виду"
    assert not hasattr(window.operations_browser, "operation_details"),         "у браузера операций осталась своя панель вкладок"


def test_operation_goes_to_the_same_panel():
    # Операция показывается там же, где устройство: панель одна
    window = _fill(_window())
    operation = _operation()
    window.on_operation_selected_for_devices(operation)

    assert window.details_panel.operation is operation, "операция не дошла до панели"
    assert window.details_panel.device is None, "в панели разом устройство и операция"


def test_operation_replaces_device_in_the_panel():
    # Наложиться данные устройства и операции не должны так же, как данные
    # двух устройств
    window = _fill(_window())
    window.select_device(window.matches[1])
    window.on_operation_selected_for_devices(_operation())

    assert window.details_panel.device is None, "устройство осталось в панели"
    assert "Мойка" in window.details_panel.title_label.text(),         "заголовок остался от устройства"


def test_operation_keeps_device_highlighted():
    # Выбор операции красит устройства по их положению в ней — снимать
    # с устройства подсветку он не должен
    window = _fill(_window())
    device = window.matches[1]
    window.select_device(device)
    window.on_operation_selected_for_devices(_operation())

    assert window.selected_match is device, "выбор устройства слетел от операции"
    assert _selected_on_scene(window) == [device], "подсветка на схеме слетела"


def test_device_returns_to_the_panel_after_operation():
    window = _fill(_window())
    window.on_operation_selected_for_devices(_operation())
    window.select_device(window.matches[0])

    assert window.details_panel.operation is None, "операция осталась в панели"
    assert window.details_panel.device is window.matches[0], "устройство не показано"


def test_copy_message_survives_mouse_move():
    # Ctrl+клик показывает сообщение о копировании на полторы секунды.
    # Раньше вид сам писал в подпись окна, и первое же движение мыши
    # затирало сообщение — прочитать его не успевали
    window = _fill(_window())
    window.show_coord_message("📋 Скопировано: (10.0, 20.0)")

    window.update_mouse_coordinates(500.0, 400.0)
    assert "Скопировано" in window.coord_label.text(), "сообщение затёрлось"

    window._clear_coord_message()
    window.update_mouse_coordinates(500.0, 400.0)
    assert "Скопировано" not in window.coord_label.text(), \
        "координаты не вернулись после сообщения"


def test_coordinate_label_survives_ctrl_click():
    # Подпись — виджет, а не строка: раньше Ctrl+клик подменял её через
    # setattr, и координаты переставали обновляться до перезапуска
    from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    window = _fill(_window())
    view = window.graphics_view
    position = QPointF(100.0, 80.0)
    event = QMouseEvent(QEvent.Type.MouseButtonPress, position,
                        view.mapToGlobal(QPoint(100, 80)),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.ControlModifier)
    view.mousePressEvent(event)

    assert hasattr(window.coord_label, "setText"), "подпись подменили строкой"


def test_detection_stops_when_asked():
    # Детекция занимает почти всё время разметки. Прерывания не было вовсе:
    # начатую разметку оставалось только пересидеть или закрыть приложение
    import numpy as np
    from contur.pdf.pdf_processor import DeviceDetector

    detector = DeviceDetector("модели-нет.pt", tile_size=64, step=64)
    detector.model = _FakeModel()

    image = np.full((256, 256, 3), 200, dtype=np.uint8)
    path = Path(__file__).resolve().parent.parent / "output" / "_stop_test.png"
    path.parent.mkdir(parents=True, exist_ok=True)

    import cv2
    cv2.imwrite(str(path), image)
    try:
        seen = []
        detector.detect_devices(str(path),
                                on_progress=lambda done, total: seen.append(done),
                                should_stop=lambda: True)
        assert detector.model.calls == 0, "модель считала после запроса остановки"

        detector.model.calls = 0
        detector.detect_devices(str(path),
                                on_progress=lambda done, total: seen.append(done),
                                should_stop=lambda: False)
        assert detector.model.calls > 0, "без запроса остановки детекция не пошла"
        assert seen, "прогресс не сообщался"
    finally:
        path.unlink(missing_ok=True)


class _FakeModel:
    # Заглушка вместо YOLO: проверяем управление циклом, а не распознавание
    names = {0: "valve"}

    def __init__(self):
        self.calls = 0

    def predict(self, batch, **kwargs):
        self.calls += 1
        return [_FakeResult() for _ in batch]


class _FakeResult:
    boxes = None


def test_cancelled_markup_leaves_cache_alone():
    # Недосчитанная разметка не должна попасть в кэш: иначе лист навсегда
    # остался бы пустым, а причину было бы не найти
    import inspect
    from contur.ui.workers import YOLOMarkingThread

    source = inspect.getsource(YOLOMarkingThread.run)
    store_at = source.find("markup_cache.store")
    guard_at = source.find("isInterruptionRequested")
    assert guard_at != -1, "поток не проверяет запрос остановки"
    assert guard_at < store_at, "запись в кэш идёт раньше проверки остановки"


def test_window_can_cancel_markup():
    window = _window()
    assert hasattr(window, "cancel_markup"), "нет отмены разметки"
    assert not window.cancel_btn.isVisible(), "кнопка отмены видна без обработки"

    window._remember_idle_state()
    window._set_busy(True, cancellable=True)
    assert window.cancel_btn.isVisible(), "кнопка отмены не появилась"
    assert not window.load_pdf_btn.isEnabled(), \
        "во время обработки можно загрузить другой файл"

    window._set_busy(False)
    assert not window.cancel_btn.isVisible()


def test_busy_restores_only_what_was_enabled():
    # Кнопка экспорта в базу неактивна, пока нет разметки. Возврат из
    # обработки не должен включать её просто так
    window = _window()
    window.export_pg_btn.setEnabled(False)
    window.load_pdf_btn.setEnabled(True)

    window._remember_idle_state()
    window._set_busy(True, cancellable=True)
    window._set_busy(False)

    assert window.load_pdf_btn.isEnabled(), "кнопка загрузки не вернулась"
    assert not window.export_pg_btn.isEnabled(), \
        "экспорт в базу включился сам, хотя разметки нет"


def test_shortcuts_need_a_modifier():
    # Горячими клавишами были одиночные буквы: нажатие «S» открывало диалог
    # выбора файла, «P» — другой. С такими клавишами поле поиска в окне
    # завести нельзя — каждая буква запускала бы действие
    window = _window()
    loose = []
    for act in window.findChildren(type(window.act_load_pdf)):
        for shortcut in act.shortcuts():
            text = shortcut.toString()
            # F и Esc безобидны: вписать схему и прервать обработку
            if len(text) == 1 and text not in ("F",):
                loose.append(f"{act.text()} → {text}")

    assert not loose, f"действия на одиночных клавишах: {loose}"


def test_menu_and_buttons_agree():
    # Пункт меню не должен разрешать то, что кнопка уже запрещает
    window = _window()
    pairs = ((window.markup_pdf_btn, window.act_markup),
             (window.report_btn, window.act_report),
             (window.export_pg_btn, window.act_export_pg))

    for button, act in pairs:
        assert button.isEnabled() == act.isEnabled(), \
            f"«{act.text()}»: кнопка {button.isEnabled()}, меню {act.isEnabled()}"

    window._allow_markup(True)
    window._allow_report(True)
    window._allow_postgres(True)
    for button, act in pairs:
        assert button.isEnabled() and act.isEnabled(), f"«{act.text()}» не включилось"


def test_window_fits_small_screen():
    # Размер был зашит как 1800x1000 — на ноутбуке 1366x768 нижние кнопки
    # оказывались за краем экрана
    from PySide6.QtGui import QGuiApplication

    window = _window()
    screen = QGuiApplication.primaryScreen().availableGeometry()
    from contur.ui import main_window
    fresh = main_window.DeviceVisualizer()

    assert fresh.width() <= screen.width() and fresh.height() <= screen.height(), \
        f"окно {fresh.width()}x{fresh.height()} больше экрана " \
        f"{screen.width()}x{screen.height()}"


def test_cached_markup_is_offered_without_asking():
    # Размеченный ранее лист достаётся из кэша за доли секунды — ждать
    # нажатия кнопки незачем. Новый лист по-прежнему ждёт: занимать машину
    # на полторы минуты без спроса нельзя
    from contur.pdf import markup_cache

    window = _window()
    window.current_pdf_path = "C:/схемы/нет-такого.pdf"
    window.current_page = 0

    started = []
    window.markup_pdf_with_yolo = lambda: started.append(True)

    original = markup_cache.lookup
    try:
        markup_cache.lookup = lambda key: None
        window._markup_if_cached()
        assert not started, "разметка запустилась, хотя в кэше пусто"

        markup_cache.lookup = lambda key: "есть.svg"
        window._markup_if_cached()
        assert started, "готовая разметка не показалась"
        assert not window._markup_started_by_user, \
            "разметка из кэша будет сопровождаться окном «Успех»"
    finally:
        markup_cache.lookup = original


def test_postgres_asks_once():
    # Раньше хост, база, пользователь и пароль спрашивались четырьмя окнами
    # подряд: ошибся в первом — проходи все заново. Порт был зашит числом
    from contur.ui.widgets import PostgresDialog

    window = _window()
    dialog = PostgresDialog(window)
    settings = dialog.db_config()

    assert set(settings) == {"host", "port", "database", "user", "password"}
    assert settings["port"] == 5432, "порт не подставился из настроек"

    dialog.port.setValue(5433)
    assert dialog.db_config()["port"] == 5433, "порт нельзя задать"


def test_files_of_different_projects_are_explained():
    # Настоящий случай: загружен чертёж молокохранилища и Lua другого
    # проекта. Приложение находило 55 устройств, сопоставляло ноль
    # и отчитывалось зелёной галочкой «✅ Сопоставлено устройств: 0» —
    # разобраться можно было только по журналу
    window = _window()
    window.contours = [
        Contour(name=name, bounds=(0.0, 0.0, 100.0, 100.0),
                center=(50.0, 50.0), tech_object=name)
        for name in ("TANK1", "TANK2", "CW_TANK1")
    ]
    window._last_match_context = (
        {"devices": [{"name": "BRINE_TANK1V1"}, {"name": "COAG1V11"},
                     {"name": "BUNKER1LS2"}]},
        [], [])

    explanation = window._explain_no_matches()

    assert "разных проектов" in explanation, f"причина не названа: {explanation!r}"
    assert "TANK1" in explanation and "BRINE_TANK1" in explanation, \
        f"не показано, что именно не совпало: {explanation!r}"


def test_matching_failure_is_not_reported_as_success():
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    window = _fill(_window(), devices=2)
    window._last_match_context = ({"devices": [{"name": "BRINE_TANK1V1"}]}, [], [])

    shown = {}
    with mock.patch.object(QMessageBox, "warning",
                           side_effect=lambda *a: shown.setdefault("warning", a[2])), \
         mock.patch.object(QMessageBox, "information",
                           side_effect=lambda *a: shown.setdefault("information", a[2])):
        window._on_matching_finished(True, [])

    assert "warning" in shown, "ноль сопоставлений показан как успех"
    assert "information" not in shown, "показано окно успеха при нуле сопоставлений"
    assert "✅" not in window.status_label.text(), \
        f"зелёная галочка при нуле: {window.status_label.text()!r}"


def test_missing_lua_is_named_as_the_cause():
    window = _window()
    window.contours = [Contour(name="TANK1", bounds=(0.0, 0.0, 10.0, 10.0),
                               center=(5.0, 5.0), tech_object="TANK1")]
    window._last_match_context = None

    explanation = window._explain_no_matches()
    assert "Lua" in explanation and "Ctrl+O" in explanation, \
        f"не сказано, что делать: {explanation!r}"


def test_broken_pdf_does_not_become_current():
    # current_pdf_path присваивался до проверки файла: после отказа окно
    # считало чертёж загруженным, и «Разметить схему» шла по битому пути
    import shutil
    import tempfile
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    window = _window()
    window.current_pdf_path = "прежний.pdf"

    folder = Path(tempfile.mkdtemp(prefix="contur_broken_"))
    try:
        broken = {
            "пустой": b"",
            "не_pdf": "это просто текст, а не чертёж".encode(),
            "обрезанный": b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type",
        }
        for name, content in broken.items():
            path = folder / f"{name}.pdf"
            path.write_bytes(content)

            shown = []
            with mock.patch.object(QMessageBox, "critical",
                                   side_effect=lambda *a: shown.append(a[2])), \
                 mock.patch.object(QMessageBox, "warning", return_value=None):
                window._open_pdf(str(path))

            assert shown, f"{name}: отказ прошёл молча"
            assert window.current_pdf_path == "прежний.pdf", \
                f"{name}: битый файл стал текущим чертежом"
            assert "Traceback" not in shown[0] and "Error" not in shown[0], \
                f"{name}: пользователю показана внутренняя ошибка: {shown[0]!r}"
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_scan_is_refused_with_an_explanation():
    # Скан открывается без ошибки и даёт ноль сегментов: конвейер молча
    # доходил до пустой схемы, и понять почему было нельзя
    import shutil
    import tempfile

    import fitz

    from contur.core import errors
    from contur.ui.workers import GeometryExtractionThread

    folder = Path(tempfile.mkdtemp(prefix="contur_scan_"))
    try:
        scan = folder / "скан.pdf"
        document = fitz.open()
        document.new_page(width=595, height=842).insert_text((72, 72), "Скан")
        document.save(str(scan))
        document.close()

        seen = []
        thread = GeometryExtractionThread(str(scan), 0)
        thread.error.connect(seen.append)
        thread.finished.connect(lambda *_: seen.append("УСПЕХ"))
        thread.run()

        assert seen, "ни ошибки, ни успеха"
        assert seen[0] == errors.NO_VECTOR_GRAPHICS, \
            f"скан не объяснён: {seen[0]!r}"
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def test_cache_can_be_cleared_from_the_window():
    # markup_cache.clear() был написан и не вызывался ниоткуда. Кэш держит
    # по 470 КБ на лист, и после переобучения модели его нужно сбросить
    # целиком — предела в 300 МБ для этого мало
    import shutil
    import tempfile
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    from contur.pdf import markup_cache

    window = _window()
    was_dir, was_disabled = markup_cache.CACHE_DIR, markup_cache.DISABLED
    markup_cache.CACHE_DIR = Path(tempfile.mkdtemp(prefix="contur_cache_ui_"))
    markup_cache.DISABLED = False
    try:
        source = markup_cache.CACHE_DIR / "источник.svg"
        source.write_text("x" * 2048, encoding="utf-8")
        markup_cache.store("к1", str(source))
        source.unlink()

        # Отказ от очистки не должен ничего удалять
        with mock.patch.object(QMessageBox, "question",
                               return_value=QMessageBox.StandardButton.No), \
             mock.patch.object(QMessageBox, "information", return_value=None):
            window.clear_markup_cache()
        assert markup_cache.lookup("к1"), "кэш очищен вопреки отказу"

        with mock.patch.object(QMessageBox, "question",
                               return_value=QMessageBox.StandardButton.Yes), \
             mock.patch.object(QMessageBox, "information", return_value=None):
            window.clear_markup_cache()
        assert markup_cache.lookup("к1") is None, "кэш не очистился"

        assert window.act_clear_cache is not None, "очистки нет в меню"
    finally:
        shutil.rmtree(markup_cache.CACHE_DIR, ignore_errors=True)
        markup_cache.CACHE_DIR, markup_cache.DISABLED = was_dir, was_disabled


def test_left_panel_has_everything_window_relies_on():
    # Сборка панели вынесена в ui_panel из 256 строк подряд. Виджеты
    # остаются полями окна: их гасят на время работы, обновляют и читают
    # из обработчиков. Пропажа любого вылезла бы не здесь, а на экране.
    window = _window()

    expected = (
        # загрузка и обработка
        "load_lua_btn", "load_objects_btn", "load_pdf_btn", "markup_pdf_btn",
        "report_btn", "export_pg_btn",
        # схемы и листы
        "scheme_selector", "close_scheme_btn",
        "prev_page_btn", "next_page_btn", "page_list_btn", "page_label",
        # ход работы
        "detection_profile", "progress_bar", "cancel_btn",
        "status_label", "file_info_label",
        # что показывать
        "tech_filter", "legend_label", "mini_map",
        "layer_background", "layer_contours", "layer_contour_names",
        "layer_devices", "layer_device_names",
        # устройства
        "device_search", "device_tree", "search_result_label",
    )

    missing = [name for name in expected if getattr(window, name, None) is None]
    assert not missing, f"панель не создала: {missing}"

    # Состояния, с которыми панель обязана появляться: гасить кнопки
    # обработки до загрузки данных, прятать полосу прогресса
    assert not window.markup_pdf_btn.isEnabled(), "разметка доступна без чертежа"
    assert not window.report_btn.isEnabled(), "отчёт доступен без данных"
    assert not window.export_pg_btn.isEnabled(), "выгрузка доступна без данных"
    assert not window.scheme_selector.isEnabled(), "выбор схемы доступен без схем"
    assert not window.progress_bar.isVisible(), "полоса прогресса видна в покое"
    assert not window.cancel_btn.isVisible(), "кнопка отмены видна в покое"

    assert all(getattr(window, name).isChecked()
               for name in ("layer_background", "layer_contours", "layer_devices")), \
        "слои выключены при запуске"

    # Кнопки, которые панель гасит только скопом
    for name in ("prev_page_btn", "next_page_btn", "page_list_btn"):
        assert not getattr(window, name).isEnabled(), \
            f"{name} доступна до загрузки многостраничного файла"


def test_window_loads_back_what_it_exported():
    # Разбор XML вынесен в xml_io и проверяется там без окна. Здесь
    # проверяется связка: окно должно разложить прочитанное по своим полям,
    # назначить цвета и перестроить дерево.
    import shutil
    import tempfile
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    window = _fill(_window(), devices=3)
    exported = Path(tempfile.mkdtemp(prefix="contur_xml_")) / "выгрузка.xml"

    # Файл пишется здесь, а не экспортом: проверяется чтение, и лишняя
    # зависимость от выгрузки сделала бы причину сбоя неоднозначной.
    # Формат — как у настоящей выгрузки, координаты в процентах
    devices = "\n".join(
        f'<Device device_type="{m.device_type}" lua_name="{m.lua_name}" '
        f'pdf_name="{m.pdf_name}" x="{m.coordinates[0] / 2000 * 100:.3f}%" '
        f'y="{m.coordinates[1] / 1500 * 100:.3f}%" confidence="0.90"/>'
        for m in window.matches)
    exported.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<PlantGeometry version="1.3" coordinate-type="percent" '
        'canvas-width="2000" canvas-height="1500">\n'
        '  <TechnologicalObjects>\n'
        '    <TechnologicalObject name="LA_TANK1">\n'
        '      <Contour name="LA_TANK1" bounds="0%,0%,100%,100%" center="50%,50%"/>\n'
        f'      <Devices>{devices}</Devices>\n'
        '    </TechnologicalObject>\n'
        '  </TechnologicalObjects>\n'
        '</PlantGeometry>\n', encoding="utf-8")

    try:
        was_devices = [m.lua_name for m in window.matches]
        was_contours = ["LA_TANK1"]

        window.matches.clear()
        window.contours.clear()
        window.tech_object_colors.clear()

        with mock.patch.object(QMessageBox, "information", return_value=None), \
             mock.patch.object(QMessageBox, "warning", return_value=None), \
             mock.patch.object(QMessageBox, "critical", return_value=None):
            window.load_xml_file(str(exported))

        assert [m.lua_name for m in window.matches] == was_devices, \
            f"после обратного чтения устройства другие: " \
            f"{[m.lua_name for m in window.matches]}"
        assert [c.name for c in window.contours] == was_contours, \
            "контуры не вернулись"
        assert window.tech_object_colors, "цвета техобъектов не назначены"
        # Цвет устройству больше не раздаётся: на схеме оно обводится
        # по габариту своего символа, а не красится кружком по типу
        assert window.device_tree.topLevelItemCount() > 0, "дерево не перестроено"
    finally:
        shutil.rmtree(exported.parent, ignore_errors=True)


def test_device_tree_shows_state_in_operation():
    # Вид с состояниями в операции был отдельным методом-двойником:
    # 16 значимых строк из 24 дословно совпадали с обычным деревом,
    # и не покрывался он ничем
    from contur.lua.objects_loader import objects_data

    window = _fill(_window(), devices=3)

    class _Operation:
        id = "op1"
        name = "Мойка"

    was_devices = objects_data.get_devices_for_operation
    was_details = objects_data.get_device_details_in_operation
    objects_data.get_devices_for_operation = lambda _: {"LA_TANK1V0": "opened",
                                                        "LA_TANK1V1": "closed"}
    objects_data.get_device_details_in_operation = lambda _, name: {
        "state_name": "Открыт", "step_name": "Подача", "step_number": 2}
    try:
        window._update_device_tree(_Operation())

        assert window.device_tree.topLevelItemCount() == 1, "техобъект не один"
        tech_item = window.device_tree.topLevelItem(0)
        assert tech_item.text(1) == "🔓1 🔒1 ⚪1", \
            f"счётчик состояний: {tech_item.text(1)!r}"

        by_name = {tech_item.child(i).text(0): tech_item.child(i)
                   for i in range(tech_item.childCount())}
        assert "🔓 V0" in by_name, f"нет открытого устройства: {list(by_name)}"
        assert "🔒 V1" in by_name, f"нет закрытого устройства: {list(by_name)}"
        assert "⚪ V2" in by_name, f"нет неиспользуемого: {list(by_name)}"

        tooltip = by_name["🔓 V0"].toolTip(0)
        for expected in ("Мойка", "ОТКРЫТО", "Открыт", "Подача"):
            assert expected in tooltip, f"в подсказке нет {expected!r}: {tooltip!r}"

        # Устройство лежит в элементе дерева и после переключения вида:
        # по нему работают подсветка и переход к устройству на схеме
        from PySide6.QtCore import Qt
        assert by_name["🔓 V0"].data(0, Qt.ItemDataRole.UserRole) is not None, \
            "в элементе дерева не осталось самого устройства"
    finally:
        objects_data.get_devices_for_operation = was_devices
        objects_data.get_device_details_in_operation = was_details


def test_operation_view_keeps_the_search():
    # Обычное дерево применяло введённый поиск заново, вид с операцией —
    # нет, и переключение на операцию показывало снова все устройства
    from contur.lua.objects_loader import objects_data

    window = _fill(_window(), devices=3)
    window.device_search.setText("V1")

    class _Operation:
        id = "op1"
        name = "Мойка"

    was_devices = objects_data.get_devices_for_operation
    objects_data.get_devices_for_operation = lambda _: {"LA_TANK1V1": "closed"}
    try:
        window._update_device_tree(_Operation())

        tech_item = window.device_tree.topLevelItem(0)
        visible = [tech_item.child(i).text(0) for i in range(tech_item.childCount())
                   if not tech_item.child(i).isHidden()]
        assert visible == ["🔒 V1"], f"поиск не применился: {visible}"
    finally:
        objects_data.get_devices_for_operation = was_devices


def test_parsing_writes_where_config_says():
    # Разбор Lua писал "output/parsed_lua.json" относительной строкой, то есть
    # в текущую папку. Собранное приложение запускают ярлыком откуда угодно,
    # и результат уезжал туда, где его потом никто не искал.
    import shutil
    import tempfile

    from contur.ui.workers import LuaParsingThread

    lua = config.INPUT_DIR / "test" / "main.io.lua"
    if not lua.exists():
        print(f"  ПРОПУСК test_parsing_writes_where_config_says: нет {lua}")
        return

    elsewhere = Path(tempfile.mkdtemp(prefix="contur_cwd_"))
    output = Path(tempfile.mkdtemp(prefix="contur_out_"))
    was_cwd = os.getcwd()
    was_path = config.PARSED_LUA_JSON
    config.PARSED_LUA_JSON = output / "parsed_lua.json"
    try:
        os.chdir(elsewhere)
        LuaParsingThread([str(lua)]).run()

        assert config.PARSED_LUA_JSON.exists(), \
            "разбор не попал туда, куда указывает config"
        assert not (elsewhere / "output").exists(), \
            "разбор создал папку output в текущем каталоге вместо своей"
    finally:
        os.chdir(was_cwd)
        config.PARSED_LUA_JSON = was_path
        shutil.rmtree(elsewhere, ignore_errors=True)
        shutil.rmtree(output, ignore_errors=True)


def test_no_relative_paths_left_in_live_code():
    # Сторож от возврата: девять таких строк уже нашлись разом,
    # и найти их можно было только перебором
    root = Path(__file__).resolve().parent.parent
    live = ("workers.py", "main_window.py", "device_matcher.py", "pdf_processor.py",
            "objects_loader.py", "widgets.py")

    offenders = {}
    for name in live:
        source = (root / name).read_text(encoding="utf-8")
        found = [line.strip() for line in source.splitlines()
                 if '"output/' in line or "'output/" in line]
        if found:
            offenders[name] = found

    assert not offenders, \
        f"пути в обход config: {offenders}"


class _FakeThread:
    """Поток, который отвечает на просьбу остановиться — или не отвечает."""

    def __init__(self, stops: bool = True):
        self.stops = stops
        self.running = True
        self.interrupted = False
        self.waited_ms = None

    def isRunning(self):
        return self.running

    def requestInterruption(self):
        self.interrupted = True

    def wait(self, milliseconds=0):
        self.waited_ms = milliseconds
        if self.stops:
            self.running = False
        return self.stops


def _fill_threads(window, stops=True):
    threads = {}
    for attribute, _ in window.BACKGROUND_THREADS:
        thread = _FakeThread(stops)
        setattr(window, attribute, thread)
        threads[attribute] = thread
    return threads


def test_close_waits_for_every_thread():
    # Дожидались только разметку. Остальные пять уничтожались на ходу:
    # Qt отвечает «QThread: Destroyed while thread is still running»,
    # а выгрузка в базу обрывалась посреди записи.
    from PySide6.QtGui import QCloseEvent

    window = _window()
    threads = _fill_threads(window)
    assert len(threads) == 6, f"фоновых потоков описано {len(threads)}, а их шесть"

    window.closeEvent(QCloseEvent())

    forgotten = [name for name, thread in threads.items() if not thread.interrupted]
    assert not forgotten, f"остановки не дождались: {forgotten}"

    still_running = [name for name, thread in threads.items() if thread.isRunning()]
    assert not still_running, f"потоки остались работать: {still_running}"


def test_close_waiting_is_bounded():
    # Ожидание идёт в потоке окна: пока оно длится, окно не отвечает.
    # Срок общий на все потоки, а не на каждый, иначе шесть сроков подряд
    # означали бы полминуты замершего окна вместо пяти секунд.
    #
    # Мерить надо настоящее время закрытия: у мгновенной заглушки время
    # не идёт, и сумма запрошенных сроков ничего не показывает.
    import time

    from PySide6.QtGui import QCloseEvent

    class _SlowThread(_FakeThread):
        def wait(self, milliseconds=0):
            self.waited_ms = milliseconds
            time.sleep(min(milliseconds, 200) / 1000)
            self.running = False
            return True

    window = _window()
    window.THREAD_WAIT_MS = 300
    for attribute, _ in window.BACKGROUND_THREADS:
        setattr(window, attribute, _SlowThread())

    started = time.monotonic()
    window.closeEvent(QCloseEvent())
    elapsed = time.monotonic() - started

    # По сроку на каждый вышло бы шесть раз по 200 мс
    assert elapsed < 0.8, \
        f"закрытие заняло {elapsed:.2f} с при общем сроке {window.THREAD_WAIT_MS} мс"


def test_close_is_refused_while_thread_will_not_stop():
    # Бросать работающий поток нельзя, но и держать окно взаперти тоже:
    # решает пользователь, и по умолчанию окно остаётся открытым
    from PySide6.QtGui import QCloseEvent
    from PySide6.QtWidgets import QMessageBox

    window = _window()
    window.postgres_thread = _FakeThread(stops=False)

    asked = []
    original = QMessageBox.question
    QMessageBox.question = staticmethod(
        lambda *args, **kwargs: (asked.append(args[2]) or QMessageBox.StandardButton.No))
    try:
        event = QCloseEvent()
        event.accept()
        window.closeEvent(event)
    finally:
        QMessageBox.question = original

    assert asked, "про незакончившуюся работу не спросили"
    assert "выгрузка в PostgreSQL" in asked[0], \
        f"не сказано, что именно ещё выполняется: {asked[0]!r}"
    assert not event.isAccepted(), "окно закрылось поверх работающего потока"


def test_postgres_asks_before_duplicating():
    # Связи и точки сопряжения не защищены от повторной вставки, а колонки
    # листа в схеме нет — отличить одну выгрузку от другой база не может.
    # Значит выбор «дописать или заменить» делает человек, и по умолчанию
    # стоит тот, который не может уничтожить чужие данные.
    from contur.ui.widgets import PostgresDialog

    window = _window()
    dialog = PostgresDialog(window)

    assert dialog.mode() == "append", \
        f"по умолчанию выбрано {dialog.mode()!r} — замена не должна быть умолчанием"

    modes = [dialog.mode_choice.itemData(i) for i in range(dialog.mode_choice.count())]
    assert modes == ["append", "replace"], f"режимы выгрузки: {modes}"

    # Предупреждение обязано меняться вместе с выбором: замена удаляет
    # и то, что пришло с других листов
    append_hint = dialog.mode_hint.text()
    dialog.mode_choice.setCurrentIndex(modes.index("replace"))
    assert dialog.mode() == "replace", "режим замены не выбирается"
    assert dialog.mode_hint.text() != append_hint, \
        "при выборе замены не сказано, что прежние данные будут удалены"
    assert "удален" in dialog.mode_hint.text().lower(), \
        f"предупреждение о замене не говорит об удалении: {dialog.mode_hint.text()!r}"


def test_postgres_mode_reaches_the_thread():
    # Выбор в диалоге должен доходить до экспортёра, иначе он украшение
    from contur.ui.workers import PostgresExportThread

    thread = PostgresExportThread("нет.svg", [], [], {}, mode="replace")
    assert thread.mode == "replace", "режим не доходит до потока выгрузки"

    default = PostgresExportThread("нет.svg", [], [], {})
    assert default.mode == "append", f"умолчание потока: {default.mode!r}"


def test_postgres_password_is_not_stored():
    # Пароль не кладём в реестр открытым текстом
    from contur.ui.widgets import PostgresDialog

    window = _window()
    dialog = PostgresDialog(window)
    dialog.password.setText("секрет")

    assert dialog.db_config()["password"] == "секрет", "пароль не дошёл до подключения"
    assert "password" not in dialog.saveable(), "пароль попал в сохраняемые настройки"


def test_postgres_export_runs_in_thread():
    # Экспорт шёл в потоке окна: Windows показывала его как переставшее
    # отвечать, пока идёт разбор SVG и запись в базу
    from PySide6.QtCore import QThread
    from contur.ui.workers import PostgresExportThread

    assert issubclass(PostgresExportThread, QThread)

    import inspect
    from contur.ui import main_window
    source = inspect.getsource(main_window.DeviceVisualizer.export_to_postgresql)
    assert "PostgresExportThread" in source, "экспорт по-прежнему в потоке окна"
    assert "processEvents" not in source, "остался обход зависания через processEvents"


def _visible_devices(window) -> int:
    total = 0
    for index in range(window.device_tree.topLevelItemCount()):
        group = window.device_tree.topLevelItem(index)
        for child_index in range(group.childCount()):
            total += int(not group.child(child_index).isHidden())
    return total


def _fill_two_groups(window):
    window.matches = [
        DeviceMatch(lua_name="LA_TANK1V101", pdf_name="V101", tech_object="LA_TANK1",
                    coordinates=(50.0, 50.0), confidence=0.9, device_type="V"),
        DeviceMatch(lua_name="LA_TANK1V102", pdf_name="V102", tech_object="LA_TANK1",
                    coordinates=(80.0, 50.0), confidence=0.9, device_type="V"),
        DeviceMatch(lua_name="LINE_M1LS2", pdf_name="LS2", tech_object="LINE_M1",
                    coordinates=(300.0, 90.0), confidence=0.9, device_type="LS"),
    ]
    window._update_tech_filter()
    window._update_device_tree()
    window.draw_scene()
    return window


def test_search_narrows_the_tree():
    # Устройств больше двух сотен в трёх десятках групп — нужное
    # приходилось прокручивать глазами
    window = _fill_two_groups(_window())
    assert _visible_devices(window) == 3

    window.device_search.setText("LS")
    assert _visible_devices(window) == 1, "поиск по типу не сработал"

    window.device_search.setText("LINE")
    assert _visible_devices(window) == 1, "поиск по технологическому объекту не сработал"

    window.device_search.setText("V10")
    assert _visible_devices(window) == 2, "поиск по имени с чертежа не сработал"

    window.device_search.setText("")
    assert _visible_devices(window) == 3, "очистка поиска не вернула список"


def test_search_survives_tree_rebuild():
    # Дерево перестраивается после разметки: введённый поиск не должен
    # сбрасываться, иначе в списке снова окажутся все устройства
    window = _fill_two_groups(_window())
    window.device_search.setText("LS")
    window._update_device_tree()

    assert _visible_devices(window) == 1, "поиск потерялся при перестроении дерева"


def test_selected_device_is_highlighted():
    from contur.ui.widgets import DeviceGraphicsItem

    window = _fill_two_groups(_window())
    item = window.device_tree.topLevelItem(0).child(0)
    window.on_tree_item_clicked(item, 0)

    highlighted = [i for i in window.graphics_view._scene.items()
                   if isinstance(i, DeviceGraphicsItem) and i.selected]
    assert len(highlighted) == 1, f"подсвечено {len(highlighted)} устройств вместо одного"
    assert highlighted[0].device_data is window.selected_match


def test_highlight_survives_redraw():
    from contur.ui.widgets import DeviceGraphicsItem

    window = _fill_two_groups(_window())
    window.on_tree_item_clicked(window.device_tree.topLevelItem(0).child(0), 0)
    window.draw_scene()

    highlighted = [i for i in window.graphics_view._scene.items()
                   if isinstance(i, DeviceGraphicsItem) and i.selected]
    assert len(highlighted) == 1, "подсветка пропала после перерисовки"


def test_click_keeps_zoom_double_click_changes_it():
    # Одиночный щелчок показывает устройство, не трогая масштаб:
    # увеличение выбирает пользователь, а не дерево
    window = _fill_two_groups(_window())
    view = window.graphics_view
    view.zoom_by(3.0)
    before = view.current_scale()

    item = window.device_tree.topLevelItem(0).child(0)
    window.on_tree_item_clicked(item, 0)
    assert abs(view.current_scale() - before) < 1e-6, "одиночный щелчок сменил масштаб"

    window.on_tree_item_double_clicked(item, 0)
    assert view.current_scale() != before, "двойной щелчок не приблизил"


def test_zoom_to_point_does_not_accumulate():
    # Масштаб задаётся, а не умножается: иначе двойной щелчок по второму
    # устройству уводил бы всё глубже
    window = _fill_two_groups(_window())
    view = window.graphics_view

    view.zoom_to_point(50.0, 50.0)
    first = view.current_scale()
    view.zoom_to_point(300.0, 90.0)

    assert abs(view.current_scale() - first) < 1e-6, "масштаб накапливается"


def _isolated_settings():
    # Хранилище уже уведено в тестовое при загрузке файла — здесь только чистим
    app_settings.storage().clear()
    return app_settings


def test_settings_survive_restart():
    # Раньше не сохранялось ничего: каждый запуск возвращал размеры окна,
    # профиль разметки и настройки отображения к исходным
    settings = _isolated_settings()

    window = _window()
    window.detection_profile.setCurrentIndex(
        window.detection_profile.findData("accurate"))
    window.contour_alpha.setValue(123)
    window.show_device_names.setChecked(False)
    window._save_settings()

    from contur.ui import main_window
    fresh = main_window.DeviceVisualizer()
    assert fresh.detection_profile.currentData() == "accurate", "профиль не запомнился"
    assert fresh.contour_alpha.value() == 123, "прозрачность не запомнилась"
    assert not fresh.show_device_names.isChecked(), "флажок подписей не запомнился"

    settings.storage().clear()


def test_password_never_reaches_storage():
    settings = _isolated_settings()

    window = _window()
    window.db_settings = {"host": "srv", "port": 5433, "database": "hmi",
                          "user": "postgres", "password": "секрет"}
    window._save_settings()

    stored = settings.load_db_settings()
    assert stored.get("host") == "srv", "параметры базы не сохранились"
    assert "password" not in stored, "пароль сохранён открытым текстом"

    settings.storage().clear()


def test_session_is_offered_not_opened():
    # Полоска предлагает открыть прошлый сеанс, но сама ничего не грузит:
    # молчание — тоже ответ
    settings = _isolated_settings()

    window = _window()
    pdf = Path(__file__).resolve().parent.parent / "output" / "_session_test.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(b"%PDF-1.4\n")

    try:
        settings.save_session([], None, str(pdf), 3)

        from contur.ui import main_window
        opened = []
        original = main_window.DeviceVisualizer._open_pdf
        main_window.DeviceVisualizer._open_pdf = lambda self, p, page=None: opened.append(p)
        try:
            fresh = main_window.DeviceVisualizer()
            assert fresh.session_bar.isVisible() or fresh.session_bar.text(), \
                "полоска предложения не появилась"
            assert "лист 4" in fresh.session_bar.text(), \
                f"номер листа не показан: {fresh.session_bar.text()!r}"
            assert not opened, "файл открылся сам, без нажатия"

            fresh._restore_last_session()
            assert opened == [str(pdf)], "нажатие «Открыть» не загрузило файл"
        finally:
            main_window.DeviceVisualizer._open_pdf = original
    finally:
        pdf.unlink(missing_ok=True)
        settings.storage().clear()


def test_recent_files_skip_missing():
    # Список нужен, чтобы открывать, а не чтобы напоминать об удалённом
    settings = _isolated_settings()

    real = Path(__file__).resolve()
    settings.remember_recent("pdf", str(real))
    settings.remember_recent("pdf", "C:/такого/файла/нет.pdf")

    files = settings.recent_files("pdf")
    assert str(real) in files
    assert not any("нет.pdf" in path for path in files), "пропавший файл остался в списке"

    settings.storage().clear()


def test_recent_menus_call_their_own_handler():
    # Обработчик привязывался замыканием, а внешний цикл заканчивался раньше
    # первого нажатия — opener у всех пунктов оказывался последним, и файл
    # из списка «Последние PDF» уходил в разбор Lua
    settings = _isolated_settings()
    window = _window()

    settings.remember_recent("pdf", str(Path(__file__).resolve()))
    settings.remember_recent("lua", str(Path(__file__).resolve().parent.parent / "contur" / "core" / "config.py"))

    called = []
    window._open_recent_pdf = lambda path: called.append(("pdf", path))
    window._open_recent_lua = lambda path: called.append(("lua", path))
    window._refresh_recent_menus()

    for act in window.recent_pdf_menu.actions():
        act.trigger()
    assert called and called[0][0] == "pdf", \
        f"пункт из «Последние PDF» ушёл не туда: {called}"

    called.clear()
    for act in window.recent_lua_menu.actions():
        act.trigger()
    assert called and called[0][0] == "lua", \
        f"пункт из «Последние Lua» ушёл не туда: {called}"

    settings.storage().clear()


def test_drop_recognises_file_types():
    window = _window()
    assert window.acceptDrops(), "окно не принимает перетаскивание"
    assert window._drop_kind("C:/схемы/лист.pdf") == ".pdf"
    assert window._drop_kind("C:/lua/main.io.lua") == "lua"
    assert window._drop_kind("C:/out/разметка.svg") == ".svg"
    assert window._drop_kind("C:/readme.txt") is None


def test_layers_can_be_hidden():
    # Раньше переключатели отображения жили в отдельном окне настроек,
    # куда за ними приходилось ходить
    from contur.ui.widgets import DeviceGraphicsItem

    window = _fill(_window())
    scene = window.graphics_view._scene

    def devices():
        return sum(1 for i in scene.items() if isinstance(i, DeviceGraphicsItem))

    assert devices() > 0

    window.layer_devices.setChecked(False)
    assert devices() == 0, "устройства не спрятались"

    window.layer_devices.setChecked(True)
    assert devices() > 0, "устройства не вернулись"


def test_legend_lists_shown_types():
    window = _fill_two_groups(_window())
    text = window.legend_label.text()

    assert window.legend_label.isVisible() or text, "легенда не появилась"
    assert "V" in text and "LS" in text, f"типы не перечислены: {text!r}"
    assert "2" in text, "количество по типу не показано"


def test_minimap_follows_the_view():
    window = _fill(_window())
    window.mini_map.refresh()

    assert not window.mini_map._scene_rect.isEmpty(), "мини-карта не увидела схему"
    assert window.mini_map._mapping() is not None, "не считается перевод координат"

    # Щелчок по карте переносит вид
    from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    view = window.graphics_view
    view.zoom_by(6.0)
    before = view.mapToScene(view.viewport().rect().center())

    point = QPointF(window.mini_map.width() * 0.8, window.mini_map.height() * 0.8)
    window.mini_map.mousePressEvent(
        QMouseEvent(QEvent.Type.MouseButtonPress, point,
                    window.mini_map.mapToGlobal(QPoint(1, 1)),
                    Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier))

    after = view.mapToScene(view.viewport().rect().center())
    assert (after - before).manhattanLength() > 1, "щелчок по карте не перенёс вид"


def test_page_titles_are_readable():
    # Страницу спрашивали числом: в файле на 265 листов надо было помнить,
    # что именно на каком
    import fitz
    from contur.ui.workers import PageTitlesThread

    pdf = config.INPUT_DIR / "test1" / "BN1-МОЛОКОХРАНИЛИЩЕ-2025Full.pdf"
    if not pdf.exists():
        print(f"  ПРОПУСК test_page_titles_are_readable: нет {pdf}")
        return

    reader = PageTitlesThread(str(pdf), 5)
    with fitz.open(pdf) as document:
        titles = [reader._page_title(document[number]) for number in range(5)]

    assert all(titles), f"есть листы без названия: {titles}"
    # Обрывки примечаний начинаются со строчной буквы
    assert not any(t[0].islower() for t in titles), f"в названия попал обрывок: {titles}"


def test_page_navigation_knows_its_limits():
    window = _window()
    from contur.ui import main_window

    scheme = main_window.LoadedScheme(pdf_path="C:/x/схема.pdf", page=0, total_pages=3)
    window.schemes = [scheme]
    window.active_scheme = scheme
    window._refresh_page_controls()

    assert not window.prev_page_btn.isEnabled(), "с первого листа можно уйти назад"
    assert window.next_page_btn.isEnabled(), "нельзя перейти на следующий лист"
    assert "1 из 3" in window.page_label.text()

    scheme.page = 2
    window._refresh_page_controls()
    assert window.prev_page_btn.isEnabled()
    assert not window.next_page_btn.isEnabled(), "с последнего листа можно уйти вперёд"


def test_panel_does_not_grow_with_the_window():
    # На развёрнутом окне свободная ширина делилась поровну, и панель
    # разрасталась: на экране 3840 она занимала 1260 пикселей — треть окна
    # под кнопки, тогда как схеме места не хватало
    window = _window()
    widths = []
    for width, height in ((1224, 720), (1920, 1080), (3840, 2160)):
        window.resize(width, height)
        QApplication.processEvents()
        widths.append(window.main_splitter.sizes()[0])

    assert len(set(widths)) == 1, f"панель меняет ширину с окном: {widths}"
    assert widths[0] <= window.PANEL_MAX_WIDTH, \
        f"панель шире допустимого: {widths[0]} > {window.PANEL_MAX_WIDTH}"

    # Вся освободившаяся ширина должна доставаться схеме
    window.resize(3840, 2160)
    QApplication.processEvents()
    panel, scheme = window.main_splitter.sizes()
    assert scheme > panel * 5, f"схеме досталось {scheme} px при панели {panel} px"


def test_panel_content_is_not_clipped():
    # Ширина считается от содержимого: при другом шрифте или масштабе экрана
    # готовое число либо обрежет подписи, либо оставит пустую полосу
    from PySide6.QtWidgets import QWidget

    window = _window()
    window.resize(1600, 900)
    QApplication.processEvents()

    inner = window.main_splitter.widget(0).widget()
    assert window.panel_width >= inner.minimumSizeHint().width(), \
        f"панели выделено {window.panel_width} px при нужных " \
        f"{inner.minimumSizeHint().width()} px"

    clipped = [child.text() for child in inner.findChildren(QWidget)
               if hasattr(child, "text") and child.minimumSizeHint().width() > inner.width()]
    assert not clipped, f"не помещаются: {clipped}"


def test_scheme_view_grows_in_height():
    # По высоте растёт вид схемы, а не список технологических операций
    window = _window()
    window.resize(1600, 700)
    QApplication.processEvents()
    short = window.right_splitter.sizes()

    window.resize(1600, 1400)
    QApplication.processEvents()
    tall = window.right_splitter.sizes()

    assert tall[0] - short[0] > tall[1] - short[1], \
        f"высота ушла списку операций: схема {short[0]}→{tall[0]}, список {short[1]}→{tall[1]}"


def test_old_layout_is_not_restored():
    # У тех, кто уже запускал приложение, сохранено прежнее положение
    # разделителей — оно вернуло бы старую раскладку и правка не подействовала бы
    settings = _isolated_settings()
    settings.save_value("layout/version", 1)
    settings.save_value("splitters/main", "старое состояние".encode("utf-8"))

    window = _window()
    window.resize(1920, 1080)
    QApplication.processEvents()

    assert window.main_splitter.sizes()[0] <= window.PANEL_MAX_WIDTH, \
        "восстановилась прежняя раскладка"

    settings.storage().clear()


def test_background_survives_redraw():
    # clear() удаляет объекты вместе с их C++ частью: подложку вынимаем
    # из сцены заранее, иначе SVG каждый раз перечитывался с диска
    window = _fill(_window())
    svg = Path(__file__).resolve().parent.parent / "output" / "_ui_state_test.svg"
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">'
        '<rect x="0" y="0" width="200" height="100" fill="white"/></svg>',
        encoding="utf-8")

    try:
        assert window.graphics_view.load_svg_background(str(svg))
        window.svg_background_path = str(svg)
        item = window.graphics_view.svg_item

        window.draw_scene()
        assert window.graphics_view.svg_item is item, "подложка пересоздалась"
    finally:
        svg.unlink(missing_ok=True)


def test_lua_loaded_after_pdf_continues_the_pipeline():
    # Сопоставление вызывалось только из _on_geometry_finished, а геометрия —
    # только из _open_pdf. Порядок «сначала чертёж, потом Lua» заходил в тупик:
    # разметка красила устройства, а каталог оставался пустым и выделять
    # на схеме было нечего — self.matches так и не заполнялся
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    window = _window()
    parsed = {"devices": [{"name": "TANK1V1"}], "nodes": []}

    # Геометрия уже извлечена — продолжать надо сопоставлением
    window.current_pdf_path = "чертёж.pdf"
    window.current_geometry_xml = "геометрия.xml"
    with mock.patch.object(QMessageBox, "information", return_value=None), \
         mock.patch.object(window, "_start_device_matching") as matching, \
         mock.patch.object(window, "_start_geometry_extraction") as geometry:
        window._on_lua_finished(True, parsed)
    assert matching.called, "Lua загрузили после чертежа, а сопоставление не пошло"
    assert not geometry.called, "геометрия извлекалась второй раз"

    # Геометрии нет: _open_pdf вышел, предложив загрузить Lua, — начинаем с неё
    window.current_geometry_xml = None
    with mock.patch.object(QMessageBox, "information", return_value=None), \
         mock.patch.object(window, "_start_device_matching") as matching, \
         mock.patch.object(window, "_start_geometry_extraction") as geometry:
        window._on_lua_finished(True, parsed)
    assert geometry.called, "конвейер не начался, хотя чертёж загружен"
    assert not matching.called, "сопоставление без геометрии"

    # Чертежа нет вовсе — трогать нечего
    window.current_pdf_path = None
    with mock.patch.object(QMessageBox, "information", return_value=None), \
         mock.patch.object(window, "_start_device_matching") as matching, \
         mock.patch.object(window, "_start_geometry_extraction") as geometry:
        window._on_lua_finished(True, parsed)
    assert not matching.called and not geometry.called, \
        "конвейер пошёл без чертежа"


def test_matching_can_be_restarted_without_reopening_the_pdf():
    # Устаревший output/parsed_lua.json от прошлого проекта давал ноль
    # сопоставлений молча, и пересчитать их было нечем: единственным входом
    # в сопоставление было повторное открытие чертежа
    from unittest import mock

    from PySide6.QtWidgets import QMessageBox

    window = _window()
    assert hasattr(window, "act_match"), "нет пункта «Сопоставить устройства»"

    titles = [action.text() for menu in window.menuBar().findChildren(type(
        window.menuBar().addMenu("x"))) for action in menu.actions()]
    assert any("Сопоставить" in title for title in titles), \
        "пункт есть, но в меню его не видно"

    window.current_pdf_path = None
    with mock.patch.object(QMessageBox, "information", return_value=None) as told, \
         mock.patch.object(window, "_continue_after_lua") as resumed:
        window.rematch_devices()
    assert told.called and not resumed.called, "без чертежа сопоставление молча ничего не делает"

    window.current_pdf_path = "чертёж.pdf"
    with mock.patch.object(window, "_continue_after_lua") as resumed:
        window.rematch_devices()
    assert resumed.called, "пункт меню не пересобирает каталог"


def test_matching_is_available_together_with_markup():
    # Разметка и сопоставление требуют одного и того же — загруженного
    # чертежа, поэтому включаться должны вместе
    window = _window()
    window._allow_markup(False)
    assert not window.act_match.isEnabled(), "сопоставление доступно без чертежа"

    window._allow_markup(True)
    assert window.act_match.isEnabled(), "чертёж есть, а сопоставить нельзя"


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
