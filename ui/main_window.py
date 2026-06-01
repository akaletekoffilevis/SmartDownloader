from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QSizePolicy,
    QApplication
)
from PySide6.QtCore import Qt, QTimer

from ui.theme import DARK_STYLE, LIGHT_STYLE
from ui.home import HomePage
from ui.download import DownloadPage
from ui.settings import SettingsPage
from ui.search import SearchPage
from ui.playlist import PlaylistPage
from ui.history import HistoryPage
import re

URL_REGEX = re.compile(
    r'https?://(?:www\.)?(?:youtube\.com|youtu\.be|tiktok\.com|'
    r'vimeo\.com|twitter\.com|x\.com|instagram\.com|'
    r'dailymotion\.com|facebook\.com)/\S+', re.IGNORECASE
)


class MainWindow(QMainWindow):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self.setWindowTitle("SmartDownloader")
        self.setMinimumSize(960, 640)
        self.resize(1100, 720)

        self._last_clipboard = ""
        self._setup_ui()
        self.apply_theme()
        self._start_clipboard_monitor()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = self._create_sidebar()
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.pages = {}
        for name, cls in [
            ("home", HomePage),
            ("download", DownloadPage),
            ("search", SearchPage),
            ("playlist", PlaylistPage),
            ("history", HistoryPage),
            ("settings", SettingsPage),
        ]:
            page = cls(self.manager, self.downloader)
            self.pages[name] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.pages["home"])

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(4)

        logo = QLabel("SmartDL")
        logo.setObjectName("title")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(24)

        self.nav_btns = {}
        nav_items = [
            ("home", "🏠 Accueil"),
            ("download", "⬇ Télécharger"),
            ("search", "🔍 Rechercher"),
            ("playlist", "📦 Playlist"),
            ("history", "📋 Historique"),
            ("settings", "⚙ Paramètres"),
        ]
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            self.nav_btns[key] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        self.clip_indicator = QLabel("📋 Surveillance inactive")
        self.clip_indicator.setObjectName("clip_indicator_idle")
        self.clip_indicator.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.clip_indicator)

        version = QLabel("v1.0")
        version.setObjectName("subtitle")
        version.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version)

        return sidebar

    def _start_clipboard_monitor(self):
        self._clipboard = QApplication.clipboard()
        self._clip_timer = QTimer()
        self._clip_timer.timeout.connect(self._check_clipboard)
        self._clip_timer.start(1500)

    def _check_clipboard(self):
        try:
            text = self._clipboard.text()
            if text and text != self._last_clipboard:
                self._last_clipboard = text
                match = URL_REGEX.search(text)
                if match:
                    url = match.group(0)
                    self.clip_indicator.setText("🔗 Lien détecté !")
                    self.clip_indicator.setObjectName("clip_indicator_detected")
                    self._refresh_style(self.clip_indicator)
                    self._on_url_detected(url)
                else:
                    self.clip_indicator.setText("📋 Surveillance active")
                    self.clip_indicator.setObjectName("clip_indicator_idle")
                    self._refresh_style(self.clip_indicator)
        except Exception:
            pass

    def _on_url_detected(self, url):
        dl_page = self.pages["download"]
        dl_page.url_input.setText(url)
        dl_page._detect()
        if self.manager.config.get("auto_download", False):
            QTimer.singleShot(600, lambda: dl_page._start_download("best-speed"))

    def _navigate(self, page_key):
        for key, btn in self.nav_btns.items():
            btn.setChecked(key == page_key)
        if page_key in self.pages:
            page = self.pages[page_key]
            self.stack.setCurrentWidget(page)
            if hasattr(page, "on_show"):
                page.on_show()

    def _refresh_style(self, widget):
        style = widget.style()
        if style:
            style.unpolish(widget)
            style.polish(widget)

    def apply_theme(self):
        theme = self.manager.config.get("theme", "dark")
        style = DARK_STYLE if theme == "dark" else LIGHT_STYLE
        self.setStyleSheet(style)
