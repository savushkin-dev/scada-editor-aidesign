# tests/test_markup_cache.py
# Кэш размеченных SVG.
#
# Разметка листа занимает до двух минут, поэтому результат сохраняется:
# повторное открытие того же листа обходится без модели. Плата — место
# на диске: около 470 КБ на лист, то есть примерно 120 МБ на проект
# из 265 листов. Предела у кэша не было вовсе, а функция очистки была
# написана и не вызывалась ниоткуда.
#
# Ключ должен меняться от всего, что влияет на разметку: файла, страницы,
# модели, параметров нарезки, версии формата. Ошибка здесь незаметна:
# из кэша молча придёт результат старого кода.
#
# Запуск из папки CONTUR:
#     python tests/test_markup_cache.py
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
import markup_cache

PARAMS = {"dpi": 300, "tile": 1024, "step": 768}


class _Sandbox:
    """Кэш во временной папке: настоящий трогать нельзя."""

    def __enter__(self):
        self.directory = Path(tempfile.mkdtemp(prefix="contur_cache_"))
        self._was_dir = markup_cache.CACHE_DIR
        self._was_disabled = markup_cache.DISABLED
        self._was_limit = markup_cache.MAX_SIZE_MB
        markup_cache.CACHE_DIR = self.directory
        markup_cache.DISABLED = False
        return self

    def __exit__(self, *_):
        markup_cache.CACHE_DIR = self._was_dir
        markup_cache.DISABLED = self._was_disabled
        markup_cache.MAX_SIZE_MB = self._was_limit
        for item in self.directory.glob("*"):
            item.unlink(missing_ok=True)
        self.directory.rmdir()
        return False

    def put(self, key: str, kilobytes: int = 1) -> str:
        source = self.directory / f"_{key}_источник.svg"
        source.write_text("x" * (kilobytes * 1024), encoding="utf-8")
        stored = markup_cache.store(key, str(source))
        source.unlink(missing_ok=True)
        return stored

    def stored(self):
        return {path.stem for path in self.directory.glob("*.svg")}


# ---------------------------------------------------------------- ключ

def _key(**changes) -> str:
    fields = {"pdf_path": __file__, "page_number": 0,
              "model_path": __file__, "generator": "gui", "params": dict(PARAMS)}
    fields.update(changes)
    return markup_cache.build_key(**fields)


def test_same_input_gives_same_key():
    assert _key() == _key(), "ключ неустойчив — кэш не сработает никогда"


def test_key_changes_with_everything_that_matters():
    # Каждое из этих отличий меняет разметку, и попадать в чужую запись нельзя
    base = _key()

    assert _key(page_number=1) != base, "номер страницы не влияет на ключ"
    assert _key(generator="console") != base, "генератор не влияет на ключ"
    assert _key(params={**PARAMS, "dpi": 200}) != base, "параметры не влияют на ключ"
    assert _key(params={**PARAMS, "tile": 512}) != base, "размер плитки не влияет"


def test_key_changes_with_format_version():
    # Версию повышают, когда меняется содержимое SVG. Без этого из кэша
    # придёт разметка старого кода — так уже случалось пять раз подряд
    base = _key()
    was = markup_cache.CACHE_VERSION
    markup_cache.CACHE_VERSION = was + 1
    try:
        assert _key() != base, "версия формата не входит в ключ"
    finally:
        markup_cache.CACHE_VERSION = was


def test_missing_file_does_not_break_the_key():
    # Ключ считается и до того, как файл проверен на существование
    assert _key(pdf_path="нет-такого-файла.pdf"), "ключ не собрался"


# ---------------------------------------------------------------- хранение

def test_stored_markup_is_found():
    with _Sandbox() as box:
        assert markup_cache.lookup("к1") is None, "кэш непустой с самого начала"

        stored = box.put("к1")
        assert Path(stored).exists(), "разметка не положена в кэш"
        assert markup_cache.lookup("к1") == stored, "положенная разметка не находится"


