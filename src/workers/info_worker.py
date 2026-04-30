import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal

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
            'javascript_runtime': './resources/yt_dlp/quickjs.exe' 
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                video_url = info.get('url') 
                if not video_url:
                    formats = info.get('formats', [])
                    best_stream = next((f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), None)
                    video_url = best_stream['url'] if best_stream else None

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