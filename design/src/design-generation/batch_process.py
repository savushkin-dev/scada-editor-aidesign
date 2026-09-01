# batch_process.py
# Пакетная обработка многостраничного PDF.
#
# Приложение работает с одной страницей за раз: для файла из 265 страниц это
# 265 ручных прогонов. Здесь тот же конвейер (геометрия -> сопоставление ->
# разметка -> экспорт) прогоняется по всем страницам подряд, каждая даёт
# свою выгрузку (XML или JSON, ключ --format), а в конце печатается сводка
# с показателями по страницам.
#
# Разметка кэшируется, поэтому повторный запуск по тем же страницам
# проходит почти мгновенно и годится, чтобы доделать прерванную обработку.
#
# Запуск из папки CONTUR:
#     python batch_process.py --pdf схема.pdf --io-lua main.io.lua --objects-lua main.objects.lua
#     python batch_process.py --pdf схема.pdf --io-lua main.io.lua main.wago.lua ...
#     python batch_process.py --pdf схема.pdf --pages 1-20 --out результаты
import console_utils  # noqa: F401  (настройка кодировки вывода)
import config

import argparse
import contextlib
import io
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_pages(text: str, total: int):
    # '1-20', '3', '1-5,8,11-13' — номера с единицы, как видит пользователь
    if not text:
        return list(range(total))

    pages = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            first, last = part.split("-", 1)
            pages.extend(range(int(first) - 1, int(last)))
        else:
            pages.append(int(part) - 1)

    return [p for p in sorted(set(pages)) if 0 <= p < total]


# значение --format → расширение файла страницы
FORMAT_SUFFIX = {"xml": ".xml", "json": ".json", "plant-json": ".plant.json"}


def export_counts(path: Path) -> dict:
    """Показатели из готовой выгрузки — что записано, а не что в памяти.

    У PlantGeometry (XML и `.plant.json`) это точки сопряжения, трубы
    и связи; у формата редактора мнемосхем таких разделов нет — там
    считаются элементы холста.
    """
    name = path.name.lower()

    if name.endswith(".plant.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        return {
            "junctions": len(document.get("junction_points", [])),
            "pipelines": len(document.get("pipelines", [])),
            "connections": len(document.get("connections", [])),
        }

    if name.endswith(".json"):
        return {"elements": len(json.loads(path.read_text(encoding="utf-8")))}

    root = ET.parse(path).getroot()
    connections = root.find("Connections")
    return {
        "junctions": int(root.get("junction-points-count") or 0),
        "pipelines": int(root.get("pipelines-count") or 0),
        "connections": int(connections.get("count")) if connections is not None else 0,
    }


