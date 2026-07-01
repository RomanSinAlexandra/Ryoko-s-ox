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
        height_val = self.quality.lower().replace("p", "").strip()
        bin_dir = resource_path(os.path.join('src', 'yt_dlp'))

        ydl_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'ffmpeg_location': bin_dir, 
            'js_runtimes': {
                'deno': {
                    'path': os.path.join(bin_dir, 'deno.exe')
                }
            },
            'remote_components': ['ejs:github'], 
            'cookiefile': os.path.join(bin_dir, 'cookies.txt'),
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        audio_formats = ['MP3', 'WAV', 'OGG', 'FLAC']
        
        # СЦЕНАРІЙ 1: Звичайне Аудіо
        if self.fmt in audio_formats:
            ydl_opts['format'] = 'bestaudio/best'
            postprocessor = {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.fmt.lower(),
            }
            if self.fmt == 'MP3':
                postprocessor['preferredquality'] = '192'
            ydl_opts['postprocessors'] = [postprocessor]
            
        # СЦЕНАРІЙ 2: TikTok
        elif "tiktok" in self.url.lower():
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = self.fmt.lower()
            ydl_opts['postprocessors'] = []

        # СЦЕНАРІЙ 3: Універсальна логіка для відео (YouTube та інші)
        else:
            if height_val == "worst":
                format_str = "worstvideo+worstaudio/worst"
            elif not height_val.isdigit():
                if self.fmt.lower() == 'mp4':
                    format_str = "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[ext=mp4]/best"
                else:
                    format_str = "bestvideo+bestaudio/best"
            else:
                if self.fmt.lower() == 'mp4':
                    format_str = (
                        f"bestvideo[height<={height_val}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
                        f"bestvideo[height<={height_val}][ext=mp4]+bestaudio[ext=m4a]/"
                        f"bestvideo[height<={height_val}]+bestaudio/"
                        f"best"
                    )
                else:
                    format_str = (
                        f"bestvideo[height<={height_val}]+bestaudio/"
                        f"bestvideo+bestaudio/"
                        f"best"
                    )
            
            ydl_opts['format'] = format_str
            ydl_opts['merge_output_format'] = self.fmt.lower()
            
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': self.fmt.lower(),
            }]
            ydl_opts['postprocessor_args'] = ['-c:a', 'aac', '-b:a', '128k']

        # Блок безпосереднього завантаження
        try:
            self.console_signal.emit(f"Starting download: {self.url} as {self.fmt} ({self.quality})")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                title = info_dict.get('title', 'File')
                self.console_signal.emit(f"✅ Successfully downloaded: {title}")
        except Exception as e:
            self.console_signal.emit(f"❌ Error: {str(e)}")
        
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