# tests/test_xml_io.py
# Чтение своего XML.
#
# Разбор жил внутри окна вперемешку с диалогом выбора файла и окнами
# сообщений, и проверить его было нельзя, не подняв окно целиком. Ошибки
# при этом тут уже случались, и обидные: свой же файл не открывался,
# потому что float("62.064%") падал, а проценты доходили до 1178%.
#
# Формат взят с настоящей выгрузки: координаты в процентах, размеры холста
# в атрибутах canvas-*, у старых файлов — только viewBox внутри SVGContent.
#
# Запуск из папки CONTUR:
#     python tests/test_xml_io.py
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.export import xml_io

CANVAS = 'canvas-width="1000" canvas-height="800"'

DOCUMENT = """<?xml version="1.0" encoding="utf-8"?>
<PlantGeometry version="1.3" coordinate-type="percent" {canvas}>
  <TechnologicalObjects>
    <TechnologicalObject name="CW_TANK1">
      <Contour name="CW_TANK1" tech_object="CW_TANK1"
               bounds="{bounds}" center="{center}"/>
      <Devices>
        <Device device_type="LS" lua_name="CW_TANK1LS1" pdf_name="LS1"
                x="{x}" y="50%" confidence="1.00" descr="Нижний уровень"
                article="IFM.LMT121"/>
        <Device device_type="LT" lua_name="CW_TANK1LT1" pdf_name="LT1"
                x="20%" y="25%" confidence="0.87"/>
      </Devices>
    </TechnologicalObject>
  </TechnologicalObjects>
</PlantGeometry>
"""


def _write(text: str) -> str:
    handle = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False,
                                         encoding="utf-8")
    handle.write(text)
    handle.close()
    return handle.name


def _document(**overrides) -> xml_io.LoadedDocument:
    fields = {"canvas": CANVAS, "bounds": "10%,20%,30%,40%",
              "center": "20%,30%", "x": "10%"}
    fields.update(overrides)
    path = _write(DOCUMENT.format(**fields))
    try:
        return xml_io.load_document(path)
    finally:
        Path(path).unlink(missing_ok=True)


# ------------------------------------------------------------ координаты

def test_percent_becomes_absolute():
    # Ради этого перевода всё и затевалось: 62.064% при холсте 1000
    # это 620.64 пункта, а не 62.064 и не 6206.4
    assert xml_io.parse_coord("62.064%", 1000.0) == 620.64
    assert xml_io.parse_coord("50%", 800.0) == 400.0


def test_absolute_stays_absolute():
    assert xml_io.parse_coord("123.4", 1000.0) == 123.4
    assert xml_io.parse_coord(" 123.4 ", None) == 123.4


def test_percent_without_canvas_is_refused():
    # Молча вернуть 62.064 вместо 620.64 хуже, чем отказаться:
    # устройство уехало бы в угол чертежа, и никто бы не понял почему
    try:
        xml_io.parse_coord("62.064%", None)
        raise AssertionError("проценты без размеров холста разобрались")
    except ValueError as e:
        assert "процент" in str(e), f"невнятная жалоба: {e}"


# ------------------------------------------------------------ размеры холста

def test_canvas_from_attributes():
    root = ET.fromstring(f'<PlantGeometry {CANVAS}/>')
    assert xml_io.canvas_size(root) == (1000.0, 800.0)


def test_canvas_from_viewbox_of_old_files():
    # Файлы, выгруженные до появления canvas-*, несут размеры только
    # внутри встроенного SVG
    root = ET.fromstring(
        '<PlantGeometry><SVGContent>'
        '&lt;svg viewBox="0 0 3368 2384"&gt;&lt;/svg&gt;'
        '</SVGContent></PlantGeometry>')
    assert xml_io.canvas_size(root) == (3368.0, 2384.0)


def test_canvas_from_viewbox_accounts_for_scale():
    # SVG мог быть снят с масштабом — тогда viewBox не в пунктах PDF
    root = ET.fromstring(
        '<PlantGeometry original-svg-coord-system="scaled_2">'
        '<SVGContent>&lt;svg viewBox="0 0 2000 1600"&gt;&lt;/svg&gt;</SVGContent>'
        '</PlantGeometry>')
    assert xml_io.canvas_size(root) == (1000.0, 800.0)


def test_canvas_absent_is_admitted():
    root = ET.fromstring('<PlantGeometry/>')
    assert xml_io.canvas_size(root) == (None, None)


# ------------------------------------------------------------ чтение файла

def test_reads_contours_and_devices():
    document = _document()

    assert len(document.contours) == 1, "контур не прочитан"
    assert len(document.matches) == 2, f"устройств {len(document.matches)}"
    assert not document.problems, f"неожиданные потери: {document.problems}"

    contour = document.contours[0]
    assert contour.name == "CW_TANK1"
    assert contour.bounds == (100.0, 160.0, 300.0, 320.0), \
        f"границы контура: {contour.bounds}"
    assert contour.center == (200.0, 240.0), f"центр контура: {contour.center}"

    device = document.matches[0]
    assert device.lua_name == "CW_TANK1LS1"
    assert device.coordinates == (100.0, 400.0), f"координаты: {device.coordinates}"
    assert device.descr == "Нижний уровень", "описание потерялось"
    assert device.confidence == 1.0


def test_percent_file_without_canvas_is_flagged():
    # Открыть такой файл нельзя, и окно обязано сказать это прямо,
    # а не показать пустую схему
    document = _document(canvas="")

    assert document.needs_canvas, "файл в процентах без холста не отмечен"
    assert not document.matches, "координаты в процентах разобрались без холста"
    assert document.problems, "потери не записаны"


def test_broken_contour_does_not_lose_the_sheet():
    # Одна кривая запись не повод потерять весь лист
    document = _document(bounds="10%,20%,30%")

    assert not document.contours, "контур из трёх чисел прошёл как исправный"
    assert len(document.matches) == 2, "устройства потерялись вместе с контуром"
    assert any("CW_TANK1" in problem for problem in document.problems), \
        f"о потере контура не сказано: {document.problems}"


def test_broken_device_does_not_lose_the_others():
    document = _document(x="не число")

    assert len(document.matches) == 1, "исправное устройство тоже потерялось"
    assert document.matches[0].lua_name == "CW_TANK1LT1"
    assert document.skipped == 1, f"потерь насчитано {document.skipped}"
    assert "CW_TANK1LS1" in document.problems[0], \
        f"в жалобе не названо устройство: {document.problems[0]}"


def test_unreadable_file_is_not_swallowed():
    # Битый файл — не то же самое, что пустой: окно должно сказать об этом
    path = _write("<PlantGeometry><TechnologicalObjects>")
    try:
        xml_io.load_document(path)
        raise AssertionError("обрезанный файл прочитался")
    except ET.ParseError:
        pass
    finally:
        Path(path).unlink(missing_ok=True)


def test_module_does_not_depend_on_qt():
    # Смысл выделения в том, что разбор проверяется без окна.
    # Импорт Qt здесь вернул бы всё как было.
    source = (Path(__file__).resolve().parent.parent / "contur" / "export" / "xml_io.py").read_text(
        encoding="utf-8")
    assert "PySide6" not in source, "в разбор XML вернулся Qt"


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
