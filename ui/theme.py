DARK_STYLE = """
QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QMainWindow, QDialog {
    background-color: #121212;
}

QLabel {
    color: #e0e0e0;
    border: none;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#subtitle {
    font-size: 14px;
    color: #9e9e9e;
}

QLabel#video_title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#video_meta {
    font-size: 13px;
    color: #999999;
}

QLabel#error_label {
    font-size: 14px;
    color: #ef5350;
}

QLabel#status_success {
    color: #4caf50;
}

QLabel#status_error {
    color: #ef5350;
}

QLabel#status_warning {
    color: #ff9800;
}

QLabel#clip_indicator_idle {
    font-size: 10px;
    color: #555555;
    padding: 4px;
}

QLabel#clip_indicator_detected {
    font-size: 10px;
    color: #4caf50;
    padding: 4px;
}

QLabel#help_text {
    color: #888888;
    font-size: 11px;
}

QLabel#history_title {
    font-weight: bold;
}

QFrame#active_frame {
    background-color: #1a1a1a;
    border-radius: 12px;
    border: 1px solid #2a2a2a;
    padding: 8px;
}

QFrame#info_frame {
    background-color: #1a1a1a;
    border-radius: 12px;
    border: 1px solid #2a2a2a;
    padding: 8px;
}

QScrollArea#queue_area {
    background-color: #1a1a1a;
    border-radius: 10px;
    border: 1px solid #2a2a2a;
}

QPushButton#oneclick {
    background-color: #e65100;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#oneclick:hover {
    background-color: #ff6f00;
}

QPushButton {
    background-color: #1e88e5;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2196f3;
}

QPushButton:pressed {
    background-color: #1565c0;
}

QPushButton#nav_btn {
    background-color: transparent;
    color: #b0b0b0;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: normal;
}

QPushButton#nav_btn:hover {
    background-color: #1e1e1e;
    color: #ffffff;
}

QPushButton#nav_btn:checked {
    background-color: #1e88e5;
    color: #ffffff;
}

QPushButton#danger {
    background-color: #c62828;
}

QPushButton#danger:hover {
    background-color: #e53935;
}

QPushButton#success {
    background-color: #2e7d32;
}

QPushButton#success:hover {
    background-color: #388e3c;
}

QPushButton#big {
    background-color: #1e88e5;
    color: white;
    border-radius: 16px;
    padding: 24px 32px;
    font-size: 18px;
    min-height: 60px;
}

QPushButton#big:hover {
    background-color: #2196f3;
}

QLineEdit {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 2px solid #333333;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 15px;
}

QLineEdit:focus {
    border-color: #1e88e5;
}

QComboBox {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 2px solid #333333;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 14px;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: #e0e0e0;
    selection-background-color: #1e88e5;
    border-radius: 6px;
}

QProgressBar {
    background-color: #1e1e1e;
    border: none;
    border-radius: 8px;
    height: 14px;
    text-align: center;
    font-size: 11px;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #1e88e5;
    border-radius: 8px;
}

QScrollBar:vertical {
    background-color: #121212;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #333333;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QListWidget {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 4px;
}

QListWidget::item {
    background-color: transparent;
    border-radius: 8px;
    padding: 10px;
    margin: 2px 0px;
}

QListWidget::item:hover {
    background-color: #252525;
}

QListWidget::item:selected {
    background-color: #1e88e5;
}

QCheckBox {
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #555555;
    background-color: #1e1e1e;
}

QCheckBox::indicator:checked {
    background-color: #1e88e5;
    border-color: #1e88e5;
}

QGroupBox {
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 16px;
    font-size: 14px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
"""

LIGHT_STYLE = """
QWidget {
    background-color: #f5f5f5;
    color: #212121;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QMainWindow, QDialog {
    background-color: #f5f5f5;
}

QLabel {
    color: #212121;
    border: none;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #121212;
}

QLabel#subtitle {
    font-size: 14px;
    color: #757575;
}

QLabel#video_title {
    font-size: 16px;
    font-weight: bold;
    color: #121212;
}

QLabel#video_meta {
    font-size: 13px;
    color: #757575;
}

QPushButton {
    background-color: #1e88e5;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2196f3;
}

QPushButton:pressed {
    background-color: #1565c0;
}

QPushButton#nav_btn {
    background-color: transparent;
    color: #616161;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}

QPushButton#nav_btn:hover {
    background-color: #e0e0e0;
    color: #212121;
}

QPushButton#nav_btn:checked {
    background-color: #1e88e5;
    color: white;
}

QPushButton#danger {
    background-color: #c62828;
}

QPushButton#danger:hover {
    background-color: #e53935;
}

QPushButton#success {
    background-color: #2e7d32;
}

QPushButton#success:hover {
    background-color: #388e3c;
}

QPushButton#big {
    background-color: #1e88e5;
    color: white;
    border-radius: 16px;
    padding: 24px 32px;
    font-size: 18px;
    min-height: 60px;
}

QPushButton#big:hover {
    background-color: #2196f3;
}

QLineEdit {
    background-color: white;
    color: #212121;
    border: 2px solid #bdbdbd;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 15px;
}

QLineEdit:focus {
    border-color: #1e88e5;
}

QComboBox {
    background-color: white;
    color: #212121;
    border: 2px solid #bdbdbd;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 14px;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: white;
    color: #212121;
    selection-background-color: #1e88e5;
    selection-color: white;
    border-radius: 6px;
}

QProgressBar {
    background-color: #e0e0e0;
    border: none;
    border-radius: 8px;
    height: 14px;
    text-align: center;
    font-size: 11px;
    color: #212121;
}

QProgressBar::chunk {
    background-color: #1e88e5;
    border-radius: 8px;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #bdbdbd;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QListWidget {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 4px;
}

QListWidget::item {
    background-color: transparent;
    border-radius: 8px;
    padding: 10px;
    margin: 2px 0px;
}

QListWidget::item:hover {
    background-color: #eeeeee;
}

QListWidget::item:selected {
    background-color: #1e88e5;
    color: white;
}

QCheckBox {
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #9e9e9e;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #1e88e5;
    border-color: #1e88e5;
}

QGroupBox {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 16px;
    font-size: 14px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

QLabel#error_label {
    font-size: 14px;
    color: #c62828;
}

QLabel#status_success {
    color: #2e7d32;
}

QLabel#status_error {
    color: #c62828;
}

QLabel#status_warning {
    color: #e65100;
}

QLabel#help_text {
    color: #888888;
    font-size: 11px;
}

QLabel#history_title {
    font-weight: bold;
}

QFrame#active_frame {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    padding: 8px;
}

QLabel#clip_indicator_idle {
    font-size: 10px;
    color: #888888;
    padding: 4px;
}

QLabel#clip_indicator_detected {
    font-size: 10px;
    color: #2e7d32;
    padding: 4px;
}

QFrame#info_frame {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    padding: 8px;
}

QScrollArea#queue_area {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
}

QPushButton#oneclick {
    background-color: #e65100;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#oneclick:hover {
    background-color: #ff6f00;
}
"""
