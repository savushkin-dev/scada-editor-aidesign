# tests/test_details_panel.py
# Панель сведений: что в неё попадает — про устройство и про операцию —
# и что показываемое не накладывается друг на друга.
#
# Наложение — главная опасность этой панели: заполняется она из пяти
# источников (описание устройства, теги контроллера, уставки объекта,
# состояния операций, свойства) и показывает то устройство, то операцию.
# Любой забытый clear() дописывал бы второе выбранное к первому. Поэтому
# проверяется не только содержимое, но и то, что после второго выбора строк
# ровно столько, сколько у второго.
#
# Запуск из папки CONTUR:
#     python tests/test_details_panel.py
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import details_panel
from data_models import DeviceMatch
from objects_loader import objects_data

# Описание объектов в том виде, в каком его отдаёт среда разработки
# контроллера: техобъект с операциями, состояния отдельным списком,
# шаги внутри state_data
OBJECTS = {
    "tech_objects": [
        {
            "id": "1", "n": 1, "tech_type": 2,
            "name": "Танк №1", "name_eplan": "LA_TANK1", "name_BC": "TANK1",
            "base_tech_object": "tank", "cooper_param_number": 3,
            "properties": {"среда": "молоко"},
            "equipment": {"насос": "M1"},
            "operations": [
                {"id": "оп1", "name": "Мойка", "base_operation": "wash",
                 "props": {"время": 10}},
            ],
        },
        # Объект назван без номера, номер отдельным полем — так его пишет
        # среда разработки контроллера почти всегда
        {
            "id": "2", "n": 1, "tech_type": 3,
            "name": "Танк рассола", "name_eplan": "BRINE_TANK",
            "name_BC": "BrineTank1Obj1", "base_tech_object": "tank",
            "operations": [],
        },
    ],
    "parameters": [
        {"id": "п1", "name": "Объём", "value": 1000, "meter": "л",
         "nameLua": "V_TANK", "oper": [1], "obj_id": "1"},
    ],
    "states": [
        {
            "state_id": "с1", "operation_id": "оп1", "operation_name": "Мойка",
            "obj_id": "1", "obj_name": "Танк №1",
            "state_data": {
                "name": "Наполнение",
                "opened_devices": ["LA_TANK1V1"],
                "steps": {
                    "1": {"name": "Первый", "opened_devices": ["LA_TANK1V1"]},
                    "2": {"name": "Второй", "closed_devices": ["LA_TANK1V1",
                                                               "LA_TANK1V2"]},
                },
            },
        },
    ],
}

VALVE = DeviceMatch(
    lua_name="LA_TANK1V1", pdf_name="V1", tech_object="LA_TANK1",
    coordinates=(100.0, 200.0), confidence=1.0, device_type="V",
    descr="Донный клапан", article="OMR.E2A", category="valve",
    subtype=13, dtype=0,
    tags={"DI": [{"node": 4, "module_offset": 1104, "logical_port": 7,
                  "physical_port": 6, "offset": 1110}],
          "par": [5000, 1], "rt_par": [8], "prop": {"IP": "10.216.98.104"}},
    view_size=(32.0, 18.0),
    view_shape=[(-8.0, -4.0, 8.0, 4.0)],
)

# Сигнал: ни артикула, ни тегов, ни операций — половина панели пуста
SIGNAL = DeviceMatch(
    lua_name="LINE_M1DI3", pdf_name="DI3", tech_object="LINE_M1",
    coordinates=(300.0, 400.0), confidence=0.7, device_type="DI",
)


def _loaded():
    objects_data.load_from_json(OBJECTS)


def _operation():
    _loaded()
    return objects_data.get_operation_by_id("оп1")


def _panel():
    QApplication.instance() or QApplication([])
    return details_panel.DetailsPanel()


# ---------------------------------------------------- сбор данных: устройство

def test_type_is_spelled_out():
    # Имя LA_TANK1V1 само по себе не говорит, клапан это или лампа
    title = details_panel.type_title("V")
    assert title.startswith("V — ") and "лапан" in title, f"тип не расшифрован: {title}"


def test_unknown_type_stays_as_is():
    assert details_panel.type_title("ZZ") == "ZZ", "неизвестный тип потерялся"
    assert details_panel.type_title("") == "не разобран", "пустой тип показан пустым"


def test_tech_object_is_found_by_eplan_name():
    _loaded()
    tech_object = details_panel.tech_object_of(VALVE)
    assert tech_object is not None, "объект LA_TANK1 не найден в описании"
    assert tech_object.name == "Танк №1", f"найден не тот объект: {tech_object.name}"


