# tests/test_postgres_export.py
# Выгрузка в PostgreSQL — 464 строки, до сих пор без единой проверки.
#
# Живой сервер здесь не нужен и вреден: проверять надо не то, что база
# приняла запись, а то, ЧТО именно ей отправлено и в каком порядке
# зафиксировано. Соединение подменяется заглушкой, которая записывает
# каждый запрос вместе с параметрами.
#
# Что закрывается проверками:
#   - параметризация запросов (сделано верно, и должно таким остаться);
#   - выгрузка как одна транзакция, а не пять отдельных фиксаций;
#   - повторная выгрузка того же листа не должна удваивать данные;
#   - перевод координат в проценты от холста;
#   - соединение закрывается при любом исходе.
#
# Запуск из папки CONTUR:
#     python tests/test_postgres_export.py
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import postgreSQL_export
from data_models import Contour, DeviceMatch

# Холст совпадает с размером «страницы PDF»: тогда масштаб равен единице
# и координаты в процентах считаются от этих же чисел
CANVAS = (1000.0, 800.0)

# Геометрия держится в стороне от краёв: extract_line_segments отбрасывает
# всё, что ближе 3% к границе, принимая это за рамку чертежа
SVG = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800"
     viewBox="0 0 1000 800">
  <rect x="200" y="200" width="40" height="40" stroke="red" fill="none"
        stroke-width="1.0" data-device-name="LA_TANK1V101"
        data-device-class="valve" data-device-conf="0.91"/>
  <rect x="600" y="500" width="40" height="40" stroke="red" fill="none"
        stroke-width="1.0" data-device-name="LA_TANK1V102"
        data-device-class="valve" data-device-conf="0.88"/>
  <line x1="240" y1="220" x2="600" y2="220" stroke="blue" stroke-width="1.0"/>
  <line x1="600" y1="220" x2="600" y2="500" stroke="blue" stroke-width="1.0"/>
  <text x="210" y="195">V101</text>
