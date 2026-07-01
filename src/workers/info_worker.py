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
    video_url = data['stream_url']  
    
    if not video_url:
        if hasattr(self, 'console_signal'):
            self.console_signal.emit("❌ Error: Stream URL is empty")
        return

    # Зупиняємо плеєр перед зміною джерела контенту
    self.media_player.stop()  # У вашому UI використовується self.media_player

    if os.path.exists(video_url):
        # Відтворення локального склеєного файлу TikTok
        self.media_player.setSource(QUrl.fromLocalFile(video_url))
        print(f"Playing local TikTok file: {video_url}")
    else:
        # Відтворення мережевого стріму YouTube
        self.media_player.setSource(QUrl(video_url))
        print(f"Streaming network video: {video_url}")

    # КРИТИЧНЕ ВИПРАВЛЕННЯ: Перемикаємо стек на відображення відеовіджета
    if hasattr(self, 'preview_stack'):
        self.preview_stack.setCurrentIndex(1)  # 1 — це self.video_widget

    # Запуск відтворення
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
        
        default_fmt = 'mp4' 
        timestamp = int(time.time())
        filename = f'tiktok_preview_{timestamp}'

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': bin_dir,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'http_headers': {
                'Referer': 'https://www.tiktok.com/'
            }
        }

        if "tiktok" in self.url.lower():
            ydl_opts['skip_download'] = False
            ydl_opts['format'] = 'best'  # Качаем ОДИН готовый файл, это решит проблему черного экрана!
            ydl_opts['outtmpl'] = os.path.join(temp_dir, f'{filename}.%(ext)s')
        else:
            ydl_opts['skip_download'] = True
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        try:
            video_url = None
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=not ydl_opts.get('skip_download', False))
            
            if "tiktok" in self.url.lower():
                ext = info.get('ext', default_fmt)
                local_path = os.path.join(temp_dir, f'{filename}.{ext}')
                
                attempts = 0
                while not os.path.exists(local_path) and attempts < 30:
                    time.sleep(0.1)
                    attempts += 1
                
                video_url = local_path
            else:
                formats = info.get('formats', [])
                best_stream = next((f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), None)
                video_url = best_stream['url'] if best_stream else info.get('url')

            data = {
                'title': info.get('title', 'No title'),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', 'No description'),
                'duration': info.get('duration'),  # Передаем исходную длительность
                'stream_url': video_url  
            }
            self.info_signal.emit(data)

        except Exception as e:
            self.error_signal.emit(str(e))