def test_tech_object_is_found_with_its_number():
    # В описании объект зовут BRINE_TANK, номер лежит отдельным полем,
    # а на чертеже и в имени устройства они вместе: BRINE_TANK1V1
    _loaded()
    valve = DeviceMatch(lua_name="BRINE_TANK1V1", pdf_name="V1",
                        tech_object="BRINE_TANK1", coordinates=(1.0, 2.0),
                        confidence=1.0, device_type="V")
    tech_object = details_panel.tech_object_of(valve)

    assert tech_object is not None, "объект с номером в имени не найден"
    assert tech_object.name == "Танк рассола", f"найден не тот: {tech_object.name}"


def test_parameters_include_device_and_object():
    _loaded()
    groups = details_panel.parameter_groups(VALVE,
                                            details_panel.tech_object_of(VALVE))
    titles = [title for title, _ in groups]

    assert len(groups) == 3, f"групп параметров: {titles}"
    assert any("par" in title for title in titles), "параметров устройства нет"
    assert any("Уставки" in title for title in titles), "уставок объекта нет"

    setpoints = next(rows for title, rows in groups if "Уставки" in title)
    assert setpoints[0][:3] == ("Объём", "1000", "л"), f"уставка разобрана как {setpoints[0]}"


def test_signals_carry_controller_address():
    row = details_panel.signal_rows(VALVE)[0]
    assert row == ("DI", "4", "1104", "7", "6", "1110"), f"адрес канала: {row}"


def test_states_cover_every_step():
    _loaded()
    entries = details_panel.state_entries(VALVE)
    statuses = sorted({e["status"] for e in entries})

    assert len(entries) == 3, f"мест, где устройство участвует: {len(entries)}"
    assert statuses == ["closed", "opened"], f"положения: {statuses}"


def test_states_are_found_by_pdf_name_too():
    # В описании операций устройство пишут и полным именем, и подписью
    objects_data.load_from_json({
        "states": [{"state_id": "с1", "operation_id": "оп1",
                    "operation_name": "Мойка", "obj_id": "1", "obj_name": "Танк",
                    "state_data": {"name": "Слив", "closed_devices": ["V1"]}}],
    })
    assert details_panel.state_entries(VALVE), "по подписи с чертежа состояния не нашлись"


def test_properties_gather_leftovers():
    _loaded()
    rows = dict(details_panel.property_rows(VALVE,
                                            details_panel.tech_object_of(VALVE)))

    assert rows.get("IP") == "10.216.98.104", "свойство устройства из Lua потеряно"
    assert "Габарит символа, пт" in rows, "габарит символа не показан"
    assert rows.get("Свойство объекта: среда") == "молоко", "свойства объекта нет"


def test_info_skips_empty_fields():
    _loaded()
    sections = dict(details_panel.device_sections(SIGNAL))
    fields = dict(sections["Устройство"])

    assert "Артикул" not in fields, "пустой артикул показан строкой"
    assert fields["Имя в Lua"] == "LINE_M1DI3", "имя устройства не показано"
    assert "Дискретный вход" in fields["Тип устройства"], "тип не расшифрован"


def test_info_says_when_object_is_unknown():
    _loaded()
    sections = dict(details_panel.device_sections(SIGNAL))
    fields = dict(sections["Технологический объект"])

    assert "В описании объектов" in fields, "молчание вместо объяснения"
    assert "main.objects.lua" in fields["В описании объектов"], \
        "не сказано, чего не хватает"


def test_operation_position_shown_when_known():
    # Положение приходит от выбранной операции — тем же путём, что красит
    # обводку устройства на схеме
    _loaded()
    match = DeviceMatch(lua_name="LA_TANK1V1", pdf_name="V1",
                        tech_object="LA_TANK1", coordinates=(1.0, 2.0),
                        confidence=1.0, device_type="V")
    match.operation_status = {"status": "opened", "state_name": "Наполнение",
                              "step_name": "Первый", "step_number": 1}

    sections = dict(details_panel.device_sections(match))
    assert "В выбранной операции" in sections, "положение в операции не показано"
    fields = dict(sections["В выбранной операции"])
    assert "открыто" in fields["Положение"], f"положение: {fields['Положение']}"
    assert fields["Шаг"] == "Первый", "шаг не показан"


# ----------------------------------------------------- сбор данных: операция

def test_operation_knows_what_it_does():
    # Тот же индекс, что отвечает «где участвует устройство», только
    # со стороны операции — рассказать разное они не могут
    entries = details_panel.operation_entries(_operation())
    devices = sorted({entry["device"] for entry in entries})

    assert devices == ["LA_TANK1V1", "LA_TANK1V2"], f"устройства операции: {devices}"
    assert all(entry["operation_id"] == "оп1" for entry in entries), \
        "в операцию попали чужие записи"


