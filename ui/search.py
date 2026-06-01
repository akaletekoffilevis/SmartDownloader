from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap
import requests


class ThumbnailLoader(QThread):
    thumbnail_ready = Signal(int, object)

    def __init__(self, thumb_url, index):
        super().__init__()
        self.thumb_url = thumb_url
        self.index = index

    def run(self):
        try:
            resp = requests.get(self.thumb_url, timeout=5)
            pixmap = QPixmap()
            pixmap.loadFromData(resp.content)
            if not pixmap.isNull():
                self.thumbnail_ready.emit(self.index, pixmap)
        except Exception:
            pass


class SearchPage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._results = []
        self._thumbnails = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Recherche vidéo")
        title.setObjectName("title")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une vidéo...")
        self.search_input.returnPressed.connect(self._search)
        search_layout.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("🔍 Rechercher")
        self.search_btn.setFixedWidth(150)
        self.search_btn.clicked.connect(self._search)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        self.results_label = QLabel("")
        self.results_label.setObjectName("subtitle")
        layout.addWidget(self.results_label)

        placeholder_frame = QFrame()
        pf_layout = QVBoxLayout(placeholder_frame)
        pf_layout.setAlignment(Qt.AlignCenter)
        placeholder_text = QLabel("Entrez un mot-clé puis appuyez sur Entrée\nou cliquez sur Rechercher")
        placeholder_text.setObjectName("subtitle")
        placeholder_text.setAlignment(Qt.AlignCenter)
        pf_layout.addWidget(placeholder_text)
        layout.addWidget(placeholder_frame, 1)

        self.list = QListWidget()
        self.list.setSpacing(4)
        self.list.setVisible(False)
        self.list.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list, 1)

    def _search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.list.clear()
        self.list.setVisible(False)
        self.results_label.setText("Recherche en cours...")

        QTimer.singleShot(100, lambda: self._do_search(query))

    def _do_search(self, query):
        results = self.downloader.search(query)
        if isinstance(results, dict) and "error" in results:
            self.results_label.setText(f"Erreur : {results['error']}")
            return

        self._results = results
        self._thumbnails = {}
        self.results_label.setText(f"{len(results)} résultat(s) trouvé(s)")
        self.list.setVisible(True)

        self._thumb_loaders = []
        for i, r in enumerate(results):
            if not isinstance(r, dict):
                continue
            title = r.get("title", "Inconnu") or "Inconnu"
            duration = r.get("duration", 0) or 0
            uploader = r.get("uploader", "") or ""
            mins, secs = divmod(int(duration), 60)
            dur = f"{mins}:{secs:02d}" if duration else "Live"

            item = QListWidgetItem()
            widget = QWidget()
            wlayout = QHBoxLayout(widget)
            wlayout.setContentsMargins(8, 4, 8, 4)

            thumb_label = QLabel()
            thumb_label.setFixedSize(120, 68)
            thumb_label.setAlignment(Qt.AlignCenter)
            thumb_label.setText("📹")
            thumb_url = r.get("thumbnail", "") or ""
            if thumb_url:
                loader = ThumbnailLoader(thumb_url, i)
                loader.thumbnail_ready.connect(
                    lambda idx, pix, lbl=thumb_label: self._set_thumbnail(lbl, pix)
                )
                self._thumb_loaders.append(loader)
                loader.start()
            wlayout.addWidget(thumb_label)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            title_label = QLabel(title[:80])
            info_layout.addWidget(title_label)

            meta_label = QLabel(f"⏱ {dur}  |  {uploader}")
            info_layout.addWidget(meta_label)
            wlayout.addLayout(info_layout, 1)

            dl_btn = QPushButton("⬇")
            dl_btn.setFixedSize(40, 40)
            item_url = r.get("url", "") or ""
            dl_btn.clicked.connect(lambda checked, u=item_url: self._quick_download(u))
            wlayout.addWidget(dl_btn)

            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

    def _on_item_clicked(self, item):
        row = self.list.row(item)
        if row < len(self._results):
            url = self._results[row].get("url", "")
            self._quick_download(url)

    def _quick_download(self, url):
        if not url:
            return
        parent = self.window()
        if hasattr(parent, "_navigate"):
            if hasattr(parent, "pages") and "download" in parent.pages:
                dl_page = parent.pages["download"]
                dl_page.url_input.setText(url)
                dl_page._detect()
            parent._navigate("download")

    def _set_thumbnail(self, label, pixmap):
        try:
            scaled = pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled)
            label.setText("")
        except Exception:
            pass

    def on_show(self):
        self.search_input.setFocus()
