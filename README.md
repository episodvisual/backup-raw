# BACKUP RAW – macOS .app (GitHub Actions)

Repo ini sudah siap **commit** dan **build otomatis** .app untuk macOS melalui GitHub Actions menggunakan PyInstaller.

> **Catatan kompatibilitas macOS:** Toolchain modern (PyInstaller + PyQt5) umumnya mendukung **macOS 10.13 High Sierra (2017)** ke atas. Target **2015 (OS X 10.11/El Capitan)** sering **tidak realistis** dengan library modern. Workflow ini menetapkan `LSMinimumSystemVersion` ke **10.13** agar build stabil.
> Jika Anda benar-benar perlu dukungan < 10.13, Anda harus membangun di Mac lama dengan toolchain lama (tidak disarankan).

## Struktur
```
.
├── src/
│   └── BACKUP_RAW.py
├── resources/
│   ├── logoku.ico
│   └── app.icns            # dibuat otomatis oleh workflow dari logoku.ico
├── tools/
│   └── ico_to_icns.py      # konversi ICO -> ICNS
├── .github/workflows/
│   └── macos-app.yml       # workflow untuk build & upload artifact .app
├── Info.plist
├── pyinstaller.spec
├── requirements.txt
└── README.md
```

## Cara pakai (disarankan via GitHub Actions)
1. Buat repo baru di GitHub dan upload semua isi ZIP ini.
2. Pastikan **Actions** aktif di repo.
3. Push/commit ke branch `main` → Workflow otomatis jalan.
4. Setelah sukses, file **`BACKUP RAW.app`** akan tersedia di tab **Actions → build-macos → Artifacts**.

## Build lokal (opsional, di Mac)
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pyinstaller pillow
python tools/ico_to_icns.py resources/logoku.ico resources/app.icns
pyinstaller --clean pyinstaller.spec
# Hasil: dist/BACKUP RAW.app
```

## Ganti ikon & metadata
- Ganti `resources/logoku.ico` dengan ikon Anda → workflow akan membuat `resources/app.icns` otomatis.
- Ubah **bundle identifier** di `pyinstaller.spec` (bagian `osx_bUNDLE_ID`) dan `Info.plist`.
- Edit versi/nama di `Info.plist`.

## Masalah umum
- **Gatekeeper/“App rusak”:** Klik kanan → Open (sekali), atau sign & notarize menggunakan Apple Developer ID (di luar cakupan repo ini).
- **Dukungan macOS lama:** Perlahan-lahan tidak didukung oleh binary wheel modern. Target minimal sudah di-set 10.13.

Semoga lancar! :)