def test_operation_sections_count_states_and_steps():
    sections = dict(details_panel.operation_sections(_operation()))
    about = dict(sections["Операция"])

    assert about["Операция"] == "Мойка", "имя операции не показано"
    assert about["Состояний"] == "1" and about["Шагов"] == "2", \
        f"состояний и шагов посчитано: {about.get('Состояний')}, {about.get('Шагов')}"
    assert about["Базовая операция"] == "wash", "базовая операция не показана"


def test_operation_properties_include_its_own():
    operation = _operation()
    tech_object = objects_data.get_object_for_operation(operation)
    rows = dict(details_panel.operation_properties(operation, tech_object))

    assert rows.get("время") == "10", "свойства самой операции потеряны"
    assert rows.get("Свойство объекта: среда") == "молоко", "свойств объекта нет"


# ---------------------------------------------------------------- сама панель

def test_panel_starts_empty():
    panel = _panel()
    assert panel.device is None and panel.operation is None, \
        "панель занята до выбора"
    assert not panel.clear_btn.isEnabled(), "сброс доступен, а сбрасывать нечего"
    assert panel.tabs.tabText(panel.PARAMS) == "Параметры", "счётчик показан впустую"


def test_device_fills_every_tab():
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)

    assert panel.device is VALVE, "устройство не запомнено"
    assert panel.clear_btn.isEnabled(), "сбросить выбранное нечем"
    assert panel.params_tree.topLevelItemCount() == 3, "группы параметров не заполнены"
    assert panel.states_tree.topLevelItemCount() == 1, "операция не показана"
    assert panel.signals_table.rowCount() == 1, "канал контроллера не показан"
    assert panel.props_table.rowCount() >= 3, "свойства не заполнены"
    assert "LA_TANK1V1" in panel.title_label.text(), "в заголовке нет имени"


def test_tab_titles_carry_counts():
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)

    assert panel.tabs.tabText(panel.SIGNALS) == "Сигналы (1)", \
        f"счётчик сигналов: {panel.tabs.tabText(panel.SIGNALS)}"
    assert panel.tabs.tabText(panel.STATES) == "Состояния (3)", \
        f"счётчик состояний: {panel.tabs.tabText(panel.STATES)}"


def test_second_device_replaces_the_first():
    # Ради этого панель и очищается перед заполнением: выбор второго
    # устройства без сброса дописывал бы его строки к строкам первого
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)
    panel.show_device(SIGNAL)

    assert panel.device is SIGNAL, "панель осталась на первом устройстве"
    assert panel.signals_table.rowCount() == 0, \
        f"каналы первого устройства остались: {panel.signals_table.rowCount()}"
    assert panel.props_table.rowCount() == 0, "свойства первого устройства остались"
    assert "LINE_M1DI3" in panel.title_label.text(), "заголовок от первого устройства"
    assert "LA_TANK1V1" not in panel.info_text.toPlainText(), \
        "сводка первого устройства осталась в тексте"


def test_repeated_show_does_not_double_rows():
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)
    before = (panel.params_tree.topLevelItemCount(), panel.signals_table.rowCount(),
              panel.props_table.rowCount())
    panel.show_device(VALVE)
    after = (panel.params_tree.topLevelItemCount(), panel.signals_table.rowCount(),
             panel.props_table.rowCount())

    assert before == after, f"строки удвоились: было {before}, стало {after}"


def test_empty_tabs_explain_themselves():
    _loaded()
    panel = _panel()
    panel.show_device(SIGNAL)

    assert panel.params_tree.topLevelItemCount() == 1, "пустая вкладка без объяснения"
    assert "Параметров нет" in panel.params_tree.topLevelItem(0).text(0), \
        "не сказано, почему параметров нет"
    assert "не участвует" in panel.states_tree.topLevelItem(0).text(0), \
        "не сказано, почему состояний нет"


# ------------------------------------------------------- операция в панели

def test_operation_fills_the_same_panel():
    panel = _panel()
    operation = _operation()
    panel.show_operation(operation)

    assert panel.operation is operation, "операция не запомнена"
    assert panel.device is None, "в панели разом устройство и операция"
    assert "Мойка" in panel.title_label.text(), "в заголовке нет имени операции"
    assert panel.params_tree.topLevelItemCount() == 1, "уставки объекта не показаны"
    assert panel.props_table.rowCount() >= 1, "свойства операции не показаны"


