# tools/export_openvino.py
# Выгрузка модели YOLO в формат OpenVINO.
#
# Зачем: детекция — единственная медленная операция проекта. На контрольном
# листе A0, минимум из трёх прогонов: PyTorch 73 с, OpenVINO 49 с, и все
# 257 рамок совпадают попарно без единого сдвига.
#
# Две тонкости, на которых выгрузка ломается уже в работе, а не при выгрузке:
#
#   1. По умолчанию модель выгружается под один кадр, а детектор подаёт по
#      четыре плитки сразу:
#          got [4,3,1024,1024] expecting [1,3,1024,1024]
#   2. Одного batch=4 мало: плиток на листе 234, и последняя пачка неполная:
#          got [2,3,1024,1024] expecting [4,3,1024,1024]
#      Поэтому размерность делается изменяемой.
#
# Выгрузку надо повторять после каждого переобучения модели: config берёт
# папку рядом с весами и не проверяет, от тех ли они весов.
#
# Запуск из папки CONTUR:
#     python tools/export_openvino.py
#     python tools/export_openvino.py --remove   # вернуться на PyTorch
import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import config
from contur.core import console_utils  # noqa: F401  (настройка кодировки вывода)
from contur.pdf.pdf_processor import DeviceDetector


def main() -> int:
    parser = argparse.ArgumentParser(description="Выгрузка модели в формат OpenVINO")
    parser.add_argument("--remove", action="store_true",
                        help="удалить выгруженную модель и вернуться на PyTorch")
    args = parser.parse_args()

    weights = Path(config.YOLO_MODEL_PATH)
    target = weights.with_name(weights.stem + "_openvino_model")

    if args.remove:
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
            print(f"🗑️ Удалено: {target}")
            print("   Приложение вернулось на PyTorch.")
        else:
            print("Выгруженной модели и не было.")
        return 0

    if not weights.exists():
        print(f"❌ Веса не найдены: {weights}")
        return 2

    try:
        import openvino  # noqa: F401
    except ImportError:
        print("❌ Не установлен openvino:  python -m pip install openvino")
        return 2

    if target.is_dir():
        print(f"Прежняя выгрузка удаляется: {target}")
        shutil.rmtree(target, ignore_errors=True)

    batch = DeviceDetector(model_path=str(weights)).batch_size
    print(f"Веса:  {weights}")
    print(f"Пачка: {batch}, размерность изменяемая, вход {config.YOLO_IMGSZ}")

    from ultralytics import YOLO
    started = time.perf_counter()
    YOLO(str(weights)).export(format="openvino", imgsz=config.YOLO_IMGSZ,
                              batch=batch, dynamic=True)
    print(f"\n✅ Выгружено за {time.perf_counter() - started:.0f} с: {target}")
    print("   Приложение подхватит её само. Проверьте контрольные числа:")
    print("   python check_pipeline.py --svg <размеченный.svg>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
