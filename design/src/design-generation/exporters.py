# exporters.py
# Выбор формата выгрузки по расширению файла.
#
# Каналов выдачи стало три, и место выбора должно быть одно: окно (Ctrl+E)
# и пакетная обработка не должны решать это каждое по-своему, иначе появится
# формат, который умеет только один из них.
#
#   *.json        — формат редактора мнемосхем: плоский массив элементов
#                   холста. Это то, что читает конечный проект
#   *.plant.json  — PlantGeometry в JSON: дерево техобъектов, трубы,
#                   связи, разметка листа. Редактор его не понимает,
#                   но в нём есть всё, что знает конвейер
#   *.xml         — тот же PlantGeometry в XML, формат нынешнего потребителя
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from data_models import Contour, DeviceMatch
from hmi_export import export_current_visualization_hmi
from json_export import export_current_visualization_json
from xml_export import export_current_visualization

# расширение → (человеческое имя, функция выгрузки).
# Порядок важен: составное «.plant.json» проверяется раньше «.json»
FORMATS: Dict[str, Tuple[str, Callable[..., bool]]] = {
    ".plant.json": ("PlantGeometry JSON", export_current_visualization_json),
    ".xml": ("XML", export_current_visualization),
    ".json": ("JSON для редактора", export_current_visualization_hmi),
}

# Формат по умолчанию — тот, ради которого выгрузку и открывают:
# файл уходит в редактор мнемосхем
DEFAULT_FORMAT = ".json"

# Фильтр для диалога сохранения: порядок задаёт формат по умолчанию
FILE_DIALOG_FILTER = ("JSON для редактора мнемосхем (*.json);;"
                      "XML files (*.xml);;"
                      "JSON PlantGeometry (*.plant.json)")


def suffix_of(output_path: str) -> str:
    """Расширение, по которому выбирается формат ('' — незнакомое)."""
    name = Path(output_path).name.lower()
    for suffix in FORMATS:
        if name.endswith(suffix):
            return suffix
    return ""


def format_name(output_path: str) -> str:
    """Как назвать формат человеку."""
    suffix = suffix_of(output_path)
    return FORMATS[suffix or DEFAULT_FORMAT][0]


def with_suffix(output_path: str, selected_filter: str = "") -> str:
    """Дописывает расширение, если человек его не набрал.

    Диалог сохранения в Qt возвращает имя без расширения, когда его не ввели
    руками, — а формат выбирается как раз по расширению.
    """
    if suffix_of(output_path):
        return str(Path(output_path))

    # Расширение берётся из самого фильтра («… (*.plant.json)»), а не из его
    # названия: названия переводятся и переписываются, шаблон — нет
    for suffix in FORMATS:
        if f"(*{suffix})" in selected_filter:
            return output_path + suffix

    return output_path + DEFAULT_FORMAT


def export_visualization(svg_path: str, output_path: str,
                         matches: List[DeviceMatch], contours: List[Contour],
                         use_percent_coords: bool = True,
                         current_operation_id: Optional[str] = None,
                         pdf_size: Optional[Tuple[float, float]] = None,
                         snap_to_geometry: bool = True) -> bool:
    """Выгружает лист в формате, который назван расширением output_path."""
    suffix = suffix_of(output_path)
    if not suffix:
        raise ValueError(f"неизвестный формат выгрузки: {Path(output_path).suffix or output_path!r}; "
                         f"допустимы {', '.join(FORMATS)}")

    _, export = FORMATS[suffix]
    return export(svg_path, output_path, matches, contours,
                  use_percent_coords=use_percent_coords,
                  current_operation_id=current_operation_id,
                  pdf_size=pdf_size, snap_to_geometry=snap_to_geometry)
