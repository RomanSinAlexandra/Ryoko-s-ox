import os
import sys
import tempfile
import yt_dlp
import time
from PyQt6.QtCore import QThread, pyqtSignal, QUrl

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def handle_info_received(self, data):
    video_url = data.get('stream_url')  
    
    if not video_url or not os.path.exists(video_url):
        if hasattr(self, 'console_signal'):
            self.console_signal.emit("❌ Ошибка: Файл предпросмотра не найден")
        return

    self.media_player.stop()

    # Привязываем вывод видео к виджету
    if hasattr(self, 'video_widget'):
        self.media_player.setVideoOutput(self.video_widget)

    # Передаем локальный файл
    self.media_player.setSource(QUrl.fromLocalFile(video_url))
    print(f"Воспроизведение локального файла превью: {video_url}")

    # Переключаем стек на видеовиджет
    if hasattr(self, 'preview_stack'):
        self.preview_stack.setCurrentIndex(1)

    self.media_player.play()

class InfoWorker(QThread):
    info_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        bin_dir = resource_path(os.path.join('src', 'yt_dlp'))
        temp_dir = tempfile.gettempdir()
        
        timestamp = int(time.time())
        filename = f'preview_{timestamp}'

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': bin_dir,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'outtmpl': os.path.join(temp_dir, f'{filename}.%(ext)s'),
            'skip_download': False, # Скачиваем файл локально и для TikTok, и для YouTube!
        }

        if "tiktok" in self.url.lower():
            ydl_opts['format'] = 'best'
            ydl_opts['http_headers'] = {'Referer': 'https://www.tiktok.com/'}
        else:
            # Для YouTube скачиваем БЫСТРОЕ легкое MP4-видео (360p), чтобы превью загружалось за секунду
            ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                # Получаем точный путь к локальному скачанному файлу превью
                local_video_path = ydl.prepare_filename(info)

            data = {
                'title': info.get('title', 'No title'),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', 'No description'),
                'duration': info.get('duration'),
                'stream_url': local_video_path  # Теперь всегда передаем локальный путь!
            }
            self.info_signal.emit(data)

        except Exception as e:
            self.error_signal.emit(str(e))