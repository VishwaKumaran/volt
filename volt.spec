# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/volt/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    # Filter out mypyc and tomli binary extensions to force pure Python usage
    [x for x in a.binaries if 'mypyc' not in x[0] and 'tomli' not in x[0]],
    a.datas,
    [],
    name='volt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
