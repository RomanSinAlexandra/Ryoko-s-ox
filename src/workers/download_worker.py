import yt_dlp
import re
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    progress_signal = pyqtSignal(str)
    console_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, url, download_path, format_type):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.format_type = format_type

    def run(self):
        ydl_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': './src/yt_dlp',
            'js_runtime': 'quickjs:./src/yt_dlp/quickjs.exe',
        }

        if self.format_type in ['MP3', 'WAV', 'OGG', 'FLAC']:
            # Настройки для аудио
            ydl_opts['format'] = 'bestaudio/best'
            
            postprocessor = {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.format_type.lower(),
            }
            
            if self.format_type == 'MP3':
                postprocessor['preferredquality'] = '192'
                
            ydl_opts['postprocessors'] = [postprocessor]
            
        elif self.format_type == 'WEBM':
            ydl_opts['format'] = 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]'
            
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        try:
            self.console_signal.emit(f"Starting download: {self.url} as {self.format_type}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                self.console_signal.emit(f"Successfully downloaded: {info_dict.get('title', 'File')}")
        except Exception as e:
            self.console_signal.emit(f"Error: {str(e)}")
        
        self.finished_signal.emit()

    def my_hook(self, d):
        if d['status'] == 'downloading':
            raw_perc = d.get('_percent_str', '0%')
            raw_speed = d.get('_speed_str', '0 B/s')

            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

            clean_perc = ansi_escape.sub('', raw_perc).strip()
            clean_speed = ansi_escape.sub('', raw_speed).strip()

            self.progress_signal.emit(clean_perc)
            self.speed_signal.emit(clean_speed)
            
        elif d['status'] == 'finished':
            self.progress_signal.emit("100%")
            self.speed_signal.emit("0 B/s")