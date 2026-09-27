import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from PyQt6.QtCore import QThread, pyqtSignal

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AutoUpdaterWorker(QThread):
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def run(self):
        bin_dir = resource_path(os.path.join('src', 'yt_dlp'))
        os.makedirs(bin_dir, exist_ok=True)

        # -------------------------------------------------------------
        # 1. ОБНОВЛЕНИЕ yt-dlp
        # -------------------------------------------------------------
        ytdlp_exe = os.path.join(bin_dir, 'yt-dlp.exe')
        
        if os.path.exists(ytdlp_exe):
            # Если вы используете внешний yt-dlp.exe
            self.status_signal.emit("🔄 Проверка обновлений yt-dlp.exe...")
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(
                    [ytdlp_exe, "-U"], 
                    capture_output=True, 
                    text=True, 
                    creationflags=creationflags
                )
                output = res.stdout.strip() or res.stderr.strip()
                self.status_signal.emit(f"✅ yt-dlp: {output}")
            except Exception as e:
                self.status_signal.emit(f"⚠️ Ошибка обновления yt-dlp.exe: {e}")
        else:
            # Если yt-dlp используется как Python-модуль
            if not hasattr(sys, '_MEIPASS'):
                # Только в исходном коде (.py), в .exe через pip обновить нельзя
                self.status_signal.emit("🔄 Обновление пакета yt-dlp через pip...")
                try:
                    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                        capture_output=True,
                        creationflags=creationflags
                    )
                    self.status_signal.emit("✅ Модуль yt-dlp обновлен через pip")
                except Exception as e:
                    self.status_signal.emit(f"⚠️ Ошибка pip update: {e}")
            else:
                self.status_signal.emit("ℹ️ Используется встроенный yt-dlp (динамические компоненты активны)")

        # -------------------------------------------------------------
        # 2. ПРОВЕРКА / ЗАГРУЗКА FFmpeg (Если файл отсутствует)
        # -------------------------------------------------------------
        ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_exe):
            self.status_signal.emit("⏬ FFmpeg не найден. Загрузка сборки...")
            try:
                # Прямая ссылка на официальный актуальный бинарник FFmpeg essentials
                url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                zip_path = os.path.join(bin_dir, "ffmpeg.zip")

                # Скачивание zip-архива
                urllib.request.urlretrieve(url, zip_path)

                # Распаковка только ffmpeg.exe
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith("ffmpeg.exe"):
                            with zip_ref.open(file) as source, open(ffmpeg_exe, "wb") as target:
                                shutil.copyfileobj(source, target)
                            break
                
                # Удаляем временный архив
                if os.path.exists(zip_path):
                    os.remove(zip_path)

                self.status_signal.emit("✅ FFmpeg успешно загружен и установлен")
            except Exception as e:
                self.status_signal.emit(f"❌ Ошибка загрузки FFmpeg: {e}")

        self.finished_signal.emit()