from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET

from contur.core import config
from contur.core.data_models import DeviceMatch, Contour
from contur.pdf.svg_geometry import (
    JunctionPoint, LineSegment, Pipeline,
    build_pipelines, detect_coordinate_system, extract_line_segments,
    find_junction_points, get_svg_dimensions, resolve_device_names, tolerance_scale,
)


class PostgresExporter:
    """Экспортёр данных в PostgreSQL.

    Разбор геометрии SVG вынесен в модуль svg_geometry — он общий
    с экспортом в XML (xml_export.py).
    """

    # Параметры подключения. Здесь лежала своя копия с зашитым паролем
    # 'postgres', и она давно разошлась с config.DB_CONFIG, где пароль пуст.
    # Источник правды один — config, там же переменные окружения CONTUR_DB_*.
    DEFAULT_DB_CONFIG = config.DB_CONFIG

    # Режимы повторной выгрузки.
    #
    # Схема зафиксирована потребителем, и колонки листа в ней нет: база
    # не может отличить строку, пришедшую с первого листа, от строки
    # с четвёртого. Контуры и устройства это переживают — они защищены
    # ON CONFLICT по имени, а имена в проекте контроллера уникальны.
    # Связи и точки сопряжения не защищены ничем и при повторной выгрузке
    # ложатся вторым комплектом.
    #
    # Догадаться за пользователя тут нельзя, поэтому выбор явный:
    #   append  — дописать (второй лист того же проекта);
    #   replace — заменить связи и точки целиком (перевыгрузка).
    # По умолчанию append: он не может уничтожить чужие данные.
    MODE_APPEND = "append"
    MODE_REPLACE = "replace"
    MODES = (MODE_APPEND, MODE_REPLACE)

    # Таблицы, у которых нет защиты от повторной вставки
    UNGUARDED_TABLES = ("connections", "junction_points")

    # Сколько строк уходит одним запросом. Замер на контрольном листе
    # с базой в Docker: вставка по строке — 3.5 с из 3.6 с всей выгрузки,
    # причём 2.94 с приходится на 4713 точек сопряжения. Одна строка стоит
    # 0.62 мс, и это чистое обращение к серверу: 5714 обращений на лист.
    # Время прямо пропорционально задержке до базы, поэтому на сетевой
    # оно росло бы кратно.
    #
    # Контуры и устройства оставлены построчными: они возвращают
    # идентификаторы через RETURNING, а стоят 0.02 и 0.14 с — усложнять
    # ради этого нечего.
    PAGE_SIZE = 1000

    def __init__(self, db_config: Dict[str, Any] | None = None, use_percent_coords: bool = True,
                 pdf_size: Optional[Tuple[float, float]] = None):
        """Инициализация экспортёра.

        pdf_size — размер страницы исходного PDF в пунктах: если задан,
        масштаб SVG вычисляется точно, иначе подбирается эвристикой.
        """
        self.db_config = db_config or self.DEFAULT_DB_CONFIG.copy()
        self.use_percent_coords = use_percent_coords
        self.pdf_size = pdf_size
        self.conn = None
        self.cursor = None

        # Для хранения извлечённых из SVG данных
        self.line_segments: List[LineSegment] = []
        self.junction_points: List[JunctionPoint] = []
        self.pipelines: List[Pipeline] = []

        # Кэш для сопоставления имён с ID в БД
        self._contour_id_cache: Dict[str, int] = {}
        self._device_id_cache: Dict[str, int] = {}

        # Итоги последней выгрузки: сколько записано и сколько уже лежало
        # в незащищённых таблицах до неё. Окно показывает это пользователю —
        # раньше оно сообщало только «данные выгружены».
        self.stats: Dict[str, int] = {}

        # Параметры SVG
        self.svg_width: float = None
        self.svg_height: float = None
        self._svg_coord_system: str = None
        self._detected_scale: float = 1.0

    def connect(self) -> bool:
        """Устанавливает соединение с PostgreSQL"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print(f"✅ Подключено к БД {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Создаёт 4 таблицы, если они не существуют"""
        # Таблица 1: контуры
        create_contours = """
        CREATE TABLE IF NOT EXISTS contours (
            id                  BIGSERIAL PRIMARY KEY,
            name                VARCHAR(255) NOT NULL UNIQUE,
            tech_object_name    VARCHAR(255) NOT NULL,
            bounds_min_x        VARCHAR(50) NOT NULL,
            bounds_min_y        VARCHAR(50) NOT NULL,
            bounds_max_x        VARCHAR(50) NOT NULL,
            bounds_max_y        VARCHAR(50) NOT NULL,
            center_x            VARCHAR(50) NOT NULL,
            center_y            VARCHAR(50) NOT NULL,
            width               VARCHAR(50),
            height              VARCHAR(50),
            created_at          TIMESTAMP DEFAULT NOW()
        );
        """

        # Таблица 2: устройства
        create_devices = """
        CREATE TABLE IF NOT EXISTS devices (
            id                  BIGSERIAL PRIMARY KEY,
            contour_id          BIGINT REFERENCES contours(id) ON DELETE CASCADE,
            lua_name            VARCHAR(255) NOT NULL UNIQUE,
            pdf_name            VARCHAR(255),
            device_type         VARCHAR(50),
            article             VARCHAR(255),
            description         TEXT,
            coord_x             VARCHAR(50) NOT NULL,
            coord_y             VARCHAR(50) NOT NULL,
            confidence          FLOAT DEFAULT 1.0,
            operation_state     VARCHAR(50),
            operation_step      VARCHAR(255),
            created_at          TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_devices_contour ON devices(contour_id);
        """

        # Таблица 3: связи (трубопроводы)
        create_connections = """
        CREATE TABLE IF NOT EXISTS connections (
            id                  BIGSERIAL PRIMARY KEY,
            name                VARCHAR(255),
            total_length        FLOAT DEFAULT 0.0,
            segment_count       INTEGER DEFAULT 0,
            connected_devices   TEXT,
            created_at          TIMESTAMP DEFAULT NOW()
        );
        """

        # Таблица 4: точки сопряжения
        create_junction_points = """
        CREATE TABLE IF NOT EXISTS junction_points (
            id                  BIGSERIAL PRIMARY KEY,
            x                   VARCHAR(50) NOT NULL,
            y                   VARCHAR(50) NOT NULL,
            red_line_id         INTEGER,
            blue_line_id        INTEGER,
            red_device_name     VARCHAR(255),
            confidence          FLOAT DEFAULT 1.0,
            contour_id          BIGINT REFERENCES contours(id) ON DELETE SET NULL,
            created_at          TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_junction_points_coords ON junction_points(x, y);
        """

        try:
            self.cursor.execute(create_contours)
            self.cursor.execute(create_devices)
            self.cursor.execute(create_connections)
            self.cursor.execute(create_junction_points)
            self.conn.commit()
            print("✅ Таблицы созданы")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания таблиц: {e}")
            self.conn.rollback()
            return False

    def drop_tables(self):
        """Удаляет таблицы (для отладки)"""
        drop_sql = """
        DROP TABLE IF EXISTS junction_points CASCADE;
        DROP TABLE IF EXISTS connections CASCADE;
        DROP TABLE IF EXISTS devices CASCADE;
        DROP TABLE IF EXISTS contours CASCADE;
        """
        try:
            self.cursor.execute(drop_sql)
            self.conn.commit()
            print("🗑️ Таблицы удалены")
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False

    # ========== Повторная выгрузка ==========

    def count_existing(self) -> Dict[str, int]:
        """Сколько строк уже лежит в таблицах без защиты от повтора.

        Нужно и до выгрузки — чтобы окно могло спросить, дописывать или
        заменять, — и во время неё, чтобы итог был честным.
        """
        counts: Dict[str, int] = {}
        for table in self.UNGUARDED_TABLES:
            # Имя таблицы берётся из константы класса, а не извне
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row = self.cursor.fetchone()
            counts[table] = int(row[0]) if row else 0
        return counts

    def _clear_unguarded(self) -> None:
        # Заменить можно только целиком: отличить строки одного листа
        # от строк другого схема не позволяет
        for table in self.UNGUARDED_TABLES:
            self.cursor.execute(f"DELETE FROM {table}")

    @staticmethod
    def _device_contours(matches: List[DeviceMatch],
                         contour_ids: Dict[str, int]) -> Dict[str, int]:
        """Полное имя устройства -> id его контура.

        Точка сопряжения знает полное имя устройства (его подставляет
        resolve_device_names), устройство знает свой техобъект, техобъект —
        это контур. Связь точная, без геометрических догадок.
        """
        return {match.lua_name: contour_ids[match.tech_object]
                for match in matches if match.tech_object in contour_ids}

    # ========== Форматирование координат ==========

    def _to_percent(self, value: float, dimension: float) -> str:
        """Преобразует абсолютное значение в проценты"""
        if dimension <= 0:
            return f"{value:.3f}"
        return f"{(value / dimension * 100):.3f}%"

    def _get_coord_value(self, value: float, is_x: bool = True) -> str:
        """Возвращает координату в нужном формате (проценты или абсолютные).

        Значение уже приведено к PDF пунктам, поэтому дополнительная
        нормализация не нужна.
        """
        if self.use_percent_coords and self.svg_width and self.svg_height:
            dimension = self.svg_width if is_x else self.svg_height
            return self._to_percent(value, dimension)
        return f"{value:.3f}"

    # ========== Запись в БД ==========

    def _insert_contours(self, contours: List[Contour]) -> Dict[str, int]:
        """Вставляет контуры, возвращает словарь имя -> id"""
        if not contours:
            return {}

        insert_sql = """
        INSERT INTO contours (name, tech_object_name, bounds_min_x, bounds_min_y, bounds_max_x, bounds_max_y, center_x, center_y, width, height)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            tech_object_name = EXCLUDED.tech_object_name,
            bounds_min_x = EXCLUDED.bounds_min_x,
            bounds_min_y = EXCLUDED.bounds_min_y,
            bounds_max_x = EXCLUDED.bounds_max_x,
            bounds_max_y = EXCLUDED.bounds_max_y,
            center_x = EXCLUDED.center_x,
            center_y = EXCLUDED.center_y,
            width = EXCLUDED.width,
            height = EXCLUDED.height
        RETURNING id, name;
        """

        result = {}
        for contour in contours:
            minx, miny, maxx, maxy = contour.bounds

            minx_str = self._get_coord_value(minx, True)
            miny_str = self._get_coord_value(miny, False)
            maxx_str = self._get_coord_value(maxx, True)
            maxy_str = self._get_coord_value(maxy, False)
            center_x_str = self._get_coord_value(contour.center[0], True)
            center_y_str = self._get_coord_value(contour.center[1], False)
            width_str = self._get_coord_value(maxx - minx, True)
            height_str = self._get_coord_value(maxy - miny, False)

            self.cursor.execute(insert_sql, (
                contour.name, contour.tech_object,
                minx_str, miny_str, maxx_str, maxy_str,
                center_x_str, center_y_str,
                width_str, height_str
            ))
            row = self.cursor.fetchone()
            if row:
                result[contour.name] = row[0]

        # Фиксации здесь нет: вся выгрузка — одна транзакция. Раньше каждая
        # таблица фиксировалась отдельно, и сбой на третьем шаге оставлял
        # в базе контуры и устройства без связей, а rollback в обработчике
        # к тому моменту откатывать было нечего.
        print(f"✅ Вставлено контуров: {len(result)}")
        return result

    def _insert_devices(self, matches: List[DeviceMatch], contour_ids: Dict[str, int]) -> Dict[str, int]:
        """Вставляет устройства, возвращает словарь lua_name -> id"""
        if not matches:
            return {}

        insert_sql = """
        INSERT INTO devices (contour_id, lua_name, pdf_name, device_type, article, description, coord_x, coord_y, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (lua_name) DO UPDATE SET
            pdf_name = EXCLUDED.pdf_name,
            device_type = EXCLUDED.device_type,
            coord_x = EXCLUDED.coord_x,
            coord_y = EXCLUDED.coord_y
        RETURNING id, lua_name;
        """

        result = {}
        for match in matches:
            contour_id = contour_ids.get(match.tech_object)
            if contour_id is None:
                continue

            coord_x_str = self._get_coord_value(match.coordinates[0], True)
            coord_y_str = self._get_coord_value(match.coordinates[1], False)

            self.cursor.execute(insert_sql, (
                contour_id, match.lua_name, match.pdf_name,
                match.device_type, match.article, match.descr,
                coord_x_str, coord_y_str, match.confidence
            ))
            row = self.cursor.fetchone()
            if row:
                result[match.lua_name] = row[0]

        print(f"✅ Вставлено устройств: {len(result)}")
        return result

    def _insert_connections(self, pipelines: List[Pipeline]) -> int:
        """Вставляет связи (трубопроводы) пачками."""
        if not pipelines:
            return 0

        # RETURNING здесь был и не читался: идентификаторы связей никому
        # не нужны, а пачке он мешает
        insert_sql = """
        INSERT INTO connections (name, total_length, segment_count, connected_devices)
        VALUES %s
        """

        rows = [(pipe.name, pipe.total_length, pipe.segment_count,
                 ",".join(pipe.connected_devices) if pipe.connected_devices else "")
                for pipe in pipelines]
        execute_values(self.cursor, insert_sql, rows, page_size=self.PAGE_SIZE)

        print(f"✅ Вставлено связей: {len(pipelines)}")
        return len(pipelines)

    def _insert_junction_points(self, junction_points: List[JunctionPoint],
                                device_contours: Dict[str, int]) -> int:
        """Вставляет точки сопряжения.

        Колонка contour_id есть в схеме с самого начала, а заполнялась
        никогда: метод принимал словарь контуров и не использовал его,
        и связь точки с контуром оставалась пустой.
        """
        if not junction_points:
            return 0

        insert_sql = """
        INSERT INTO junction_points (x, y, red_line_id, blue_line_id, red_device_name, confidence, contour_id)
        VALUES %s
        """

        rows, linked = [], 0
        for jp in junction_points:
            contour_id = device_contours.get(jp.red_device_name)
            linked += contour_id is not None
            rows.append((self._get_coord_value(jp.x, True),
                         self._get_coord_value(jp.y, False),
                         jp.red_line_id, jp.blue_line_id,
                         jp.red_device_name, jp.confidence, contour_id))

        execute_values(self.cursor, insert_sql, rows, page_size=self.PAGE_SIZE)

        print(f"✅ Вставлено точек сопряжения: {len(junction_points)} "
              f"(из них с привязкой к контуру: {linked})")
        return len(junction_points)

    # ========== Главный метод экспорта ==========

    def export(self, svg_path: str, matches: List[DeviceMatch],
               contours: List[Contour], auto_create_tables: bool = True,
               mode: str = MODE_APPEND) -> bool:
        """
        Экспорт данных в PostgreSQL.

        Параметры:
        - svg_path: путь к размеченному SVG
        - matches: список сопоставленных устройств
        - contours: список распознанных контуров
        - auto_create_tables: создавать таблицы автоматически
        - mode: 'append' — дописать к тому, что уже есть;
                'replace' — сначала очистить связи и точки сопряжения

        Возвращает:
        - True при успехе, False при ошибке
        """
        if mode not in self.MODES:
            raise ValueError(f"неизвестный режим выгрузки: {mode!r}; "
                             f"допустимы {self.MODES}")

        if not self.connect():
            return False

        try:
            if auto_create_tables:
                self.create_tables()

            print("\n📊 Начало экспорта в PostgreSQL...")

            # 1. Разбираем SVG и приводим координаты к PDF пунктам
            svg_root = ET.parse(svg_path).getroot()

            self._svg_coord_system, self._detected_scale = detect_coordinate_system(
                svg_root, self.pdf_size)
            print(f"🔍 Детектирована система координат SVG: {self._svg_coord_system}")

            self.svg_width, self.svg_height = get_svg_dimensions(svg_root, self._detected_scale)
            print(f"📐 Нормализованные размеры SVG: {self.svg_width} x {self.svg_height}")

            if self.use_percent_coords and not (self.svg_width and self.svg_height):
                print("⚠️ Размеры холста неизвестны — запись в абсолютных координатах")
                self.use_percent_coords = False

            self.line_segments = extract_line_segments(
                svg_root, self._detected_scale, (self.svg_width, self.svg_height))

            # 2. Находим точки сопряжения и разрешаем короткие подписи
            #    в полные имена устройств из Lua
            geometry_scale = tolerance_scale(svg_root)
            self.junction_points = find_junction_points(self.line_segments,
                                                        scale=geometry_scale)
            resolve_device_names(
                self.junction_points,
                [(m.lua_name, m.pdf_name, m.coordinates[0], m.coordinates[1]) for m in matches],
                scale=geometry_scale)

            # 3. Строим трубопроводы из синих сегментов
            blue_segments = [seg for seg in self.line_segments if seg.color == "blue"]
            self.pipelines = build_pipelines(blue_segments, self.junction_points,
                                             scale=geometry_scale)

            # 4. Смотрим, что уже лежит в незащищённых таблицах, и при
            #    замене очищаем их — в той же транзакции, что и вставка
            existing = self.count_existing()
            if mode == self.MODE_REPLACE:
                self._clear_unguarded()
                print(f"🗑️ Заменяется прежнее: связей {existing['connections']}, "
                      f"точек сопряжения {existing['junction_points']}")
            elif any(existing.values()):
                print(f"➕ Дописывается к имеющемуся: связей "
                      f"{existing['connections']}, точек сопряжения "
                      f"{existing['junction_points']}")

            # 5. Вставляем контуры
            contour_ids = self._insert_contours(contours)

            # 6. Вставляем устройства
            device_ids = self._insert_devices(matches, contour_ids)

            # 7. Вставляем связи (трубопроводы)
            conn_count = self._insert_connections(self.pipelines)

            # 8. Вставляем точки сопряжения
            jp_count = self._insert_junction_points(
                self.junction_points, self._device_contours(matches, contour_ids))

            # Единственная фиксация данных: до неё в базе нет ничего
            # из этой выгрузки, после — всё
            self.conn.commit()

            self.stats = {
                "контуров": len(contour_ids),
                "устройств": len(device_ids),
                "связей": conn_count,
                "точек сопряжения": jp_count,
                "было связей": existing["connections"],
                "было точек": existing["junction_points"],
            }

            print("\n" + "=" * 50)
            print("📊 ИТОГИ ЭКСПОРТА:")
            print(f"   - Контуров: {len(contour_ids)}")
            print(f"   - Устройств: {len(device_ids)}")
            print(f"   - Связей: {conn_count}")
            print(f"   - Точек сопряжения: {jp_count}")
            print("=" * 50)

            return True

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
        finally:
            self.disconnect()


