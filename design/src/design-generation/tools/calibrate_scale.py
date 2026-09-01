# tools/calibrate_scale.py
# Подбор масштаба детекции.
#
# Модель обучалась на изображениях, где рамка устройства занимает 0.20-0.30
# стороны кадра. При нарезке листа A0 плитками 1024 на рендере 200 dpi символ
# занимает около 0.087 — в 2.5-3.5 раза меньше, чем при обучении.
#
# Относительный размер символа = размер символа в пикселях / размер плитки,
# поэтому его можно менять двумя способами: поднимать DPI рендера или брать
# плитку меньше и масштабировать её до входа сети (imgsz). Оба варианта
# увеличивают число плиток, то есть время. Скрипт прогоняет сетку параметров
# и печатает, что каждый вариант даёт.
#
# Запуск из папки CONTUR:
#     python tools/calibrate_scale.py
#     python tools/calibrate_scale.py --pdf input/test1.pdf --grid 200x1024,300x512
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_utils  # noqa: F401  (настройка кодировки вывода)
import config

import argparse
import contextlib
import io
import statistics
import tempfile
import time

import cv2

from pdf_processor import DeviceDetector, PDFToPNGConverter

# Пары «DPI рендера × размер плитки». Шаг всегда 75% плитки.
DEFAULT_GRID = [
    (200, 1024),   # как сейчас в pdf_processor
    (300, 1024),   # как сейчас в GUI
    (200, 512),    # относительный размер символа вдвое больше
    (300, 640),    # примерно втрое больше
]


def parse_grid(text: str):
    grid = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        dpi, tile = item.lower().split("x")
        grid.append((int(dpi), int(tile)))
    return grid


def measure(pdf_path: str, page: int, dpi: int, tile: int, model_path: str) -> dict:
    png_dir = tempfile.mkdtemp()
    with contextlib.redirect_stdout(io.StringIO()):
        png_paths = PDFToPNGConverter(dpi=dpi).convert(pdf_path, png_dir, page)
    if not png_paths:
        return {"error": "не удалось отрендерить страницу"}

    image = cv2.imread(png_paths[0])
    height, width = image.shape[:2]

    detector = DeviceDetector(model_path, tile_size=tile, step=int(tile * 0.75))

    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()) as log:
        boxes = detector.detect_devices(png_paths[0])
    elapsed = time.perf_counter() - start

    tiles = 0
    for line in log.getvalue().splitlines():
        if "Плиток:" in line:
            tiles = int(line.split("Плиток:")[1].split("(")[0].strip())

    if not boxes:
        return {"boxes": 0, "seconds": elapsed, "tiles": tiles,
                "png": f"{width}x{height}", "error": "устройств не найдено"}

    sizes = sorted((box.width + box.height) / 2 for box in boxes)
    confidences = sorted(box.confidence for box in boxes)
    median_size = sizes[len(sizes) // 2]

    return {
        "png": f"{width}x{height}",
        "tiles": tiles,
        "boxes": len(boxes),
        "seconds": elapsed,
        # Главный показатель: во сколько раз символ меньше обучающего 0.20-0.30
        "relative_size": median_size / tile,
        "median_size_px": median_size,
        "conf_median": statistics.median(confidences),
        "conf_high": sum(1 for c in confidences if c >= 0.7),
        "conf_low": sum(1 for c in confidences if c < 0.5),
        "classes": {name: sum(1 for b in boxes if b.cls_name == name)
                    for name in sorted({b.cls_name for b in boxes})},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Подбор масштаба детекции")
    parser.add_argument("--pdf", default=str(config.INPUT_DIR / "test1" /
                                             "BN1-МОЛОКОХРАНИЛИЩЕ-2025Full-4.pdf"))
    parser.add_argument("--page", type=int, default=0)
    parser.add_argument("--grid", default="", help="список вида 200x1024,300x512")
    args = parser.parse_args()

    if not Path(args.pdf).exists():
        print(f"❌ Нет файла: {args.pdf}")
        return 2

    grid = parse_grid(args.grid) if args.grid else DEFAULT_GRID
    model_path = str(config.YOLO_MODEL_PATH)

    print(f"Лист: {args.pdf} (страница {args.page + 1})")
    print(f"Модель: {model_path}")
    print("При обучении рамка занимала 0.20-0.30 стороны кадра\n")

    header = (f"{'DPI':>5} {'плитка':>7} {'плиток':>7} {'устройств':>10} "
              f"{'отн.размер':>11} {'увер.med':>9} {'>=0.7':>6} {'<0.5':>5} {'время':>8}")
    print(header)
    print("-" * len(header))

    results = []
    for dpi, tile in grid:
        result = measure(args.pdf, args.page, dpi, tile, model_path)
        result.update({"dpi": dpi, "tile": tile})
        results.append(result)

        if result.get("error") and not result.get("boxes"):
            print(f"{dpi:>5} {tile:>7} {'—':>7} {'—':>10}   {result['error']}")
            continue

        print(f"{dpi:>5} {tile:>7} {result['tiles']:>7} {result['boxes']:>10} "
              f"{result['relative_size']:>11.3f} {result['conf_median']:>9.2f} "
              f"{result['conf_high']:>6} {result['conf_low']:>5} {result['seconds']:>7.1f}с")

    print()
    usable = [r for r in results if r.get("boxes")]
    if usable:
        # Лучший — тот, у кого больше всего уверенных детекций;
        # при равенстве выигрывает более быстрый
        best = max(usable, key=lambda r: (r["conf_high"], -r["seconds"]))
        print(f"Больше всего уверенных детекций: {best['dpi']} dpi, плитка {best['tile']} "
              f"({best['conf_high']} рамок с уверенностью >= 0.7 за {best['seconds']:.0f} с)")
        print("Классы:", best.get("classes"))
        print("\nЧтобы закрепить выбор, задайте переменные окружения:")
        print(f"   CONTUR_YOLO_DPI={best['dpi']}")
        print(f"   CONTUR_YOLO_TILE_SIZE={best['tile']}")
        print(f"   CONTUR_YOLO_STEP={int(best['tile'] * 0.75)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
