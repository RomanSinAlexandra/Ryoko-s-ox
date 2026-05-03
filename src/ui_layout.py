import os
import sys

from PyQt6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QLineEdit, 
                             QTextEdit, QFrame, QStackedWidget, QSlider)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtMultimediaWidgets import QVideoWidget

from src.widgets import ClickableLineEdit

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Ui_MainWindow:
    
    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(10, 10, 10, 10)

        input_frame = QFrame()
        input_frame.setProperty("class", "panel")
        input_layout = QVBoxLayout(input_frame)
        
        input_layout.addWidget(QLabel("URL links"))
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.btn_open_url = QPushButton("Open")
        url_layout.addWidget(self.btn_open_url)
        url_layout.addWidget(self.url_input)
        input_layout.addLayout(url_layout)

        input_layout.addWidget(QLabel("Download way"))
        path_layout = QHBoxLayout()
        self.path_input = ClickableLineEdit()
        self.path_input.setPlaceholderText("Click to select folder...")
        self.path_input.setText(self.settings["download_path"])
        self.btn_open_folder = QPushButton("Show") 
        path_layout.addWidget(self.btn_open_folder)
        path_layout.addWidget(self.path_input)
        input_layout.addLayout(path_layout)

        settings_row = QHBoxLayout()

        type_layout = QHBoxLayout()
        type_left = QVBoxLayout()
        type_left.addWidget(QLabel("Type file"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["MP4", "MP3", "WAV", "OGG", "FLAC", "WEBM"])
        self.type_combo.setFixedWidth(100)
        type_left.addWidget(self.type_combo)

        quality_left = QVBoxLayout()
        quality_left.addWidget(QLabel("Quality"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["1080p", "720p", "480p", "360p", "Worst"])
        self.quality_combo.setFixedWidth(100)
        quality_left.addWidget(self.quality_combo)

        settings_row.addLayout(type_left)
        settings_row.addLayout(quality_left)
        settings_row.addStretch()
        
        input_layout.addLayout(settings_row)
        
        self.btn_download = QPushButton("Download")
        self.btn_download.setProperty("class", "btn-primary")

        type_layout.addLayout(type_left)
        type_layout.addStretch()
        type_layout.addWidget(self.btn_download)
        input_layout.addLayout(type_layout)
        input_layout.addStretch()

        preview_frame = QFrame()
        preview_frame.setProperty("class", "panel")
        preview_layout = QVBoxLayout(preview_frame)

        self.preview_stack = QStackedWidget()

        self.thumbnail_label = QLabel("")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: black; color: white;")
        
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        self.media_player.setVideoOutput(self.video_widget)

        self.preview_stack.addWidget(self.thumbnail_label)
        self.preview_stack.addWidget(self.video_widget)
        
        controls_layout = QHBoxLayout()
        
        self.btn_back = QPushButton(QIcon(resource_path("resource/ico/back.svg")), "")
        self.btn_play = QPushButton(QIcon(resource_path("resource/ico/play.svg")), "")
        self.btn_forward = QPushButton(QIcon(resource_path("resource/ico/forward.svg")), "")

        icon_size = QSize(24, 24)
        self.btn_back.setIconSize(icon_size)
        self.btn_play.setIconSize(icon_size)
        self.btn_forward.setIconSize(icon_size)
        
        self.lbl_time = QLabel("00:00 / 00:00")
        
        volume_container = QHBoxLayout()
        volume_container.setSpacing(5)
        
        self.btn_mute = QPushButton(QIcon(resource_path("resource/ico/volume.svg")), "")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setFlat(True)
        
        self.player_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.player_volume_slider.setRange(0, 100)
        self.player_volume_slider.setValue(50)
        self.player_volume_slider.setFixedWidth(100)

        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, 0)

        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #333; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #1a73e8; width: 14px; margin: -3px 0; border-radius: 7px; }
        """)
        
        volume_container.addWidget(self.btn_mute)
        volume_container.addWidget(self.player_volume_slider)

        controls_layout.addWidget(self.lbl_time)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_back)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_forward)
        controls_layout.addStretch()
        controls_layout.addLayout(volume_container)

        preview_layout.addWidget(self.preview_stack, stretch=1)
        preview_layout.addWidget(self.timeline_slider)
        preview_layout.addLayout(controls_layout)  
        
        status_frame = QFrame()
        status_frame.setProperty("class", "panel")
        status_layout = QVBoxLayout(status_frame)

        self.lbl_web_status = QLabel("🟢 Web status: Online")
        self.lbl_dl_status = QLabel("⚪ Download status: Idle")

        self.anim_label = QLabel()
        self.anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie(resource_path("resource/image/loading.gif")) 
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.anim_label.setMovie(self.movie)
        self.anim_label.setFixedSize(150, 150) 
        self.movie.start()

        status_layout.addWidget(self.lbl_web_status)
        status_layout.addWidget(self.lbl_dl_status)
        status_layout.addWidget(self.anim_label, alignment=Qt.AlignmentFlag.AlignCenter)
        status_layout.addStretch()
        
        stats_layout = QHBoxLayout()
        
        perc_layout = QVBoxLayout()
        perc_layout.addWidget(QLabel("Download percentage"))
        self.lbl_perc_val = QLabel("0%")
        self.lbl_perc_val.setProperty("class", "status-val")
        perc_layout.addWidget(self.lbl_perc_val)

        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("Download speed"))
        self.lbl_speed_val = QLabel("0 B/s")
        self.lbl_speed_val.setProperty("class", "status-val")
        speed_layout.addWidget(self.lbl_speed_val)

        stats_layout.addLayout(perc_layout)
        stats_layout.addLayout(speed_layout)
        status_layout.addLayout(stats_layout)

        console_frame = QFrame()
        console_frame.setProperty("class", "panel")
        console_layout = QVBoxLayout(console_frame)
        console_layout.addWidget(QLabel("Console"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)

        desc_frame = QFrame()
        desc_frame.setProperty("class", "panel")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.addWidget(QLabel("Description"))
        self.desc_output = QTextEdit()
        self.desc_output.setReadOnly(True)
        desc_layout.addWidget(self.desc_output)

        grid.addWidget(input_frame, 0, 0, 1, 1)
        grid.addWidget(preview_frame, 0, 1, 1, 2)
        grid.addWidget(status_frame, 1, 0, 1, 1)
        grid.addWidget(console_frame, 1, 1, 1, 1)
        grid.addWidget(desc_frame, 1, 2, 1, 1)