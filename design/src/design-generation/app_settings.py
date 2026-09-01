# app_settings.py
# Что приложение помнит между запусками.
#
# Раньше не помнило ничего: каждый запуск начинался с трёх диалогов выбора
# файлов, диалоги открывались в папке запуска, а размеры окна, положение
# разделителей и настройки отображения возвращались к исходным.
#
# Хранилище — QSettings, то есть реестр Windows под HKCU\Software\CONTUR\Viewer.
# Пароль базы сюда не кладём: держать его открытым текстом нельзя,
# а шифровать здесь нечем.
import os
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QByteArray, QSettings

ORGANISATION = "CONTUR"
APPLICATION = "Viewer"

# Сколько последних файлов помнить в каждом списке
RECENT_LIMIT = 10


def storage() -> QSettings:
    return QSettings(ORGANISATION, APPLICATION)


def save_value(key: str, value: Any) -> None:
    storage().setValue(key, value)


def load_value(key: str, default: Any = None) -> Any:
    return storage().value(key, default)


def load_bool(key: str, default: bool) -> bool:
    # QSettings возвращает строки «true»/«false», а не логические значения
    value = storage().value(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


def load_int(key: str, default: int) -> int:
    try:
        return int(storage().value(key, default))
    except (TypeError, ValueError):
        return default


def save_geometry(window) -> None:
    settings = storage()
    settings.setValue("window/geometry", window.saveGeometry())
    settings.setValue("window/state", window.saveState())


def restore_geometry(window) -> bool:
    # Возвращает False, если сохранённого размера нет — тогда окно
    # выставляется по размеру экрана
    settings = storage()
    geometry = settings.value("window/geometry")
    if not isinstance(geometry, QByteArray) or geometry.isEmpty():
        return False

    window.restoreGeometry(geometry)
    state = settings.value("window/state")
    if isinstance(state, QByteArray) and not state.isEmpty():
        window.restoreState(state)
    return True


# Версия раскладки окна. Повышать, когда меняются пропорции панелей: иначе
# сохранённое положение разделителей вернёт прежнюю раскладку и правка
# не подействует у тех, кто уже запускал приложение.
# v2: левая панель перестала расти вместе с окном (занимала треть экрана).
LAYOUT_VERSION = 2


def save_splitter(name: str, splitter) -> None:
    settings = storage()
    settings.setValue("layout/version", LAYOUT_VERSION)
    settings.setValue(f"splitters/{name}", splitter.saveState())


def restore_splitter(name: str, splitter) -> None:
    if load_int("layout/version", 0) != LAYOUT_VERSION:
        return
    state = storage().value(f"splitters/{name}")
    if isinstance(state, QByteArray) and not state.isEmpty():
        splitter.restoreState(state)


def last_directory(kind: str) -> str:
    # Диалоги открывались в папке запуска, и до чертежей приходилось
    # добираться заново при каждом открытии
    path = storage().value(f"directories/{kind}", "")
    return path if path and os.path.isdir(path) else ""


def remember_directory(kind: str, file_path: str) -> None:
    if not file_path:
        return
    folder = os.path.dirname(os.path.abspath(file_path))
    if os.path.isdir(folder):
        storage().setValue(f"directories/{kind}", folder)


def recent_files(kind: str) -> List[str]:
    # Пропавшие файлы не показываем: список нужен, чтобы открывать,
    # а не чтобы напоминать об удалённом
    stored = storage().value(f"recent/{kind}", [])
    if isinstance(stored, str):
        stored = [stored]
    return [path for path in (stored or []) if os.path.exists(path)]


def remember_recent(kind: str, file_path: str) -> None:
    if not file_path:
        return
    path = os.path.abspath(file_path)
    files = [item for item in recent_files(kind) if os.path.abspath(item) != path]
    files.insert(0, path)
    storage().setValue(f"recent/{kind}", files[:RECENT_LIMIT])


def save_session(lua_files: List[str], objects_file: Optional[str],
                 pdf_path: Optional[str], page: int) -> None:
    settings = storage()
    settings.setValue("session/lua", lua_files or [])
    settings.setValue("session/objects", objects_file or "")
    settings.setValue("session/pdf", pdf_path or "")
    settings.setValue("session/page", int(page))


def load_session() -> Dict[str, Any]:
    settings = storage()
    lua = settings.value("session/lua", [])
    if isinstance(lua, str):
        lua = [lua] if lua else []

    session = {
        "lua": [path for path in (lua or []) if os.path.exists(path)],
        "objects": settings.value("session/objects", "") or "",
        "pdf": settings.value("session/pdf", "") or "",
        "page": load_int("session/page", 0),
    }
    if session["objects"] and not os.path.exists(session["objects"]):
        session["objects"] = ""
    if session["pdf"] and not os.path.exists(session["pdf"]):
        session["pdf"] = ""
    return session


def has_session(session: Dict[str, Any]) -> bool:
    return bool(session.get("pdf") or session.get("lua") or session.get("objects"))


def save_db_settings(settings: Dict[str, Any]) -> None:
    # Пароль сюда не попадает: его отфильтровывает PostgresDialog.saveable()
    storage().setValue("database", {key: value for key, value in settings.items()
                                    if key != "password"})


def load_db_settings() -> Dict[str, Any]:
    stored = storage().value("database", {})
    return dict(stored) if isinstance(stored, dict) else {}
