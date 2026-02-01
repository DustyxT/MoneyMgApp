# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\USER\\Desktop\\Money management app\\backend\\main.py'],
    pathex=['C:\\Users\\USER\\Desktop\\Money management app\\backend'],
    binaries=[],
    datas=[('C:\\Users\\USER\\Desktop\\Money management app\\frontend', 'frontend')],
    hiddenimports=['uvicorn', 'fastapi', 'pandas', 'numpy', 'math', 'uuid', 'datetime', 'json', 'pathlib', 'typing', 'routes', 'services', 'models', 'utils'],
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
    a.binaries,
    a.datas,
    [],
    name='ManageUrWealth',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