# ========== Упрощённая функция экспорта ==========

def export_to_postgresql(svg_path: str, matches: List[DeviceMatch],
                         contours: List[Contour],
                         db_config: Dict[str, Any] | None = None,
                         auto_create_tables: bool = True,
                         use_percent_coords: bool = True,
                         pdf_size: Optional[Tuple[float, float]] = None,
                         mode: str = PostgresExporter.MODE_APPEND) -> bool:
    """
    Упрощённая функция экспорта в PostgreSQL.
    Аналог export_current_visualization из xml_export.py

    Пример использования:
        from postgresql_export import export_to_postgresql
        success = export_to_postgresql(
            svg_path="output/marked_up.svg",
            matches=device_matches,
            contours=contour_list,
            db_config={'host': 'localhost', 'database': 'hmi_design', 'user': 'postgres', 'password': '123'}
        )
    """
    exporter = PostgresExporter(db_config, use_percent_coords=use_percent_coords,
                                pdf_size=pdf_size)
    return exporter.export(svg_path, matches, contours, auto_create_tables, mode)


# ========== Точка входа для тестирования ==========
if __name__ == "__main__":
    # Тестовый запуск
    from contur.core.data_models import DeviceMatch, Contour

    test_contours = [
        Contour(name="TestContour", tech_object="TechObj1",
                bounds=(100, 100, 500, 400), center=(300, 250))
    ]

    test_matches = [
        DeviceMatch(lua_name="V-101", pdf_name="Задвижка 101",
                    tech_object="TechObj1", coordinates=(200, 200),
                    confidence=0.95, device_type="valve")
    ]

    success = export_to_postgresql(
        svg_path="path/to/svg.svg",
        matches=test_matches,
        contours=test_contours
    )

    if success:
        print("✅ Тестовый экспорт успешен")
    else:
        print("❌ Ошибка тестового экспорта")
