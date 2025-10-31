#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sequential Folder Backup System - Modern Interface
"""

import os
import shutil
import time
import traceback
import sys # Import sys
import warnings # Import warnings
# --- IMPOR LISENSI DIMODIFIKASI (OFFLINE) ---
# import requests (DIHAPUS)
# import json (DIHAPUS)
# --- AKHIR IMPOR ---
from datetime import datetime
# --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar, QFrame, QMessageBox,
    QSizePolicy, QGridLayout, QDialog, QScrollBar, QListWidget, QFileDialog,
    QRadioButton, QCheckBox, QLineEdit, QGroupBox, QComboBox,
    QStackedWidget, QMenu 
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QPropertyAnimation, QEasingCurve, QSharedMemory, QUrl, QLocale, QDateTime
# --- Impor untuk logo (disederhanakan) ---
from PyQt5.QtGui import (
    QIcon, QFont, QPainter, QColor, QPen, QPainterPath, QDragEnterEvent, QDropEvent,
    QPixmap # QConicalGradient dihapus
)
# --- Akhir impor logo ---
from multiprocessing import freeze_support
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtGui import QDesktopServices
# --- AKHIR PERUBAHAN MIGRASI ---
import platform
import re
# --- Impor Tambahan untuk Lisensi Online ---
import requests
import uuid
import hashlib
import json
from functools import partial
import subprocess # <<< PERBAIKAN 1: Menambahkan import yang hilang
# --- Akhir Impor Lisensi ---

# Global sound effect object agar tidak langsung dihapus
_popup_sound_effect = None

# --- AWAL BLOK TERJEMAHAN GLOBAL ---
# Memindahkan kamus terjemahan ke scope global agar bisa diakses
# oleh dialog lisensi (yang muncul sebelum main window)

SUPPORTED_LANGUAGES = {
    'id': 'Bahasa Indonesia',
    'en': 'English'
}

def get_all_translations():
    """
    Mendefinisikan semua string UI untuk i18n.
    Ini sekarang global agar bisa diakses oleh check_license().
    """
    return {
        'app_title': {
            'id': 'BACKUP RAW',
            'en': 'BACKUP RAW',
        },
        'btn_settings_text': {
            'id': 'Pengaturan',
            'en': 'Settings',
        },
        'source_group': {
            'id': 'sumber RAW (kamera/kartu sd)',
            'en': 'RAW source (camera/sd card)',
        },
        'source_label_title': {
            'id': 'Folder Sumber:',
            'en': 'Source Folder:',
        },
        'source_label_default': {
            'id': 'Sumber tidak terdeteksi',
            'en': 'Source not detected',
        },
        'btn_change_source': {
            'id': 'Ganti...',
            'en': 'Change...',
        },
        'group_step_2': {
            'id': 'Metode',
            'en': 'Method',
        },
        'radio_mode_folder': {
            'id': 'Cocokkan via Folder JPG',
            'en': 'Match by JPG Folder',
        },
        'radio_mode_list': {
            'id': 'Cocokkan via Nama File',
            'en': 'Match by Filename',
        },
        'group_match_folders': {
            'id': 'Folder JPG (untuk Dicocokkan)',
            'en': 'JPG Folders (to Match)',
        },
        'group_file_types': {
            'id': 'Tipe File (dari Sumber)',
            'en': 'File Types (from Source)',
        },
        'btn_add_jpg': {
            'id': 'Tambah Folder',
            'en': 'Add Folder',
        },
        'context_delete': {
            'id': 'Hapus Pilihan',
            'en': 'Delete Selected',
        },
        'check_backup_raw_source': {
            'id': 'Salin File RAW',
            'en': 'Copy RAW Files',
        },
        'check_backup_jpg_source': {
            'id': 'Salin File JPG',
            'en': 'Copy JPG Files',
        },
        'group_filenames': {
            'id': 'Daftar Nama File',
            'en': 'Filename List',
        },
        'filename_filter_label': {
            'id': 'Pisahkan dgn koma (,) atau baris baru. Cth: _DSC1234...',
            'en': 'Separate with comma (,) or new line. E.g.: _DSC1234...',
        },
        'group_destination': {
            'id': 'Tujuan (Output)',
            'en': 'Destination (Output)',
        },
        'custom_output_label': {
            'id': 'Folder:',
            'en': 'Folder:',
        },
        'custom_output_placeholder': {
            'id': 'Pilih folder... (Wajib)',
            'en': 'Select folder... (Required)',
        },
        'btn_browse_output': {
            'id': 'Cari...',
            'en': 'Browse...',
        },
        'btn_backup': {
            'id': 'MULAI BACKUP',
            'en': 'START BACKUP',
        },
        'log_label': {
            'id': 'Log:',
            'en': 'Log:',
        },
        'btn_refresh': {
            'id': 'Segarkan',
            'en': 'Refresh',
        },
        # --- Status Messages ---
        'status_ready': {
            'id': 'Status: 🟢 Siap',
            'en': 'Status: 🟢 Ready',
        },
        'status_no_source': {
            'id': 'Status: 🔴 Folder Sumber tidak ditemukan',
            'en': 'Status: 🔴 Source folder not found',
        },
        'status_no_jpg_folder': {
            'id': 'Status: 🔴 Tidak ada folder JPG (Metode A)',
            'en': 'Status: 🔴 No JPG folder (Method A)',
        },
        'status_no_custom_output': {
            'id': 'Status: 🔴 Tidak ada folder output',
            'en': 'Status: 🔴 No output folder',
        },
        'status_no_file_type': {
            'id': 'Status: 🔴 Pilih tipe file (RAW/JPG)',
            'en': 'Status: 🔴 Select file type (RAW/JPG)',
        },
        'status_list_empty': {
            'id': 'Status: 🔴 Daftar nama file kosong',
            'en': 'Status: 🔴 Filename list empty',
        },
        'status_output_required': {
            'id': 'Status: 🔴 Folder output diperlukan',
            'en': 'Status: 🔴 Output folder required',
        },
        'status_processing': {
            'id': 'Status: 🟠 Memproses...',
            'en': 'Status: 🟠 Processing...',
        },
        'status_cancelled': {
            'id': 'Status: 🔴 Dibatalkan',
            'en': 'Status: 🔴 Cancelled',
        },
        'status_no_match': {
            'id': 'Status: ⚠️ Tidak ada file yang cocok',
            'en': 'Status: ⚠️ No matching files found',
        },
        'status_completed': {
            'id': 'Status: ✅ Selesai', 
            'en': 'Status: ✅ Completed',
        },
        'status_folders_selected': {
            'id': 'Status: {count} folder dipilih',
            'en': 'Status: {count} folder(s) selected',
        },
        
        # --- KUNCI BARU UNTUK POPUP ---
        'dialog_error_title': {
            'id': 'Error Kritis',
            'en': 'Critical Error',
        },
        'dialog_complete_title': {
            'id': 'Backup Selesai',
            'en': 'Backup Completed',
        },
        'popup_continue_backup_title': {
            'id': 'Lanjutkan Backup',
            'en': 'Continue Backup',
        },
        'popup_continue_backup_text': {
            'id': 'Folder sumber terhubung kembali. Lanjutkan backup?',
            'en': 'Source folder reconnected. Continue backup?',
        },
        'popup_disconnected_title': {
            'id': 'Sumber Terputus',
            'en': 'Source Disconnected',
        },
        'popup_disconnected_text': {
            'id': 'Folder sumber telah terputus! Backup dihentikan.',
            'en': 'Source folder has been disconnected! Backup stopped.',
        },
        'popup_settings_title': {
            'id': 'Pengaturan Bahasa',
            'en': 'Language Settings',
        },
        'popup_settings_label': {
            'id': 'Pilih Bahasa Aplikasi:',
            'en': 'Select Application Language:',
        },
        'popup_settings_ok': {
            'id': 'OK',
            'en': 'OK',
        },
        'popup_complete_files': {
            'id': '{count} file berhasil dibackup!',
            'en': '{count} files backed up successfully!',
        },
        'popup_complete_location': {
            'id': 'Lokasi: {folder}',
            'en': 'Location: {folder}',
        },
        'popup_complete_ok': {
            'id': 'OK',
            'en': 'OK',
        },
        'popup_complete_open': {
            'id': 'Buka Folder',
            'en': 'Open Folder',
        },
        'popup_complete_folder_not_found_title': {
            'id': 'Folder Tidak Ditemukan',
            'en': 'Folder Not Found',
        },
        'popup_complete_folder_not_found_text': {
            'id': 'Folder RAW tidak ditemukan atau tidak ada:\n{folder}',
            'en': 'RAW folder not found or does not exist:\n{folder}',
        },
        'popup_error_output_mandatory': {
            'id': 'Folder output wajib diisi. Silakan pilih satu.',
            'en': 'Output folder is mandatory. Please select one.',
        },
        'popup_error_no_jpg_folder': {
            'id': 'Tidak ada folder JPG tujuan yang dipilih. Harap tambahkan setidaknya satu folder JPG untuk dicocokkan.',
            'en': 'No JPG destination folder selected. Please add at least one JPG folder to match against.',
        },
        'popup_error_no_file_type': {
            'id': 'Pilih setidaknya satu tipe file (RAW atau JPG) untuk dibackup dari sumber.',
            'en': 'Please select at least one file type (RAW or JPG) to back up from the source.',
        },
        'popup_error_empty_list': {
            'id': 'Daftar nama file kosong. Harap masukkan setidaknya satu nama file.',
            'en': 'Filename list is empty. Please enter at least one filename.',
        },
        'popup_error_no_source': {
            'id': 'Folder sumber tidak dipilih atau tidak ditemukan. Harap sambungkan kamera atau pilih folder sumber secara manual.',
            'en': 'Source folder is not selected or not found. Please connect the camera or select a source folder manually.',
        },
        'popup_error_low_disk': {
            'id': 'Peringatan: Ruang disk di drive {drive} menipis (Tersisa: {mb:.1f} MB)',
            'en': 'Warning: Low disk space on drive {drive} (Available: {mb:.1f} MB)',
        },
        'popup_error_resume': {
            'id': 'Gagal melanjutkan backup:\n{e}',
            'en': 'Failed to resume backup:\n{e}',
        },
        'popup_close_title': {
            'id': 'Backup Sedang Berjalan',
            'en': 'Backup in Progress',
        },
        'popup_close_text': {
            'id': 'Backup masih berjalan. Yakin ingin keluar dan membatalkan backup?',
            'en': 'Backup is still running. Are you sure you want to exit and cancel the backup?',
        },
        'popup_disk_full': {
            'id': 'Disk Penuh! Backup dihentikan.',
            'en': 'Disk Full! Backup stopped.',
        },

        # --- KUNCI BARU UNTUK LISENSI ---
        'lic_title': {
            'id': 'Aktivasi Lisensi - BACKUP RAW',
            'en': 'License Activation - BACKUP RAW',
        },
        'lic_needed': {
            'id': 'Aktivasi Diperlukan',
            'en': 'Activation Required',
        },
        'lic_prompt': {
            'id': 'Masukkan kunci lisensi Anda untuk mengaktifkan software.',
            'en': 'Enter your license key to activate the software.',
        },
        'lic_placeholder': {
            'id': 'Contoh: XXXX-XXXX-XXXX-XXXX',
            'en': 'Example: XXXX-XXXX-XXXX-XXXX',
        },
        'lic_btn_activate': {
            'id': 'Aktivasi Online',
            'en': 'Activate Online',
        },
        'lic_btn_exit': {
            'id': 'Keluar',
            'en': 'Exit',
        },
        'lic_contacting': {
            'id': 'Menghubungi server aktivasi...',
            'en': 'Contacting activation server...',
        },
        'lic_err_empty': {
            'id': 'Kunci tidak boleh kosong. Silakan coba lagi.',
            'en': 'Key cannot be empty. Please try again.',
        },
        'lic_val_success_title': {
            'id': 'Aktivasi Berhasil',
            'en': 'Activation Successful',
        },
        'lic_val_success_text': {
            'id': 'Lisensi telah diaktivasi di PC ini. Software akan dimulai.',
            'en': 'License has been activated on this PC. The software will now start.',
        },
        'lic_val_err_save_title': {
            'id': 'Error Kritis',
            'en': 'Critical Error',
        },
        'lic_val_err_save_text': {
            'id': 'Gagal menyimpan file lisensi lokal:\n{e}\n\nPastikan Anda memiliki izin tulis.',
            'en': 'Failed to save local license file:\n{e}\n\nEnsure you have write permissions.',
        },
        'lic_err_get_hash_title': {
            'id': 'Error Kritis',
            'en': 'Critical Error',
        },
        'lic_err_get_hash_text': {
            'id': 'Gagal mendapatkan ID PC unik. Tidak dapat menjalankan software.',
            'en': 'Failed to get unique PC ID. Cannot run software.',
        },
        # Kunci untuk ValidationWorker (dikirim ke dialog)
        'lic_val_invalid_key': {
            'id': 'Aktivasi Gagal: Kunci lisensi tidak valid.',
            'en': 'Activation Failed: Invalid license key.',
        },
        'lic_val_data_format': {
            'id': 'Error: Format data server salah.',
            'en': 'Error: Invalid server data format.',
        },
        'lic_val_key_used': {
            'id': 'Aktivasi Gagal: Kunci ini telah dipakai di PC lain.',
            'en': 'Activation Failed: This key is already used on another PC.',
        },
        'lic_val_server_fail': {
            'id': 'Gagal aktivasi di server (Error: {code})',
            'en': 'Failed to activate on server (Error: {code})',
        },
        'lic_val_no_internet': {
            'id': 'Aktivasi Gagal: Cek koneksi internet Anda.',
            'en': 'Activation Failed: Check your internet connection.',
        },
        'lic_val_unknown_err': {
            'id': 'Terjadi Error: {e}',
            'en': 'An Error Occurred: {e}',
        },
        'lic_val_success_saving': {
            'id': 'Aktivasi Berhasil! Menyimpan lisensi...',
            'en': 'Activation Successful! Saving license...',
        }
    }

# --- AKHIR BLOK TERJEMAHAN GLOBAL ---


# Custom QListWidget dengan drag & drop support untuk folder
class DragDropListWidget(QListWidget):
    folder_added = pyqtSignal(str)  # Signal ketika folder berhasil ditambahkan
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.setDragDropMode(QListWidget.DropOnly)
        
        # --- TAMBAHAN UNTUK KLIK KANAN & MULTI-SELECT ---
        self.setSelectionMode(QListWidget.ExtendedSelection) # Izinkan pilih banyak
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # --- AKHIR PERUBAHAN MIGRASI ---
        self.customContextMenuRequested.connect(self.show_context_menu)
        # --- AKHIR TAMBAHAN ---
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Cek apakah ada folder yang valid
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    local_path = url.toLocalFile()
                    if os.path.isdir(local_path):
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            # Cek apakah ada folder yang valid
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    local_path = url.toLocalFile()
                    if os.path.isdir(local_path):
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            folders_added = []
            
            for url in urls:
                if url.isLocalFile():
                    local_path = url.toLocalFile()
                    if os.path.isdir(local_path):
                        # Normalisasi path
                        normalized_path = os.path.normpath(local_path)
                        
                        # Cek apakah folder sudah ada di list
                        existing_items = []
                        for i in range(self.count()):
                            existing_items.append(self.item(i).text())
                        
                        if normalized_path not in existing_items:
                            folders_added.append(normalized_path)
                            self.folder_added.emit(normalized_path)
            
            if folders_added:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    # --- FUNGSI KLIK KANAN (TANPA ICON) ---
    def show_context_menu(self, pos):
        """Menampilkan menu konteks (klik kanan)"""
        # Dapatkan item di posisi kursor
        item = self.itemAt(pos)
        # Periksa juga apakah ada item yang *terpilih* (bisa jadi klik di area kosong tapi item terpilih)
        selected_items = self.selectedItems()
        
        if not selected_items: # Hanya tampilkan menu jika ada item yang terpilih
            return

        # Dapatkan main window untuk mengakses terjemahan
        main_window = self.window()
        try:
            # --- HAPUS EMOJI DARI TEKS MENU ---
            # Gunakan helper tr() yang baru di main_window
            delete_text = main_window.tr('context_delete')
        except Exception:
            delete_text = "Hapus Pilihan" # Fallback

        menu = QMenu()
        delete_action = menu.addAction(delete_text)
        # --- setIcon Dihapus ---
        
        # Hubungkan aksi ke fungsi hapus di main window
        delete_action.triggered.connect(main_window.remove_selected_jpg_folder)
        
        # Tampilkan menu di posisi kursor global
        menu.exec(self.mapToGlobal(pos))
    # --- AKHIR FUNGSI KLIK KANAN ---

    # --- METHOD BARU UNTUK TOMBOL KEYBOARD ---
    def keyPressEvent(self, event):
        """Menangani penekanan tombol keyboard"""
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        if event.key() == Qt.Key_Delete:
            # --- AKHIR PERUBAHAN MIGRASI ---
            # Jika tombol Delete ditekan, panggil fungsi hapus di main window
            main_window = self.window()
            main_window.remove_selected_jpg_folder()
        else:
            # Biarkan tombol lain berfungsi normal
            super().keyPressEvent(event)
    # --- AKHIR METHOD BARU ---


# Fungsi normalisasi nama file (hilangkan spasi, underscore, tanda hubung, lowercase)
def normalize_name(name):
    return re.sub(r'[\s_-]', '', os.path.splitext(name)[0]).lower()

# Pastikan kita menyapu dari ROOT DCIM meskipun input menunjuk ke subfolder di dalamnya
def ensure_dcim_root(p):
    try:
        current = os.path.abspath(p)
        while True:
            base = os.path.basename(current)
            if base.lower() == 'dcim':
                return current
            parent = os.path.dirname(current)
            if not parent or parent == current:
                break
            current = parent
        return p
    except Exception:
        return p

# Buat key kanonik yang toleran untuk pencocokan nama JPG/RAW
def keyify(name_no_ext):
    s = name_no_ext or ''
    s = s.strip()
    # Hilangkan underscore di depan
    s = re.sub(r'^_+', '', s)
    # Hilangkan spasi sebelum tanda kurung
    s = re.sub(r'\s+\)', ')', s)
    # Hapus sufiks umum di akhir nama (case-insensitive)
    # Contoh: (1), (12), -edit, copy, copy(2), salin, salinan
    s = re.sub(r'(\s*\(\d+\)\s*$)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'(\s*-?\s*edit\s*$)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'(\s*-?\s*copy(?:\s*\(\d+\))?\s*$)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'(\s*-?\s*salin(?:an)?\s*$)', '', s, flags=re.IGNORECASE)
    # Hilangkan spasi/underscore/hyphen dan lowercase
    s = re.sub(r'[\s_-]+', '', s).lower()
    return s

def find_dcim_folder_static():
    """
    Fungsi global untuk menemukan folder DCIM.
    Dipindahkan dari ModernBackupApp agar bisa diakses oleh poller.
    """
    possible_paths = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'DCIM'),
    ]
    # Tambahkan DCIM di drive D:..Z:
    for code in range(ord('D'), ord('Z') + 1):
        possible_paths.append(f"{chr(code)}:/DCIM")
    for path in possible_paths:
        try:
            if os.path.exists(path) and os.path.isdir(path):
                return path
        except Exception:
            continue
    return None

class CameraMonitor(QObject):
    camera_connected = pyqtSignal()
    camera_disconnected = pyqtSignal()
    
    def __init__(self, dcim_path):
        super().__init__()
        self.dcim_path = dcim_path
        self.running = True
        self.last_state = self.check_camera_state()
        self.debounce_time = 0
        # DEBUG: log path yang dipantau
        print(f"[CameraMonitor] Monitoring path: {self.dcim_path}")
        
    def run(self):
        print("[CameraMonitor] run() started")
        while self.running:
            current_state = self.check_camera_state()
            if current_state != self.last_state:
                current_time = time.time()
                # Debounce untuk mencegah deteksi berulang cepat
                if current_time - self.debounce_time > 2:  # Hanya deteksi setiap 2 detik
                    # FIX: Menggunakan variabel lokal 'current_state'
                    print(f"[CameraMonitor] State changed: {self.last_state} -> {current_state}")
                    if current_state:
                        print("[CameraMonitor] Emitting camera_connected")
                        self.camera_connected.emit()
                    else:
                        print("[CameraMonitor] Emitting camera_disconnected")
                        self.camera_disconnected.emit()
                    self.last_state = current_state
                    self.debounce_time = current_time
            QThread.msleep(1000)
    
    def check_camera_state(self):
        try:
            # Perhatikan: ini mengecek path DCIM yang terdeteksi/dipilih, BUKAN DCIM root
            return os.path.exists(self.dcim_path) and os.path.isdir(self.dcim_path)
        except:
            return False

    def stop(self):
        self.running = False

class SpeedGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speeds = []  # dalam MB/s
        self.setMinimumHeight(50)
        self.setMaximumHeight(60)

    def update_speeds(self, speeds):
        self.speeds = speeds[-60:]  # simpan max 60 data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        margin = 8
        
        # Warna grafik (hanya tema terang)
        graph_color = QColor("#20b1d4")
        fill_color = QColor("#20b1d4"); fill_color.setAlpha(60)
        bg_color = QColor("#eaf6fa")
        grid_color = QColor("#b6e2f0")

        painter.fillRect(0, 0, w, h, bg_color)
        # Grid tipis
        painter.setPen(QPen(grid_color, 1, ))
        for i in range(1, 4):
            y = margin + i * (h-2*margin) / 4
            painter.drawLine(0, int(y), w, int(y))
        if not self.speeds:
            return
        max_speed = max(max(self.speeds), 1)
        points = len(self.speeds)
        step = w / max(points-1, 1)
        # Smooth curve
        path = QPainterPath()
        x0 = 0
        y0 = h - margin - int((self.speeds[0] / max_speed) * (h-2*margin))
        path.moveTo(x0, y0)
        for i in range(1, points):
            x = int(i * step)
            y = h - margin - int((self.speeds[i] / max_speed) * (h-2*margin))
            cx = int((x + x0) / 2)
            cy = int((y + y0) / 2)
            path.quadTo(x0, y0, cx, cy)
            x0, y0 = x, y
        path.lineTo(w, h-margin)
        path.lineTo(0, h-margin)
        path.closeSubpath()
        # Fill area
        painter.setPen(Qt.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(path)
        # Draw line
        path2 = QPainterPath()
        x0 = 0
        y0 = h - margin - int((self.speeds[0] / max_speed) * (h-2*margin))
        path2.moveTo(x0, y0)
        for i in range(1, points):
            x = int(i * step)
            y = h - margin - int((self.speeds[i] / max_speed) * (h-2*margin))
            cx = int((x + x0) / 2)
            cy = int((y + y0) / 2)
            path2.quadTo(x0, y0, cx, cy)
            x0, y0 = x, y
        painter.setPen(QPen(graph_color, 2))
        painter.setBrush(Qt.NoBrush)
        # --- AKHIR PERUBAHAN MIGRASI ---
        painter.drawPath(path2)

class SmoothProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup Process")
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.setWindowModality(Qt.ApplicationModal)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Content container
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Icon
        self.icon_label = QLabel("🔄")
        self.icon_label.setFont(QFont("Arial", 24))
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # Title
        title = QLabel("Backup in Progress")
        title_font = QFont("Arial", 25, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # --- AKHIR PERUBAHAN MIGRASI ---

        # Animated progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(20)
        
        # Set background (hanya tema terang)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: transparent;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                /* GANTI WARNA GRAFIK: Menggunakan pink cerah */
                background-color: #FF63A4; 
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Grafik kecepatan transfer
        self.speed_graph = SpeedGraphWidget()
        layout.addWidget(self.speed_graph)

        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        # File label
        self.file_label = QLabel("Preparing backup...")
        self.file_label.setStyleSheet("font-size: 12px;")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)

        # Speed label
        self.speed_label = QLabel("Speed: 0 MB/s")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.speed_label)
        # --- AKHIR PERUBAHAN MIGRASI ---

        # ETA container
        eta_container = QWidget()
        eta_layout = QHBoxLayout(eta_container)
        eta_layout.setContentsMargins(0, 0, 0, 0)

        eta_title = QLabel("Estimated Time:")
        eta_title.setStyleSheet("font-weight: bold;")
        eta_layout.addWidget(eta_title)

        self.eta_value = QLabel("Calculating...")
        eta_layout.addWidget(self.eta_value)

        eta_layout.addStretch()
        layout.addWidget(eta_container)

        # Time detail container
        time_container = QWidget()
        time_layout = QGridLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setHorizontalSpacing(15)
        time_layout.setVerticalSpacing(5)

        units = ["Hours", "Minutes", "Seconds", "Milliseconds"]
        # --- PERBAIKAN 2: Simpan referensi label agar tidak rapuh ---
        self.time_labels = {} # Buat dictionary untuk menyimpan label
        
        for i, unit in enumerate(units):
            label = QLabel(unit + ":")
            label.setStyleSheet("font-size: 10px; color: #777;")
            # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
            label.setAlignment(Qt.AlignCenter)
            time_layout.addWidget(label, 0, i)

            value_label = QLabel("00")
            value_label.setObjectName(f"time_{unit.lower()}") # Memberi nama objek
            value_label.setStyleSheet("font-size: 12px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # --- AKHIR PERUBAHAN MIGRASI ---
            time_layout.addWidget(value_label, 1, i)
            
            self.time_labels[unit.lower()] = value_label # Simpan referensi
            # --- AKHIR PERBAIKAN 2 ---

        layout.addWidget(time_container)

        # Cancel button
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.setStyleSheet("""
            /* GANTI WARNA CANCEL: Tetap merah agar jelas */
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.btn_cancel)

        # Stretch
        layout.addStretch()

        # Set layout and add to main layout
        content_widget.setLayout(layout)
        main_layout.addWidget(content_widget, 1)

        # Flexible size
        self.resize(500, 350)

        # Progress variables
        self.start_time = time.time()
        self.last_update = 0
        self.file_count = 0
        self.total_files = 0
        # Smooth progress variables
        self._progress_target = 0
        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(10) # Interval animasi
        self._progress_timer.timeout.connect(self._smooth_update_progress)
        self.total_bytes = 0
        self.speed_history = []  # MB/s
        self.last_bytes_copied = 0
        self.last_speed_time = time.time()
        
        # --- PERBAIKAN KRITIS 1: Panggil apply_theme() ---
        self.apply_theme() # Panggil apply_theme yang hilang

    # --- PERBAIKAN KRITIS 1: Tambahkan metode 'apply_theme' yang hilang ---
    def apply_theme(self):
        self.setStyleSheet("""
            QDialog, QMessageBox {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                /* GANTI WARNA TOMBOL POPUP: Pink cerah */
                background-color: #FF63A4;
                color: white;
            }
            QPushButton:hover {
                background-color: #D64C87; /* Lebih gelap dari pink cerah */
            }
        """)
        # Atur stylesheet khusus untuk tombol cancel
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
    # --- PERBAIKAN KRITIS 1: Tambahkan metode 'update_progress' yang hilang ---
    def update_progress(self, percent, filename, total_bytes, bytes_copied):
        self._progress_target = percent
        if not self._progress_timer.isActive():
            self._progress_timer.start()
            
        self.file_label.setText(f"{filename}") # Tampilkan nama file (tanpa "Backing up:")
        self.total_bytes = total_bytes
        # ETA calculation
        elapsed = time.time() - self.start_time
        
        # --- Hitung kecepatan transfer ---
        now = time.time()
        dt = now - self.last_speed_time
        avg_speed_mb_for_eta = 0 # Inisialisasi

        if dt > 0.1: # Update kecepatan setiap 100ms
            speed = (bytes_copied - self.last_bytes_copied) / dt / 1024 / 1024  # MB/s
            self.speed_history.append(max(speed, 0))
            self.speed_history = self.speed_history[-60:] # Simpan 60 data point terakhir
            self.last_bytes_copied = bytes_copied
            self.last_speed_time = now
            self.speed_graph.update_speeds(self.speed_history)
            self.speed_label.setText(f"Speed: {speed:.2f} MB/s")

        # --- Logika ETA: Gunakan rata-rata kecepatan terbaru ---
        if self.speed_history:
            # Hitung rata-rata dari histori kecepatan
            avg_speed_mb_for_eta = sum(self.speed_history) / len(self.speed_history)
        
        # Fallback ke rata-rata total jika kecepatan terbaru 0 (misal di awal)
        if avg_speed_mb_for_eta == 0 and elapsed > 0 and bytes_copied > 0:
             avg_speed_mb_for_eta = (bytes_copied / elapsed) / 1024 / 1024 # avg total dalam MB/s

        if avg_speed_mb_for_eta > 0:
            speed_eta_bytes = avg_speed_mb_for_eta * 1024 * 1024 # Kecepatan rata-rata terbaru (bytes/s)
            remaining = total_bytes - bytes_copied
            eta_seconds = remaining / speed_eta_bytes
            
            if eta_seconds < 0: eta_seconds = 0 
            
            hours = int(eta_seconds // 3600)
            minutes = int((eta_seconds % 3600) // 60)
            seconds = int(eta_seconds % 60)
            milliseconds = int((eta_seconds - int(eta_seconds)) * 1000)
            eta_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s" # Tampilan ETA utama
            self.eta_value.setText(eta_str)
            
            # Update label detail menggunakan findChild
            # --- PERBAIKAN 2: Gunakan referensi label yang disimpan ---
            if self.time_labels.get("hours"):
                self.time_labels["hours"].setText(f"{hours:02d}")
                self.time_labels["minutes"].setText(f"{minutes:02d}")
                self.time_labels["seconds"].setText(f"{seconds:02d}")
                self.time_labels["milliseconds"].setText(f"{milliseconds:03d}")
            # --- AKHIR PERBAIKAN 2 ---
        else:
            self.eta_value.setText("Calculating...")
            # --- PERBAIKAN 2: Gunakan referensi label yang disimpan ---
            if self.time_labels.get("hours"):
                self.time_labels["hours"].setText("00")
                self.time_labels["minutes"].setText("00")
                self.time_labels["seconds"].setText("00")
                self.time_labels["milliseconds"].setText("000")
            # --- AKHIR PERBAIKAN 2 ---
        
        if percent >= 100 or (total_bytes > 0 and bytes_copied >= total_bytes):
            self.progress_bar.setValue(100)
            self._progress_timer.stop()

    # --- PERBAIKAN KRITIS 1: Tambahkan metode '_smooth_update_progress' yang hilang ---
    def _smooth_update_progress(self):
        current_value = self.progress_bar.value()
        target = self._progress_target
        
        if current_value == target:
            if target == 100:
                self._progress_timer.stop()
            return

        # Jika sudah sangat dekat (misal <2%), langsung set ke target
        if abs(current_value - target) < 2:
            new_value = int(target)
        else:
            # Interpolasi
            new_value = int(current_value + (target - current_value) * 0.15) # 15% per tick
            
        self.progress_bar.setValue(new_value)
        
        if new_value == target and target == 100:
            self._progress_timer.stop()


# --- PERBAIKAN: CLASS ModernBackupApp DIMASUKKAN DI SINI ---
class ModernBackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- PINDAHKAN SEMUA VARIABEL INIT KE SINI ---
        # --- PERUBAHAN: Mulai dengan self.dcim_folder = None ---
        self.dcim_folder = None # Akan diisi oleh poller
        self.jpg_folders = []
        self.backup_thread = None
        self.camera_monitor = None
        self.camera_thread = None
        self.backup_in_progress = False
        self.backup_paused = False
        self.backup_resume_available = False
        self.backup_interrupted = False
        self.progress_dialog = None
        self.stats = {}
        self._resume_files = None
        self._resume_index = 0
        self._resume_backup_folder = None
        self.last_success_file = ""
        self.manual_source_set = False # <<< PERBAIKAN 1: Flag untuk menonaktifkan poller

        
        # Pengaturan default
        self.max_files_to_scan = 5000  # Batasi pemindaian awal
        self.marker_size_threshold = 10 * 1024 * 1024  # 10MB
        
        # --- Pengaturan Bahasa ---
        # Ambil dari kamus global
        self.translations = get_all_translations()
        
        # Coba deteksi bahasa sistem
        # system_lang = QLocale.system().name() # Cth: "id_ID" # <-- DIHAPUS
        # --- PERUBAHAN: Jadikan Bahasa Indonesia sebagai default ---
        # if system_lang.startswith('en'): # <-- DIHAPUS
        #     self.current_language = 'en'
        # else:
        #     self.current_language = 'id' # Default ke 'id'
        self.current_language = 'id' # <-- LANGSUNG SET KE 'id'
        # --- Akhir Pengaturan Bahasa ---

        self._setup_ui()
        self._apply_translations() # Terapkan bahasa
        
        # --- SARAN 4: Hapus Timer Jam ---
        # # Update jam setiap detik
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_clock)
        # self.timer.start(1000)
        # self.update_clock() # Panggil sekali saat start
        
        # --- PERUBAHAN: Hapus start CameraMonitor dari __init__ ---
        # Blok 'if self.dcim_folder...' dihapus dari sini.
        
        # --- PERUBAHAN: Panggil poller drive pertama kali ---
        self._check_and_set_source(is_startup=True) 
        
        # --- PERUBAHAN: Mulai timer untuk memonitor drive baru ---
        self.drive_poll_timer = QTimer(self)
        self.drive_poll_timer.timeout.connect(self._check_and_set_source)
        self.drive_poll_timer.start(3000) # Cek setiap 3 detik
        
        self.resize(500, 750) # Ukuran awal
        self._log("Application started.")
        # --- AKHIR DARI INIT ---

    # --- METHOD apply_theme YANG HILANG, DITAMBAHKAN DI SINI ---
    def apply_theme(self):
        # Warna yang diambil dari gambar gradien
        COLOR_BG_LIGHT = "#F8FAFC" # Background
        COLOR_ACCENT_START = "#6C63FF" # Biru/Ungu Terang (Aksen Utama)
        COLOR_ACCENT_END = "#FF63A4" # Pink Cerah (Aksen Sekunder)
        COLOR_TEXT_DARK = "#0F172A"
        COLOR_BORDER = "#CBD5E1"
        COLOR_INPUT_BG = "#E2E8F0"
        
        # Tema terang (satu-satunya tema)
        self.setStyleSheet(f"""
QWidget#central_widget {{
    background-color: {COLOR_BG_LIGHT};
}}
QLabel, QFrame {{ /* QCheckBox dihapus dari sini */
    background-color: transparent;
    color: {COLOR_TEXT_DARK};
}}

/* +++ GAYA TOMBOL MODE BARU +++ */
QRadioButton#ModeRadioButton {{
    background-color: {COLOR_INPUT_BG}; /* Abu-abu seperti text box */
    color: {COLOR_TEXT_DARK}; /* Teks gelap */
    border: none;
    border-radius: 8px;
    padding: 6px 8px; /* <<< DIPENDEKKAN KIRI-KANAN (dari 10px) */
    font-weight: bold;
}}
QRadioButton#ModeRadioButton::indicator {{
    width: 0px; 
    height: 0px;
    image: none; 
    margin: 0px;  
    padding: 0px; 
}}
QRadioButton#ModeRadioButton:hover:!checked {{
    background-color: {COLOR_BORDER}; /* Abu-abu sedikit lebih gelap */
}}
QRadioButton#ModeRadioButton:checked {{
    /* GANTI TEMA Checked: Gunakan gradien */
    background-color: {COLOR_ACCENT_START}; /* Fallback solid color */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_ACCENT_START}, stop:1 {COLOR_ACCENT_END});
    color: white;
}}
QRadioButton#ModeRadioButton:checked:hover {{
    /* Gradien tetap, tapi opacity/warna sedikit diubah untuk efek hover */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_ACCENT_START}, stop:1 {COLOR_ACCENT_END});
    opacity: 0.9; /* Tidak didukung, tapi biarkan untuk niat */
}}
/* +++ AKHIR GAYA TOMBOL MODE +++ */

/* +++ GAYA CHECKBOX BARU +++ */
QCheckBox {{
    background-color: {COLOR_INPUT_BG}; /* Abu-abu seperti text box */
    color: {COLOR_TEXT_DARK}; /* Teks gelap */
    border: none;
    border-radius: 8px;
    padding: 8px 10px; /* <<< DIPENDEKKAN KIRI-KANAN (dari 14px) */
    font-weight: bold;
    spacing: 10px; 
}}
QCheckBox::indicator {{
    width: 0px; 
    height: 0px;
    image: none; 
    margin: 0px;  
    padding: 0px; 
}}
QCheckBox:hover:!checked {{
    background-color: {COLOR_BORDER}; /* Abu-abu sedikit lebih gelap */
}}
QCheckBox:checked {{
    /* GANTI TEMA Checked: Gunakan gradien */
    background-color: {COLOR_ACCENT_START}; /* Fallback solid color */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_ACCENT_START}, stop:1 {COLOR_ACCENT_END});
    color: white;
}}
QCheckBox:checked:hover {{
    /* Gradien tetap */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_ACCENT_START}, stop:1 {COLOR_ACCENT_END});
}}
/* +++ AKHIR GAYA CHECKBOX BARU +++ */

/* +++ GAYA GROUPBOX BARU +++ */
QGroupBox {{
    font-weight: bold;
    font-size: 10pt;
    color: {COLOR_TEXT_DARK};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    margin-top: 10px; /* Ruang untuk judul */
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: {COLOR_BG_LIGHT}; /* Sama dengan bg window */
}}
/* +++ AKHIR GAYA GROUPBOX BARU +++ */

#title_label {{
    color: {COLOR_TEXT_DARK};
    font-size: 16pt;
    font-weight: bold;
    background-color: transparent;
}}
#jpg_folder_label {{
    color: {COLOR_TEXT_DARK};
}}
#footer_label {{
    color: {COLOR_TEXT_DARK};
}}
#log_label {{
    color: {COLOR_TEXT_DARK};
}}
QPushButton {{
    color: white;
    border-radius: 8px;
    padding: 6px 10px; 
    font-weight: bold;
    /* GANTI WARNA TOMBOL STANDAR: Gunakan gradien */
    background-color: {COLOR_ACCENT_START}; /* Fallback solid color */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_ACCENT_START}, stop:1 {COLOR_ACCENT_END});
}}
QPushButton:hover {{
    /* Gradien hover lebih terang atau gelap, di sini dibuat lebih gelap */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #5C53E5, stop:1 #E55291);
}}
QPushButton:disabled {{
    color: #94A3B8;
    background-color: {COLOR_INPUT_BG};
}}
QLineEdit {{
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT_DARK};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 4px 6px;
}}
QListWidget#jpg_folder_list, QTextEdit#filename_filter_list {{
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT_DARK};
    border: 1px solid {COLOR_INPUT_BG};
    border-radius: 4px;
    padding: 6px;
}}
QTextEdit#log_text {{
    background-color: {COLOR_INPUT_BG};
    color: {COLOR_TEXT_DARK};
    border-radius: 4px;
    padding: 6px;
}}
QScrollBar:vertical {{
    background: {COLOR_INPUT_BG};
    width: 16px;
    margin: 0px 0px 0px 0px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #b6b6b6;
    min-height: 48px;
    border-radius: 4px;
    border: 2px solid #d1d5db;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    border: none;
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {COLOR_INPUT_BG};
    height: 16px;
    margin: 0px 0px 0px 0px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #b6b6b6;
    min-width: 48px;
    border-radius: 4px;
    border: 2px solid #d1d5db;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    background: none;
    border: none;
    width: 0px;
}}
""")
        self.jpg_folder_list.setStyleSheet("")
        
        # Paksa warna log_text setelah style global
        if hasattr(self, 'log_text'):
            self.log_text.setStyleSheet(f"background-color: {COLOR_INPUT_BG}; color: {COLOR_TEXT_DARK}; border-radius: 4px; padding: 6px;")

        # GANTI WARNA STATUS: Gunakan warna yang tidak terlalu mencolok (hijau/merah tetap)
        self.status_label.setStyleSheet("color: #0D9488; background-color: transparent;")
        
        # Style untuk tombol pengaturan
        if hasattr(self, 'btn_settings'):
            self.btn_settings.setStyleSheet(f"""
                QPushButton {{
                    font-size: 10pt; 
                    font-weight: bold;
                    color: #475569;
                    background-color: transparent;
                    border: none;
                    padding: 0px 5px;
                    margin: 0px;
                }}
                QPushButton:hover {{
                    color: {COLOR_ACCENT_END}; /* Hover pink cerah */
                }}
            """)
    # --- AKHIR DARI METHOD apply_theme ---

    # --- SARAN 4: Hapus method update_clock ---
    # def update_clock(self):
    #     ...

    # --- METHOD tr() BARU UNTUK HELPER TERJEMAHAN ---
    
    # --- PERUBAHAN: Tambahkan metode _check_and_set_source ---
    def _check_and_set_source(self, is_startup=False):
        """
        Mengecek drive untuk folder DCIM. 
        Dipanggil oleh timer (setiap 3 dtk) dan saat startup.
        (VERSI BARU: Menghormati pilihan manual)
        """
        
        # 1. Jika user SUDAH memilih manual
        if self.manual_source_set:
            # Kita hanya perlu mengecek apakah path manual itu masih ada
            try:
                # Periksa dcim_folder yang sudah disetel secara manual
                path_exists = os.path.exists(self.dcim_folder) and os.path.isdir(self.dcim_folder)
            except Exception:
                path_exists = False
                
            if not path_exists:
                # Path manual terputus!
                self._log(f"Sumber manual terputus: {self.dcim_folder}")
                if not self.backup_in_progress:
                    self.dcim_folder = None
                    self.source_label.setText(self.tr('source_label_default'))
                    self._update_status(self.tr('status_no_source'), "#e74c3c")
                    self.manual_source_set = False # Reset flag agar auto-detect aktif lagi
                    self._restart_camera_monitor() # Matikan monitor lama
            return # Selesai. Jangan biarkan auto-detect menimpa.

        # 2. Jika user BELUM memilih manual (mode auto-detect)
        new_path = find_dcim_folder_static() # Ini adalah path DCIM otomatis

        if new_path and new_path != self.dcim_folder:
            # Auto-detect menemukan DCIM, dan itu beda dari yang sekarang
            self._log(f"Sumber DCIM terdeteksi: {new_path}")
            self.dcim_folder = new_path
            self.source_label.setText(new_path)
            if not self.backup_in_progress:
                self._update_status(self.tr('status_ready'), "#2ecc71")
            self._restart_camera_monitor() 
        
        elif not new_path and self.dcim_folder:
            # Auto-detect TIDAK menemukan DCIM, dan kita punya path DCIM lama
            # (Ini berarti DCIM-nya baru saja dicabut)
            if not self.backup_in_progress:
                self.dcim_folder = None
                self.source_label.setText(self.tr('source_label_default'))
                self._update_status(self.tr('status_no_source'), "#e74c3c")
                self._restart_camera_monitor() # Matikan monitor lama
        
        elif is_startup and not new_path:
            # Panggilan pertama saat startup dan tidak ada DCIM
            self._log("Tidak ada sumber DCIM terdeteksi saat startup. Memonitor...")
            self._update_status(self.tr('status_no_source'), "#e74c3c")
    
    # --- AKHIR PERUBAHAN ---

    def tr(self, key):
        """Helper untuk mendapatkan terjemahan dengan fallback ke English."""
        lang = self.current_language
        try:
            return self.translations[key][lang]
        except KeyError:
            try:
                # Fallback ke English
                return self.translations[key]['en']
            except KeyError:
                # Fallback ke key itu sendiri jika tidak ditemukan
                print(f"WARNING: Missing translation for key: {key}")
                return key
    # --- AKHIR METHOD tr() BARU ---
    
    # --- SARAN 2: Hapus method refresh_log ---
    # def refresh_log(self):
    #    ...

    def camera_connected(self):
        # Show resume popup if backup_interrupted True
        if self.backup_interrupted or self.backup_resume_available or self.backup_paused or self.backup_in_progress:
            self._log("Source reconnected (resume/interrupted), show resume popup")
            QTimer.singleShot(0, self._show_camera_reconnected)

    def camera_disconnected(self):
        self._log("camera_disconnected called")
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.stop()
        if self.progress_dialog:
            self.progress_dialog.reject()
            self.progress_dialog = None
        if self.backup_in_progress:
            QTimer.singleShot(0, self._show_camera_disconnected_popup)
        # Set resume flag
        self.backup_paused = True
        self.backup_resume_available = True
        self.backup_interrupted = True

    def _show_camera_reconnected(self):
        play_popup_sound("question")
        msg_box = QMessageBox(self)
        # --- TERJEMAHAN ---
        msg_box.setWindowTitle(self.tr('popup_continue_backup_title'))
        msg_box.setText(self.tr('popup_continue_backup_text'))
        # --- AKHIR TERJEMAHAN ---
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        msg_box.setIcon(QMessageBox.Question)
        
        # Hanya tema terang
        msg_box.setStyleSheet("""
            QDialog, QMessageBox {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                background-color: #FF63A4; /* GANTI WARNA */
                color: white;
            }
            QPushButton:hover {
                background-color: #D64C87; /* GANTI WARNA */
            }
        """)
        
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = msg_box.exec_() # <-- PERUBAHAN: exec() -> exec_()
        if reply == QMessageBox.Yes:
        # --- AKHIR PERUBAHAN MIGRASI ---
            self._resume_backup()

    def _show_camera_disconnected_popup(self):
        play_popup_sound("warning")
        msg_box = QMessageBox(self)
        # --- TERJEMAHAN ---
        msg_box.setWindowTitle(self.tr('popup_disconnected_title'))
        msg_box.setText(self.tr('popup_disconnected_text'))
        # --- AKHIR TERJEMAHAN ---
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        msg_box.setIcon(QMessageBox.Warning)
        
        # Hanya tema terang
        msg_box.setStyleSheet("""
            QDialog, QMessageBox {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                background-color: #FF63A4; /* GANTI WARNA */
                color: white;
            }
            QPushButton:hover {
                background-color: #D64C87; /* GANTI WARNA */
            }
        """)
        
        msg_box.exec_() # <-- PERUBAHAN: exec() -> exec_()
        # --- AKHIR PERUBAHAN MIGRASI ---
        self.backup_paused = True
        self.backup_resume_available = True
        self.backup_interrupted = True

    def _find_dcim_folder(self):
        possible_paths = [
            os.path.join(os.environ.get('USERPROFILE', ''), 'DCIM'),
        ]
        # Tambahkan DCIM di drive D:..Z:
        for code in range(ord('D'), ord('Z') + 1):
            possible_paths.append(f"{chr(code)}:/DCIM")
        for path in possible_paths:
            try:
                if os.path.exists(path) and os.path.isdir(path):
                    return path
            except Exception:
                continue
        return None

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14) # Margin bawah ditambah sedikit
        main_layout.setSpacing(12) # Jarak antar elemen utama ditambah

        # === PERBAIKAN FONT: Definisikan font yang aman di satu tempat ===
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        font_title = QFont()
        font_title.setPointSize(15)
        font_title.setWeight(QFont.Bold)

        # --- SARAN 4: Hapus font_clock ---
        # font_clock = QFont()
        # font_clock.setPointSize(9)

        font_btn = QFont()
        font_btn.setPointSize(9)
        font_btn.setWeight(QFont.Bold)

        font_label_bold = QFont()
        font_label_bold.setPointSize(9)
        font_label_bold.setWeight(QFont.Bold)

        font_label_normal = QFont()
        font_label_normal.setPointSize(9)

        font_label_small = QFont()
        font_label_small.setPointSize(8)

        font_label_small_bold = QFont()
        font_label_small_bold.setPointSize(8)
        font_label_small_bold.setWeight(QFont.Bold)

        font_mono_normal = QFont("Courier New")
        font_mono_normal.setPointSize(9)

        font_mono_small = QFont("Courier New")
        font_mono_small.setPointSize(8)

        font_start_btn = QFont()
        font_start_btn.setPointSize(12)
        font_start_btn.setWeight(QFont.Bold)
        # --- AKHIR PERUBAHAN MIGRASI ---

        # --- SARAN 2: Hapus font_refresh_btn ---
        # font_refresh_btn = QFont()
        # font_refresh_btn.setPointSize(7)

        font_footer = QFont()
        font_footer.setPointSize(8)
        font_footer.setItalic(True)
        # === AKHIR DEFINISI FONT ===

        # === Header: Title + Settings + Time ===
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        self.title_label = QLabel("...") # Placeholder
        self.title_label.setObjectName("title_label")
        self.title_label.setFont(font_title) # <-- PERBAIKAN FONT
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # --- AKHIR PERUBAHAN MIGRASI ---
        header_row.addWidget(self.title_label, 1)
        
        # --- SARAN 4: Hapus clock_label ---
        # Small clock label
        # self.clock_label = QLabel()
        # ... (block deleted) ...
        # header_row.addWidget(self.clock_label, 0)
        
        # Tombol Pengaturan (Baru)
        self.btn_settings = QPushButton("...") # --- GANTI DARI "⚙️"
        # --- HAPUS 'setFixedSize' DAN 'setIcon' ---
        self.btn_settings.setToolTip("Pengaturan Bahasa / Language Settings")
        self.btn_settings.clicked.connect(self._open_settings)
        # --- STYLING DIHAPUS DARI SINI, AKAN DIATUR OLEH THEME GLOBAL ---
        header_row.addWidget(self.btn_settings)

        # Small clock label (Dipindahkan ke atas)
        main_layout.addLayout(header_row)

        # === GROUPBOX LANGKAH 1: SUMBER ===
        self.group_step_1 = QGroupBox("...") # Placeholder
        source_layout = QGridLayout() # Gunakan GridLayout untuk perataan
        source_layout.setContentsMargins(10, 15, 10, 10) # Beri margin dalam
        source_layout.setSpacing(10) # Jarak antar elemen di groupbox

        self.btn_change_source = QPushButton("...") # Placeholder
        self.btn_change_source.setFixedHeight(30)
        self.btn_change_source.setFont(font_btn) # <-- PERBAIKAN FONT
        self.btn_change_source.clicked.connect(self._change_source_folder)
        source_layout.addWidget(self.btn_change_source, 0, 0) # <<< PINDAH KE KIRI (0, 0)

        # --- SARAN 3: Hapus source_label_title ---
        # self.source_label_title = QLabel("...") # Placeholder
        # ... (block deleted) ...
        # source_layout.addWidget(self.source_label_title, 0, 1) # <<< PINDAH KE (0, 1)
        
        self.source_label = QLabel(self.dcim_folder if self.dcim_folder else "...") # Placeholder
        self.source_label.setFont(font_label_normal) # <-- PERBAIKAN FONT
        self.source_label.setWordWrap(True)
        self.source_label.setStyleSheet("color: #333;")
        source_layout.addWidget(self.source_label, 0, 1) # <<< PINDAH KE (0, 1)

        source_layout.setColumnStretch(1, 1) # <<< UBAH STRETCH ke kolom 1
        self.group_step_1.setLayout(source_layout)
        main_layout.addWidget(self.group_step_1)


        # === GROUPBOX LANGKAH 2: METODE ===
        self.group_step_2 = QGroupBox("...") # Placeholder
        step_2_layout = QVBoxLayout()
        step_2_layout.setContentsMargins(10, 15, 10, 10) # Beri margin dalam
        step_2_layout.setSpacing(10) # Jarak antar elemen di groupbox

        # --- Pilihan Mode ---
        mode_layout = QHBoxLayout()
        self.radio_mode_folder = QRadioButton("...") # Placeholder
        self.radio_mode_folder.setObjectName("ModeRadioButton")
        self.radio_mode_folder.setFont(font_btn) # <-- PERBAIKAN FONT
        self.radio_mode_folder.setChecked(True)
        
        self.radio_mode_list = QRadioButton("...") # Placeholder
        self.radio_mode_list.setObjectName("ModeRadioButton")
        self.radio_mode_list.setFont(font_btn) # <-- PERBAIKAN FONT
        
        mode_layout.addWidget(self.radio_mode_folder)
        mode_layout.addWidget(self.radio_mode_list)
        mode_layout.addStretch(1) # <<< TAMBAHAN: Mencegah tombol mode melebar
        step_2_layout.addLayout(mode_layout)
        
        self.group_step_2.setLayout(step_2_layout)
        main_layout.addWidget(self.group_step_2)

        # --- SARAN 1: Tambahkan QGroupBox Tipe File Global di sini ---
        # === GROUPBOX TIPE FILE (BARU, DIGABUNGKAN) ===
        self.group_file_types_GLOBAL = QGroupBox("...") # Placeholder
        layout_file_types_GLOBAL = QHBoxLayout(self.group_file_types_GLOBAL) # Use QHBoxLayout
        layout_file_types_GLOBAL.setContentsMargins(10, 15, 10, 10) # Margin dalam
        layout_file_types_GLOBAL.setSpacing(8) # Jarak antar checkbox

        self.check_backup_raw_source_GLOBAL = QCheckBox("...") # Placeholder
        self.check_backup_raw_source_GLOBAL.setFont(font_label_normal) # <-- PERBAIKAN FONT
        self.check_backup_raw_source_GLOBAL.setChecked(True) # Default RAW
        layout_file_types_GLOBAL.addWidget(self.check_backup_raw_source_GLOBAL)
        
        self.check_backup_jpg_source_GLOBAL = QCheckBox("...") # Placeholder
        self.check_backup_jpg_source_GLOBAL.setFont(font_label_normal) # <-- PERBAIKAN FONT
        self.check_backup_jpg_source_GLOBAL.setChecked(False) # Default non-JPG
        layout_file_types_GLOBAL.addWidget(self.check_backup_jpg_source_GLOBAL)
        
        layout_file_types_GLOBAL.addStretch(1) # Agar tidak melebar
        
        main_layout.addWidget(self.group_file_types_GLOBAL)

        # === STACKED WIDGET (LANGKAH 3) ===
        self.stacked_widget = QStackedWidget()
        # Beri sedikit margin atas untuk memisahkan dari GroupBox 2
        self.stacked_widget.setStyleSheet("margin-top: 5px;")
        main_layout.addWidget(self.stacked_widget)
        
        # --- HALAMAN 1: METODE FOLDER ---
        self.page_folder_match = QWidget()
        layout_folder_match = QVBoxLayout(self.page_folder_match)
        layout_folder_match.setSpacing(12) # Jarak antar groupbox di halaman ini

        # GroupBox untuk List Folder JPG
        self.group_match_folders = QGroupBox("...") # Placeholder
        layout_match_folders = QVBoxLayout(self.group_match_folders)
        layout_match_folders.setContentsMargins(10, 15, 10, 10) # Margin dalam
        layout_match_folders.setSpacing(12) # <<< TAMBAH JARAK (dari 8)
        
        self.jpg_folder_list = DragDropListWidget()
        self.jpg_folder_list.setObjectName("jpg_folder_list")
        self.jpg_folder_list.setMinimumHeight(100)
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.jpg_folder_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # --- AKHIR PERUBAHAN MIGRASI ---
        self.jpg_folder_list.folder_added.connect(self.on_folder_dropped)
        layout_match_folders.addWidget(self.jpg_folder_list, 1)

        self.btn_add_jpg = QPushButton("...") # Placeholder
        # --- HAPUS 'setIcon' DARI SINI ---
        self.btn_add_jpg.setFixedHeight(30)
        self.btn_add_jpg.setFont(font_btn) # <-- PERBAIKAN FONT
        self.btn_add_jpg.clicked.connect(self.add_jpg_folder)
        
        btn_row_layout = QHBoxLayout()
        btn_row_layout.addWidget(self.btn_add_jpg) # Tambahkan tombol
        btn_row_layout.addStretch(1) # Tambahkan stretch di kanan
        
        layout_match_folders.addLayout(btn_row_layout, 0) # Stretch 0
        layout_folder_match.addWidget(self.group_match_folders, 1)
        
        # --- SARAN 1: Hapus group_file_types_A ---
        # self.group_file_types_A = QGroupBox("...") # Placeholder
        # ... (block deleted) ...
        # layout_folder_match.addWidget(self.group_file_types_A, 0)
        
        self.stacked_widget.addWidget(self.page_folder_match)

        # --- HALAMAN 2: METODE LIST ---
        self.page_list_match = QWidget()
        layout_list_match = QVBoxLayout(self.page_list_match)
        layout_list_match.setContentsMargins(0, 0, 0, 0)
        layout_list_match.setSpacing(12) # Jarak antar groupbox di halaman ini

        self.group_filenames = QGroupBox("...") # Placeholder
        layout_filenames = QVBoxLayout(self.group_filenames)
        layout_filenames.setContentsMargins(10, 15, 10, 10) # Margin dalam
        layout_filenames.setSpacing(8) # Jarak antar textedit & label

        self.filename_filter_list = QTextEdit()
        self.filename_filter_list.setObjectName("filename_filter_list")
        self.filename_filter_list.setMinimumHeight(100)
        self.filename_filter_list.setFont(font_mono_normal) # <-- PERBAIKAN FONT
        layout_filenames.addWidget(self.filename_filter_list)
        
        self.filename_filter_label = QLabel("...") # Placeholder
        self.filename_filter_label.setFont(font_label_small) # <-- PERBAIKAN FONT
        self.filename_filter_label.setWordWrap(True)
        layout_filenames.addWidget(self.filename_filter_label)
        
        layout_list_match.addWidget(self.group_filenames, 1)
        
        # --- SARAN 1: Hapus group_file_types_B ---
        # self.group_file_types_B = QGroupBox("...") # Placeholder (akan diisi terjemahan)
        # ... (block deleted) ...
        # layout_list_match.addWidget(self.group_file_types_B, 0)
        
        self.stacked_widget.addWidget(self.page_list_match)
        
        # Hubungkan radio button ke stacked widget
        self.radio_mode_folder.toggled.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.radio_mode_list.toggled.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # === GROUPBOX LANGKAH TERAKHIR: TUJUAN (SELALU WAJIB) ===
        self.group_destination = QGroupBox("...") # Placeholder
        layout_destination = QGridLayout(self.group_destination)
        layout_destination.setContentsMargins(10, 15, 10, 10) # Margin dalam
        layout_destination.setSpacing(10) # Jarak antar elemen di groupbox

        self.btn_browse_output = QPushButton("...") # Placeholder
        self.btn_browse_output.setFixedHeight(30)
        self.btn_browse_output.setFont(font_btn) # <-- PERBAIKAN FONT
        self.btn_browse_output.clicked.connect(self.browse_custom_output)
        layout_destination.addWidget(self.btn_browse_output, 0, 0) # <<< PINDAH KE KIRI (0, 0)

        self.custom_output_label = QLabel("...") # Placeholder
        self.custom_output_label.setFont(font_label_bold) # <-- PERBAIKAN FONT
        layout_destination.addWidget(self.custom_output_label, 0, 1) # <<< PINDAH KE (0, 1)
        
        self.line_custom_output = QLineEdit()
        self.line_custom_output.setPlaceholderText("...") # Placeholder
        self.line_custom_output.setFont(font_label_normal) # <-- PERBAIKAN FONT
        layout_destination.addWidget(self.line_custom_output, 0, 2) # <<< PINDAH KE (0, 2)
        
        layout_destination.setColumnStretch(2, 1) # <<< UBAH STRETCH ke kolom 2
        main_layout.addWidget(self.group_destination)


        # === Tombol START ===
        self.btn_backup = QPushButton("...") # Placeholder
        # --- HAPUS 'setIcon' DARI SINI ---
        self.btn_backup.setFixedHeight(44)
        self.btn_backup.setFont(font_start_btn) # <-- PERBAIKAN FONT
        self.btn_backup.clicked.connect(self._start_backup)
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        main_layout.addWidget(self.btn_backup, 0, Qt.AlignHCenter) 
 
        # Small status below main button
        self.status_label = QLabel("...") # Placeholder
        self.status_label.setFont(font_label_normal) # <-- PERBAIKAN FONT
        self.status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.status_label)
        # --- AKHIR PERUBAHAN MIGRASI ---

        # --- SARAN 2: Hapus log_label ---
        # Log viewer
        # self.log_label = QLabel("...") # Placeholder
        # ... (block deleted) ...
        # main_layout.addWidget(self.log_label)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("log_text")
        self.log_text.setReadOnly(True)
        self.log_text.setFont(font_mono_small) # <-- PERBAIKAN FONT
        self.log_text.setMinimumHeight(120)
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.log_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        # --- AKHIR PERUBAHAN MIGRASI ---
        main_layout.addWidget(self.log_text)
        main_layout.setStretchFactor(self.stacked_widget, 1)
        main_layout.setStretchFactor(self.log_text, 0)

        # --- SARAN 2: Hapus bottom_row (btn_refresh) ---
        # Bottom row: Refresh log
        # bottom_row = QHBoxLayout()
        # ... (block deleted) ...
        # main_layout.addLayout(bottom_row)
        
        # Footer
        self.footer_label = QLabel("powered by episodvisual ©2025") # <-- PERUBAHAN FOOTER
        self.footer_label.setObjectName("footer_label")
        # footer_font = QFont("Montserrat", 8) # <-- DIHAPUS
        # footer_font.setItalic(True) # <-- DIHAPUS
        self.footer_label.setFont(font_footer) # <-- PERBAIKAN FONT
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.footer_label.setAlignment(Qt.AlignCenter)
        # --- AKHIR PERUBAHAN MIGRASI ---
        main_layout.addWidget(self.footer_label) 
        self.footer_label.setStyleSheet("background-color: transparent;")

        # Apply theme after all widgets are created
        self.apply_theme()
        # Paksa warna log_text setelah apply_theme
        self.log_text.setStyleSheet("background-color: #E2E8F0; color: #0F172A; border-radius: 4px; padding: 6px;")
        
        # --- TAMBAHAN ICON APLIKASI ---
        # Menggunakan QIcon dengan file .ico yang diunggah
        
        # >>> PERBAIKAN UNTUK MEMASTIKAN ICON MUNCUL (EDISI JALUR ABSOLUT) <<<
        try:
            # Dapatkan path absolut ke folder tempat script ini berada
            # Ini adalah kunci agar 'logoku.ico' selalu ditemukan
            if getattr(sys, 'frozen', False):
                # Jika dijalankan sebagai .exe (hasil PyInstaller)
                base_dir = os.path.dirname(sys.executable)
            else:
                # Jika dijalankan sebagai script .py
                base_dir = os.path.dirname(os.path.realpath(__file__))
            
            # Gabungkan dengan nama file icon
            icon_path = os.path.join(base_dir, 'logoku.ico')
            
            # Muat file ICO ke QPixmap, lalu konversi ke QIcon
            icon_pixmap = QPixmap(icon_path)
            
            if not icon_pixmap.isNull():
                self.setWindowIcon(QIcon(icon_pixmap))
                # Juga set ikon untuk QApplication agar lebih konsisten
                QApplication.instance().setWindowIcon(QIcon(icon_pixmap))
            else:
                self._log(f"❌ Warning: Gagal memuat icon dari {icon_path}. Cek apakah file ada.")
        except Exception as e:
            self._log(f"❌ Error saat memuat icon: {e}")

    # --- HAPUS: FUNGSI create_app_icon() yang bermasalah ---
    # def create_app_icon(self):
    #     ...
    # --- AKHIR HAPUS create_app_icon() ---

    # === METHOD BARU UNTUK MENGGANTI SUMBER ===
    # ... existing code ...
    # === METHOD BARU UNTUK MENGGANTI SUMBER ===
    def _change_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder (e.g., Camera DCIM or other folder)")
        if folder:
            normalized_path = os.path.normpath(folder)
            self.dcim_folder = normalized_path
            self.source_label.setText(normalized_path)
            self.manual_source_set = True # <<< PERBAIKAN 2: Set flag manual
            # --- PERBAIKAN: Pindahkan log & restart KE DALAM if block ---
            self._log(f"Source folder changed to: {normalized_path}")
            # --- PERUBAHAN: Panggil helper baru ---
            self._restart_camera_monitor()
        # --- HAPUS DARI LUAR if block ---
        # self._log(f"Source folder changed to: {normalized_path}")
        
        # --- PERUBAHAN: Panggil helper baru ---
        # self._restart_camera_monitor() # (Sudah dipindah ke atas)

    
    def browse_custom_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            normalized_path = os.path.normpath(folder)
            self.line_custom_output.setText(normalized_path)
            self._log(f"Custom output folder set to: {normalized_path}")

    # === METHOD BARU UNTUK BAHASA ===
    
    # --- FUNGSI _create_translations() DIHAPUS (sudah pindah global) ---

    def _apply_translations(self):
        """Menerapkan bahasa yang dipilih ke semua elemen UI"""
        
        # Terapkan semua terjemahan menggunakan helper self.tr()
        self.setWindowTitle(self.tr('app_title'))
        self.title_label.setText(self.tr('app_title'))
        
        # --- TAMBAHAN UNTUK TOMBOL SETTINGS ---
        self.btn_settings.setText(self.tr('btn_settings_text'))
        
        # --- Langkah 1 ---
        self.group_step_1.setTitle(self.tr('source_group'))
        # --- SARAN 3: Hapus terjemahan source_label_title ---
        # self.source_label_title.setText(self.tr('source_label_title'))
        if not self.dcim_folder:
            self.source_label.setText(self.tr('source_label_default'))
        self.btn_change_source.setText(self.tr('btn_change_source'))
        
        # --- Langkah 2 ---
        self.group_step_2.setTitle(self.tr('group_step_2'))
        self.radio_mode_folder.setText(self.tr('radio_mode_folder'))
        self.radio_mode_list.setText(self.tr('radio_mode_list'))
        
        # --- SARAN 1: Tambahkan terjemahan Tipe File Global ---
        self.group_file_types_GLOBAL.setTitle(self.tr('group_file_types'))
        self.check_backup_raw_source_GLOBAL.setText(self.tr('check_backup_raw_source'))
        self.check_backup_jpg_source_GLOBAL.setText(self.tr('check_backup_jpg_source'))

        # --- Halaman 1 (Folder) ---
        self.group_match_folders.setTitle(self.tr('group_match_folders'))
        self.btn_add_jpg.setText(self.tr('btn_add_jpg')) # <-- KUNCI BARU
        # --- SARAN 1: Hapus terjemahan group_file_types_A ---
        # self.group_file_types_A.setTitle(self.tr('group_file_types'))
        # ... (lines deleted) ...
        
        # --- Halaman 2 (List) ---
        self.group_filenames.setTitle(self.tr('group_filenames'))
        self.filename_filter_label.setText(self.tr('filename_filter_label'))
        # --- SARAN 1: Hapus terjemahan group_file_types_B ---
        # self.group_file_types_B.setTitle(self.tr('group_file_types'))
        # ... (lines deleted) ...
        
        # --- Langkah Terakhir (Tujuan) ---
        self.group_destination.setTitle(self.tr('group_destination'))
        self.custom_output_label.setText(self.tr('custom_output_label'))
        self.line_custom_output.setPlaceholderText(self.tr('custom_output_placeholder'))
        self.btn_browse_output.setText(self.tr('btn_browse_output'))
        
        # --- Tombol Utama & Log ---
        self.btn_backup.setText(self.tr('btn_backup')) # <-- KUNCI BARU
        
        # --- SARAN 2: Hapus terjemahan log_label dan btn_refresh ---
        # self.log_label.setText(self.tr('log_label'))
        # self.btn_refresh.setText(self.tr('btn_refresh')) # <-- KUNCI BARU

        # Terapkan status (jika belum berjalan)
        if not self.backup_in_progress:
            self._update_status(self.tr('status_ready'), "#2ecc71")
            
        # --- SARAN 4: Hapus pemanggilan update_clock ---
        # Update jam/tanggal
        # self.update_clock()

    # === AKHIR METHOD BAHASA ===

    def _open_settings(self):
        """Membuka dialog pengaturan bahasa"""
        dialog = QDialog(self)
        # --- TERJEMAHAN ---
        dialog.setWindowTitle(self.tr('popup_settings_title'))
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20) # Beri padding
        layout.setSpacing(15)
        
        # --- TERJEMAHAN ---
        label = QLabel(self.tr('popup_settings_label'))
        layout.addWidget(label)
        
        combo = QComboBox()
        # Isi combo box dengan nama bahasa
        for lang_name in SUPPORTED_LANGUAGES.values():
            combo.addItem(lang_name)
            
        # Set pilihan saat ini
        current_lang_name = SUPPORTED_LANGUAGES.get(self.current_language, 'Bahasa Indonesia')
        combo.setCurrentText(current_lang_name)
        
        layout.addWidget(combo)
        
        # Tombol OK
        # --- TERJEMAHAN ---
        btn_ok = QPushButton(self.tr('popup_settings_ok'))
        def apply_and_close():
            selected_lang_name = combo.currentText()
            # Cari key bahasa (cth: 'id') dari nama (cth: 'Bahasa Indonesia')
            for key, name in SUPPORTED_LANGUAGES.items():
                if name == selected_lang_name:
                    self.current_language = key
                    break
            self._apply_translations()
            dialog.accept()
            
        btn_ok.clicked.connect(apply_and_close)
        layout.addWidget(btn_ok)
        
        # --- TAMBAHKAN TEMA TERANG ---
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
                font-size: 10pt;
            }
            QComboBox {
                background-color: #E2E8F0;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                selection-background-color: #FF63A4; /* GANTI WARNA */
                selection-color: white;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                background-color: #FF63A4; /* GANTI WARNA */
                color: white;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #D64C87; /* GANTI WARNA */
            }
        """)
        # --- AKHIR TEMA ---
        
        dialog.exec_() # <-- PERUBAHAN: exec() -> exec_()

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scroll_bar = self.log_text.verticalScrollBar()
        if scroll_bar is not None:
            scroll_bar.setValue(scroll_bar.maximum())
    
    def _update_progress(self, percent, filename, total_bytes, bytes_copied):
        if self.progress_dialog:
            self.progress_dialog.update_progress(percent, filename, total_bytes, bytes_copied)
    
    def _update_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; background-color: transparent;")
    
    def _update_stats(self, stats):
        self.stats.update(stats)
        self._log(f"📊 Stats: {stats}")
    
    def _show_backup_complete(self, folder, file_count):
        if self.last_success_file:
            self._log(f"Last file copied: {self.last_success_file}")
        play_popup_sound("info")
        dialog = QDialog(self)
        # --- TERJEMAHAN ---
        dialog.setWindowTitle(self.tr('dialog_complete_title'))
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        dialog.setWindowModality(Qt.ApplicationModal)
        # Main layout
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        # Content container
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        # Icon
        icon_label = QLabel("✅")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(icon_label)
        # --- TERJEMAHAN (f-string) ---
        msg = QLabel(self.tr('popup_complete_files').format(count=file_count))
        msg_font = QFont() # <-- PERBAIKAN FONT
        msg_font.setPointSize(12) # <-- PERBAIKAN FONT
        msg_font.setWeight(QFont.Bold) # <-- PERBAIKAN FONT
        msg.setFont(msg_font) # <-- PERBAIKAN FONT
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet("background-color: transparent;")
        layout.addWidget(msg)
        # --- TERJEMAHAN (f-string) ---
        folder_label = QLabel(self.tr('popup_complete_location').format(folder=folder))
        folder_font = QFont() # <-- PERBAIKAN FONT
        folder_font.setPointSize(9) # <-- PERBAIKAN FONT
        folder_label.setFont(folder_font) # <-- PERBAIKAN FONT
        folder_label.setWordWrap(True)
        folder_label.setAlignment(Qt.AlignCenter)
        # --- AKHIR PERUBAHAN MIGRASI ---
        folder_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(folder_label)
        # Button container
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 20, 0, 0)
        btn_layout.setSpacing(10)
        # --- TERJEMAHAN ---
        btn_ok = QPushButton(self.tr('popup_complete_ok'))
        btn_ok.setStyleSheet("""
                QPushButton {
                    background-color: #FF63A4; /* GANTI WARNA */
                    color: white;
                padding: 8px;
                border-radius: 5px;
                min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #D64C87; /* GANTI WARNA */
                }
        """)
        btn_ok.clicked.connect(dialog.accept)
        # --- TERJEMAHAN ---
        btn_open = QPushButton(self.tr('popup_complete_open'))
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF; /* GANTI WARNA: Biru/Ungu Aksen */
                color: white;
                    padding: 8px;
                border-radius: 5px;
                min-width: 80px;
                }
            QPushButton:hover {
                background-color: #5C53E5; /* GANTI WARNA */
                }
            """)
        def open_folder():
            import os
            norm_folder = os.path.normpath(folder) if folder else ''
            print(f"[DEBUG] Open Folder: {norm_folder}")
            if not norm_folder or not os.path.exists(norm_folder):
                # --- TERJEMAHAN (f-string) ---
                QMessageBox.warning(self, 
                                    self.tr('popup_complete_folder_not_found_title'), 
                                    self.tr('popup_complete_folder_not_found_text').format(folder=norm_folder))
                return
            try:
                # --- PERBAIKAN "OPEN FOLDER" (Final) ---
                if platform.system() == "Windows":
                    # os.startfile() adalah perintah Windows native untuk membuka path
                    # Ini jauh lebih andal daripada subprocess('explorer')
                    os.startfile(norm_folder)
                elif platform.system() == "Darwin": # macOS
                    subprocess.Popen(['open', norm_folder])
                else: # Linux
                    subprocess.Popen(['xdg-open', norm_folder])
            except Exception as e:
                # Fallback terakhir jika semua gagal
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(norm_folder))
                except Exception as e2:
                    QMessageBox.critical(self, "Open Folder Error", f"Failed to open folder (tried 2 methods):\n{norm_folder}\n\nMethod 1: {e}\nMethod 2: {e2}")
        btn_open.clicked.connect(open_folder)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_open)
        layout.addWidget(btn_container)
        # Add stretch to fill space
        layout.addStretch()
        main_layout.addWidget(content_widget)
        
        # Apply theme (hanya terang)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel {
                background-color: transparent;
                color: #3d3545;
            }
            QPushButton {
                background-color: #20b1d4;
                color: white;
                padding: 8px;
                border-radius: 5px;
                min-width: 80px;
            }
        """)
        
        # Fixed size
        
        # Show dialog centered
        dialog_rect = dialog.frameGeometry()
        center_point = self.frameGeometry().center()
        dialog_rect.moveCenter(center_point)
        dialog.move(dialog_rect.topLeft())
        dialog.exec_() # <-- PERUBAHAN: exec() -> exec_()
    
    def _show_error(self, message):
        play_popup_sound("error")
        error_dialog = QMessageBox(self)
        # --- TERJEMAHAN ---
        error_dialog.setWindowTitle(self.tr('dialog_error_title'))
        error_dialog.setText(message) # Pesan sudah diterjemahkan oleh pemanggil
        # --- AKHIR TERJEMAHAN ---
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        error_dialog.setIcon(QMessageBox.Critical)
        
        # Hanya tema terang
        error_dialog.setStyleSheet("""
            QDialog, QMessageBox {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                background-color: #FF63A4; /* GANTI WARNA */
                color: white;
            }
            QPushButton:hover {
                background-color: #D64C87; /* GANTI WARNA */
            }
        """)
        
        error_dialog.exec_() # <-- PERUBAHAN: exec() -> exec_()
        # --- AKHIR PERUBAHAN MIGRASI ---
    
    def _start_backup(self):
        try:
            if self.backup_in_progress:
                self._log("Backup is already in progress. Please wait until it finishes.")
                return
            self.btn_backup.setEnabled(False)
            if not self.backup_resume_available:
                self._resume_files = None
                self._resume_index = 0
                self._resume_backup_folder = None
            
            # --- VALIDASI BARU (LOGIKA DISESUAIKAN) ---
            is_folder_mode = self.radio_mode_folder.isChecked()
            
            # --- VALIDASI BARU: Output folder Wajib untuk SEMUA mode ---
            custom_output = self.line_custom_output.text().strip()
            if not custom_output:
                # --- TERJEMAHAN ---
                self._show_error(self.tr('popup_error_output_mandatory'))
                self._update_status(self.tr('status_no_custom_output'), "#e74c3c")
                self.btn_backup.setEnabled(True)
                return
            # --- AKHIR VALIDASI BARU ---

            mode_str = 'folder' if is_folder_mode else 'list'
            filter_list = []
            
            # --- Variabel untuk checkbox baru ---
            # --- SARAN 1: Baca dari Checkbox GLOBAL ---
            backup_raw_files = self.check_backup_raw_source_GLOBAL.isChecked()
            backup_jpg_files = self.check_backup_jpg_source_GLOBAL.isChecked()

            if is_folder_mode:
                # --- SARAN 1: Hapus bacaan Checkbox A ---
                # backup_raw_files = self.check_backup_raw_source_A.isChecked()
                # backup_jpg_files = self.check_backup_jpg_source_A.isChecked()

                if not self.jpg_folders:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_no_jpg_folder'))
                    self._update_status(self.tr('status_no_jpg_folder'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return
                
                # --- Validasi checkbox baru ---
                if not backup_raw_files and not backup_jpg_files:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_no_file_type'))
                    self._update_status(self.tr('status_no_file_type'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return

            else: # Mode List
                # --- SARAN 1: Hapus bacaan Checkbox B ---
                # backup_raw_files = self.check_backup_raw_source_B.isChecked()
                # backup_jpg_files = self.check_backup_jpg_source_B.isChecked()

                filter_text = self.filename_filter_list.toPlainText().strip()
                if not filter_text:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_empty_list'))
                    self._update_status(self.tr('status_list_empty'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return
                
                # --- Validasi checkbox baru (untuk Mode List) ---
                if not backup_raw_files and not backup_jpg_files:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_no_file_type'))
                    self._update_status(self.tr('status_no_file_type'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return
                
                # Parse filter list
                self._log("Applying filename filter...")
                normalized_text = filter_text.replace('\n', ',')
                raw_list = normalized_text.split(',')
                for item in raw_list:
                    item_stripped = item.strip()
                    if item_stripped:
                        # --- PERBAIKAN KRITIS 3: Hapus ekstensi ---
                        item_no_ext = os.path.splitext(item_stripped)[0]
                        filter_list.append(item_no_ext.lower())
                        # --- BUKAN: filter_list.append(item_stripped.lower()) ---
                        
                filter_list = list(set(filter_list)) # Hapus duplikat
                self._log(f"Filter keywords: {filter_list}")

            # Cek Source Folder (Kamera/Manual)
            if not self.dcim_folder or not os.path.exists(self.dcim_folder):
                # --- TERJEMAHAN ---
                self._show_error(self.tr('popup_error_no_source'))
                self._update_status(self.tr('status_no_source'), "#e74c3c")
                self.btn_backup.setEnabled(True)
                return

            # --- CEK SISA RUANG DISK (disederhanakan) ---
            backup_drive_path = custom_output # Selalu pakai custom_output
            
            if backup_drive_path:
                backup_drive = os.path.splitdrive(backup_drive_path)[0] + "\\"
                try:
                    free_bytes = shutil.disk_usage(backup_drive).free
                    if free_bytes < 100 * 1024 * 1024: # Cek jika sisa < 100MB
                        # --- TERJEMAHAN (f-string) ---
                        self._show_error(self.tr('popup_error_low_disk').format(drive=backup_drive, mb=free_bytes/1024/1024))
                        # Biarkan lanjut, tapi beri peringatan
                except Exception:
                    pass # Gagal cek sisa ruang

            # --- Cek folder 'RAW' dihapus, karena tidak relevan lagi ---
            
            self.backup_in_progress = True
            self._update_status(self.tr('status_processing'), "#f39c12")
            self._log("\n" + "="*40)
            self._log("🚀 STARTING BACKUP PROCESS")
            self._log(f"Mode: {mode_str.upper()}")
            self._log("="*40)
            self.stats = {
                'total_files': 0,
                'markers_found': 0,
                'files_to_backup': 0,
                'backup_folder': "",
                'elapsed_time': 0.0
            }
            
            self.progress_dialog = SmoothProgressDialog(self)
            self.progress_dialog.btn_cancel.clicked.connect(self.cancel_backup)
            dialog_rect = self.progress_dialog.frameGeometry()
            center_point = self.frameGeometry().center()
            dialog_rect.moveCenter(center_point)
            self.progress_dialog.move(dialog_rect.topLeft())
            self.progress_dialog.show()
            
            self.backup_thread = BackupThread(
                self.dcim_folder,
                self.max_files_to_scan,
                self.marker_size_threshold,
                mode=mode_str,
                jpg_folders=self.jpg_folders,
                filename_list=filter_list,
                custom_output_folder=custom_output, # <-- SELALU kirim custom_output
                resume_files=self._resume_files,
                resume_index=self._resume_index,
                resume_backup_folder=self._resume_backup_folder,
                backup_raw_files=backup_raw_files,     # <-- Kirim flag baru
                backup_jpg_files=backup_jpg_files,     # <-- Kirim flag baru
                # --- Kirim terjemahan ke Thread ---
                translations=self.translations,
                lang=self.current_language
            )
            self.backup_thread.update_log.connect(self._log)
            self.backup_thread.update_progress.connect(self._update_progress)
            self.backup_thread.update_status.connect(self._update_status)
            self.backup_thread.backup_completed.connect(self._show_backup_complete)
            self.backup_thread.show_error.connect(self._show_error) # Slot ini sekarang menerima pesan yg sudah diterjemahkan
            self.backup_thread.update_stats.connect(self._update_stats)
            self.backup_thread.camera_disconnected.connect(self.camera_disconnected)
            self.backup_thread.resume_state.connect(self.set_resume_state)
            self.backup_thread.file_copied.connect(self.set_last_success_file)
            self.backup_thread.finished.connect(self.on_backup_finished)
            self.backup_thread.start()
        except Exception as e:
            self._log(f"❌ Error occurred during backup start: {e}")
            import traceback
            traceback.print_exc()
            self.btn_backup.setEnabled(True)
    
    def on_backup_finished(self):
        self.btn_backup.setEnabled(True)
        self.backup_in_progress = False
        self.backup_interrupted = False          # Reset interrupted only if backup is truly finished
        # Reset resume state only if backup is finished
        self._resume_files = None
        self._resume_index = 0
        self._resume_backup_folder = None
        if self.progress_dialog:
            self.progress_dialog.accept()
            self.progress_dialog = None
        
        # Perbarui status ke 'Siap' HANYA jika tidak ada interupsi
        if not self.backup_interrupted and not self.backup_paused:
             self._update_status(self.tr('status_ready'), "#2ecc71")

    def closeEvent(self, event):
        # Confirm if backup is still running
        if getattr(self, 'backup_in_progress', False):
            msg_box = QMessageBox(self)
            # --- TERJEMAHAN ---
            msg_box.setWindowTitle(self.tr('popup_close_title'))
            msg_box.setText(self.tr('popup_close_text'))
            # --- AKHIR TERJEMAHAN ---
            # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
            msg_box.setIcon(QMessageBox.Warning)
            
            # Hanya tema terang
            msg_box.setStyleSheet("""
                QDialog, QMessageBox {
                    background-color: #f7f7f7;
                    border-radius: 10px;
                }
                QLabel {
                    color: #3d3545;
                    background-color: transparent;
                }
                QPushButton {
                    font-weight: bold;
                    min-width: 80px;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #FF63A4; /* GANTI WARNA */
                    color: white;
                }
                QPushButton:hover {
                    background-color: #D64C87; /* GANTI WARNA */
                }
            """)
            
            reply = msg_box.exec_() # <-- PERUBAHAN: exec() -> exec_()
            if reply == QMessageBox.No:
            # --- AKHIR PERUBAHAN MIGRASI ---
                event.ignore()
                return
        if self.camera_monitor:
            self.camera_monitor.stop()
        if self.camera_thread:
            self.camera_thread.quit()
            self.camera_thread.wait(1000)
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.stop()
            self.backup_thread.wait(2000)
        event.accept()

    def set_resume_state(self, files, index, backup_folder):
        self._resume_files = files
        self._resume_index = index
        self._resume_backup_folder = backup_folder

    def add_jpg_folder(self):
        # --- KEMBALIKAN KE DIALOG SATU FOLDER ---
        folder = QFileDialog.getExistingDirectory(self, "Select JPG Folder")
        if folder:
            # Normalisasi path
            normalized_path = os.path.normpath(folder)
            
            # Cek apakah folder sudah ada di list
            existing_items = [self.jpg_folder_list.item(i).text() for i in range(self.jpg_folder_list.count())]
            if normalized_path not in existing_items: # Cek di UI list
                 if normalized_path not in self.jpg_folders: # Cek di list internal
                    # Tambahkan ke list internal
                    self.jpg_folders.append(normalized_path)
                    # Tambahkan ke UI list
                    self.jpg_folder_list.addItem(normalized_path)
                    # Log sukses
                    self._log(f"📁 Destination folder added: {normalized_path}")
                    
                    # --- TERJEMAHAN (f-string) ---
                    status_text = self.tr('status_folders_selected').format(count=len(self.jpg_folders))
                    self._update_status(status_text, "#2ecc71")
                 else:
                    # Folder sudah ada, beri peringatan
                    self._log(f"⚠️ Destination folder already in list: {normalized_path}")
            else:
                 # Folder sudah ada, beri peringatan
                 self._log(f"⚠️ Destination folder already in list: {normalized_path}")
        # --- AKHIR PENGEMBALIAN ---

    def remove_selected_jpg_folder(self):
        selected_items = self.jpg_folder_list.selectedItems()
        if not selected_items: # Jika tidak ada yang dipilih, jangan lakukan apa-apa
            return

        items_removed = 0
        for item in selected_items:
            folder_path = item.text()
            # Normalisasi path untuk pencocokan
            normalized_path = os.path.normpath(folder_path)
            
            # Hapus dari list internal
            if normalized_path in self.jpg_folders:
                self.jpg_folders.remove(normalized_path)
                self._log(f"🗑️ Folder JPG dihapus: {normalized_path}")
                items_removed += 1
            
            # Hapus dari UI list
            self.jpg_folder_list.takeItem(self.jpg_folder_list.row(item))
        
        if items_removed > 0:
            # Update status
            if self.jpg_folders:
                # --- TERJEMAHAN (f-string) ---
                status_text = self.tr('status_folders_selected').format(count=len(self.jpg_folders))
                self._update_status(status_text, "#2ecc71")
            else:
                self._update_status(self.tr('status_ready'), "#2ecc71")

    # --- METHOD BARU (YANG HILANG) ---
    def cancel_backup(self):
        """Membatalkan proses backup yang sedang berjalan."""
        self._log("❌ Backup cancellation requested by user...")
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.stop()
            self.backup_thread.wait(2000) # Tunggu thread berhenti
        
        if self.progress_dialog:
            self.progress_dialog.reject() # Tutup dialog progres
            self.progress_dialog = None
        
        # Reset semua flag
        self.btn_backup.setEnabled(True) # Aktifkan tombol start lagi
        self.backup_in_progress = False
        self.backup_paused = False
        self.backup_resume_available = False
        self.backup_interrupted = False

        # Reset state resume
        self._resume_files = None
        self._resume_index = 0
        self._resume_backup_folder = None
        
        # --- TERJEMAHAN ---
        self._update_status(self.tr('status_cancelled'), "#e74c3c")
        self._log("❌ Backup cancelled by user.")

    def _resume_backup(self):
        try:
            if not self._resume_files or self._resume_index is None or not isinstance(self._resume_files, list) or self._resume_index >= len(self._resume_files):
                self.backup_resume_available = False
                self.btn_backup.setEnabled(True)
                self.btn_backup.clicked.connect(self._start_backup)  # Automatically start new backup
                return
            if self.backup_in_progress:
                self._log("Backup is already in progress. Please wait until it finishes.")
                return
            self.btn_backup.setEnabled(False)
            self.backup_paused = False
            self.backup_resume_available = False
            self.backup_in_progress = True
            self.backup_interrupted = False
            
            # --- TERJEMAHAN ---
            self._update_status(self.tr('status_processing'), "#f39c12")
            
            self._log("\n" + "="*40)
            self._log("⏪ RESUMING BACKUP")
            self._log("="*40)
            
            # +++ VALIDASI & PERSIAPAN UNTUK RESUME (DISESUAIKAN) +++
            is_folder_mode = self.radio_mode_folder.isChecked()
            
            # --- VALIDASI BARU: Output folder Wajib untuk SEMUA mode ---
            custom_output = self.line_custom_output.text().strip()
            if not custom_output:
                # --- TERJEMAHAN ---
                self._show_error(self.tr('popup_error_output_mandatory'))
                self._update_status(self.tr('status_no_custom_output'), "#e74c3c")
                self.btn_backup.setEnabled(True)
                return
            # --- AKHIR VALIDASI BARU ---
            
            mode_str = 'folder' if is_folder_mode else 'list'
            filter_list = []

            # --- Variabel untuk checkbox baru (UNTUK RESUME) ---
            # --- SARAN 1: Baca dari Checkbox GLOBAL ---
            backup_raw_files = self.check_backup_raw_source_GLOBAL.isChecked()
            backup_jpg_files = self.check_backup_jpg_source_GLOBAL.isChecked()

            if is_folder_mode:
                # --- SARAN 1: Hapus bacaan Checkbox A ---
                # backup_raw_files = self.check_backup_raw_source_A.isChecked()
                # backup_jpg_files = self.check_backup_jpg_source_A.isChecked()
                # Validasi checkbox
                if not backup_raw_files and not backup_jpg_files:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_no_file_type'))
                    self._update_status(self.tr('status_no_file_type'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return
            
            elif not is_folder_mode: # Mode List
                # --- SARAN 1: Hapus bacaan Checkbox B ---
                # backup_raw_files = self.check_backup_raw_source_B.isChecked()
                # backup_jpg_files = self.check_backup_jpg_source_B.isChecked()
                
                filter_text = self.filename_filter_list.toPlainText().strip()
                if not filter_text:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_empty_list'))
                    self.btn_backup.setEnabled(True)
                    return
                
                # --- Validasi checkbox baru (untuk Mode List) ---
                if not backup_raw_files and not backup_jpg_files:
                    # --- TERJEMAHAN ---
                    self._show_error(self.tr('popup_error_no_file_type'))
                    self._update_status(self.tr('status_no_file_type'), "#e74c3c")
                    self.btn_backup.setEnabled(True)
                    return
                
                # Parse filter list
                normalized_text = filter_text.replace('\n', ',')
                raw_list = normalized_text.split(',')
                for item in raw_list:
                    item_stripped = item.strip()
                    if item_stripped:
                        # --- PERBAIKAN KRITIS 3: Hapus ekstensi ---
                        item_no_ext = os.path.splitext(item_stripped)[0]
                        filter_list.append(item_no_ext.lower())
                filter_list = list(set(filter_list))
            
            self.progress_dialog = SmoothProgressDialog(self)
            self.progress_dialog.btn_cancel.clicked.connect(self.cancel_backup)
            dialog_rect = self.progress_dialog.frameGeometry()
            center_point = self.frameGeometry().center()
            dialog_rect.moveCenter(center_point)
            self.progress_dialog.move(dialog_rect.topLeft())
            self.progress_dialog.show()
            
            self.backup_thread = BackupThread(
                self.dcim_folder,
                self.max_files_to_scan,
                self.marker_size_threshold,
                mode=mode_str,
                jpg_folders=self.jpg_folders,
                filename_list=filter_list,
                custom_output_folder=custom_output, # <-- SELALU kirim custom_output
                resume_files=self._resume_files,
                resume_index=self._resume_index,
                resume_backup_folder=self._resume_backup_folder,
                backup_raw_files=backup_raw_files,     # <-- Kirim flag baru
                backup_jpg_files=backup_jpg_files,     # <-- Kirim flag baru
                # --- Kirim terjemahan ke Thread ---
                translations=self.translations,
                lang=self.current_language
            )
            self.backup_thread.update_log.connect(self._log)
            self.backup_thread.update_progress.connect(self._update_progress)
            self.backup_thread.update_status.connect(self._update_status)
            self.backup_thread.backup_completed.connect(self._show_backup_complete)
            self.backup_thread.show_error.connect(self._show_error)
            self.backup_thread.update_stats.connect(self._update_stats)
            self.backup_thread.camera_disconnected.connect(self.camera_disconnected)
            self.backup_thread.resume_state.connect(self.set_resume_state)
            self.backup_thread.file_copied.connect(self.set_last_success_file)
            self.backup_thread.finished.connect(self.on_backup_finished)
            self.backup_thread.start()
        except Exception as e:
            self._log(f"❌ Error occurred during backup resume: {e}")
            # --- TERJEMAHAN (f-string) ---
            QMessageBox.critical(self, self.tr('dialog_error_title'), self.tr('popup_error_resume').format(e=e))
            self.btn_backup.setEnabled(True)

    def set_last_success_file(self, path):
        self.last_success_file = path

    def on_folder_dropped(self, folder_path):
        """Menangani folder yang di-drop ke list"""
        try:
            # Normalisasi path
            normalized_path = os.path.normpath(folder_path)
            
            # Cek apakah folder sudah ada di list
            if normalized_path not in self.jpg_folders:
                # Tambahkan ke list internal
                self.jpg_folders.append(normalized_path)
                # Tambahkan ke UI list
                self.jpg_folder_list.addItem(normalized_path)
                # Log sukses
                self._log(f"📁 Destination folder added: {normalized_path}")
                # --- TERJEMAHAN (f-string) ---
                self._update_status(self.tr('status_folders_selected').format(count=len(self.jpg_folders)), "#2ecc71")
            else:
                # Folder sudah ada, beri peringatan
                self._log(f"⚠️ Destination folder already in list: {normalized_path}")
        except Exception as e:
            self._log(f"❌ Error adding folder: {e}")
            self._update_status("Status: Error adding folder", "#e74c3c")
            
    # --- PERUBAHAN: Helper baru untuk me-restart CameraMonitor ---
    def _restart_camera_monitor(self):
        """Menghentikan monitor lama (jika ada) dan memulai monitor baru untuk self.dcim_folder."""
        
        # Matikan monitor lama
        if self.camera_thread:
            self.camera_monitor.stop()
            self.camera_thread.quit()
            self.camera_thread.wait()
            self._log("Camera monitor stopped.")
            self.camera_monitor = None
            self.camera_thread = None

        # Mulai monitor baru jika path valid dan BUKAN (bukan) pilihan manual yang terputus
        if self.dcim_folder and os.path.exists(self.dcim_folder):
            self.camera_monitor = CameraMonitor(self.dcim_folder)
            self.camera_thread = QThread()
            self.camera_monitor.moveToThread(self.camera_thread)
            self.camera_monitor.camera_connected.connect(self.camera_connected)
            self.camera_monitor.camera_disconnected.connect(self.camera_disconnected)
            self.camera_thread.started.connect(self.camera_monitor.run)
            self.camera_thread.start()
            self._log(f"Camera monitor started for new path: {self.dcim_folder}")
        else:
            self._log(f"Cannot start monitor: path does not exist or is None.")
    # --- AKHIR PERUBAHAN ---

    # --- AKHIR DARI SEMUA METODE ModernBackupApp ---

# --- KELAS BACKUPTHREAD YANG HILANG DITAMBAHKAN DI SINI ---
class BackupThread(QThread):
    """
    Thread terpisah untuk menangani proses backup agar UI tidak freeze.
    """
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(float, str, int, int) # percent, filename, total_bytes, bytes_copied
    update_status = pyqtSignal(str, str)
    backup_completed = pyqtSignal(str, int) # backup_folder, file_count
    show_error = pyqtSignal(str) # --- Signal ini sekarang mengirimkan pesan yang SUDAH diterjemahkan ---
    update_stats = pyqtSignal(dict)
    camera_disconnected = pyqtSignal()
    resume_state = pyqtSignal(object, int, str) # Kirim 'object' (list)
    file_copied = pyqtSignal(str)

    def __init__(self, dcim_folder, max_files, marker_size, 
                 mode, jpg_folders, filename_list, custom_output_folder,
                 resume_files, resume_index, resume_backup_folder,
                 backup_raw_files, backup_jpg_files, 
                 translations, lang): # --- Terima terjemahan ---
        super().__init__()
        self.dcim_folder = dcim_folder
        self.max_files_to_scan = max_files
        self.marker_size_threshold = marker_size
        self._running = True
        
        # Pengaturan Mode
        self.mode = mode
        self.jpg_folders = jpg_folders or []
        self.filename_list = filename_list or []
        self.custom_output_folder = custom_output_folder
        
        # Pengaturan Tipe File
        self.backup_raw_files = backup_raw_files
        self.backup_jpg_files = backup_jpg_files
        
        # Resume State
        self._resume_files = resume_files
        self._resume_index = resume_index
        self._resume_backup_folder = resume_backup_folder

        # --- Simpan terjemahan ---
        self.translations = translations
        self.lang = lang

    # --- Tambahkan helper tr() di dalam thread ---
    def tr(self, key):
        """Helper untuk mendapatkan terjemahan dengan fallback ke English."""
        try:
            return self.translations[key][self.lang]
        except KeyError:
            try:
                # Fallback ke English
                return self.translations[key]['en']
            except KeyError:
                # Fallback ke key itu sendiri jika tidak ditemukan
                print(f"WARNING (Thread): Missing translation for key: {key}")
                return key

    def stop(self):
        self._running = False
        self.update_log.emit("Backup stopping...")

    def run(self):
        try:
            start_time = time.time()
            copied_count = 0 # Lacak jumlah file yang *baru* dicopy sesi ini
            
            # Ekstensi file yang dikenal
            raw_extensions = {'.nef', '.cr2', '.cr3', '.arw', '.orf', '.rw2', '.raf', '.dng', '.pef'}
            jpg_extensions = {'.jpg', '.jpeg'}

            files_to_backup = [] # List of tuples: (source_path, dest_path, size)
            
            # Tentukan folder output
            if not self.custom_output_folder:
                 # Ini seharusnya sudah divalidasi oleh UI, tapi sebagai fallback
                self.show_error.emit(self.tr('popup_error_output_mandatory'))
                return

            backup_folder = os.path.normpath(self.custom_output_folder)
            self.update_log.emit(f"Output folder set to: {backup_folder}")

            # Buat folder jika belum ada
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            # --- Bagian 1: Tentukan file apa saja yang akan di-backup ---
            
            if self._resume_files:
                # Lanjutkan dari state sebelumnya
                self.update_log.emit("Resuming previous backup...")
                files_to_backup = self._resume_files # Ini adalah list of tuples
                backup_folder = self._resume_backup_folder
                start_index = self._resume_index
            
            else:
                # Mulai backup baru, cari file
                start_index = 0
                self.update_log.emit("Starting new backup, scanning files...")
                
                # --- LOGIKA PENCARIAN (MODE FOLDER) ---
                if self.mode == 'folder':
                    self.update_log.emit("Mode: Folder. Finding matching files...")
                    
                    # 1. Buat set (daftar unik) nama file JPG target
                    jpg_filenames_set = set()
                    self.update_log.emit(f"Scanning {len(self.jpg_folders)} JPG folder(s)...")
                    for folder in self.jpg_folders:
                        for root, _, files in os.walk(folder):
                            for filename in files:
                                if filename.lower().endswith(('.jpg', '.jpeg')):
                                    # Gunakan keyify untuk normalisasi
                                    key = keyify(os.path.splitext(filename)[0])
                                    jpg_filenames_set.add(key)
                    
                    if not jpg_filenames_set:
                        self.show_error.emit(self.tr('popup_error_no_jpg_folder')) 
                        return
                    self.update_log.emit(f"Found {len(jpg_filenames_set)} unique JPG filenames to match.")
                    
                    # 2. Pindai folder SUMBER (DCIM)
                    self.update_log.emit(f"Scanning source folder: {self.dcim_folder}")
                    for root, _, files in os.walk(self.dcim_folder):
                        for filename in files:
                            if not self._running:
                                self.update_status.emit(self.tr('status_cancelled'), "#e74c3c")
                                return
                            
                            file_no_ext, file_ext = os.path.splitext(filename)
                            file_ext_lower = file_ext.lower()
                            
                            is_raw = file_ext_lower in raw_extensions
                            is_jpg = file_ext_lower in jpg_extensions
                            
                            if (self.backup_raw_files and is_raw) or (self.backup_jpg_files and is_jpg):
                                source_key = keyify(file_no_ext)
                                if source_key in jpg_filenames_set:
                                    source_path = os.path.join(root, filename)
                                    dest_path = os.path.join(backup_folder, filename)
                                    try:
                                        size = os.path.getsize(source_path)
                                        files_to_backup.append((source_path, dest_path, size))
                                    except OSError:
                                        self.update_log.emit(f"⚠️ Could not get size for {filename}, skipping.")

                # --- LOGIKA PENCARIAN (MODE LIST) ---
                elif self.mode == 'list':
                    self.update_log.emit("Mode: List. Finding files matching keyword list...")
                    
                    filter_keywords = [f.lower() for f in (self.filename_list or [])]
                    
                    if not filter_keywords:
                        self.show_error.emit(self.tr('popup_error_empty_list'))
                        return
                        
                    self.update_log.emit(f"Scanning source with {len(filter_keywords)} keywords...")
                    
                    for root, _, files in os.walk(self.dcim_folder):
                        if not self._running:
                            self.update_status.emit(self.tr('status_cancelled'), "#e74c3c")
                            return
                            
                        for filename in files:
                            file_path = os.path.join(root, filename)
                            file_no_ext, file_ext = os.path.splitext(filename)
                            file_no_ext_lower = file_no_ext.lower()
                            file_ext_lower = file_ext.lower()
                            
                            is_raw = file_ext_lower in raw_extensions
                            is_jpg = file_ext_lower in jpg_extensions
                            
                            if (self.backup_raw_files and is_raw) or (self.backup_jpg_files and is_jpg):
                                is_match = False
                                for keyword in filter_keywords:
                                    # LOGIKA BARU: .endswith()
                                    # Ini cocok jika filter_list = ['1234'] dan nama file = ['_dsc1234']
                                    if file_no_ext_lower.endswith(keyword):
                                        is_match = True
                                        break
                                
                                if is_match:
                                    dest_path = os.path.join(backup_folder, filename)
                                    try:
                                        size = os.path.getsize(file_path)
                                        files_to_backup.append((file_path, dest_path, size))
                                    except OSError:
                                        self.update_log.emit(f"⚠️ Could not get size for {filename}, skipping.")
            
            # --- Bagian 2: Lakukan proses penyalinan (copy) ---
            
            # Hapus duplikat (berdasarkan source_path)
            seen_sources = set()
            unique_files_to_backup = []
            for (source, dest, size) in files_to_backup:
                if source not in seen_sources:
                    unique_files_to_backup.append((source, dest, size))
                    seen_sources.add(source)
            
            files_to_backup = sorted(unique_files_to_backup) # Sortir berdasarkan source_path
            total_files_in_list = len(files_to_backup)
            
            if total_files_in_list == 0:
                self.update_log.emit("No matching files found to back up.")
                self.update_status.emit(self.tr('status_no_match'), "#f39c12")
                return

            self.update_log.emit(f"Total files in list: {total_files_in_list} (starting from {start_index + 1})")
            
            # --- PERBAIKAN LOGIKA PROGRESS BAR ---
            # Hitung total ukuran file (hanya untuk file yang *akan* dicopy)
            total_size_to_copy = 0
            for i in range(start_index, total_files_in_list):
                total_size_to_copy += files_to_backup[i][2] # (source, dest, size)
            
            # Hitung total bytes yang sudah dicopy (untuk resume)
            bytes_copied_at_start = 0
            for i in range(start_index):
                 bytes_copied_at_start += files_to_backup[i][2]

            # Total ukuran pekerjaan = yang sudah selesai + yang akan dikerjakan
            # Ini adalah denominator (pembagi) yang KONSTAN
            total_job_size = total_size_to_copy + bytes_copied_at_start
            # Buat variabel running terpisah untuk numerator (pembilang)
            running_bytes_copied = bytes_copied_at_start

            self.update_log.emit(f"Total job size: {total_job_size / (1024*1024):.2f} MB")
            self.update_log.emit(f"Resuming at: {running_bytes_copied / (1024*1024):.2f} MB")
            # --- AKHIR PERBAIKAN LOGIKA ---
            
            files_copied_this_session = 0

            for i in range(start_index, total_files_in_list):
                if not self._running:
                    self.update_status.emit(self.tr('status_cancelled'), "#e74c3c")
                    self.resume_state.emit(files_to_backup, i, backup_folder)
                    self.update_log.emit(f"Backup paused. Ready to resume from file {i+1}/{total_files_in_list}")
                    return
                
                source_path, dest_path, file_size = files_to_backup[i]
                filename = os.path.basename(source_path)
                
                try:
                    if not os.path.exists(source_path):
                        self.update_log.emit(f"⚠️ Skipping (file not found): {filename}")
                        running_bytes_copied += file_size # Anggap sudah tercopy jika source hilang
                        continue
                    
                    # Update progress
                    # --- PERBAIKAN: Gunakan variabel yang benar ---
                    percent = (running_bytes_copied / total_job_size) * 100 if total_job_size > 0 else 0
                    self.update_progress.emit(percent, f"({i+1}/{total_files_in_list}) {filename}", total_job_size, running_bytes_copied)
                    
                    # Cek jika file sudah ada
                    if os.path.exists(dest_path) and os.path.getsize(dest_path) == file_size:
                        self.update_log.emit(f"Skipping (already exists): {filename}")
                        running_bytes_copied += file_size # Hitung sebagai sudah dicopy
                    else:
                        self.update_log.emit(f"Copying: {filename}")
                        # --- Proses copy aman ---
                        temp_dest_path = dest_path + ".part"
                        
                        with open(source_path, 'rb') as fsrc, open(temp_dest_path, 'wb') as fdst:
                            while True:
                                if not self._running: # Cek di dalam loop read/write
                                    raise Exception("Backup cancelled during file copy")
                                chunk = fsrc.read(1024 * 1024) # 1MB chunk
                                if not chunk:
                                    break
                                fdst.write(chunk)
                                
                                # Update progress di dalam loop copy
                                # --- PERBAIKAN: Gunakan variabel yang benar ---
                                running_bytes_copied += len(chunk)
                                percent = (running_bytes_copied / total_job_size) * 100 if total_job_size > 0 else 0
                                self.update_progress.emit(percent, f"({i+1}/{total_files_in_list}) {filename}", total_job_size, running_bytes_copied)

                        os.replace(temp_dest_path, dest_path)
                        # --- Akhir proses copy aman ---
                        
                        self.file_copied.emit(dest_path) # Kirim sinyal file sukses
                        files_copied_this_session += 1

                except Exception as e:
                    self.update_log.emit(f"❌ ERROR copying {filename}: {e}")
                    
                    # --- PERBAIKAN 3: Penanganan Disk Putus ---
                    # Hapus file .part jika gagal
                    try:
                        if 'temp_dest_path' in locals() and os.path.exists(temp_dest_path):
                            os.remove(temp_dest_path)
                    except Exception as e_rm:
                        self.update_log.emit(f"⚠️ Failed to remove .part file: {e_rm}")
                        
                    if "No space left on device" in str(e):
                        self.show_error.emit(self.tr('popup_disk_full'))
                        self.resume_state.emit(files_to_backup, i, backup_folder)
                        return # Hentikan thread
                    
                    # Jika error adalah OSError (kemungkinan disk/kamera dicabut)
                    # Hentikan loop dan thread
                    if isinstance(e, (OSError, IOError)):
                        self.update_log.emit(f"❌ Device disconnected or critical I/O Error. Stopping backup.")
                        self.camera_disconnected.emit() # Kirim sinyal kamera putus
                        self.resume_state.emit(files_to_backup, i, backup_folder)
                        return # Hentikan thread
                    # --- AKHIR PERBAIKAN 3 ---
                    
                    # Jika error lain (misal file permission), lanjut ke file berikutnya
                    running_bytes_copied += file_size # Anggap file ini gagal & dilewati

            # Selesai
            elapsed_time = time.time() - start_time
            # --- PERBAIKAN: Kirim total yang benar saat selesai ---
            self.update_progress.emit(100, "Backup complete!", total_job_size, total_job_size)
            self.update_log.emit(f"✅ Backup complete. {files_copied_this_session} new files copied.")
            self.update_status.emit(f"{self.tr('status_completed')} ({files_copied_this_session} file)", "#2ecc71")
            self.backup_completed.emit(backup_folder, files_copied_this_session)
            
        except Exception as e:
            self.update_log.emit(f"❌ A critical error occurred in the backup thread: {e}")
            traceback.print_exc()
            self.show_error.emit(f"{self.tr('dialog_error_title')}: {e}")
# --- AKHIR DARI KELAS BACKUPTHREAD ---


# Fungsi untuk memutar suara popup Windows
def play_popup_sound(kind="info"):
    global _popup_sound_effect
    try:
        if _popup_sound_effect is None:
            _popup_sound_effect = QSoundEffect()
        sound = _popup_sound_effect
        if kind == "error":
            sound.setSource(QUrl.fromLocalFile(r"C:\\Windows\\Media\\Windows Critical Stop.wav"))
        elif kind == "warning":
            sound.setSource(QUrl.fromLocalFile(r"C:\\Windows\\Media\\Windows Exclamation.wav"))
        else:
            sound.setSource(QUrl.fromLocalFile(r"C:\\Windows\\Media\\Windows Notify.wav"))
        sound.setVolume(0.5)
        sound.play()
    except Exception as e:
        print(f"Sound error: {e}")

# --- AWAL BLOK LISENSI ONLINE ---

# !!! INI ADALAH URL DATABASE ANDA !!!
FIREBASE_URL = "https://lisensibackupraw-default-rtdb.firebaseio.com/"

def get_pc_hash():
    """Mengambil MAC address dan mengubahnya menjadi hash SHA256 yang unik."""
    try:
        # Ambil MAC address sebagai string
        mac = str(uuid.getnode())
        # Hash string tersebut agar aman dan anonim
        pc_hash = hashlib.sha256(mac.encode('utf-8')).hexdigest()
        return pc_hash
    except Exception:
        # Fallback jika uuid gagal
        return "failed-to-get-hash"

def get_license_filepath():
    """Mendapatkan path file lisensi yang aman di folder APPDATA."""
    system = platform.system()
    try:
        if system == "Windows":
            # C:\Users\<Nama>\AppData\Roaming
            app_data = os.environ.get("APPDATA")
        elif system == "Darwin": # macOS
            # /Users/<Nama>/Library/Application Support
            app_data = os.path.expanduser("~/Library/Application Support")
        else: # Linux
            # /home/<Nama>/.config
            app_data = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        
        if not app_data: # Fallback jika env var tidak ada
            app_data = os.getcwd()

        # Buat folder khusus untuk app Anda agar rapi
        app_folder = os.path.join(app_data, "BackupRaw")
        if not os.path.exists(app_folder):
            os.makedirs(app_folder, exist_ok=True)
            
        return os.path.join(app_folder, "backupraw.license")
    except Exception:
        # Fallback jika ada error izin, simpan di folder kerja
        return os.path.join(os.getcwd(), "backupraw.license")

class ActivationDialog(QDialog):
    """Dialog popup untuk meminta kunci lisensi."""
    def __init__(self, pc_hash, translations, lang, parent=None):
        super().__init__(parent)
        self.pc_hash = pc_hash
        self.license_key = ""
        
        # --- Terima terjemahan ---
        self.translations = translations
        self.lang = lang
        # --- Buat helper tr() lokal ---
        def tr(key):
            try:
                return self.translations[key][self.lang]
            except KeyError:
                try:
                    return self.translations[key]['en'] # Fallback
                except KeyError:
                    return key
        self.tr = tr
        # --- Akhir setup terjemahan ---
        
        # --- TERJEMAHAN ---
        self.setWindowTitle(self.tr('lic_title'))
        # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # --- TERJEMAHAN ---
        title = QLabel(self.tr('lic_needed'))
        title_font = QFont() # <-- PERBAIKAN FONT
        title_font.setPointSize(14) # <-- PERBAIKAN FONT
        title_font.setWeight(QFont.Bold) # <-- PERBAIKAN FONT
        title.setFont(title_font) # <-- PERBAIKAN FONT
        layout.addWidget(title, 0, Qt.AlignHCenter)

        # --- TERJEMAHAN ---
        self.status_label = QLabel(self.tr('lic_prompt'))
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        # --- AKHIR PERUBAHAN MIGRASI ---

        self.key_input = QLineEdit()
        # --- TERJEMAHAN ---
        self.key_input.setPlaceholderText(self.tr('lic_placeholder'))
        key_font = QFont("Courier New") # <-- PERBAIKAN FONT
        key_font.setPointSize(10) # <-- PERBAIKAN FONT
        self.key_input.setFont(key_font) # <-- PERBAIKAN FONT
        layout.addWidget(self.key_input)

        # Tombol
        btn_layout = QHBoxLayout()
        # --- TERJEMAHAN ---
        self.activate_btn = QPushButton(self.tr('lic_btn_activate'))
        self.activate_btn.clicked.connect(self.do_activation)
        
        # --- TERJEMAHAN ---
        self.cancel_btn = QPushButton(self.tr('lic_btn_exit'))
        self.cancel_btn.clicked.connect(self.reject) # Keluar dari app

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.activate_btn)
        layout.addLayout(btn_layout)

        # Terapkan styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f7f7f7;
                border-radius: 10px;
            }
            QLabel {
                color: #3d3545;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                padding: 8px;
                border-radius: 5px;
                color: white;
            }
            QPushButton#activate_btn {
                background-color: #FF63A4; /* GANTI WARNA */
            }
            QPushButton#activate_btn:hover {
                background-color: #D64C87; /* GANTI WARNA */
            }
            QPushButton#cancel_btn {
                background-color: #e74c3c;
            }
            QPushButton#cancel_btn:hover {
                background-color: #c0392b;
            }
        """)
        # Beri nama objek agar stylesheet spesifik bisa berlaku
        self.activate_btn.setObjectName("activate_btn")
        self.cancel_btn.setObjectName("cancel_btn")

    def do_activation(self):
        """Mencoba validasi kunci secara online."""
        key = self.key_input.text().strip().upper()
        if not key:
            # --- TERJEMAHAN ---
            self.status_label.setText(self.tr('lic_err_empty'))
            return

        # --- TERJEMAHAN ---
        self.status_label.setText(self.tr('lic_contacting'))
        self.activate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        QApplication.processEvents() # Paksa UI update

        # Kirim ke fungsi validasi (yang berjalan di thread lain agar UI tidak freeze)
        # Kita pakai QThread sederhana untuk operasi jaringan
        self.worker = ValidationWorker(key, self.pc_hash)
        self.worker.finished.connect(self.on_validation_finished)
        self.worker.start()

    def on_validation_finished(self, success, message_key, format_arg):
        """
        Dipanggil saat validasi online selesai.
        'message_key' adalah KUNCI terjemahan, 'format_arg' adalah data (jika ada).
        """
        
        # --- PERBAIKAN KRITIS 4: Logika format pesan ---
        raw_message = self.tr(message_key)
        message = raw_message
        try:
            if format_arg: # Jika format_arg tidak kosong
                if '{e}' in raw_message:
                    message = raw_message.format(e=format_arg)
                elif '{code}' in raw_message:
                    message = raw_message.format(code=format_arg)
        except Exception:
            message = raw_message # Fallback jika format gagal
            
        self.status_label.setText(message)
        # --- AKHIR PERBAIKAN ---
        
        self.activate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

        if success:
            # Sukses! Simpan lisensi lokal dan tutup dialog
            try:
                filepath = get_license_filepath()
                with open(filepath, 'w') as f:
                    f.write(self.pc_hash)
                
                # Beri tahu pengguna bahwa sukses
                msg_box = QMessageBox(self)
                # --- TERJEMAHAN ---
                msg_box.setWindowTitle(self.tr('lic_val_success_title'))
                msg_box.setText(self.tr('lic_val_success_text'))
                # --- AKHIR TERJEMAHAN ---
                # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
                msg_box.setIcon(QMessageBox.Information)
                
                # Terapkan stylesheet lokal untuk MEMASTIKAN tombol OK terlihat
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #f7f7f7;
                        border-radius: 10px;
                    }
                    QLabel {
                        color: #3d3545;
                        background-color: transparent;
                    }
                    QPushButton {
                        font-weight: bold;
                        min-width: 80px;
                        padding: 8px;
                        border-radius: 5px;
                        background-color: #FF63A4; /* GANTI WARNA */
                        color: white; /* Teks putih */
                    }
                    QPushButton:hover {
                        background-color: #D64C87; /* GANTI WARNA */
                    }
                """)
                msg_box.exec_() # <-- PERUBAHAN: exec() -> exec_()
                
                self.accept() # Tutup dialog dengan status "sukses"
                # --- AKHIR PERUBAHAN MIGRASI ---
            except Exception as e:
                # --- TERJEMAHAN (f-string) ---
                err_msg = self.tr('lic_val_err_save_text').format(e=e)
                self.status_label.setText(err_msg)
                QMessageBox.critical(self, self.tr('lic_val_err_save_title'), err_msg)
                # --- AKHIR TERJEMAHAN ---

class ValidationWorker(QThread):
    """
    Worker thread untuk validasi online agar UI tidak freeze.
    Signal 'finished' sekarang mengirimkan (bool, str_key, str_arg)
    """
    # --- PERBAIKAN KRITIS 4: Ubah sinyal ---
    finished = pyqtSignal(bool, str, str) # (success, message_key, format_arg)

    def __init__(self, key, pc_hash):
        super().__init__()
        self.key = key
        self.pc_hash = pc_hash

    def run(self):
        try:
            # 1. BACA data dari Firebase
            url_read = f"{FIREBASE_URL}/licenses/{self.key}.json"
            response = requests.get(url_read, timeout=10)

            if response.status_code != 200 or response.text == "null":
                # --- PERBAIKAN KRITIS 4: Kirim arg kosong ---
                self.finished.emit(False, 'lic_val_invalid_key', '')
                return

            data = response.json()
            server_pc_id = data.get("pc_id")

            if server_pc_id is None:
                # --- PERBAIKAN KRITIS 4: Kirim arg kosong ---
                self.finished.emit(False, 'lic_val_data_format', '')
                return

            # 2. CEK PC ID
            # Kunci sudah dipakai PC lain
            if server_pc_id != "" and server_pc_id != self.pc_hash:
                # --- PERBAIKAN KRITIS 4: Kirim arg kosong ---
                self.finished.emit(False, 'lic_val_key_used', '')
                return
            
            # Kunci masih kosong ("") or sama dengan PC ini (self.pc_hash)
            # Keduanya valid, lanjutkan ke penulisan.
            
            # 3. TULIS (Aktivasi) data ke Firebase
            url_write = f"{FIREBASE_URL}/licenses/{self.key}/pc_id.json"
            payload = json.dumps(self.pc_hash) # Kirim hash PC kita
            
            response_write = requests.put(url_write, data=payload, timeout=10)

            if response_write.status_code == 200:
                # --- PERBAIKAN KRITIS 4: Kirim arg kosong ---
                self.finished.emit(True, 'lic_val_success_saving', '')
            else:
                # --- PERBAIKAN KRITIS 4: Kirim status code ---
                self.finished.emit(False, 'lic_val_server_fail', str(response_write.status_code))

        except requests.exceptions.ConnectionError:
            # --- PERBAIKAN KRITIS 4: Kirim arg kosong ---
            self.finished.emit(False, 'lic_val_no_internet', '')
        except Exception as e:
            # --- PERBAIKAN KRITIS 4: Kirim pesan error ---
            self.finished.emit(False, 'lic_val_unknown_err', str(e)) 

def check_license():
    """
    Fungsi utama pengecekan lisensi.
    Mengembalikan True jika valid, False jika gagal/dibatalkan.
    """
    # --- TERJEMAHAN UNTUK FUNGSI PRA-APP ---
    # Dapatkan bahasa sistem SEBELUM app dibuat
    # system_lang = QLocale.system().name()[:2] # 'id' atau 'en' # <-- DIHAPUS
    # --- PERUBAHAN: Jadikan Bahasa Indonesia sebagai default ---
    # if system_lang == 'en': # <-- DIHAPUS
    #     system_lang = 'en'
    # else:
    #     system_lang = 'id' # Default ke 'id'
    system_lang = 'id' # <-- LANGSUNG SET KE 'id'
        
    translations = get_all_translations()
    
    # Buat helper tr() lokal
    def lic_tr(key):
        try:
            return translations[key][system_lang]
        except KeyError:
            try:
                return translations[key]['en'] # Fallback
            except KeyError:
                return key
    # --- AKHIR SETUP TERJEMAHAN ---

    license_file = get_license_filepath()
    current_pc_hash = get_pc_hash()

    if current_pc_hash == "failed-to-get-hash":
        # --- TERJEMAHAN ---
        QMessageBox.critical(None, 
                             lic_tr('lic_err_get_hash_title'), 
                             lic_tr('lic_err_get_hash_text'))
        return False

    # 1. Cek file lisensi lokal (Fast path)
    if os.path.exists(license_file):
        try:
            with open(license_file, 'r') as f:
                stored_hash = f.read().strip()
            if stored_hash == current_pc_hash:
                # Sukses! Lisensi lokal cocok dengan PC ini
                return True
            else:
                # File lisensi ada, tapi hash-nya beda (dicopy dari PC lain)
                pass # Lanjut ke aktivasi online
        except Exception:
            # File lisensi rusak
            pass # Lanjut ke aktivasi online

    # 2. Jika lisensi lokal tidak ada / tidak cocok, tunjukkan dialog
    # --- Kirim terjemahan & bahasa ke dialog ---
    dialog = ActivationDialog(current_pc_hash, translations, system_lang)
    # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
    if dialog.exec_() == QDialog.Accepted:
    # --- AKHIR PERUBAHAN MIGRASI ---
        return True # Aktivasi online baru saja berhasil
    
    # Jika user menekan "Keluar" (reject)
    return False

# --- AKHIR BLOK LISENSI ONLINE ---\


if __name__ == "__main__":
    
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    freeze_support()
    
    # --- PERBAIKAN KRITIS 2: Pindahkan 'app' ke atas ---\
    app = QApplication(sys.argv)
    
    # Single instance lock
    shared_memory = QSharedMemory("ModernBackupAppSingleInstance")
    if not shared_memory.create(1):
        sys.exit(0)  # Exit silently if another instance already exists
    
    # --- PERBAIKAN KRITIS 2: Simpan referensi shared_memory ---\
    app.shared_memory = shared_memory
    
    # --- PENTING: BARIS app.setStyle("Fusion") DIHAPUS UNTUK FIX BUG TEMA DI KOMPUTER LAIN ---\
    
    # --- BLOK PENGECEKAN LISENSI ---\
    # Memanggil fungsi cek lisensi SEBELUM memuat main window
    # Fungsi ini sekarang sudah memiliki terjemahan internal
    if not check_license():
        sys.exit(0) # Keluar jika lisensi gagal atau dibatalkan
    # --- AKHIR BLOK LISENSI ---\

    window = ModernBackupApp()
    window.show()
    # --- PERUBAHAN MIGRASI: PyQt6 -> PyQt5 ---
    sys.exit(app.exec_())

