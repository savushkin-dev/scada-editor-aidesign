# tests/test_schemes.py
# Переключение между загруженными схемами.
#
# Раньше приложение держало одну схему и при загрузке следующей ничего
# не сбрасывало: размеченный SVG предыдущей оставался фоном под контурами
# новой, и две схемы накладывались друг на друга.
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_models import Contour, DeviceMatch


def _window():
    from PySide6.QtWidgets import QApplication
    import xml_viewer
    QApplication.instance() or QApplication([])
    return xml_viewer.DeviceVisualizer(), xml_viewer.LoadedScheme


def _scheme(cls, name: str, page: int = 0, devices: int = 1):
    return cls(
        pdf_path=f"C:/схемы/{name}.pdf", page=page, total_pages=3,
        contours=[Contour(name=f"{name}_TANK", bounds=(0, 0, 10, 10),
                          center=(5, 5), tech_object=f"{name}_TANK")],
        matches=[DeviceMatch(lua_name=f"{name}V{i}", pdf_name=f"V{i}",
                             tech_object=f"{name}_TANK", coordinates=(float(i), 2.0),
                             confidence=0.9) for i in range(devices)],
    )


def test_switching_replaces_state():
    window, cls = _window()
    first, second = _scheme(cls, "первая", devices=2), _scheme(cls, "вторая", devices=5)
    window.schemes = [first, second]

    window._apply_scheme(first)
    assert len(window.matches) == 2
    assert window.contours[0].name == "первая_TANK"

    window._remember_active_scheme()
    window._apply_scheme(second)
    assert len(window.matches) == 5, "устройства предыдущей схемы остались"
    assert window.contours[0].name == "вторая_TANK", "контуры не заменились"
    assert window.current_pdf_path.endswith("вторая.pdf")


def test_switching_back_keeps_results():
    # Переключение туда и обратно не должно терять уже посчитанное
    window, cls = _window()
    first, second = _scheme(cls, "первая", devices=2), _scheme(cls, "вторая", devices=5)
    window.schemes = [first, second]

    window._apply_scheme(first)
    window._remember_active_scheme()
    window._apply_scheme(second)
    window._remember_active_scheme()
    window._apply_scheme(first)

    assert len(window.matches) == 2
    assert window.contours[0].name == "первая_TANK"


def test_background_cleared_when_scheme_has_no_svg():
    # Ключевая проверка: фон предыдущей схемы не должен оставаться
    window, cls = _window()
    first, second = _scheme(cls, "первая"), _scheme(cls, "вторая")
    first.svg_path = "не-существует.svg"
    window.schemes = [first, second]

    window._apply_scheme(first)
    window._apply_scheme(second)
    assert window.graphics_view.svg_item is None, "подложка предыдущей схемы осталась"
    assert window.svg_background_path is None


def test_title_shows_page_for_multipage():
    _, cls = _window()
    single = cls(pdf_path="C:/x/схема.pdf", page=0, total_pages=1)
    multi = cls(pdf_path="C:/x/схема.pdf", page=4, total_pages=265)
    assert single.title == "схема.pdf"
    assert "5" in multi.title and "схема.pdf" in multi.title


def test_same_page_is_one_scheme():
    # Один и тот же лист не должен попадать в список дважды
    _, cls = _window()
    a = cls(pdf_path="C:/x/схема.pdf", page=2)
    b = cls(pdf_path="C:/x/схема.pdf", page=2)
    c = cls(pdf_path="C:/x/схема.pdf", page=3)
    assert a.key == b.key and a.key != c.key


def test_closing_last_scheme_clears_view():
    window, cls = _window()
    only = _scheme(cls, "единственная")
    window.schemes = [only]
    window._apply_scheme(only)
    window._refresh_scheme_selector()

    window.close_current_scheme()
    assert window.schemes == []
    assert window.active_scheme is None
    assert window.matches == [] and window.contours == []
    assert window.graphics_view.svg_item is None


def test_closing_one_of_two_switches_to_other():
    window, cls = _window()
    first, second = _scheme(cls, "первая", devices=2), _scheme(cls, "вторая", devices=5)
    window.schemes = [first, second]
    window._apply_scheme(second)
    window._refresh_scheme_selector()

    window.close_current_scheme()
    assert window.schemes == [first]
    assert window.active_scheme is first
    assert len(window.matches) == 2


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
