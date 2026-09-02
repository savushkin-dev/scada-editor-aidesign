# tests/test_device_matching.py
# Привязка подписи с чертежа к техобъекту.
#
# Основной случай простой: подпись внутри контура — устройство того объекта,
# которым контур подписан. Но Eplan ставит обозначение НАД символом, и у
# устройств на самой верхней кромке ряда подпись выходит за контур: символ
# внутри, подпись снаружи на 2-8 пт. На контрольном листе так теряются
# двенадцать клапанов CIP-коллектора (M1V91...M6V92) — на чертеже они есть,
# а в отчёте числятся пропавшими.
#
# Разбирать это расстоянием нельзя: ряды отстоят друг от друга на 11-14 пт,
# и подпись бывает ближе к нижней кромке чужого ряда, чем к верхней кромке
# своего. Поэтому проверки ниже сторожат именно направление и оба ограничителя
# (контур ждёт такое устройство, место не занято).
#
# Запуск из папки CONTUR:
#     python tests/test_device_matching.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import config
from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.matching.device_matcher import (BARE_NAME_CONFIDENCE, LABEL_ABOVE_CONFIDENCE,
                            SHEET_OBJECT_CONFIDENCE,
                            build_match_report, format_match_report, match_devices,
                            nearest_contour_below, sheet_object_from_texts)

# Ряды как на контрольном листе: высокие полосы во всю ширину, между ними
# зазор меньше, чем строка текста. Ось y растёт вниз, min_y — верхняя кромка.
#
# Стороны прямоугольника обязательны: без них попадание считается по описанной
# рамке с допуском в 5 пт, и подпись, лежащая над кромкой, ошибочно засчитается
# внутрь — на настоящем чертеже стороны есть, и она остаётся снаружи.
def row(name, min_x, min_y, max_x, max_y):
    corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    return {
        "name": name,
        "bounds": (min_x, min_y, max_x, max_y),
        "center": ((min_x + max_x) / 2, (min_y + max_y) / 2),
        # strict здесь не нужен: замыкаем список сам на себя
        "segments": list(zip(corners, corners[1:] + corners[:1])),  # noqa: B905
    }


ROW_M2 = row("=TM+M2", 150.0, 1924.8, 3135.0, 2024.0)
ROW_M1 = row("=TM+M1", 150.0, 2035.3, 3135.0, 2103.4)
ROWS = [ROW_M2, ROW_M1]

LUA = {"devices": [
    {"name": "M1V1", "descr": "Приём", "article": "ART-1"},
    {"name": "M1V91", "descr": "CIP-", "article": "ART-91"},
    {"name": "M2V91", "descr": "CIP-", "article": "ART-91"},
]}


def label(name, x, y):
    return {"device_name": name, "center": (x, y), "text": f"-{name}"}


def matched(contours, texts, lua=LUA):
    return {(m.tech_object, m.pdf_name): m for m in match_devices(lua, contours, texts)}


# ------------------------------------------------------- подпись внутри контура

def test_label_inside_contour_matches():
    result = matched(ROWS, [label("V1", 500.0, 2050.8)])
    assert ("M1", "V1") in result, "подпись внутри контура должна сопоставляться"
    assert result[("M1", "V1")].lua_name == "M1V1"
    assert result[("M1", "V1")].confidence == 1.0, \
        "привязка по попаданию внутрь контура сомнений не вызывает"
    assert result[("M1", "V1")].descr == "Приём", "данные устройства берутся из Lua"


# ------------------------------------------------------ подпись над кромкой

def test_label_above_top_edge_goes_to_contour_below():
    # Ровно случай M1V91: подпись на 5 пт выше верхней кромки своего ряда
    result = matched(ROWS, [label("V91", 2999.0, 2030.3)])
    assert ("M1", "V91") in result, "подпись над кромкой должна достаться этому ряду"
    assert ("M2", "V91") not in result, "ряд сверху её забирать не должен"
    assert result[("M1", "V91")].confidence == LABEL_ABOVE_CONFIDENCE, \
        "выведенная привязка помечается уверенностью ниже единицы"
    assert result[("M1", "V91")].descr == "CIP-"


def test_direction_beats_distance():
    # Ставим подпись так, чтобы по расстоянию выигрывал чужой ряд сверху:
    # до его нижней кромки 4.0 пт, до верхней кромки своего — 7.3 пт.
    # Ровно так лежат подписи M3V91 и M4V91 на контрольном листе.
    y = 2028.0
    assert y - ROW_M2["bounds"][3] < ROW_M1["bounds"][1] - y, \
        "проверка бессмысленна, если по расстоянию ближе как раз нужный ряд"

    result = matched(ROWS, [label("V91", 2999.0, y)])
    assert ("M1", "V91") in result, "решает направление, а не расстояние"
    assert ("M2", "V91") not in result