def test_disabled_cache_stores_nothing():
    with _Sandbox():
        markup_cache.DISABLED = True
        source = Path(tempfile.mkdtemp(prefix="contur_off_")) / "разметка.svg"
        source.write_text("...", encoding="utf-8")
        try:
            assert markup_cache.store("к1", str(source)) == str(source), \
                "при отключённом кэше путь подменён"
            assert markup_cache.lookup("к1") is None, "отключённый кэш что-то отдал"
        finally:
            source.unlink(missing_ok=True)
            source.parent.rmdir()


def test_meta_travels_with_its_markup():
    with _Sandbox():
        box_key = "к1"
        markup_cache.store_meta(box_key, {"точек": 4713})
        assert markup_cache.load_meta(box_key) == {"точек": 4713}
        assert markup_cache.load_meta("другой") is None


def test_clear_removes_everything():
    # Функция была написана и не вызывалась ниоткуда — теперь она в меню
    with _Sandbox() as box:
        box.put("к1")
        box.put("к2")
        markup_cache.store_meta("к1", {"точек": 1})

        assert markup_cache.clear() == 3, "удалено не всё, включая спутники"
        assert not box.stored() and markup_cache.lookup("к1") is None


# ---------------------------------------------------------------- предел

def test_size_counts_markup_with_its_meta():
    with _Sandbox() as box:
        box.put("к1", kilobytes=10)
        markup_cache.store_meta("к1", {"точек": list(range(500))})

        size = markup_cache.size_bytes()
        assert size > 10 * 1024, f"спутник не посчитан: {size}"


def test_cache_stays_within_the_limit():
    # Кэш рос без предела: старые записи не удалялись ни при смене версии
    # разметки, ни при смене модели, а попасть в них уже нельзя
    with _Sandbox() as box:
        markup_cache.MAX_SIZE_MB = 1  # предел в мегабайт

        for number in range(4):
            box.put(f"к{number}", kilobytes=400)
            os.utime(box.directory / f"к{number}.svg", (number, number))

        markup_cache.prune()

        assert markup_cache.size_bytes() <= 1024 * 1024, \
            f"кэш вышел за предел: {markup_cache.size_bytes()} байт"
        assert box.stored(), "удалено вообще всё"


def test_oldest_entries_go_first():
    with _Sandbox() as box:
        for number in range(3):
            box.put(f"к{number}", kilobytes=100)
            os.utime(box.directory / f"к{number}.svg", (number, number))

        removed = markup_cache.prune(max_bytes=150 * 1024)

        assert removed == 2, f"удалено записей: {removed}"
        assert box.stored() == {"к2"}, f"осталось: {box.stored()}"


def test_lookup_protects_from_eviction():
    # Лист, к которому возвращаются, не должен уходить первым только
    # потому, что его разметили давно
    with _Sandbox() as box:
        for number in range(3):
            box.put(f"к{number}", kilobytes=100)
            os.utime(box.directory / f"к{number}.svg", (number, number))

        markup_cache.lookup("к0")  # обратились к самой давней
        markup_cache.prune(max_bytes=150 * 1024)

        assert "к0" in box.stored(), f"запись, к которой обращались, вытеснена: {box.stored()}"


def test_meta_is_removed_with_its_markup():
    # Разметка без своих точек сопряжения неполная: спутник обязан уйти
    # вместе с SVG, иначе останется мусор с чужим ключом
    with _Sandbox() as box:
        box.put("к1", kilobytes=100)
        markup_cache.store_meta("к1", {"точек": 1})
        box.put("к2", kilobytes=100)
        os.utime(box.directory / "к1.svg", (1, 1))
        os.utime(box.directory / "к2.svg", (2, 2))

        markup_cache.prune(max_bytes=150 * 1024)

        assert not (box.directory / "к1.json").exists(), "спутник остался без разметки"
        assert markup_cache.load_meta("к1") is None


def test_prune_does_nothing_when_there_is_room():
    with _Sandbox() as box:
        box.put("к1", kilobytes=10)
        assert markup_cache.prune() == 0, "тронуты записи при свободном месте"
        assert box.stored() == {"к1"}


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
