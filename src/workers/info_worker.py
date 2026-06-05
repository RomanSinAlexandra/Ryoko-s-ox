import yt_dlp
import os
import sys
from PyQt6.QtCore import QThread, pyqtSignal

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class InfoWorker(QThread):
    info_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,

            'js_runtimes': {
                'deno': {
                    'path': resource_path(os.path.join('src', 'yt_dlp', 'deno.exe'))
                }
            },
            'remote_components': 'ejs:github',
            'cookiefile': resource_path(os.path.join('src', 'yt_dlp', 'cookies.txt')),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                formats = info.get('formats', [])
                best_stream = next((f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), None)
                video_url = best_stream['url'] if best_stream else info.get('url')

                data = {
                    'title': info.get('title', 'No title'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', 'No description'),
                    'duration': info.get('duration'),
                    'stream_url': video_url
                }
                self.info_signal.emit(data)
        except Exception as e:
            self.error_signal.emit(str(e))