def test_operation_tree_groups_by_state_and_step():
    panel = _panel()
    panel.show_operation(_operation())

    assert panel.states_tree.topLevelItemCount() == 1, "состояние не показано"
    state = panel.states_tree.topLevelItem(0)
    assert "Наполнение" in state.text(0), f"состояние подписано как {state.text(0)!r}"
    # Шага два плюс строка «задано состоянием» — положение бывает задано
    # самим состоянием, без шага
    assert state.childCount() == 3, f"шагов под состоянием: {state.childCount()}"
    assert sum(state.child(i).childCount() for i in range(3)) == 4, \
        "устройства шагов не перечислены"


def test_operation_shows_steps_without_devices():
    # Скелет берётся у самой операции: шаг без устройств — это тоже шаг,
    # а иначе операция, которая ничего не открывает, выглядела бы вовсе
    # без состояний
    objects_data.load_from_json({
        "tech_objects": [{"id": "1", "n": 1, "name": "Танк",
                          "operations": [{"id": "оп9", "name": "Пауза"}]}],
        "states": [{"state_id": "с9", "operation_id": "оп9",
                    "operation_name": "Пауза", "obj_id": "1", "obj_name": "Танк",
                    "state_data": {"name": "Ожидание",
                                   "steps": {"1": {"name": "Выдержка"}}}}],
    })
    panel = _panel()
    panel.show_operation(objects_data.get_operation_by_id("оп9"))

    assert panel.states_tree.topLevelItemCount() == 1, "состояние не показано"
    state = panel.states_tree.topLevelItem(0)
    assert state.childCount() == 1, f"шагов под состоянием: {state.childCount()}"
    assert "Выдержка" in state.child(0).text(0), "шаг без устройств пропал"
    assert "нет" in state.child(0).text(1), "не сказано, что устройств нет"
    assert panel.tabs.tabText(panel.STATES) == "Состояния (2)", \
        f"счётчик: {panel.tabs.tabText(panel.STATES)}"


def test_operation_steps_show_how_many_devices():
    panel = _panel()
    panel.show_operation(_operation())

    state = panel.states_tree.topLevelItem(0)
    counters = [state.child(i).text(1) for i in range(state.childCount())]
    assert any("🔒 2" in text for text in counters), \
        f"шаг не сказал, сколько устройств закрывает: {counters}"


def test_signals_tab_hidden_for_operation():
    # Каналы ввода-вывода есть у устройства, а не у операции: пустая вкладка
    # выглядела бы потерянными данными
    _loaded()
    panel = _panel()
    panel.show_operation(_operation())
    assert not panel.tabs.isTabVisible(panel.SIGNALS), "у операции показаны «Сигналы»"

    panel.show_device(VALVE)
    assert panel.tabs.isTabVisible(panel.SIGNALS), "у устройства пропали «Сигналы»"


def test_operation_replaces_device_without_mixing():
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)
    panel.show_operation(_operation())

    assert panel.device is None, "устройство осталось выбранным"
    assert panel.signals_table.rowCount() == 0, "каналы устройства остались"
    assert "LA_TANK1V1" not in panel.title_label.text(), "заголовок от устройства"


def test_device_replaces_operation_without_mixing():
    _loaded()
    panel = _panel()
    panel.show_operation(_operation())
    panel.show_device(SIGNAL)

    assert panel.operation is None, "операция осталась выбранной"
    assert "Мойка" not in panel.info_text.toPlainText(), "сводка операции осталась"


# ---------------------------------------------------------------- сброс

def test_clear_returns_panel_to_empty():
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)
    panel.clear()

    assert panel.device is None and panel.operation is None, "выбранное осталось"
    assert panel.params_tree.topLevelItemCount() == 0, "параметры остались"
    assert panel.states_tree.topLevelItemCount() == 0, "состояния остались"
    assert panel.signals_table.rowCount() == 0, "сигналы остались"
    assert panel.props_table.rowCount() == 0, "свойства остались"
    assert panel.tabs.tabText(panel.SIGNALS) == "Сигналы", "счётчик остался от устройства"
    assert not panel.clear_btn.isEnabled(), "кнопка сброса осталась доступной"


def test_clear_button_tells_the_window():
    # Подсветку на схеме снимает окно: панель про сцену ничего не знает
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)

    told = []
    panel.cleared.connect(lambda: told.append(True))
    panel.clear_btn.click()

    assert told, "окно не узнало о сбросе"
    assert panel.device is None, "панель не очистилась по своей же кнопке"


def test_clear_itself_is_silent():
    # clear() зовёт и окно — если бы он слал сигнал, сброс ходил бы по кругу
    _loaded()
    panel = _panel()
    panel.show_device(VALVE)

    told = []
    panel.cleared.connect(lambda: told.append(True))
    panel.clear()

    assert not told, "clear() шлёт сигнал и зацикливает сброс"


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
