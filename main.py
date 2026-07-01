import os
import platform
import subprocess
import webbrowser
import json
import sys
import urllib.request

from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from src.ui_layout import Ui_MainWindow 
from src.styles.styles import get_main_stylesheet
from src.workers.download_worker import DownloadWorker
from src.workers.info_worker import InfoWorker

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ryoko`s Box")
        self.setWindowIcon(QIcon(resource_path("resource/image/favicon.ico")))
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

        self.media_player.positionChanged.connect(self.update_timeline_position)
        self.media_player.durationChanged.connect(self.update_timeline_duration)
        
        self.timeline_slider.sliderMoved.connect(self.set_video_position)
        self.player_volume_slider.valueChanged.connect(self.update_volume)
        self.movie.finished.connect(self.movie.start)
        
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.btn_mute.clicked.connect(self.toggle_mute)

        self.type_combo.currentTextChanged.connect(self.on_format_type_changed)
        self.btn_download_preview.clicked.connect(self.save_thumbnail)

    def on_format_type_changed(self, text):
        audio_formats = ["mp3", "m4a", "wav", "flac", "audio", "звук"] 
        
        if text.lower() in audio_formats:
            self.quality_combo.hide()
            self.quality_label.hide() 
        else:
            self.quality_combo.show()
            self.quality_label.show()

    def update_volume(self, value):
        self.audio_output.setVolume(value / 100)
        
        if self.audio_output.isMuted() and value > 0:
            self.audio_output.setMuted(False)
            self.btn_mute.setIcon(QIcon(resource_path("resource/ico/volume.svg")))

    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play.setIcon(QIcon(resource_path("resource/ico/play.svg")))
        else:

            self.preview_stack.setCurrentWidget(self.video_widget)
            self.media_player.play()
            self.btn_play.setIcon(QIcon(resource_path("resource/ico/pause.svg")))

    def on_media_status_changed(self, status):

        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.preview_stack.setCurrentWidget(self.thumbnail_label)

            self.btn_play.setIcon(QIcon(resource_path("resource/ico/replay.svg")))

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

        # Отображение превью-картинки
        if data.get('thumbnail'):
            try:
                req = urllib.request.Request(data['thumbnail'], headers={'User-Agent': 'Mozilla/5.0'})
                image_data = urllib.request.urlopen(req).read()
                self.current_thumbnail_data = image_data

                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap.fromImage(image)

                scaled_pixmap = pixmap.scaled(
                    640, 480,
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
            except Exception as e:
                self.log_console(f"Error loading thumbnail: {e}")

        self.preview_stack.setCurrentWidget(self.thumbnail_label)
        
        video_url = data.get('stream_url')
        if video_url:
            # Обязательно останавливаем плеер перед сменой источника
            self.media_player.stop()

            # Проверяем, локальный ли это файл (для TikTok) или сетевой (для YouTube)
            if os.path.exists(video_url):
                self.media_player.setSource(QUrl.fromLocalFile(video_url))
                self.log_console(f"Local preview file loaded (TikTok).")
            else:
                self.media_player.setSource(QUrl(video_url))
                self.log_console("Network video stream loaded (YouTube).")

            # Фикс длительности: если yt-dlp вернул секунды, переводим в мс для слайдера
            if data.get('duration'):
                try:
                    duration_ms = int(float(data['duration']) * 1000)
                    self.update_timeline_duration(duration_ms)
                except (ValueError, TypeError):
                    pass

            self.btn_play.setIcon(QIcon(resource_path("resource/ico/play.svg")))
        else:
            self.log_console("Could not resolve video stream URL.")

    def save_thumbnail(self):

        if not hasattr(self, 'current_thumbnail_data') or not self.current_thumbnail_data:
            self.log_console("Error: No thumbnail loaded. Please load a valid URL first.")
            return

        default_path = os.path.join(self.path_input.text(), "preview.jpg")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Thumbnail", default_path, "JPEG Images (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:

                with open(file_path, "wb") as f:
                    f.write(self.current_thumbnail_data)
                self.log_console(f"Thumbnail saved successfully to: {file_path}")
            except Exception as e:
                self.log_console(f"Error saving thumbnail: {e}")

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
        quality = self.quality_combo.currentText()

        self.movie.start()

        if not url or not path:
            self.log_console("Please specify a URL and download directory.")
            return

        self.btn_download.setEnabled(False)
        self.lbl_dl_status.setText("🔴 Download status: Downloading")
        self.log_console("Initializing yt-dlp...")

        self.worker = DownloadWorker(url, path, fmt, quality)
        self.worker.console_signal.connect(self.log_console)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.speed_signal.connect(self.update_speed)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.start()

    def log_console(self, text):
        self.console_output.append(text)

    def update_timeline_duration(self, duration):

        self.timeline_slider.setRange(0, duration)
        self.update_time_label() # Обновляем текст

    def update_timeline_position(self, position):

        if not self.timeline_slider.isSliderDown():
            self.timeline_slider.setValue(position)
        self.update_time_label()

    def set_video_position(self, position):

        self.media_player.setPosition(position)

    def update_time_label(self):

        pos = self.media_player.position()
        dur = self.media_player.duration()
        
        def format_ms(ms):
            s = (ms // 1000) % 60
            m = (ms // (1000 * 60)) % 60
            h = (ms // (1000 * 60 * 60))
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"
        
        self.lbl_time.setText(f"{format_ms(pos)} / {format_ms(dur)}")

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

    def toggle_mute(self):

        is_muted = self.audio_output.isMuted()
        new_mute_state = not is_muted

        self.audio_output.setMuted(new_mute_state)
        
        if new_mute_state:

            self.btn_mute.setIcon(QIcon(resource_path("resource/ico/mute.svg")))
        else:

            self.btn_mute.setIcon(QIcon(resource_path("resource/ico/volume.svg")))
            current_vol = self.player_volume_slider.value()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
