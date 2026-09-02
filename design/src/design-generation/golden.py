# golden.py
# Эталонные показатели контрольного листа и сверка с ними.
#
# Зачем. Конвейер держится на числах — сколько сегментов разобрано, сколько
# устройств найдено и подписано, сколько получилось труб и связей. Эти числа
# лежали только в описании проекта, то есть сверялись глазами и по памяти. Именно так
# в проект дважды приезжали тихие регрессии: разметка теряла половину линий,
# а отчёт показывал правдоподобные цифры, и никто не замечал неделями.
#
# Теперь показатели записаны в tests/golden/*.json, и check_pipeline сверяет
# с ними каждый прогон. Расхождение — это либо поломка, либо намеренное
# изменение; во втором случае эталон обновляется отдельной командой, и правка
# видна в истории отдельным коммитом.
#
# Сам размеченный SVG в репозиторий не кладём: он восстанавливается из PDF
# и весов модели, а полтора мегабайта в истории ни к чему. Вместо него хеш.
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

GOLDEN_DIR = Path(__file__).resolve().parent / "tests" / "golden"

# Показатели времени шумят от загрузки машины, поэтому сверяются с запасом.
# Четверть — то, что уже не спишешь на шум: замеры разметки от прогона
# к прогону расходились на 5-8%.
TIME_TOLERANCE = 0.25

# Ключи, которые сверяются как время, а не как точное число
TIME_KEYS = ("время_запуска_с", "время_разметки_с")


def path_for(pdf_path: str, page: int) -> Path:
    return GOLDEN_DIR / f"{Path(pdf_path).stem}_лист{page + 1}.json"


def file_digest(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def load(pdf_path: str, page: int) -> Optional[Dict[str, Any]]:
    target = path_for(pdf_path, page)
    if not target.exists():
        return None
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"⚠️ Эталон не читается ({target.name}): {e}")
        return None


def save(pdf_path: str, page: int, metrics: Dict[str, Any]) -> Path:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    target = path_for(pdf_path, page)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, sort_keys=True)
    return target


def compare(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    # Возвращает список расхождений человеческим языком. Пустой — всё сошлось.
    problems = []

    for key, want in sorted(expected.items()):
        if key not in actual:
            # Показатель мог не считаться в этом прогоне — например, экспорт
            # не запускался без --svg. Это не расхождение
            continue

        got = actual[key]
        if key in TIME_KEYS:
            if not isinstance(want, (int, float)) or not want:
                continue
            if got > want * (1 + TIME_TOLERANCE):
                problems.append(f"{key}: было {want}, стало {got} "
                                f"(медленнее на {(got / want - 1) * 100:.0f}%)")
            continue

        if got != want:
            problems.append(f"{key}: было {want}, стало {got}")

    new_keys = sorted(set(actual) - set(expected))
    if new_keys:
        problems.append("новые показатели, эталон не обновлён: " + ", ".join(new_keys))

    return problems


def format_report(pdf_path: str, page: int, problems: List[str]) -> str:
    if not problems:
        return "  [OK]   сверка с эталоном: расхождений нет"

    lines = [f"  [СБОЙ] сверка с эталоном ({path_for(pdf_path, page).name}):"]
    lines += [f"           {p}" for p in problems]
    lines.append("           если изменение намеренное: "
                 "python check_pipeline.py --svg <svg> --update-golden")
    return "\n".join(lines)