def test_label_below_contour_is_not_taken():
    # Ниже нижней кромки M1 — под ним ряда нет, притягивать не к чему
    assert not matched(ROWS, [label("V91", 2999.0, 2108.0)]), \
        "подпись под контуром его подписью не считается"


def test_unexpected_name_above_contour_is_ignored():
    # Так на контрольном листе отсеиваются подписи самих рядов (+M1, +M2)
    assert not matched(ROWS, [label("M1", 159.0, 2031.0)]), \
        "устройства M1M1 в Lua нет — привязывать нечего"


def test_far_label_is_not_pulled_in():
    # Один ряд, чтобы над ним было пусто и мешать было нечему
    far = ROW_M1["bounds"][1] - config.LABEL_ABOVE_CONTOUR_MAX - 1
    assert not matched([ROW_M1], [label("V91", 2999.0, far)]), \
        "дальше порога подпись к контуру не относится"
    near = ROW_M1["bounds"][1] - config.LABEL_ABOVE_CONTOUR_MAX + 1
    assert matched([ROW_M1], [label("V91", 2999.0, near)]), \
        "ближе порога — относится"


def test_label_outside_horizontal_range_is_ignored():
    result = matched(ROWS, [label("V91", 3300.0, 2030.3)])
    assert not result, "подпись сбоку от ряда его устройством не является"


def test_inside_label_wins_over_one_above():
    # Место занято подписью внутри контура — второй такой же брать нельзя,
    # иначе одно устройство Lua сопоставится дважды
    result = match_devices(LUA, ROWS, [label("V91", 2999.0, 2050.0),
                                       label("V91", 2999.0, 2030.3)])
    assert len(result) == 1, f"устройство сопоставлено дважды: {result}"
    assert result[0].confidence == 1.0, "остаться должна привязка по попаданию внутрь"


def test_each_row_gets_its_own_label():
    # Шесть рядов и шесть одинаковых подписей — как на контрольном листе
    result = matched(ROWS, [label("V91", 2999.0, 2030.3),   # над M1
                            label("V91", 2999.0, 1919.7)])  # над M2
    assert set(result) == {("M1", "V91"), ("M2", "V91")}, \
        f"подписи разошлись по рядам неверно: {sorted(result)}"


# ------------------------------------------------------ выбор контура снизу

def test_nearest_contour_below_prefers_closer_edge():
    assert nearest_contour_below((2999.0, 2030.3), ROWS) is ROW_M1
    assert nearest_contour_below((2999.0, 1919.7), ROWS) is ROW_M2


def test_nearest_contour_below_skips_unnamed_and_distant():
    assert nearest_contour_below((2999.0, 1000.0), ROWS) is None, \
        "до ближайшей кромки далеко"
    assert nearest_contour_below((2999.0, 2200.0), ROWS) is None, \
        "ниже всех контуров"


# ------------------------------------------------ отчёт о расхождениях
#
# «Есть в Lua, нет на чертеже» должно означать настоящую пропажу. Сигналы
# ввода-вывода туда попадали и топили её: на листе 13 mozzarella 36 строк
# про сигналы против 5 настоящих.

SIGNALS_LUA = {"devices": [
    {"name": "M1V1", "descr": "Приём"},
    {"name": "M1V2", "descr": "Не нарисован"},
    {"name": "M1DI1", "descr": "Мойка готова (Аппаратный)"},
    {"name": "M1DO11", "descr": "Приемник готов (Аппаратный)"},
    {"name": "M1AI1", "descr": "Расход продукта (Аппаратный)"},
    {"name": "M1AO1", "descr": "Задание температуры (Аппаратный)"},
    {"name": "M1WATCHDOG1", "descr": "Сторожевой таймер"},
]}


def report_for(texts, lua=SIGNALS_LUA, contours=(ROW_M1,)):
    contours = list(contours)
    matches = match_devices(lua, contours, texts)
    return build_match_report(lua, contours, texts, matches)


def test_io_signals_are_not_counted_as_missing():
    report = report_for([label("V1", 500.0, 2050.8)])
    assert [item["name"] for item in report["missing_on_drawing"]] == ["M1V2"], \
        "в пропаже должно остаться только настоящее устройство"
    assert report["io_signals"] == 4, "DI, DO, AI и AO считаются отдельно"
    assert report["non_devices"] == 1, "WATCHDOG считается как раньше"


def test_signals_are_named_in_the_report_text():
    text = format_match_report(report_for([label("V1", 500.0, 2050.8)]))
    assert "Есть в Lua, нет на этом листе: 1" in text
    assert "Сигналы ввода-вывода" in text, "число сигналов не должно пропадать молча"


