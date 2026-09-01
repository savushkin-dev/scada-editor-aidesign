# -*- mode: python ; coding: utf-8 -*-
# Сборка:  pyinstaller МоеПриложение.spec
#
# Модель YOLO вкладывается в сборку — config.find_yolo_model() ищет её
# сначала рядом с exe (runs/detect/<запуск>/weights/best.pt), затем внутри
# сборки. Можно и не вкладывать: тогда положите папку runs рядом с exe
# или задайте переменную окружения CONTUR_YOLO_MODEL.
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

MODEL_RELATIVE = Path('runs/detect/train2/weights/best.pt')

datas = []
if MODEL_RELATIVE.exists():
    datas.append((str(MODEL_RELATIVE), str(MODEL_RELATIVE.parent)))

# Каталог готовых фигур библиотеки: без него выгрузка молча
# остаётся с двумя встроенными фигурами и рисует устройства по-старому.
# Ищется через config.BUNDLE_DIR, то есть в корне вшитых ресурсов
CATALOGUE = Path('hmi_symbols.json')
if CATALOGUE.exists():
    datas.append((str(CATALOGUE), '.'))

# ultralytics тянет свои конфиги и подмодули, которые статический анализ не находит
datas += collect_data_files('ultralytics')

a = Analysis(
    ['xml_viewer.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    # lupa при импорте сама перебирает файлы своей папки, выбирая самую
    # новую сборку Lua: os.listdir(os.path.dirname(__file__)) с поиском
    # lua*.pyd. Статический анализ такого не видит — папки lupa в сборке
    # не оказывалось, и приложение падало ещё до появления окна:
    #     FileNotFoundError: [WinError 3] ... '_internal\\lupa'
    # То есть разбор Lua в собранном виде не работал вовсе.
    hiddenimports=(collect_submodules('ultralytics') + collect_submodules('lupa')
                   + ['workers', 'widgets']),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='МоеПриложение',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='МоеПриложение',
)
