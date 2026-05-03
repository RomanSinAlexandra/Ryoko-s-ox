import os
import sys
import yt_dlp
import re
from PyQt6.QtCore import QThread, pyqtSignal

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DownloadWorker(QThread):
    progress_signal = pyqtSignal(str)
    console_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, url, download_path, fmt, quality):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.fmt = fmt
        self.quality = quality

    def run(self):

        height = self.quality.replace("p", "")

        ydl_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'ffmpeg_location': resource_path('src/yt_dlp'),
            'js_runtime': 'quickjs:' + resource_path('src/yt_dlp/quickjs.exe'),
        }

        audio_formats = ['MP3', 'WAV', 'OGG', 'FLAC']
        
        if self.fmt in audio_formats:

            ydl_opts['format'] = 'bestaudio/best'
            postprocessor = {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.fmt.lower(),
            }
            if self.fmt == 'MP3':
                postprocessor['preferredquality'] = '192'
            ydl_opts['postprocessors'] = [postprocessor]
            
        else:

            if self.quality == "Worst":
                format_str = f"worstvideo[ext={self.fmt.lower()}]+worstaudio/worst"
            else:

                format_str = f"bestvideo[height<={height}][ext={self.fmt.lower()}]+bestaudio/best[height<={height}]"
            
            ydl_opts['format'] = format_str

        try:
            self.console_signal.emit(f"Starting download: {self.url} as {self.fmt} ({self.quality})")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                title = info_dict.get('title', 'File')
                self.console_signal.emit(f"Successfully downloaded: {title}")
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