def test_missing_section_warns_about_other_sheets():
    # Раздел читался как поломка распознавания, а обычно это устройство
    # соседнего листа: у объекта CIP на листе 13 mozzarella нарисован один
    # клапан из пяти, остальные на других листах
    text = format_match_report(report_for([label("V1", 500.0, 2050.8)]))
    assert "нескольким листам" in text, "нет оговорки про соседние листы"

    empty = format_match_report(report_for([label("V1", 500.0, 2050.8),
                                            label("V2", 700.0, 2050.8)]))
    assert "Есть в Lua, нет на этом листе: 0" in empty
    assert "нескольким листам" not in empty, "оговорка ни к чему, когда пропаж нет"


def test_label_repeating_contour_name_is_a_line_reference():
    # На контрольном листе так подписаны красные стрелки «M7 -> К ПОУ 1»
    # на пяти рядах: подпись повторяет имя своего контура, устройством не является
    report = report_for([label("V1", 500.0, 2050.8), label("M1", 3000.0, 2050.8)])
    assert report["unknown_labels"] == [], \
        f"ссылка на линию попала в список отсутствующих в Lua: {report['unknown_labels']}"
    assert report["object_references"] == 1

    text = format_match_report(report)
    assert "Ссылки на линии" in text, "число ссылок не должно пропадать молча"


def test_real_label_absent_from_lua_is_still_reported():
    # MCA1V1101 с контрольного листа: настоящий клапан, которого нет в Lua
    report = report_for([label("V1", 500.0, 2050.8), label("V77", 3000.0, 2050.8)])
    assert [item["label"] for item in report["unknown_labels"]] == ["V77"]
    assert report["object_references"] == 0


def test_drawn_signal_still_matches():
    # Убирать сигналы из разбора имён нельзя: если на чертеже такая подпись
    # всё же есть, устройство должно сопоставиться как обычно
    report = report_for([label("V1", 500.0, 2050.8), label("DI1", 700.0, 2050.8)])
    assert report["matched"] == 2, "подписанный сигнал сопоставляется"


def test_signal_sheet_reports_its_missing_signals():
    # Лист, на котором сигналы рисуют (страницы 5-14 контрольного проекта):
    # раз один сигнал сопоставился, остальные здесь — настоящие пропажи,
    # и прятать их в отдельную строку нельзя
    report = report_for([label("DI1", 700.0, 2050.8)])
    assert report["io_signals"] == 0, "лист сигнальный, отдельной строки быть не должно"
    missing = [item["name"] for item in report["missing_on_drawing"]]
    assert "M1DO11" in missing and "M1AI1" in missing and "M1AO1" in missing, \
        f"несопоставленные сигналы сигнального листа потерялись: {missing}"


def test_process_sheet_hides_signals_from_missing():
    # Технологический лист: ни одного сигнала не сопоставлено, значит их тут
    # и не рисуют — в пропажах им делать нечего
    report = report_for([label("V1", 500.0, 2050.8)])
    assert report["io_signals"] == 4
    assert [item["name"] for item in report["missing_on_drawing"]] == ["M1V2"]


# ------------------------------------------------- владелец из штампа листа

# Штамп: знак «+» отдельной ячейкой, содержимое — той же строкой правее.
# Знаков «+» на листе бывает несколько, штамп — самый нижний.
def stamp(location, x=1139.3, y=815.5):
    return [{"text": "+", "center": (x, y)},
            {"text": location, "center": (x + 15.0, y + 0.2)}]


def test_sheet_object_read_from_title_block():
    texts = [*stamp("PRIEM"),
             {"text": "=", "center": (1139.3, 804.1)},
             {"text": "TM", "center": (1149.5, 804.3)},
             {"text": "+CAB2", "center": (47.5, 181.0)}]
    assert sheet_object_from_texts(texts) == "PRIEM"
    assert sheet_object_from_texts([{"text": "=", "center": (1139.3, 804.1)}]) is None


def test_label_outside_contours_belongs_to_sheet_object():
    # Лист 5: двенадцать сигналов PRIEM стоят столбцом посреди листа,
    # блока «+PRIEM» вокруг них нет вовсе, и владелец известен только
    # из штампа. Ни один такой сигнал не сопоставлялся.
    lua = {"devices": [{"name": "PRIEMDI16", "descr": "Готовность"},
                       {"name": "M1V1", "descr": "Приём"}]}
    result = {(m.tech_object, m.pdf_name): m
              for m in match_devices(lua, ROWS, [label("DI16", 533.0, 400.0)], "PRIEM")}

    assert ("PRIEM", "DI16") in result, "подпись вне контуров осталась без владельца"
    assert result[("PRIEM", "DI16")].confidence == SHEET_OBJECT_CONFIDENCE, \
        "владелец выведен из штампа — уверенность должна быть ниже единицы"


