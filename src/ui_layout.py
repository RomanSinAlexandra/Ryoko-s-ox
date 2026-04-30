from PyQt6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QLineEdit, 
                             QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtMultimediaWidgets import QVideoWidget

from src.widgets import ClickableLineEdit

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

        type_layout = QHBoxLayout()
        type_left = QVBoxLayout()
        type_left.addWidget(QLabel("Type file"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["MP4", "MP3", "WAV", "OGG", "FLAC", "WEBM"])
        self.type_combo.setFixedWidth(100)
        type_left.addWidget(self.type_combo)
        
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
        
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        self.media_player.setVideoOutput(self.video_widget)
        
        controls_layout = QHBoxLayout()
        self.btn_back = QPushButton(QIcon("resource/ico/back.svg"), "")
        self.btn_play = QPushButton(QIcon("resource/ico/play.svg"), "")
        self.btn_forward = QPushButton(QIcon("resource/ico/forward.svg"), "")

        icon_size = QSize(24, 24)
        self.btn_back.setIconSize(icon_size)
        self.btn_play.setIconSize(icon_size)
        self.btn_forward.setIconSize(icon_size)
        
        self.lbl_time = QLabel("00:00 / 00:00")
        
        controls_layout.addWidget(self.lbl_time)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_back)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_forward)
        controls_layout.addStretch()

        preview_layout.addWidget(self.video_widget, stretch=1)
        preview_layout.addLayout(controls_layout)

        status_frame = QFrame()
        status_frame.setProperty("class", "panel")
        status_layout = QVBoxLayout(status_frame)

        self.lbl_web_status = QLabel("🟢 Web status: Online")
        self.lbl_dl_status = QLabel("⚪ Download status: Idle")

        self.anim_label = QLabel()
        self.anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("resource/image/loading.gif") 
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