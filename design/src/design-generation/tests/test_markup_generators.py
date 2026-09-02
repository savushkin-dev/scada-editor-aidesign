# tests/test_markup_generators.py
# Два генератора размеченного SVG должны давать одно и то же.
#
# Разметку собирают два независимых куска кода: workers._create_svg_with_markup
# для окна (через svgwrite) и pdf_processor._create_svg_content для консоли
# (сборкой строк). Одну и ту же ошибку в них уже дважды исправляли порознь,
# а сверить их между собой было нечем.
#
# Сверка нашла настоящую поломку в консольном пути: device_marks создавался
# только внутри «если это устройство», а использовался всегда. Первые элементы
# листа падали на UnboundLocalError, перехват их молча выбрасывал — 59 штук
# из 1108, — а дальше синие трубы получали метки последнего встреченного
# устройства, то есть чужое имя и класс.
#
# Запуск из папки CONTUR:
#     python tests/test_markup_generators.py
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import config

# Небольшой лист: детекция около десяти секунд вместо полутора минут
TEST_PDF = config.INPUT_DIR / "test" / "BN1-Растворение-3.pdf"
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


def _app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _describe(path: str) -> dict:
    # Показатели считаются тем же разбором, каким пользуется экспорт
    from contur.pdf import svg_geometry as g
    from contur.export.xml_export import get_pdf_page_size

    root = ET.parse(path).getroot()
    _, scale = g.detect_coordinate_system(root, get_pdf_page_size(str(TEST_PDF), 0))
    dimensions = g.get_svg_dimensions(root, scale)
    segments = g.extract_line_segments(root, scale, dimensions, verbose=False)
    tolerance = g.tolerance_scale(root)
    junctions = g.find_junction_points(segments, verbose=False, scale=tolerance)
    pipelines = g.build_pipelines([s for s in segments if s.color == "blue"],
                                  junctions, verbose=False, scale=tolerance)

    return {
        "линий": len(root.findall(".//svg:line", SVG_NS)),
        "кривых": len(root.findall(".//svg:path", SVG_NS)),
        "текстов": len(root.findall(".//svg:text", SVG_NS)),
        "сегментов": len(segments),
        "красных": sum(1 for s in segments if s.color == "red"),
        "синих": sum(1 for s in segments if s.color == "blue"),
        "с именем": sum(1 for s in segments if s.device_name),
        "с классом": sum(1 for s in segments if s.device_class),
        "точек сопряжения": len(junctions),
        "трубопроводов": len(pipelines),
    }


def _both_markups():
    # Детекция выполняется один раз: сравнивать генераторы надо
    # на одинаковых рамках, иначе разница будет от модели, а не от кода
    import fitz

    from contur.pdf import markup_cache
    from contur.pdf.pdf_processor import PDFToSVGConverter
    from contur.ui.workers import YOLOMarkingThread

    _app()
    markup_cache.DISABLED = True

    thread = YOLOMarkingThread(str(TEST_PDF), 0, "balanced")
    png = str(config.OUTPUT_DIR / "_generators_test.png")
    config.ensure_output_dir()
    thread._convert_pdf_to_png(str(TEST_PDF), png)
    try:
        boxes = thread._detect_devices(png)
        gui_svg = thread._create_svg_with_markup(str(TEST_PDF), boxes)

        converter = PDFToSVGConverter(page_number=0)
        with fitz.open(TEST_PDF) as document:
            page = document[0]
            pdf_width, pdf_height = page.rect.width, page.rect.height
            zoom = converter.converter.dpi / 72
            irect = (page.rect * fitz.Matrix(zoom, zoom)).irect

        scaled = [b.scaled(pdf_width / irect.width, pdf_height / irect.height)
                  for b in boxes]
        content = converter._create_svg_content(str(TEST_PDF), scaled)
        console_svg = str(config.OUTPUT_DIR / "_generators_console.svg")
        with open(console_svg, "w", encoding="utf-8") as f:
            f.write(content[0] if isinstance(content, tuple) else content)

        return gui_svg, console_svg
    finally:
        Path(png).unlink(missing_ok=True)


def test_generators_agree():
    if not TEST_PDF.exists():
        print(f"  ПРОПУСК test_generators_agree: нет {TEST_PDF}")
        return

    gui_svg, console_svg = _both_markups()
    try:
        gui, console = _describe(gui_svg), _describe(console_svg)
        different = {key: (gui[key], console[key]) for key in gui if gui[key] != console[key]}
        assert not different, f"генераторы разошлись: {different}"
        assert gui["сегментов"] > 100, "разметка подозрительно пустая"
    finally:
        for path in (gui_svg, console_svg):
            Path(path).unlink(missing_ok=True)


def test_console_generator_marks_only_devices():
    # Синяя труба не должна нести имя и класс устройства: так было, когда
    # метки оставались от предыдущего элемента
    if not TEST_PDF.exists():
        print(f"  ПРОПУСК test_console_generator_marks_only_devices: нет {TEST_PDF}")
        return

    from contur.pdf import svg_geometry as g
    from contur.export.xml_export import get_pdf_page_size

    _, console_svg = _both_markups()
    try:
        root = ET.parse(console_svg).getroot()
        _, scale = g.detect_coordinate_system(root, get_pdf_page_size(str(TEST_PDF), 0))
        segments = g.extract_line_segments(root, scale,
                                           g.get_svg_dimensions(root, scale), verbose=False)

        stray = [s for s in segments if s.color == "blue" and (s.device_name or s.device_class)]
        assert not stray, f"меток устройств на синих трубах: {len(stray)}"
    finally:
        Path(console_svg).unlink(missing_ok=True)


def test_lost_elements_are_counted():
    # Молчаливый пропуск уже стоил 59 потерянных элементов из 1108: ошибка
    # гасилась, а счётчик считал их отрисованными
    import inspect

    from contur.pdf.pdf_processor import MAX_FAILED_SHARE, PDFToSVGConverter

    source = inspect.getsource(PDFToSVGConverter._create_svg_content)
    assert "failed_elements" in source, "консольный генератор не считает потери"
    assert "MAX_FAILED_SHARE" in source, "нет порога, при котором разметка отвергается"
    assert 0 < MAX_FAILED_SHARE <= 10, f"порог потерь странный: {MAX_FAILED_SHARE}"

    from contur.ui import workers
    assert "MAX_FAILED_SHARE" in inspect.getsource(workers.YOLOMarkingThread), \
        "оконный генератор держит собственный порог вместо общего"


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