def test_sheet_object_takes_only_unique_labels():
    # Лист 34: вне контуров четыре подписи «-SB1». Без проверки на повтор
    # одно устройство MCC1SB1 получило бы четыре привязки в разных местах
    lua = {"devices": [{"name": "MCC1SB1", "descr": "Кнопка"}]}
    texts = [label("SB1", 374.7, 220.3), label("SB1", 374.7, 379.1)]
    assert match_devices(lua, ROWS, texts, "MCC1") == []


def test_sheet_object_missing_from_lua_is_ignored():
    # Лист 240: в штампе «+CAB10», но такого техобъекта в Lua нет —
    # привязывать не к чему
    lua = {"devices": [{"name": "LINE_M10HL1", "descr": "Светодиод"}]}
    assert match_devices(lua, ROWS, [label("HL1", 318.1, 265.7)], "CAB10") == []


def test_label_inside_contour_is_not_taken_by_sheet_object():
    # Подпись внутри своего контура разбирает первый проход, и владелец
    # из штампа её не перехватывает
    lua = {"devices": [{"name": "M1V1", "descr": "Приём"},
                       {"name": "PRIEMV1", "descr": "Другое"}]}
    result = {(m.tech_object, m.pdf_name): m
              for m in match_devices(lua, ROWS, [label("V1", 500.0, 2050.8)], "PRIEM")}

    assert ("M1", "V1") in result
    assert ("PRIEM", "V1") not in result


# ------------------------------------------- устройства без техобъекта в имени

def test_device_without_tech_object_is_matched_by_its_name():
    # Проект MCA1: общая обвязка станции мойки названа в Lua просто «V1»,
    # «LT2», «FQT1» — без объекта впереди. Таких устройств 22 из 356,
    # и ни один путь сопоставления их не видел: каждый ищет устройство
    # внутри объекта. Лист общей обвязки с 74 подписями давал одно
    # сопоставление вместо двадцати
    lua = {"devices": [{"name": "V1", "descr": "Танк щелочи. Дренаж"},
                       {"name": "LT2", "descr": "Танк кислоты. Уровень"}]}
    result = {m.pdf_name: m for m in match_devices(lua, [], [label("V1", 500.0, 400.0),
                                                            label("LT2", 700.0, 400.0)])}

    assert set(result) == {"V1", "LT2"}, f"сопоставлено: {sorted(result)}"
    assert result["V1"].lua_name == "V1", "имя в Lua потеряно"
    assert result["V1"].tech_object == "", "устройству приписан чужой объект"
    assert result["V1"].descr == "Танк щелочи. Дренаж", "описание не доехало"
    assert result["V1"].confidence == BARE_NAME_CONFIDENCE, \
        "владельца у устройства нет — уверенность должна быть ниже привязки по штампу"


def test_bare_name_does_not_steal_a_label_from_its_owner():
    # Подпись «V1» на листе объекта LINE1 — это его V1, а не безымянное
    # устройство: владельцы разбираются раньше
    lua = {"devices": [{"name": "V1", "descr": "Общая обвязка"},
                       {"name": "M1V1", "descr": "Приём"}]}
    result = {(m.tech_object, m.pdf_name) for m in
              match_devices(lua, ROWS, [label("V1", 500.0, 2050.8)])}

    assert ("M1", "V1") in result, "подпись внутри контура не досталась объекту"
    assert ("", "V1") not in result, "безымянное устройство перехватило чужую подпись"


def test_bare_name_takes_only_unique_labels():
    # То же ограничение, что и у привязки по штампу: одно устройство
    # не должно получить четыре привязки в разных местах листа
    lua = {"devices": [{"name": "V1", "descr": "Общая обвязка"}]}
    texts = [label("V1", 374.7, 220.3), label("V1", 374.7, 379.1)]
    assert match_devices(lua, [], texts) == []


def test_bare_name_ignores_labels_inside_named_contours():
    # Внутри контура у устройства есть владелец, даже если тот его не ждал
    lua = {"devices": [{"name": "V5", "descr": "Общая обвязка"}]}
    assert match_devices(lua, ROWS, [label("V5", 500.0, 2050.8)]) == []


def test_flow_switch_type_is_parsed():
    # FS (реле потока) не было в списке типов: три устройства проекта MCA1
    # не разбирались вовсе
    lua = {"devices": [{"name": "LINE1FS1", "descr": "Наличие потока"}]}
    result = match_devices(lua, [], [label("FS1", 500.0, 400.0)], "LINE1")

    assert len(result) == 1, "устройство с типом FS не сопоставилось"
    assert result[0].device_type == "FS", f"тип разобран как {result[0].device_type!r}"


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
