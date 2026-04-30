from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import pyqtSignal

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()