def process_page(page: int, args, shared) -> dict:
    from extract_geometry import extract_line_segments, extract_text_elements
    from segment_data import SegmentData
    from contour_detector import find_contours, find_all_contour_names_by_proximity, gen_xml
    from device_matcher import (load_pdf_geometry, find_pdf_device_texts, match_devices,
                                build_match_report, sheet_object_from_texts)
    from data_models import Contour
    from pdf_processor import PDFToSVGConverter
    from exporters import export_visualization
    from xml_export import get_pdf_page_size

    result = {"page": page + 1}
    started = time.perf_counter()

    raw = extract_line_segments(args.pdf, page)
    texts = extract_text_elements(args.pdf, page)
    if not raw:
        result["skipped"] = "нет векторной графики"
        return result

    segments = [SegmentData(**s) for s in raw]
    contours = find_contours(segments)
    find_all_contour_names_by_proximity(contours, segments, texts, shared["lua_names"],
                                        config.CONTOUR_NAME_MAX_DISTANCE)

    geometry_xml = shared["out_dir"] / f"page_{page + 1:03d}_geometry.xml"
    gen_xml(segments, contours).write(str(geometry_xml), encoding="utf-8", xml_declaration=True)

    pdf_contours, _ = load_pdf_geometry(str(geometry_xml))
    device_texts = find_pdf_device_texts(args.pdf, page)
    matches = match_devices(shared["lua_devices"], pdf_contours, device_texts,
                            sheet_object_from_texts(texts))

    report = build_match_report(shared["lua_devices"], pdf_contours, device_texts, matches)
    result.update({
        "contours": len(contours),
        "named_contours": sum(1 for c in contours if c.name),
        "matches": len(matches),
        "missing": len(report["missing_on_drawing"]),
        "unknown": len(report["unknown_labels"]),
    })

    # Список найденных устройств нужен, чтобы посчитать покрытие по всему проекту
    result["devices"] = sorted({m.lua_name for m in matches if m.lua_name})
    result["objects"] = sorted({m.tech_object for m in matches if m.tech_object})

    if not matches:
        result["skipped"] = "нет сопоставленных устройств"
        result["seconds"] = time.perf_counter() - started
        return result

    if args.no_markup:
        # Обследование покрытия: разметка и экспорт на сопоставление не влияют
        result["seconds"] = time.perf_counter() - started
        return result

    # Разметка и экспорт
    svg_path = shared["out_dir"] / f"page_{page + 1:03d}_marked.svg"
    formats = ["xml", "json"] if args.format == "both" else [args.format]
    export_paths = [shared["out_dir"] / f"page_{page + 1:03d}{FORMAT_SUFFIX[fmt]}"
                    for fmt in formats]

    matched = [(m.lua_name, m.coordinates[0], m.coordinates[1]) for m in matches if m.lua_name]
    converter = PDFToSVGConverter(scale_factor=args.scale, page_number=page,
                                  matched_devices=matched)
    marked_svg, _ = converter.convert(args.pdf, str(svg_path))
    if not marked_svg:
        result["skipped"] = "разметка не удалась"
        result["seconds"] = time.perf_counter() - started
        return result

    export_contours = [Contour(name=c.name, bounds=c.bounds, center=c.center, tech_object=c.name)
                       for c in contours if c.name]
    pdf_size = get_pdf_page_size(args.pdf, page)

    # Каждый формат выгружается своим проходом: разметка при этом разбирается
    # заново, поэтому --format both стоит примерно вдвое дороже одного формата
    exported = [path for path in export_paths
                if export_visualization(marked_svg, str(path), matches, export_contours,
                                        pdf_size=pdf_size)]
    if exported:
        result["exported"] = [path.name for path in exported]
        for path in exported:
            result.update(export_counts(path))
    else:
        result["skipped"] = "экспорт не удался"

    result["seconds"] = time.perf_counter() - started
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Пакетная обработка страниц PDF")
    parser.add_argument("--pdf", required=True, help="многостраничная схема")
    # Файлов устройств бывает несколько (main.io.lua вместе с main.wago.lua) —
    # окно грузит их вместе, и пакетная обработка должна видеть столько же.
    # С одним файлом на проекте mozzarella терялся 41 устройство, а покрытие
    # считалось от неверного знаменателя — 730 вместо 771.
    parser.add_argument("--io-lua", nargs="+",
                        default=[str(config.INPUT_DIR / "test1" / "main.io.lua")],
                        help="main.io.lua, можно несколько файлов подряд")
    parser.add_argument("--objects-lua", default=str(config.INPUT_DIR / "test1" / "main.objects.lua"))
    parser.add_argument("--pages", default="", help="1-20 или 3,5,9 (по умолчанию все)")
    parser.add_argument("--out", default="", help="папка результатов")
    parser.add_argument("--scale", type=float, default=1.25, help="масштаб SVG")
    parser.add_argument("--format", choices=("xml", "json", "plant-json", "both"),
                        default="xml",
                        help="формат выгрузки страницы: xml — PlantGeometry (page_NNN.xml); "
                             "json — формат редактора мнемосхем (page_NNN.json); "
                             "plant-json — PlantGeometry в JSON (page_NNN.plant.json); "
                             "both — xml и json сразу (стоит вдвое дороже)")
    parser.add_argument("--quiet", action="store_true", help="гасить вывод этапов")
    parser.add_argument("--no-markup", action="store_true",
                        help="только геометрия и сопоставление, без разметки YOLO и экспорта: "
                             "быстрое обследование покрытия по всем страницам")
    args = parser.parse_args()

    for path in (args.pdf, args.objects_lua, *args.io_lua):
        if not Path(path).exists():
            print(f"❌ Нет файла: {path}")
            return 2

    from extract_geometry import page_count
    from parse_lua import merge_lua_data, parse_lua_file
    from parse_lua_objects import parse_objects_file, extract_all_data
    from device_matcher import extract_lua_names

    total = page_count(args.pdf)
    pages = parse_pages(args.pages, total)
    if not pages:
        print("❌ Не выбрано ни одной страницы")
        return 2

    out_dir = Path(args.out) if args.out else config.OUTPUT_DIR / "batch"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Файл: {args.pdf}")
    print(f"Страниц в файле: {total}, обрабатывается: {len(pages)}")
    print(f"Результаты: {out_dir}\n")

    print("Разбор Lua...")
    lua_devices = merge_lua_data([parse_lua_file(path) for path in args.io_lua])
    lua_objects = extract_all_data(parse_objects_file(args.objects_lua))

    # Разобранное надо ещё и загрузить. Раньше пакетный прогон только читал
    # файл ради имён объектов, а описание операций оставалось незагруженным —
    # и каждая страница уезжала без состояний устройств: `contur_states`
    # не было ни у одного из 233 устройств контрольного листа, хотя тот же
    # лист через окно и через check_pipeline давал 1911
    from objects_loader import objects_data

    objects_data.load_from_json(lua_objects)
    print(f"   устройств: {len(lua_devices['devices'])}, "
          f"техобъектов: {len(lua_objects['tech_objects'])}\n")

    shared = {
        "lua_devices": lua_devices,
        "lua_names": extract_lua_names(lua_objects),
        "out_dir": out_dir,
    }

    header = (f"{'стр.':>5} {'контуров':>9} {'сопост.':>8} {'связок':>7} "
              f"{'труб':>6} {'соедин.':>8} {'время':>7}  примечание")
    print(header)
    print("-" * len(header))

    results = []
    for page in pages:
        try:
            if args.quiet:
                with contextlib.redirect_stdout(io.StringIO()):
                    result = process_page(page, args, shared)
            else:
                buffer = io.StringIO()
                with contextlib.redirect_stdout(buffer):
                    result = process_page(page, args, shared)
        except Exception as e:
            result = {"page": page + 1, "skipped": f"{type(e).__name__}: {e}"}

        results.append(result)
        # У формата редактора нет труб и связей — вместо них видно,
        # сколько элементов холста получила страница
        note = result.get("skipped", "")
        if not note and "elements" in result:
            note = f"элементов: {result['elements']}"
        print(f"{result['page']:>5} {result.get('contours', '—'):>9} "
              f"{result.get('matches', '—'):>8} {result.get('junctions', '—'):>7} "
              f"{result.get('pipelines', '—'):>6} {result.get('connections', '—'):>8} "
              f"{result.get('seconds', 0):>6.0f}с  {note}")

    done = [r for r in results if r.get("exported") or (args.no_markup and not r.get("skipped"))]
    print()
    print(f"Обработано страниц: {len(done)} из {len(pages)}")
    if done:
        print(f"   сопоставлено устройств (с повторами по страницам): "
              f"{sum(r.get('matches', 0) for r in done)}")
        print(f"   соединений: {sum(r.get('connections', 0) for r in done)}")
        # Сумма по листам, а не по проекту: устройство, отсутствующее на своём
        # листе, обычно нарисовано на соседнем. Проектное число — ниже, в покрытии
        print(f"   нет на своём листе (сумма по страницам): "
              f"{sum(r.get('missing', 0) for r in done)}, "
              f"нет в Lua: {sum(r.get('unknown', 0) for r in done)}")
    print(f"   суммарное время: {sum(r.get('seconds', 0) for r in results):.0f} с")

    # Покрытие: сколько устройств из Lua найдено суммарно по всем страницам
    found_devices, found_objects = set(), set()
    for r in results:
        found_devices.update(r.get("devices", []))
        found_objects.update(r.get("objects", []))

    all_devices = {d["name"] for d in lua_devices.get("devices", []) if d.get("name")}
    missing = sorted(all_devices - found_devices)

    full_run = len(pages) == total
    print()
    print("ПОКРЫТИЕ" + (" ПРОЕКТА" if full_run else f" ПО ОБРАБОТАННЫМ СТРАНИЦАМ ({len(pages)} из {total})"))
    print(f"   устройств в Lua:              {len(all_devices)}")
    print(f"   найдено:                      {len(found_devices)} "
          f"({len(found_devices) * 100 // max(1, len(all_devices))}%)")
    if full_run:
        print(f"   не найдено ни на одной странице: {len(missing)}")
    else:
        # На части страниц вывод о покрытии всего проекта делать нельзя
        print(f"   не встретилось на этих страницах: {len(missing)} "
              f"(на остальных страницах могут быть)")
    print(f"   техобъектов встретилось:      {len(found_objects)}")
    if missing:
        print(f"   примеры отсутствующих: {', '.join(missing[:12])}")

    coverage = out_dir / "coverage.json"
    with open(coverage, "w", encoding="utf-8") as f:
        json.dump({"pages_processed": len(pages), "pages_total": total,
                   "full_run": full_run,
                   "total": sorted(all_devices), "found": sorted(found_devices),
                   "missing": missing, "objects": sorted(found_objects)},
                  f, ensure_ascii=False, indent=2)
    print(f"   подробности: {coverage}")

    summary = out_dir / "summary.json"
    with open(summary, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nСводка: {summary}")

    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
