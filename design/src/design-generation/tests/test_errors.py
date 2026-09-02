# tests/test_errors.py
# Понятные сообщения об ошибках.
#
# Замерено на битом входе: пользователю показывали текст библиотеки —
# «Cannot open empty file: filename='C:/...'» и «error loading code:
# [string "<python>"]:88: unfinished string near <eof>». По ним нельзя
# понять ни что случилось, ни что делать.
#
# Ошибки библиотек узнаются по имени класса, поэтому здесь заводятся
# подделки с теми же именами: настоящие fitz и lupa ради проверки
# сообщений загружать незачем.
#
# Запуск из папки CONTUR:
#     python tests/test_errors.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import errors


class EmptyFileError(Exception):
    pass


class FileDataError(Exception):
    pass


class LuaSyntaxError(Exception):
    pass


class ЧужаяОшибка(Exception):
    pass


def test_empty_file_is_explained():
    message = errors.describe(EmptyFileError(
        "Cannot open empty file: filename='C:/схемы/пустой.pdf'."))

    assert "пуст" in message.lower(), f"сообщение: {message!r}"
    assert "Cannot open" not in message, "текст библиотеки просочился к пользователю"


def test_not_a_pdf_is_explained():
    message = errors.describe(FileDataError("Failed to open file 'C:/схемы/текст.pdf'."))

    assert "не PDF" in message or "повреждён" in message, f"сообщение: {message!r}"
    assert "Failed to open" not in message


def test_lua_error_names_the_line():
    # Номер строки — единственное, что в сообщении библиотеки было полезным
    message = errors.describe(LuaSyntaxError(
        'error loading code: [string "<python>"]:88: unfinished string near <eof>'))

    assert "синтаксис" in message.lower(), f"сообщение: {message!r}"
    assert "строка 88" in message, f"номер строки потерян: {message!r}"


def test_lua_error_without_line_still_reads():
    message = errors.describe(LuaSyntaxError("что-то пошло не так"))

    assert "синтаксис" in message.lower()
    assert "строка" not in message, f"выдуман номер строки: {message!r}"
    assert "{where}" not in message, "образец подстановки остался в тексте"


def test_our_own_messages_pass_through():
    # «В PDF нет страницы 99 (всего 1)» переписывать незачем
    for own in (ValueError("В Lua-файле нет блока 'nodes'"),
                IndexError("В PDF нет страницы 99 (всего 1)")):
        message = errors.describe(own)
        assert message == str(own), f"своё сообщение переписано: {message!r}"


def test_unknown_error_keeps_its_type():
    # Если объяснения нет, пользователь должен получить хотя бы то,
    # что можно переслать вместе с журналом
    message = errors.describe(ЧужаяОшибка("подробности"))

    assert "ЧужаяОшибка" in message and "подробности" in message, f"сообщение: {message!r}"


def test_error_without_text_is_still_named():
    assert errors.describe(ЧужаяОшибка()) == "ЧужаяОшибка"


def test_key_error_does_not_leak_its_tuple():
    # У KeyError str() даёт "'ключ'" с кавычками, а у пустого — служебный вид
    message = errors.describe(KeyError("devices"))
    assert message, "сообщение пустое"


def test_file_name_is_short_and_at_the_end():
    # Полный путь в тексте библиотеки нечитаем, а имя файла нужно
    message = errors.describe(EmptyFileError("Cannot open empty file"),
                              path=r"C:\Users\1\Desktop\схемы\БН1-Молоко.pdf")

    assert message.endswith("Файл: БН1-Молоко.pdf"), f"сообщение: {message!r}"
    assert "C:" not in message, "полный путь показан пользователю"


def test_scan_is_explained_not_silently_empty():
    # Скан открывается без ошибки и даёт ноль сегментов: без объяснения
    # пользователь видит пустую схему и не знает почему
    assert "скан" in errors.NO_VECTOR_GRAPHICS.lower()
    assert "векторн" in errors.NO_VECTOR_GRAPHICS.lower()


def test_module_stays_light():
    # Модуль зовут из мест, где ни PyMuPDF, ни Lua не загружены
    source = (Path(__file__).resolve().parent.parent / "errors.py").read_text(
        encoding="utf-8")
    for heavy in ("import fitz", "import lupa", "PySide6"):
        assert heavy not in source, f"в сообщения об ошибках попал {heavy}"


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
