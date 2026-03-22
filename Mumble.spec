# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
src_root = project_root / "src"
assets_root = src_root / "assets"
icon_path = assets_root / "mumble_icon.png"


a = Analysis(
    ["run_modern_mumble.py"],
    pathex=[str(src_root)],
    binaries=[],
    datas=[(str(assets_root), "assets")],
    hiddenimports=[
        "ui_redesign.main_app",
        "shared.adaptive_speech",
        "shared.cloud_speech",
    ],
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
    name="Mumble",
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
    icon=[str(icon_path)] if icon_path.exists() else None,
)
