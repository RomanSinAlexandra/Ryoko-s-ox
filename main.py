import os
import platform
import subprocess
import webbrowser
import json
import sys

from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from src.ui_layout import Ui_MainWindow 
from src.styles import get_main_stylesheet
from src.workers.download_worker import DownloadWorker
from src.workers.info_worker import InfoWorker

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ryoko Downloader")
        self.setWindowIcon(QIcon("resource/image/favicon.ico"))
        self.resize(1100, 700)

        self.load_settings() 

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        self.setup_ui()
        
        self.connect_signals()

        self.setStyleSheet(get_main_stylesheet())

    def connect_signals(self):
        self.url_input.textChanged.connect(self.on_url_changed)
        self.btn_open_url.clicked.connect(self.open_link_in_browser)
        
        self.path_input.clicked.connect(self.browse_folder)
        self.btn_open_folder.clicked.connect(self.open_download_folder)
        
        self.btn_download.clicked.connect(self.start_download)
        
        self.btn_back.clicked.connect(lambda: self.seek_relative(-5000))
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_forward.clicked.connect(lambda: self.seek_relative(5000))
        
        self.media_player.positionChanged.connect(self.update_time_label)
        self.media_player.durationChanged.connect(self.update_time_label)
        
        self.movie.finished.connect(self.movie.start)

    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play.setIcon(QIcon("resource/ico/play.svg"))
        else:
            self.media_player.play()
            self.btn_play.setIcon(QIcon("resource/ico/pause.svg"))

    def seek_relative(self, ms):
        new_pos = self.media_player.position() + ms
        self.media_player.setPosition(max(0, new_pos))

    def update_time_label(self):
        pos = self.media_player.position()
        dur = self.media_player.duration()
        
        def format_ms(ms):
            s = (ms // 1000) % 60
            m = (ms // (1000 * 60)) % 60
            return f"{m:02d}:{s:02d}"
        
        self.lbl_time.setText(f"{format_ms(pos)} / {format_ms(dur)}")

    def on_url_changed(self):
        url = self.url_input.text()
        if url.startswith("http") and len(url) > 15:
            if hasattr(self, 'info_thread') and self.info_thread.isRunning():
                self.info_thread.terminate()
            
            self.info_thread = InfoWorker(url)
            self.info_thread.info_signal.connect(self.setup_preview)
            self.info_thread.start()

    def setup_preview(self, data):
        self.desc_output.setText(f"{data['title']}\n\n{data['description']}")
        
        if data['stream_url']:
            self.media_player.setSource(QUrl(data['stream_url']))
            self.media_player.pause() 
            self.btn_play.setIcon(QIcon("resource/ico/play.svg"))
            self.log_console("Video stream loaded.")
        else:
            self.log_console("Could not resolve video stream URL.")

    def browse_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if directory:
            self.path_input.setText(directory)
            self.settings["download_path"] = directory
            self.save_settings()
            self.log_console(f"Download path changed and saved: {directory}")

    def load_settings(self):
        self.settings_file = "settings.json"
        self.settings = {
            "download_path": os.path.expanduser("~\\Downloads") 
        }
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as file:
                    loaded_data = json.load(file)
                    self.settings.update(loaded_data)
            except Exception as e:
                self.log_console(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as file:
                json.dump(self.settings, file, indent=4, ensure_ascii=False)
        except Exception as e:
            self.log_console(f"Error saving settings: {e}")

    def start_download(self):
        url = self.url_input.text()
        path = self.path_input.text()
        fmt = self.type_combo.currentText()

        self.movie.start()

        if not url or not path:
            self.log_console("Please specify a URL and download directory.")
            return

        self.btn_download.setEnabled(False)
        self.lbl_dl_status.setText("🔴 Download status: Downloading")
        self.log_console("Initializing yt-dlp...")

        self.worker = DownloadWorker(url, path, fmt)
        self.worker.console_signal.connect(self.log_console)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.speed_signal.connect(self.update_speed)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.start()

    def log_console(self, text):
        self.console_output.append(text)

    def open_link_in_browser(self):
        url = self.url_input.text()
        if url.startswith("http"):
            webbrowser.open(url)
        else:
            self.log_console("Error: Please enter a valid URL to open in the browser.")

    def open_download_folder(self):
        path = self.path_input.text()
        
        if not path or not os.path.exists(path):
            self.log_console("Error: The specified path does not exist or is not selected.")
            return

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def update_progress(self, perc):
        self.lbl_perc_val.setText(perc)

    def update_speed(self, speed):
        self.lbl_speed_val.setText(speed)

    def download_finished(self):
        self.btn_download.setEnabled(True)
        self.lbl_dl_status.setText("⚪ Download status: Idle")
        self.lbl_perc_val.setText("0%")
        self.lbl_speed_val.setText("0 B/s")
        self.log_console("--- Process completed ---")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())