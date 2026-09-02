# tests/test_detection_engine.py
# Выбор движка детекции: PyTorch или выгруженная модель OpenVINO.
#
# Замер на контрольном листе A0, минимум из трёх прогонов: PyTorch 73 с,
# OpenVINO на процессоре 49 с, и все 257 рамок совпали попарно без единого
# сдвига. На встроенной графике быстрее втрое, но десять рамок из 257
# расходятся на 34-1202 пикселя — поэтому устройство задано жёстко.
#
# Здесь проверяется не скорость, а безопасность переключения:
#   - без установленного openvino выгруженная модель игнорируется;
#   - путь к весам не подменяется, иначе обесценился бы весь кэш разметки;
#   - на графику нельзя съехать случайно.
#
# Запуск из папки CONTUR:
#     python tests/test_detection_engine.py
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contur.core import config
from contur.core import console_utils  # noqa: F401  (кодировка вывода, как в точках входа)
from contur.pdf.pdf_processor import DeviceDetector


def _with(engine="auto", openvino_installed=True, exported=True):
    """Подставляет обстановку: движок, наличие пакета и выгруженной модели."""
    spec = object() if openvino_installed else None
    return (mock.patch.object(config, "YOLO_ENGINE", engine),
            mock.patch("importlib.util.find_spec", return_value=spec),
            mock.patch.object(Path, "is_dir", return_value=exported))


def _find(**setup):
    patches = _with(**setup)
    for patch in patches:
        patch.start()
    try:
        return config.find_openvino_model()
    finally:
        for patch in patches:
            patch.stop()


# ---------------------------------------------------------------- выбор

def test_exported_model_is_used_when_available():
    assert _find() is not None, "выгруженная модель не найдена при полной обстановке"


def test_missing_package_falls_back_to_torch():
    # Выгрузка могла остаться от прежней установки, а сам пакет уже удалён.
    # Без проверки загрузка такой модели падает — и приложение вместе с ней
    assert _find(openvino_installed=False) is None, \
        "без установленного openvino выгруженная модель всё равно выбрана"


def test_missing_export_falls_back_to_torch():
    assert _find(exported=False) is None


def test_engine_can_be_pinned_to_torch():
    # Нужно, чтобы сравнить движки или откатиться, ничего не удаляя
    assert _find(engine="torch") is None, "CONTUR_YOLO_ENGINE=torch не действует"


# ---------------------------------------------------------------- безопасность

def test_weights_path_is_not_substituted():
    # На пути к весам держится ключ кэша разметки: подмена обесценила бы
    # весь накопленный кэш, хотя результат детекции тот же самый
    weights = str(config.YOLO_MODEL_PATH)
    detector = DeviceDetector(model_path=weights)

    assert detector.model_path == weights, "путь к весам подменён при создании"

    with mock.patch.object(config, "find_openvino_model",
                           return_value=Path("выгруженная")), \
         mock.patch("ultralytics.YOLO", create=True) as yolo:
        detector._load_model()

    assert detector.model_path == weights, "путь к весам подменён при загрузке"
    assert "выгруженная" in str(yolo.call_args[0][0]), \
        "выгруженная модель не передана в YOLO"


def test_torch_gets_no_device_argument():
    # У PyTorch довод device не нужен, и передавать его незачем
    detector = DeviceDetector(model_path=str(config.YOLO_MODEL_PATH))

    with mock.patch.object(config, "find_openvino_model", return_value=None), \
         mock.patch("ultralytics.YOLO", create=True):
        detector._load_model()

    assert detector.device is None, f"устройство при PyTorch: {detector.device!r}"


def test_openvino_runs_on_processor_only():
    # На встроенной графике десять рамок из 257 расходятся: съехать туда
    # случайно нельзя
    assert "gpu" not in config.OPENVINO_DEVICE.lower(), \
        f"движок настроен на графику: {config.OPENVINO_DEVICE}"

    detector = DeviceDetector(model_path=str(config.YOLO_MODEL_PATH))
    with mock.patch.object(config, "find_openvino_model",
                           return_value=Path("выгруженная")), \
         mock.patch("ultralytics.YOLO", create=True):
        detector._load_model()

    assert detector.device == config.OPENVINO_DEVICE
    assert "cpu" in detector.device.lower(), f"устройство: {detector.device}"


def test_export_tool_keeps_the_batch_and_dynamic_shape():
    # Две грабли, на которых выгрузка ломается уже в работе:
    #   batch=1 по умолчанию -> got [4,...] expecting [1,...]
    #   batch=4 без dynamic  -> got [2,...] expecting [4,...] на последней пачке
    source = (Path(__file__).resolve().parent.parent /
              "tools" / "export_openvino.py").read_text(encoding="utf-8")

    assert "batch=batch" in source, "выгрузка не учитывает размер пачки детектора"
    assert "dynamic=True" in source, "выгрузка без изменяемой размерности"


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
