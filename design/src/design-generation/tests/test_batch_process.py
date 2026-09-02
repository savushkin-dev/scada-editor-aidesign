# tests/test_batch_process.py
# Пакетная обработка многостраничного PDF.
#
# 262 строки без единой проверки. Инструмент нужен ровно тогда, когда
# страниц много: на файле из 265 листов ошибка в разборе номеров или
# в подсчёте покрытия обнаружится через час работы, а не сразу.
#
# Разбор номеров страниц проверяется напрямую, остальное — настоящим
# прогоном в режиме обследования (--no-markup): он занимает меньше
# секунды, потому что не зовёт модель.
#
# Запуск из папки CONTUR:
#     python tests/test_batch_process.py
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import batch_process
import config
import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from batch_process import parse_pages

ROOT = Path(__file__).resolve().parent.parent

SMALL_PDF = config.INPUT_DIR / "test" / "BN1-Растворение-3.pdf"
IO_LUA = config.INPUT_DIR / "test" / "main.io.lua"
OBJECTS_LUA = config.INPUT_DIR / "test" / "main.objects.lua"

# Большой файл в репозиторий не кладут (30 МБ), поэтому проверки на нём
# пропускаются, а не падают
BIG_PDF = config.INPUT_DIR / "test1" / "BN1-МОЛОКОХРАНИЛИЩЕ-2025Full.pdf"


def _run(pdf: Path, out_dir: Path, *extra):
    """Прогон в этом же процессе: возвращает (код возврата, вывод).

    Отдельным процессом было проще, но замер покрытия его не видит:
    16% вместо настоящих. Внутри процесса заодно быстрее — не тратится
    запуск интерпретатора и повторный импорт PyMuPDF.
    """
    argv = ["batch_process.py", "--pdf", str(pdf),
            "--io-lua", str(IO_LUA), "--objects-lua", str(OBJECTS_LUA),
            "--out", str(out_dir), "--no-markup", "--quiet", *extra]

    was_argv, was_cwd = sys.argv, os.getcwd()
    buffer = io.StringIO()
    sys.argv = argv
    os.chdir(ROOT)
    try:
        with contextlib.redirect_stdout(buffer):
            code = batch_process.main()
    finally:
        sys.argv = was_argv
        os.chdir(was_cwd)

    return code, buffer.getvalue()


# ---------------------------------------------------------------- номера страниц

def test_empty_selection_means_all_pages():
    assert parse_pages("", 5) == [0, 1, 2, 3, 4]


def test_range_counts_from_one():
    # Пользователь называет страницы с единицы, внутри они с нуля.
    # Ошибка на единицу здесь означала бы обработку не тех листов
    assert parse_pages("1-20", 265) == list(range(20))
    assert parse_pages("3", 10) == [2]


def test_mixed_selection():
    assert parse_pages("1-5,8,11-13", 20) == [0, 1, 2, 3, 4, 7, 10, 11, 12]


def test_spaces_are_tolerated():
    assert parse_pages(" 1-3 , 7 ", 10) == [0, 1, 2, 6]


def test_repeats_are_collapsed_and_sorted():
    assert parse_pages("5,1-3,2,5", 10) == [0, 1, 2, 4]


def test_pages_outside_the_file_are_dropped():
    # '1-500' на файле из 10 листов не должно ронять обработку
    assert parse_pages("1-500", 10) == list(range(10))
    assert parse_pages("999", 10) == []
    assert parse_pages("0", 10) == [], "нулевая страница превращается в -1"


def test_reversed_range_selects_nothing():
    assert parse_pages("5-3", 10) == []


def test_trailing_comma_is_ignored():
    assert parse_pages("1,2,", 10) == [0, 1]


# ---------------------------------------------------------------- прогон

def test_survey_run_writes_summary_and_coverage():
    if not (SMALL_PDF.exists() and IO_LUA.exists() and OBJECTS_LUA.exists()):
        print("  ПРОПУСК test_survey_run_writes_summary_and_coverage: нет входных файлов")
        return

    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(SMALL_PDF, out_dir, "--pages", "1")
        assert code == 0, f"обследование завершилось с кодом {code}:\n{output[-800:]}"

        summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert len(summary) == 1, f"страниц в сводке: {len(summary)}"

        page = summary[0]
        assert page["page"] == 1, "номер страницы в сводке считается не с единицы"
        assert page["matches"] > 0, f"на листе не сопоставлено ничего: {page}"
        assert page["devices"], "список найденных устройств пуст"
        assert page["objects"], "список техобъектов пуст"
        assert "seconds" in page, "время обработки не записано"

        coverage = json.loads((out_dir / "coverage.json").read_text(encoding="utf-8"))
        assert coverage["pages_processed"] == 1
        assert coverage["pages_total"] == 1
        assert coverage["full_run"] is True, "весь файл обработан, а прогон не полный"
        assert set(coverage["found"]) <= set(coverage["total"]), \
            "найдено устройство, которого нет в Lua"
        assert set(coverage["missing"]) == set(coverage["total"]) - set(coverage["found"]), \
            "ненайденные не сходятся с разностью списков"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_survey_does_not_draw_anything():
    # --no-markup существует ради скорости: он не должен звать модель
    # и оставлять размеченные SVG
    if not SMALL_PDF.exists():
        print("  ПРОПУСК test_survey_does_not_draw_anything: нет входных файлов")
        return

    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        _run(SMALL_PDF, out_dir, "--pages", "1")

        assert not list(out_dir.glob("*_marked.svg")), "обследование нарисовало разметку"

        # Геометрия называется page_001_geometry.xml и под page_*.xml тоже
        # подходит, поэтому выгрузку отличаем явно
        exported = [path for path in out_dir.glob("page_*.xml")
                    if not path.stem.endswith("_geometry")]
        assert not exported, f"обследование выгрузило XML: {[p.name for p in exported]}"
        assert list(out_dir.glob("*_geometry.xml")), "геометрия не сохранена"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_partial_run_does_not_claim_project_coverage():
    # Вывод «не найдено ни на одной странице» по трём листам из 265
    # был бы неправдой: на остальных они могут быть
    if not BIG_PDF.exists():
        print(f"  ПРОПУСК test_partial_run_does_not_claim_project_coverage: нет {BIG_PDF.name}")
        return

    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(BIG_PDF, out_dir, "--pages", "1")
        assert code in (0, 1), f"код возврата {code}"

        coverage = json.loads((out_dir / "coverage.json").read_text(encoding="utf-8"))
        assert coverage["full_run"] is False, "часть файла выдана за весь файл"
        assert coverage["pages_total"] > coverage["pages_processed"]
        assert "могут быть" in output, \
            "в сводке нет оговорки про необработанные страницы"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


