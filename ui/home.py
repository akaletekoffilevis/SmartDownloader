from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer


class HomePage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("SmartDownloader")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Téléchargez vos vidéos en un clic")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        cards = [
            ("⬇ Coller un lien\nDétection automatique", self._go_download),
            ("🔍 Rechercher\nTrouver des vidéos", self._go_search),
            ("📦 Playlist\nTélécharger en masse", self._go_playlist),
            ("📋 Historique\nVos téléchargements", self._go_history),
        ]
        for text, callback in cards:
            card = QPushButton(text)
            card.setObjectName("big")
            card.setMinimumHeight(110)
            card.setCursor(Qt.PointingHandCursor)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.clicked.connect(callback)
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        layout.addSpacing(24)

        active_label = QLabel("Téléchargements en cours")
        active_label.setObjectName("subtitle")
        layout.addWidget(active_label)

        self.active_frame = QFrame()
        self.active_frame.setObjectName("active_frame")
        self.af_layout = QVBoxLayout(self.active_frame)
        self.af_layout.setAlignment(Qt.AlignTop)
        self.no_active_label = QLabel("Aucun téléchargement actif")
        self.no_active_label.setAlignment(Qt.AlignCenter)
        self.no_active_label.setObjectName("subtitle")
        self.af_layout.addWidget(self.no_active_label)
        layout.addWidget(self.active_frame, 1)

    def _go_download(self):
        parent = self.window()
        if hasattr(parent, "_navigate"):
            parent._navigate("download")

    def _go_search(self):
        parent = self.window()
        if hasattr(parent, "_navigate"):
            parent._navigate("search")

    def _go_history(self):
        parent = self.window()
        if hasattr(parent, "_navigate"):
            parent._navigate("history")

    def _go_playlist(self):
        parent = self.window()
        if hasattr(parent, "_navigate"):
            parent._navigate("playlist")

    def _refresh_active(self):
        for i in reversed(range(self.af_layout.count())):
            item = self.af_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        active = list(self.manager.active_downloads)
        if active:
            self.no_active_label = QLabel(f"📥 {len(active)} téléchargement(s) en cours")
            self.no_active_label.setAlignment(Qt.AlignCenter)
            self.no_active_label.setObjectName("subtitle")
            self.af_layout.addWidget(self.no_active_label)
            for url in active[:5]:
                lbl = QLabel(f"  ⬇ {url[:60]}")
                lbl.setObjectName("subtitle")
                self.af_layout.addWidget(lbl)
        else:
            self.no_active_label = QLabel("Aucun téléchargement actif")
            self.no_active_label.setAlignment(Qt.AlignCenter)
            self.no_active_label.setObjectName("subtitle")
            self.af_layout.addWidget(self.no_active_label)
        self.af_layout.addStretch()

    def on_show(self):
        self._refresh_active()
