# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/volt/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["ddc459050edb75a05942__mypyc"],
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
    name='volt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    onefile=True,
    console=True,
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
    strip=True,
    upx=False,
    upx_exclude=[],
    name='volt',
)
