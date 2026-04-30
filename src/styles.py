def get_main_stylesheet():
    return """
        QMainWindow {
            background-color: #1a1818;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        QFrame[class="panel"] {
            background-color: #312d2a;
            border-radius: 5px;
        }
        QLineEdit, QTextEdit {
            background-color: #242220;
            border: 1px solid #4a4542;
            border-radius: 4px;
            color: #ffffff;
            padding: 5px;
            font-size: 13px;
        }
        QComboBox {
            background-color: #242220;
            color: #ffffff;
            border: 1px solid #4a4542;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton {
            background-color: #2a4c8c;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #3b66b5;
        }
        QPushButton[class="btn-primary"] {
            background-color: #1a5ac9;
            padding: 10px 30px;
            font-size: 14px;
        }
        QPushButton[class="btn-primary"]:hover {
            background-color: #2a6ce0;
        }
        QLabel[class="status-val"] {
            background-color: #242220;
            padding: 5px;
            border-radius: 4px;
            min-width: 80px;
        }
        """