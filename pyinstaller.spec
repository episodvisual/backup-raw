# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.osx import osxutils

block_cipher = None

app_name = "BACKUP RAW"
bundle_id = "id.episodevisual.backupraw"

a = Analysis(
    ['src/BACKUP_RAW.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/app.icns', 'resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=app_name,
    debug=False,
    strip=False,
    upx=False,
    console=False,  # windowed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.icns',
)

app = BUNDLE(
    exe,
    name=f"{app_name}.app",
    icon='resources/app.icns',
    bundle_identifier=bundle_id,
    info_plist='Info.plist',
)
