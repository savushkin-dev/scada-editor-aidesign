# app_log.py
# Журнал работы приложения.
#
# Диагностика в проекте написана через print — около двухсот вызовов
# в шестнадцати модулях. В собранном приложении console=False, sys.stdout
# равен None, и console_utils отправляет оба потока в устройство-пустышку.
# То есть ровно в том виде, в каком приложение отдают людям, оно немое:
# ни ошибки, ни причины закрытия узнать нечем.
#
# Переписывать двести print на logging — большая правка без выигрыша:
# консольные пути (check_pipeline, batch_process) этим выводом и живут,
# он там и есть результат. Поэтому вывод не подменяется, а раздваивается:
# идёт на прежнее место и попадает в файл рядом с результатами.
#
# Модуль не знает про Qt: окно передаёт свой способ показать ошибку
# отдельно, через install_excepthook(reporter=...).
import os
import sys
import time
import traceback
from contextlib import suppress
from pathlib import Path
from typing import Callable, Optional, TextIO

import config

LOG_NAME = "contur.log"

# Предел размера. При переполнении журнал переезжает в contur.log.1,
# прежний .1 удаляется: две последние сессии — достаточная глубина,
# а расти без предела здесь нечему.
MAX_BYTES = 2 * 1024 * 1024

_log_file: Optional[TextIO] = None
_original_streams: dict = {}


def log_path() -> Path:
    return Path(os.environ.get("CONTUR_LOG_PATH", str(config.OUTPUT_DIR / LOG_NAME)))


class _Tee:
    """Пишет и в исходный поток, и в журнал.

    Ошибку записи в журнал глушим намеренно: диск может быть переполнен
    или папка защищена от записи, и это не повод ронять приложение,
    которое до сих пор работало.
    """

    def __init__(self, stream: TextIO, log: TextIO):
        self._stream = stream
        self._log = log

    def write(self, text: str) -> int:
        written = self._stream.write(text)
        with suppress(OSError, ValueError):
            self._log.write(text)
        return written

    def flush(self) -> None:
        self._stream.flush()
        with suppress(OSError, ValueError):
            self._log.flush()

    def isatty(self) -> bool:
        return getattr(self._stream, "isatty", lambda: False)()

    def __getattr__(self, name):
        return getattr(self._stream, name)


def _rotate(path: Path) -> None:
    # ValueError здесь не теоретический: путь с недопустимым символом даёт
    # именно его, а не OSError, и на нём journal ронял бы приложение
    # ещё до появления окна
    try:
        if path.exists() and path.stat().st_size > MAX_BYTES:
            previous = path.with_suffix(path.suffix + ".1")
            previous.unlink(missing_ok=True)
            path.rename(previous)
    except (OSError, ValueError):
        pass


def start() -> Optional[Path]:
    """Открывает журнал и заворачивает в него вывод. Возвращает путь к файлу.

    Повторный вызов ничего не делает: раздвоить уже раздвоенный поток
    значило бы писать каждую строку дважды.
    """
    global _log_file
    if _log_file is not None:
        return log_path()

    path = log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _rotate(path)
        _log_file = open(path, "a", encoding="utf-8", buffering=1)  # noqa: SIM115
    except (OSError, ValueError) as e:
        # Без журнала приложение работать может, а вот падать из-за журнала
        # не должно ни в коем случае
        print(f"⚠️ Журнал недоступен ({e}) — вывод только в консоль")
        return None

    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            continue
        _original_streams[name] = stream
        setattr(sys, name, _Tee(stream, _log_file))

    write(f"запуск, python {sys.version.split()[0]}, "
          f"собрано: {'да' if config.IS_FROZEN else 'нет'}")
    return path


def stop() -> None:
    # Нужно проверкам: они запускают и останавливают журнал по многу раз
    global _log_file
    for name, stream in _original_streams.items():
        setattr(sys, name, stream)
    _original_streams.clear()

    if _log_file is not None:
        with suppress(OSError):
            _log_file.close()
        _log_file = None


def write(message: str) -> None:
    """Строка со временем — в журнал, минуя консоль.

    Отметка времени ставится только здесь. У обычного print её нет
    намеренно: он часто рисует таблицы и полосы прогресса, и время
    в начале каждой строки сделало бы их нечитаемыми.
    """
    if _log_file is None:
        return
    with suppress(OSError, ValueError):
        _log_file.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        _log_file.flush()


def install_excepthook(reporter: Optional[Callable[[str, str], None]] = None) -> None:
    """Ставит перехватчик необработанных исключений.

    Без него ошибка в обработчике сигнала Qt уходила в никуда: печаталась
    в поток, которого в собранном приложении нет. Окно оставалось на экране
    в непонятном состоянии, и узнать причину было нечем.

    reporter(краткое, подробное) — способ показать ошибку человеку.
    Его передаёт окно; сам модуль про Qt не знает.
    """
    previous = sys.excepthook

    def handle(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            previous(exc_type, exc_value, exc_traceback)
            return

        details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        write("НЕОБРАБОТАННАЯ ОШИБКА\n" + details)

        short = f"{exc_type.__name__}: {exc_value}"
        if reporter is not None:
            try:
                reporter(short, details)
            except Exception:
                # Сообщить не удалось — это не повод потерять саму ошибку
                previous(exc_type, exc_value, exc_traceback)
                return

        previous(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle
