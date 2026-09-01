# console_utils.py
# Настройка стандартных потоков вывода.
#
# Решает две проблемы:
#  1. Консоль Windows работает в cp1251, а сообщения содержат эмодзи (📄 ✅ ❌).
#     print() падал с UnicodeEncodeError и обрывал обработку.
#  2. В собранном PyInstaller приложении (console=False) sys.stdout равен None,
#     и любой print() приводит к AttributeError.
#
# Модуль выполняет настройку при импорте, поэтому его достаточно
# импортировать первым в точках входа.
import io
import os
import sys


def setup_console(encoding: str = "utf-8") -> None:
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)

        # Собранное GUI-приложение: потока нет вовсе
        if stream is None:
            # Поток живёт до конца работы приложения, закрывать его нечем
            setattr(sys, name, open(os.devnull, "w", encoding=encoding))  # noqa: SIM115
            continue

        # Обычный запуск: переводим поток в UTF-8, недопустимые символы заменяем
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding=encoding, errors="replace")
                continue
            except (ValueError, OSError):
                pass

        # Поток без reconfigure (например, подменённый на StringIO) — оставляем как есть
        if isinstance(stream, io.TextIOBase):
            continue


setup_console()
