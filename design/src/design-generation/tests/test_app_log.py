# tests/test_app_log.py
# Журнал работы приложения.
#
# До него собранное приложение было немым: console=False, sys.stdout равен
# None, console_utils отправляет оба потока в устройство-пустышку. Двести
# print по всем модулям писали в никуда, необработанная ошибка не оставляла
# следа, и на вопрос «почему закрылось» ответить было нечем.
#
# Проверяется главное свойство: журнал ничего не ломает. Он раздваивает
# вывод, а не подменяет его; недоступный файл не мешает приложению
# работать; ошибка при записи в журнал не превращается в ошибку приложения.
#
# Запуск из папки CONTUR:
#     python tests/test_app_log.py
import io
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app_log
import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)


class _Sandbox:
    """Журнал во временной папке, с гарантией уборки за собой."""

    def __init__(self, name="contur.log"):
        self.directory = tempfile.mkdtemp(prefix="contur_log_")
        self.path = Path(self.directory) / name

    def __enter__(self):
        os.environ["CONTUR_LOG_PATH"] = str(self.path)
        return self

    def __exit__(self, *_):
        app_log.stop()
        os.environ.pop("CONTUR_LOG_PATH", None)
        for item in Path(self.directory).glob("*"):
            item.unlink(missing_ok=True)
        Path(self.directory).rmdir()
        return False

    def text(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""


def test_print_reaches_the_log():
    with _Sandbox() as box:
        assert app_log.start() == box.path, "журнал открылся не там, где просили"
        print("сообщение из конвейера")
        sys.stdout.flush()

        assert "сообщение из конвейера" in box.text(), \
            "обычный print не попал в журнал"


def test_console_output_is_not_swallowed():
    # Раздвоение, а не подмена: консольные пути (check_pipeline,
    # batch_process) этим выводом и живут, он там и есть результат
    with _Sandbox():
        original = sys.stdout
        collected = io.StringIO()
        sys.stdout = collected
        try:
            app_log.start()
            print("видно в обоих местах")
            sys.stdout.flush()
        finally:
            app_log.stop()
            sys.stdout = original

        assert "видно в обоих местах" in collected.getvalue(), \
            "журнал перехватил вывод вместо того, чтобы его продублировать"


def test_start_twice_does_not_double_output():
    with _Sandbox() as box:
        app_log.start()
        app_log.start()
        print("один раз")
        sys.stdout.flush()

        assert box.text().count("один раз") == 1, \
            "повторный запуск журнала раздваивает каждую строку"


def test_unhandled_error_lands_in_the_log():
    with _Sandbox() as box:
        app_log.start()

        seen = []
        app_log.install_excepthook(lambda short, details: seen.append(short))
        try:
            try:
                raise ValueError("схема не разобралась")
            except ValueError:
                sys.excepthook(*sys.exc_info())
        finally:
            sys.excepthook = sys.__excepthook__

        recorded = box.text()
        assert "ValueError: схема не разобралась" in recorded, \
            "трассировка не записана в журнал"
        assert "НЕОБРАБОТАННАЯ ОШИБКА" in recorded, "ошибку не отличить от обычного вывода"
        assert seen == ["ValueError: схема не разобралась"], \
            f"пользователю не сообщили об ошибке: {seen}"


def test_reporter_failure_does_not_hide_the_error():
    # Если показать окно не удалось, ошибка всё равно должна остаться
    # видимой: иначе перехватчик превращается в глушитель
    with _Sandbox() as box:
        app_log.start()

        def broken_reporter(short, details):
            raise RuntimeError("окна уже нет")

        app_log.install_excepthook(broken_reporter)
        try:
            try:
                raise KeyError("устройство")
            except KeyError:
                sys.excepthook(*sys.exc_info())
        finally:
            sys.excepthook = sys.__excepthook__

        assert "KeyError" in box.text(), "ошибка потерялась вместе со сбойным окном"


def test_keyboard_interrupt_is_left_alone():
    # Ctrl+C — не поломка, окно с трассировкой на него показывать незачем
    with _Sandbox():
        app_log.start()

        seen = []
        app_log.install_excepthook(lambda short, details: seen.append(short))
        try:
            try:
                raise KeyboardInterrupt()
            except KeyboardInterrupt:
                sys.excepthook(*sys.exc_info())
        finally:
            sys.excepthook = sys.__excepthook__

        assert not seen, "прерывание с клавиатуры показано как ошибка приложения"


def test_unwritable_log_does_not_break_the_application():
    # Диск переполнен или папка защищена от записи — приложение обязано
    # работать дальше, просто без журнала
    previous = os.environ.get("CONTUR_LOG_PATH")
    os.environ["CONTUR_LOG_PATH"] = str(Path(tempfile.gettempdir()) / "нет" / "такой" /
                                        "папки" / "\0недопустимое" / "contur.log")
    try:
        assert app_log.start() is None, "недоступный журнал выдал себя за открытый"
        print("приложение продолжает работать")
        sys.stdout.flush()
    finally:
        app_log.stop()
        if previous is None:
            os.environ.pop("CONTUR_LOG_PATH", None)
        else:
            os.environ["CONTUR_LOG_PATH"] = previous


def test_log_does_not_grow_without_limit():
    # Кэш разметки уже показал, чем кончается рост без предела
    with _Sandbox() as box:
        original_limit = app_log.MAX_BYTES
        app_log.MAX_BYTES = 200
        try:
            app_log.start()
            print("x" * 500)
            sys.stdout.flush()
            app_log.stop()

            app_log.start()
            print("после переезда")
            sys.stdout.flush()
        finally:
            app_log.MAX_BYTES = original_limit

        previous = box.path.with_suffix(box.path.suffix + ".1")
        assert previous.exists(), "переполненный журнал не переехал в .1"
        assert "x" * 500 in previous.read_text(encoding="utf-8"), \
            "прежние записи потеряны при переезде"
        assert "после переезда" in box.text(), "новый журнал не пишется"

        previous.unlink(missing_ok=True)


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
