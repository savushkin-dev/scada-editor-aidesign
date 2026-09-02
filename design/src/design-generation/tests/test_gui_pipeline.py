# tests/test_gui_pipeline.py
# Проверка пути, по которому идёт приложение: фоновые потоки и генератор SVG
# на svgwrite. Все проверки конвейера работали с готовым SVG и этот путь
# не трогали — в нём подряд жили три поломки:
#   * DeviceMatchingThread не имел page_number, хотя обращался к нему;
#   * заголовок SVG собирался до создания DeviceLabeler;
#   * svgwrite отвергал data-device-name, и разметка теряла половину линий.
#
# Запуск из папки CONTUR:
#     python tests/test_gui_pipeline.py
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from data_models import DeviceBox

TEST_PDF = config.INPUT_DIR / "test" / "BN1-Растворение-3.pdf"


def _app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_threads_accept_page_number():
    # Потоки обязаны знать страницу: без неё на многостраничном файле
    # в обработку попадают данные со всех страниц сразу
    from workers import DeviceMatchingThread, GeometryExtractionThread, YOLOMarkingThread
    _app()

    matching = DeviceMatchingThread("lua.json", "file.pdf", "geom.xml", 3)
    assert matching.page_number == 3

    geometry = GeometryExtractionThread("file.pdf", 2)
    assert geometry.page_number == 2

    markup = YOLOMarkingThread("file.pdf", 1)
    assert markup.page_number == 1


def test_matching_thread_default_page():
    from workers import DeviceMatchingThread
    _app()
    assert DeviceMatchingThread("lua.json", "file.pdf", "geom.xml").page_number == 0


def test_gui_markup_generates_complete_svg():
    # Генератор на svgwrite должен отрисовать всё и проставить атрибуты
    if not TEST_PDF.exists():
        print(f"  ПРОПУСК test_gui_markup_generates_complete_svg: нет {TEST_PDF}")
        return

    import fitz
    from workers import YOLOMarkingThread
    _app()

    with fitz.open(TEST_PDF) as doc:
        page = doc[0]
        primitives = sum(len(p.get("items", [])) for p in page.get_drawings())
        width, height = page.rect.width, page.rect.height

    # Рамки задаём вручную — модель для этой проверки не нужна
    boxes = [DeviceBox(width * 0.3, height * 0.3, width * 0.35, height * 0.35, "valve", 0.9),
             DeviceBox(width * 0.5, height * 0.5, width * 0.55, height * 0.55, "sensor", 0.8)]

    thread = YOLOMarkingThread(str(TEST_PDF), 0,
                               matched_devices=[("TANK1V1", width * 0.32, height * 0.32)])
    svg_path = thread._create_svg_with_markup(str(TEST_PDF), boxes)

    root = ET.parse(svg_path).getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    drawn = (len(root.findall(".//svg:line", ns)) + len(root.findall(".//svg:path", ns))
             + len(root.findall(".//svg:rect", ns)))

    # Белый фон добавляет один rect, поэтому сравниваем с запасом
    assert drawn >= primitives, f"отрисовано {drawn} из {primitives} примитивов"
    assert root.get("data-device-count") == "2"
    assert root.get("data-device-named") is not None, "нет счётчика подписанных рамок"
    assert root.get("data-device-size") is not None

    os.unlink(svg_path)


def test_matched_xml_serializes_numeric_fields():
    # subtype и dtype приходят из Lua числами: ElementTree падает на них
    # при записи файла («cannot serialize 13 (type int)»)
    import tempfile
    from data_models import DeviceMatch
    from device_matcher import generate_output_xml

    match = DeviceMatch(lua_name="TANK1V1", pdf_name="V1", tech_object="TANK1",
                        coordinates=(10.0, 20.0), confidence=1.0,
                        device_type="V", subtype=13, dtype=0)

    out = Path(tempfile.mkdtemp()) / "matched.xml"
    generate_output_xml([match], [], [], output_path=str(out))

    device = ET.parse(out).getroot().find(".//Device")
    assert device.get("subtype") == "13"
    assert device.get("dtype") == "0"


def test_png_size_matches_real_render():
    # Координаты рамок переводятся из пикселей в точки PDF делением на размер
    # растра. Раньше ради этого размера страница рендерилась в PNG второй раз
    # (3.1 с на сжатие картинки 14034x9934), теперь он считается из
    # прямоугольника страницы. Ошибка здесь сдвинет всю разметку.
    if not TEST_PDF.exists():
        print(f"  ПРОПУСК test_png_size_matches_real_render: нет {TEST_PDF}")
        return

    import fitz
    from workers import YOLOMarkingThread
    _app()

    with fitz.open(TEST_PDF) as doc:
        page = doc[0]
        for profile in ("fast", "balanced", "accurate"):
            thread = YOLOMarkingThread(str(TEST_PDF), 0, profile)
            zoom = thread.DPI / 72
            rendered = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            assert thread._png_size(page) == (rendered.width, rendered.height), \
                f"размер растра разошёлся с рендером, профиль {profile}"


def test_model_is_not_imported_at_startup():
    # ultralytics тянет torch — 1.9 с из 2.65 с запуска. Импорт в шапке
    # pdf_processor.py удлинял старт втрое даже когда разметку не запускали.
    # Проверка запускается отдельным процессом: в текущем torch мог загрузиться
    # раньше, из другой проверки
    import subprocess
    code = ("import sys; import xml_viewer; "
            "print('torch' in sys.modules or 'ultralytics' in sys.modules)")
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, env=env,
                         cwd=str(Path(__file__).resolve().parent.parent))
    assert out.stdout.strip().endswith("False"), \
        f"модель загружается при старте приложения: {out.stdout.strip()}"


def test_middle_button_name_exists():
    # В PySide6 средняя кнопка называется MiddleButton; обращение к MidButton
    # бросало AttributeError на каждое отпускание кнопки мыши
    from PySide6.QtCore import Qt
    assert hasattr(Qt.MouseButton, "MiddleButton")
    import widgets
    source = Path(widgets.__file__).read_text(encoding="utf-8")
    assert "MouseButton.MidButton" not in source


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
