# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['vmctl.py'],
    pathex=[".", "lib"],
    binaries=[],
    datas=[],
    hiddenimports=[ ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,        # <-- Faster import time
    optimize=1,            # <-- Bytecode optimization
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='vmctl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             # <-- No UPX = faster load
    upx_exclude=[],
    console=True,
    runtime_tmpdir="C:\\TEMP",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=False,          # <-- You requested onefile
    noarchive=True,
)