</svg>
"""

MATCHES = [
    DeviceMatch(lua_name="LA_TANK1V101", pdf_name="V101", tech_object="LA_TANK1",
                coordinates=(220.0, 220.0), confidence=0.91, device_type="V",
                article="ART-1", descr="Клапан подачи"),
    DeviceMatch(lua_name="LA_TANK1V102", pdf_name="V102", tech_object="LA_TANK1",
                coordinates=(620.0, 520.0), confidence=0.88, device_type="V"),
]

CONTOURS = [
    Contour(name="LA_TANK1", bounds=(150.0, 150.0, 700.0, 600.0),
            center=(425.0, 375.0), tech_object="LA_TANK1"),
]


# ------------------------------------------------------------ заглушка базы

class FakeCursor:
    """Курсор, который ничего не выполняет, но всё запоминает."""

    def __init__(self, log, fail_on=None, connection=None):
        self.log = log
        self.fail_on = fail_on or ""
        # execute_values спрашивает у курсора соединение, чтобы узнать
        # кодировку клиента
        self.connection = connection
        self._last_sql = ""
        self._next_id = 100

    def execute(self, sql, params=None):
        # Пакетная вставка отдаёт готовый запрос байтами
        if isinstance(sql, bytes):
            sql = sql.decode("utf-8", errors="replace")
        compact = " ".join(sql.split())
        if self.fail_on and self.fail_on in compact:
            raise RuntimeError(f"база отказала: {self.fail_on}")
        self.log.append((compact, params))
        self._last_sql = compact

    def mogrify(self, template, args=None):
        """Экранирование значений драйвером.

        Нужно пакетной вставке: execute_values собирает один запрос из строк,
        подготовленных этим методом. Настоящий psycopg2 экранирует здесь
        по правилам PostgreSQL — подделка лишь повторяет форму.
        """
        rendered = ", ".join("NULL" if value is None else repr(value)
                             for value in (args or ()))
        return f"({rendered})".encode()

    def fetchone(self):
        if "COUNT(" in self._last_sql.upper():
            return (0,)
        if "RETURNING" not in self._last_sql:
            return None
        self._next_id += 1
        return (self._next_id, "row")

    def close(self):
        self.log.append(("CURSOR CLOSE", None))


class FakeConnection:
    encoding = "UTF8"

    def __init__(self, log, fail_on=None):
        self.log = log
        self._cursor = FakeCursor(log, fail_on, connection=self)

    def cursor(self):
        return self._cursor

    def commit(self):
        self.log.append(("COMMIT", None))

    def rollback(self):
        self.log.append(("ROLLBACK", None))

    def close(self):
        self.log.append(("CONNECTION CLOSE", None))


def _run_export(svg_path, fail_on=None, mode=None, **kwargs):
    """Выполняет выгрузку с подменённым psycopg2, возвращает журнал запросов."""
    log = []
    fake = types.SimpleNamespace(connect=lambda **_: FakeConnection(log, fail_on))

    original = postgreSQL_export.psycopg2
    postgreSQL_export.psycopg2 = fake
    try:
        exporter = postgreSQL_export.PostgresExporter(
            db_config={"host": "localhost", "database": "test"},
            pdf_size=CANVAS, **kwargs)
        extra = {"mode": mode} if mode else {}
        success = exporter.export(svg_path, MATCHES, CONTOURS, **extra)
    finally:
        postgreSQL_export.psycopg2 = original

    return success, log


def _svg_file(tmp_name="_postgres_test.svg"):
    import config
    config.ensure_output_dir()
    path = config.OUTPUT_DIR / tmp_name
    path.write_text(SVG, encoding="utf-8")
    return str(path)


def _inserts(log, table):
    return [(sql, params) for sql, params in log
            if sql.upper().startswith(f"INSERT INTO {table.upper()}")]


# ------------------------------------------------------------ проверки

def test_export_reaches_all_four_tables():
    # Опорная проверка: если она падает, остальные ничего не значат
    svg = _svg_file()
    try:
        success, log = _run_export(svg)
        assert success, "выгрузка вернула отказ на исправных данных"

        for table in ("contours", "devices", "connections", "junction_points"):
            assert _inserts(log, table), f"ни одной вставки в {table}"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_no_query_is_built_from_data():
    """Ни один запрос не собирается из данных руками.

    Раньше проверялось буквально: ни одно значение не должно появляться
    в тексте запроса. С пакетной вставкой это перестало быть правдой —
    execute_values собирает один запрос из строк, которые экранировал сам
    драйвер, и без этого 4713 точек сопряжения уходили бы по одной.

    Защита от инъекции при этом никуда не делась, просто держится на другом:
    экранирует psycopg2, а не сам экспортёр. Проверяется теперь именно это.
    """
    import ast

    source = (Path(__file__).resolve().parent.parent /
              "postgreSQL_export.py").read_text(encoding="utf-8")

    suspicious = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not node.args:
            continue

        called = node.func
        name = called.attr if isinstance(called, ast.Attribute) else getattr(
            called, "id", "")
        if name not in ("execute", "execute_values"):
            continue

        # У execute_values первый довод — курсор, запрос вторым
        sql = node.args[1] if name == "execute_values" else node.args[0]

        if isinstance(sql, ast.BinOp):
            suspicious.append((node.lineno, "запрос склеен из кусков"))
        elif isinstance(sql, ast.JoinedStr):
            # f-строка допустима только для имени таблицы: они берутся
            # из константы класса, а не из данных
            for part in sql.values:
                if isinstance(part, ast.FormattedValue):
                    inserted = getattr(part.value, "id", None)
                    if inserted != "table":
                        suspicious.append((node.lineno,
                                           f"в запрос подставлено {inserted}"))

    assert not suspicious, f"запросы, собранные из данных: {suspicious}"


def test_values_go_to_the_driver_as_parameters():
    # Там, где параметры передаются отдельно, значения не должны
    # оказываться в тексте запроса
    external = ({m.lua_name for m in MATCHES} | {m.pdf_name for m in MATCHES} |
                {c.name for c in CONTOURS} | {"Клапан подачи", "ART-1"})

    svg = _svg_file()
    try:
        _, log = _run_export(svg)

        checked = 0
        for sql, params in log:
            if params is None:
                continue
            checked += 1
            for value in external:
                assert value not in sql, \
                    f"значение {value!r} вклеено в текст запроса: {sql[:90]}"

        assert checked, "не нашлось ни одного запроса с параметрами"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_data_is_written_in_one_transaction():
    # Сейчас commit стоит после каждой таблицы. Сбой на третьем шаге оставляет
    # базу с контурами и устройствами, но без связей, а rollback в обработчике
    # к этому моменту откатывать уже нечего.
    svg = _svg_file()
    try:
        _, log = _run_export(svg)

        operations = [sql for sql, _ in log]
        insert_positions = [i for i, sql in enumerate(operations)
                            if sql.upper().startswith("INSERT INTO")]
        assert insert_positions, "вставок нет вовсе"

        first, last = insert_positions[0], insert_positions[-1]
        commits_inside = [i for i, sql in enumerate(operations)
                          if sql == "COMMIT" and first < i < last]
        assert not commits_inside, (
            f"данные фиксируются по частям: {len(commits_inside)} промежуточных "
            "COMMIT между первой и последней вставкой")
    finally:
        Path(svg).unlink(missing_ok=True)


def test_failed_export_leaves_nothing_behind():
    # Отказ на вставке точек сопряжения не должен оставлять в базе
    # контуры и устройства от той же выгрузки
    svg = _svg_file()
    try:
        success, log = _run_export(svg, fail_on="INSERT INTO junction_points")
        assert not success, "выгрузка со сбоем отчиталась об успехе"

        operations = [sql for sql, _ in log]
        rollback_at = operations.index("ROLLBACK")
        first_insert = next(i for i, sql in enumerate(operations)
                            if sql.upper().startswith("INSERT INTO"))

        # Фиксация создания таблиц до всякой вставки законна — это DDL.
        # Недопустима фиксация данных между первой вставкой и сбоем.
        premature = [i for i, sql in enumerate(operations)
                     if sql == "COMMIT" and first_insert < i < rollback_at]
        assert not premature, \
            "часть данных зафиксирована до сбоя — в базе остался обрывок выгрузки"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_replace_mode_clears_previous_rows():
    # Контуры и устройства защищены ON CONFLICT по имени, а связи и точки
    # сопряжения — ничем: повторная выгрузка листа кладёт их вторым
    # комплектом. Колонки листа в схеме нет и добавить её нельзя, поэтому
    # «заменить» означает заменить целиком — и решает это человек.
    svg = _svg_file()
    try:
        _, log = _run_export(svg, mode="replace")
        operations = [sql.upper() for sql, _ in log]

        for table in ("connections", "junction_points"):
            assert any(sql.startswith(f"DELETE FROM {table.upper()}")
                       for sql in operations), \
                f"режим замены не очищает {table}"

        # Удаление обязано попасть в ту же транзакцию, что и вставка,
        # иначе сбой выгрузки оставит базу пустой
        delete_at = min(i for i, sql in enumerate(operations)
                        if sql.startswith("DELETE FROM"))
        commits_after = [i for i, sql in enumerate(operations)
                         if sql == "COMMIT" and i > delete_at]
        assert len(commits_after) == 1, \
            f"после очистки {len(commits_after)} фиксаций вместо одной"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_append_mode_counts_what_is_already_there():
    # Дополнение — законный режим: второй лист того же проекта. Но молчать
    # о том, что в базе уже лежат связи, нельзя — именно так и появляется
    # второй комплект, неотличимый от первого.
    svg = _svg_file()
    try:
        _, log = _run_export(svg, mode="append")
        operations = [sql.upper() for sql, _ in log]

        assert not any(sql.startswith("DELETE FROM") for sql in operations), \
            "режим дополнения удаляет чужие данные"

        for table in ("connections", "junction_points"):
            assert any(sql.startswith("SELECT COUNT(") and table.upper() in sql
                       for sql in operations), \
                f"перед вставкой не сосчитано, сколько строк уже есть в {table}"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_junction_points_keep_contour_link():
    # Колонка contour_id есть в схеме, а метод принимает contour_ids
    # и не использует их: связь точек с контуром всегда пустая
    svg = _svg_file()
    try:
        _, log = _run_export(svg)
        inserts = _inserts(log, "junction_points")
        assert inserts, "нет вставок в junction_points"

        sql = inserts[0][0].upper()
        assert "CONTOUR_ID" in sql, \
            "точки сопряжения пишутся без contour_id — колонка всегда NULL"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_coordinates_are_percent_of_canvas():
    # Потребитель ждёт проценты: устройство на 220 пт при холсте 800
    # по вертикали — это 27.500%
    svg = _svg_file()
    try:
        _, log = _run_export(svg)

        contour = _inserts(log, "contours")[0][1]
        assert contour[2] == "15.000%", f"minx контура: {contour[2]}"
        assert contour[3] == "18.750%", f"miny контура: {contour[3]}"

        device = _inserts(log, "devices")[0][1]
        assert device[6] == "22.000%", f"x устройства: {device[6]}"
        assert device[7] == "27.500%", f"y устройства: {device[7]}"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_absolute_coordinates_when_asked():
    svg = _svg_file()
    try:
        _, log = _run_export(svg, use_percent_coords=False)
        device = _inserts(log, "devices")[0][1]
        assert device[6] == "220.000", f"x устройства: {device[6]}"
        assert "%" not in device[7], f"y устройства: {device[7]}"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_connection_is_closed_on_every_path():
    svg = _svg_file()
    try:
        for fail_on in (None, "INSERT INTO devices"):
            _, log = _run_export(svg, fail_on=fail_on)
            operations = [sql for sql, _ in log]
            assert "CONNECTION CLOSE" in operations, \
                f"соединение осталось открытым (сбой на {fail_on})"
    finally:
        Path(svg).unlink(missing_ok=True)


def test_failed_connection_reports_without_raising():
    # Недоступная база — обычное дело, а не повод для трассировки в окне
    def refuse(**_):
        raise OSError("сервер не отвечает")

    original = postgreSQL_export.psycopg2
    postgreSQL_export.psycopg2 = types.SimpleNamespace(connect=refuse)
    try:
        exporter = postgreSQL_export.PostgresExporter(db_config={"host": "нет"})
        assert exporter.export("нет.svg", MATCHES, CONTOURS) is False, \
            "недоступная база должна давать отказ, а не исключение"
    finally:
        postgreSQL_export.psycopg2 = original


def test_settings_have_single_source():
    # config.DB_CONFIG держит пустой пароль, а DEFAULT_DB_CONFIG в экспортёре —
    # зашитый 'postgres'. Два источника правды расходятся молча.
    import config

    default = postgreSQL_export.PostgresExporter.DEFAULT_DB_CONFIG
    assert default.get("password", "") == config.DB_CONFIG["password"], (
        "настройки базы заданы в двух местах и расходятся: "
        f"экспортёр {default.get('password')!r}, config "
        f"{config.DB_CONFIG['password']!r}")


def test_big_tables_go_in_batches():
    # Замер с базой в Docker: вставка по строке — 3.5 с из 3.6 с всей
    # выгрузки, и 2.94 с из них на 4713 точек сопряжения. Время прямо
    # пропорционально задержке до сервера, поэтому на сетевой базе
    # построчная вставка растянулась бы кратно.
    svg = _svg_file()
    try:
        _, log = _run_export(svg)

        for table in ("connections", "junction_points"):
            inserts = _inserts(log, table)
            assert len(inserts) <= 2, \
                f"{table}: {len(inserts)} запросов вместо пачки"

        # Контуры и устройства остаются построчными: они возвращают
        # идентификаторы и стоят сотые доли секунды
        assert _inserts(log, "contours"), "контуры не вставляются"
    finally:
        Path(svg).unlink(missing_ok=True)


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