# ------------------------------------------------------- несколько файлов Lua
#
# Файлов с устройствами у проекта бывает несколько (main.io.lua вместе
# с main.wago.lua). check_pipeline это уже умеет, а пакетная обработка брала
# один: на mozzarella она не видела 41 устройство и считала покрытие
# от неверного знаменателя — 730 вместо 771.


def _devices_in_coverage(out_dir: Path) -> int:
    coverage = json.loads((out_dir / "coverage.json").read_text(encoding="utf-8"))
    return len(coverage["total"])


def test_several_io_lua_files_are_accepted():
    if not (SMALL_PDF.exists() and IO_LUA.exists()):
        print("  ПРОПУСК test_several_io_lua_files_are_accepted: нет входных файлов")
        return

    one = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    two = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(SMALL_PDF, one, "--pages", "1")
        assert code == 0, f"прогон с одним файлом не прошёл:\n{output[-500:]}"

        # Второе появление --io-lua перекрывает первое, что и даёт два файла
        code, output = _run(SMALL_PDF, two, "--pages", "1",
                            "--io-lua", str(IO_LUA), str(IO_LUA))
        assert code == 0, f"прогон с двумя файлами не прошёл:\n{output[-500:]}"

        assert _devices_in_coverage(two) == _devices_in_coverage(one), \
            "один и тот же файл, поданный дважды, изменил число устройств"
    finally:
        shutil.rmtree(one, ignore_errors=True)
        shutil.rmtree(two, ignore_errors=True)


def test_every_io_lua_file_is_checked_for_existence():
    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(SMALL_PDF, out_dir, "--io-lua",
                            str(IO_LUA), "нет-такого-файла.lua")
        assert code == 2, f"код возврата {code}: пропущен несуществующий файл Lua"
        assert "Нет файла" in output, f"невнятный отказ: {output[:200]}"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


# ---------------------------------------------------------------- отказы

def test_missing_file_is_refused_before_any_work():
    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(Path("нет-такого-файла.pdf"), out_dir)
        assert code == 2, f"код возврата {code}"
        assert "Нет файла" in output, f"невнятный отказ: {output[:200]}"
        assert not (out_dir / "summary.json").exists(), \
            "сводка написана при отсутствующем файле"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_empty_selection_of_pages_is_refused():
    if not SMALL_PDF.exists():
        print("  ПРОПУСК test_empty_selection_of_pages_is_refused: нет входных файлов")
        return

    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, output = _run(SMALL_PDF, out_dir, "--pages", "999")
        assert code == 2, f"код возврата {code}"
        assert "Не выбрано ни одной страницы" in output, \
            f"невнятный отказ: {output[:300]}"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


# ---------------------------------------------------------------- формат выгрузки

def test_counts_read_from_both_formats():
    # Сводка берёт числа из готового файла, а не из памяти: так в неё попадает
    # то, что действительно записано. Формата два — читаться должны оба
    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        xml_path = out_dir / "page_001.xml"
        xml_path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<PlantGeometry junction-points-count="7" pipelines-count="3">'
            '  <Connections count="2"/>'
            '</PlantGeometry>', encoding="utf-8")

        json_path = out_dir / "page_001.plant.json"
        json_path.write_text(json.dumps({
            "junction_points": [{}] * 7,
            "pipelines": [{}] * 3,
            "connections": [{}] * 2,
        }), encoding="utf-8")

        assert batch_process.export_counts(xml_path) == batch_process.export_counts(json_path)
        assert batch_process.export_counts(json_path) == {
            "junctions": 7, "pipelines": 3, "connections": 2}

        # У формата редактора мнемосхем таких разделов нет — считаются
        # элементы холста. «.plant.json» тоже заканчивается на «.json»,
        # и перепутать их значит выдать в сводку чужие числа
        hmi_path = out_dir / "page_001.json"
        hmi_path.write_text(json.dumps([{"type": "line"}] * 12), encoding="utf-8")
        assert batch_process.export_counts(hmi_path) == {"elements": 12}
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_survey_ignores_requested_format():
    # --no-markup не доходит до выгрузки, и --format не должен этого менять
    if not SMALL_PDF.exists():
        print("  ПРОПУСК test_survey_ignores_requested_format: нет входных файлов")
        return

    out_dir = Path(tempfile.mkdtemp(prefix="contur_batch_"))
    try:
        code, _ = _run(SMALL_PDF, out_dir, "--pages", "1", "--format", "json")
        assert code in (0, 1), f"код возврата {code}"
        assert not list(out_dir.glob("page_*.json")), "обследование выгрузило JSON"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


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
