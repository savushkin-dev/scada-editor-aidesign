# markup_cache.py
# Кэш размеченных SVG.
#
# Разметка YOLO занимает ~30 секунд на лист, но при неизменных исходных данных
# результат каждый раз одинаковый. Повторная работа с той же схемой (перезапуск
# приложения, возврат к другой странице, эксперименты с экспортом) больше
# не требует повторной детекции.
#
# Ключ учитывает всё, что влияет на результат: сам файл (размер и время
# изменения), номер страницы, модель, параметры нарезки и генератор SVG.
# Если что-то из этого поменялось — ключ другой, и разметка выполняется заново.
import hashlib
import json
import os
import shutil
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config

CACHE_DIR = Path(os.environ.get("CONTUR_CACHE_DIR", str(config.OUTPUT_DIR / "markup_cache")))

# Версия формата разметки. Повышать при любом изменении, которое меняет
# содержимое SVG, иначе из кэша будет отдаваться результат старого кода.
# v2: в разметке GUI терялись линии устройств (svgwrite отвергал
#     data-device-name), закэшированные SVG были неполными.
# v3: в SVG добавлены data-device-class и data-device-conf.
# v4: подписи берутся и от сопоставленных устройств — имена стали полными.
# v5: в корень SVG добавлен data-device-named.
# v6: из разметки убраны пустые элементы <text> (три штуки на лист);
#     в консольном генераторе починена потеря элементов и чужие метки
#     на синих трубах.
CACHE_VERSION = 6

# CONTUR_DISABLE_CACHE=1 полностью отключает кэш
DISABLED = os.environ.get("CONTUR_DISABLE_CACHE", "").strip() not in ("", "0", "false", "False")

# Предел размера кэша. Один размеченный лист занимает около 470 КБ, то есть
# проект из 265 листов — примерно 120 МБ. Кэш при этом рос без всякого
# предела: старые записи не удалялись ни при смене версии разметки, ни при
# смене модели, а ключ у них другой, и попасть в них уже нельзя.
# Берём с запасом, чтобы целый проект помещался целиком.
MAX_SIZE_MB = int(os.environ.get("CONTUR_CACHE_MAX_MB", 300))


def _file_signature(path: str) -> Dict[str, Any]:
    try:
        stat = Path(path).stat()
        return {"path": str(Path(path).resolve()), "size": stat.st_size, "mtime": int(stat.st_mtime)}
    except OSError:
        return {"path": str(path), "size": None, "mtime": None}


def build_key(pdf_path: str, page_number: int, model_path: str,
              generator: str, params: Dict[str, Any]) -> str:
    payload = {
        "version": CACHE_VERSION,
        "pdf": _file_signature(pdf_path),
        "page": page_number,
        "model": _file_signature(model_path),
        "generator": generator,
        "params": params,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def lookup(key: str) -> Optional[str]:
    # Путь к готовому SVG или None
    if DISABLED:
        return None
    candidate = CACHE_DIR / f"{key}.svg"
    if not candidate.exists():
        return None

    # Отмечаем обращение: при переполнении первыми уходят те записи,
    # к которым дольше всего не возвращались
    with suppress(OSError):
        os.utime(candidate, None)
    return str(candidate)


def store(key: str, svg_path: str) -> str:
    # Кладёт SVG в кэш и возвращает путь к копии (или исходный путь при ошибке)
    if DISABLED:
        return svg_path
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        target = CACHE_DIR / f"{key}.svg"
        shutil.copyfile(svg_path, target)
        prune()
        return str(target)
    except OSError as e:
        print(f"⚠️ Не удалось сохранить разметку в кэш: {e}")
        return svg_path


def _entries() -> List[Tuple[Path, int, float]]:
    """Записи кэша: (SVG, размер вместе со спутником, время обращения)."""
    if not CACHE_DIR.exists():
        return []

    found = []
    for svg in CACHE_DIR.glob("*.svg"):
        try:
            size = svg.stat().st_size
            touched = svg.stat().st_mtime
        except OSError:
            continue

        meta = svg.with_suffix(".json")
        with suppress(OSError):
            size += meta.stat().st_size
        found.append((svg, size, touched))
    return found


def size_bytes() -> int:
    return sum(size for _, size, _ in _entries())


def prune(max_bytes: Optional[int] = None) -> int:
    """Удаляет самые давние записи, пока кэш не уложится в предел.

    Возвращает число удалённых записей. Спутник .json уходит вместе
    со своим SVG: без него разметка из кэша неполная.
    """
    limit = MAX_SIZE_MB * 1024 * 1024 if max_bytes is None else max_bytes
    entries = _entries()
    total = sum(size for _, size, _ in entries)
    if total <= limit:
        return 0

    removed = 0
    for svg, size, _ in sorted(entries, key=lambda item: item[2]):
        if total <= limit:
            break
        try:
            svg.unlink()
            svg.with_suffix(".json").unlink(missing_ok=True)
        except OSError:
            continue
        total -= size
        removed += 1

    if removed:
        print(f"🧹 Кэш разметки: удалено записей {removed}, "
              f"осталось {total / 1048576:.0f} МБ")
    return removed


def store_meta(key: str, data: Any) -> None:
    # Сопутствующие данные (например, точки сопряжения), чтобы результат
    # из кэша полностью совпадал с результатом полной разметки
    if DISABLED:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_DIR / f"{key}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError as e:
        print(f"⚠️ Не удалось сохранить данные разметки в кэш: {e}")


def load_meta(key: str) -> Optional[Any]:
    if DISABLED:
        return None
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def clear() -> int:
    # Удаляет весь кэш, возвращает число удалённых файлов
    if not CACHE_DIR.exists():
        return 0
    removed = 0
    for pattern in ("*.svg", "*.json"):
        for item in CACHE_DIR.glob(pattern):
            try:
                item.unlink()
                removed += 1
            except OSError:
                pass
    return removed
