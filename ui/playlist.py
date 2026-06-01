import os
import re
from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QCheckBox,
    QFrame, QScrollArea, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, QTimer


class PlaylistPage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._entries = []
        self._checkbox_map = {}
        self._connected = False
        self._error_count = 0
        self._max_errors = 5
        self._playlist_title = ""
        self._current_dl_url = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Playlist Manager")
        title.setObjectName("title")
        layout.addWidget(title)

        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Collez un lien de playlist YouTube...")
        self.url_input.returnPressed.connect(self._detect)
        url_layout.addWidget(self.url_input, 1)

        self.detect_btn = QPushButton("🔍 Détecter la playlist")
        self.detect_btn.clicked.connect(self._detect)
        url_layout.addWidget(self.detect_btn)
        layout.addLayout(url_layout)

        self.info_label = QLabel("")
        self.info_label.setObjectName("subtitle")
        layout.addWidget(self.info_label)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)

        self.select_all_btn = QPushButton("✓ Tout sélectionner")
        self.select_all_btn.clicked.connect(self._toggle_select_all)
        ctrl_layout.addWidget(self.select_all_btn)

        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setObjectName("subtitle")
        progress_layout.addWidget(self.progress_label)
        ctrl_layout.addLayout(progress_layout, 1)

        self.dl_btn = QPushButton("⬇ Télécharger la playlist")
        self.dl_btn.setObjectName("success")
        self.dl_btn.setFixedWidth(250)
        self.dl_btn.setMinimumHeight(44)
        self.dl_btn.clicked.connect(self._download_selected)
        ctrl_layout.addWidget(self.dl_btn)

        layout.addLayout(ctrl_layout)

        self._all_selected = True

    def _detect(self):
        url = self.url_input.text().strip()
        if not url:
            return

        self.list.clear()
        self._checkbox_map = {}
        self.info_label.setText("Détection en cours...")

        QTimer.singleShot(200, lambda: self._do_detect(url))

    def _do_detect(self, url):
        info = self.downloader.get_video_info(url)
        if "error" in info:
            self.info_label.setText(f"Erreur : {info['error']}")
            return

        entries = info.get("entries", [])
        if not entries:
            self.info_label.setText("Aucune vidéo trouvée dans cette playlist")
            return

        self._entries = entries
        self._playlist_title = info.get("title", "") or ""
        self.info_label.setText(f"{len(entries)} vidéos trouvées")

        for i, entry in enumerate(entries):
            title = entry.get("title", f"Vidéo {i+1}")
            duration = entry.get("duration", 0)
            mins, secs = divmod(int(duration), 60)
            dur = f"{mins}:{secs:02d}" if duration else "?"

            item = QListWidgetItem()
            widget = QWidget()
            wlayout = QHBoxLayout(widget)
            wlayout.setContentsMargins(8, 4, 8, 4)

            cb = QCheckBox()
            cb.setChecked(True)
            self._checkbox_map[i] = cb
            wlayout.addWidget(cb)

            label = QLabel(f"{i+1}. {title[:70]}")
            wlayout.addWidget(label, 1)

            dur_label = QLabel(dur)
            dur_label.setObjectName("subtitle")
            dur_label.setFixedWidth(50)
            dur_label.setAlignment(Qt.AlignRight)
            wlayout.addWidget(dur_label)

            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

        self._all_selected = True

    def _toggle_select_all(self):
        self._all_selected = not self._all_selected
        self.select_all_btn.setText(
            "✓ Tout sélectionner" if self._all_selected else "□ Tout désélectionner"
        )
        for cb in self._checkbox_map.values():
            cb.setChecked(self._all_selected)

    def _connect_signals(self):
        self._disconnect_signals()
        self.downloader.progress_signal.connect(self._on_progress)
        self.downloader.complete_signal.connect(self._on_complete)
        self.downloader.error_signal.connect(self._on_error)
        self._connected = True

    def _disconnect_signals(self):
        if self._connected:
            try:
                self.downloader.progress_signal.disconnect(self._on_progress)
                self.downloader.complete_signal.disconnect(self._on_complete)
                self.downloader.error_signal.disconnect(self._on_error)
            except (TypeError, RuntimeError):
                pass
            self._connected = False

    def _download_selected(self):
        selected = []
        for i, entry in enumerate(self._entries):
            if i in self._checkbox_map and self._checkbox_map[i].isChecked():
                selected.append(entry)

        if not selected:
            return

        self.dl_btn.setEnabled(False)
        self.dl_btn.setText("⏳ Téléchargement...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._download_queue = list(selected)
        self._download_total = len(selected)
        self._download_index = 0
        self._error_count = 0
        self._connect_signals()
        self._download_next()

    def _on_progress(self, data):
        percent = data.get("percent", 0)
        speed = data.get("speed", "")
        eta = data.get("eta", "")
        subtitle = data.get("title", "")
        current = self._download_index + 1 if hasattr(self, '_download_index') else 0
        total = self._download_total if hasattr(self, '_download_total') else 0
        prefix = f"[{current}/{total}]" if total else ""
        text = f"{prefix} {subtitle[:40]}"
        if speed:
            text += f" | {speed}"
        if eta:
            text += f" | ETA {eta}"
        self.progress_label.setText(text)
        overall = int(((current - 1 + percent / 100) / total) * 100) if total else 0
        self.progress_bar.setValue(min(overall, 99))

    def _download_next(self):
        if self._error_count >= self._max_errors:
            self.progress_label.setText(f"❌ Trop d'erreurs ({self._max_errors}), arrêt")
            self.progress_label.setObjectName("status_error")
            self._download_finished()
            return

        if self._download_index >= len(self._download_queue):
            self.progress_label.setText("✅ Playlist terminée !")
            self.progress_label.setObjectName("status_success")
            self._download_finished()
            return

        entry = self._download_queue[self._download_index]
        url = entry.get("url", "")
        title = entry.get("title", "")

        if not url:
            self._download_index += 1
            QTimer.singleShot(100, self._download_next)
            return

        if self.downloader.is_busy:
            QTimer.singleShot(1000, self._download_next)
            return

        self.progress_label.setText(f"[{self._download_index+1}/{self._download_total}] {title[:50]}...")
        self.progress_bar.setValue(int((self._download_index / self._download_total) * 100))

        playlist_dir = self._sanitize_folder_name(
            self._guess_playlist_name()
        ) or "Playlist"
        output_dir = os.path.join(self.manager.get_download_dir(), playlist_dir)

        self._current_dl_url = url
        self.manager.acquire_download(url)
        self.downloader.download(url, output_dir=output_dir, mode="best-speed")

    def _on_complete(self, data):
        if data.get("url") != getattr(self, '_current_dl_url', None):
            return
        self._download_index += 1
        QTimer.singleShot(100, self._download_next)

    def _on_error(self, data):
        if data.get("url") != getattr(self, '_current_dl_url', None):
            return
        self._error_count += 1
        self._download_index += 1
        QTimer.singleShot(500, self._download_next)

    def _download_finished(self):
        self._disconnect_signals()
        self.dl_btn.setEnabled(True)
        self.dl_btn.setText("⬇ Télécharger la playlist")
        self.progress_bar.setValue(100 if self._error_count < self._max_errors else 0)

    def _sanitize_folder_name(self, name):
        return re.sub(r'[^\w\s-]', '', name).strip()[:30]

    def _guess_playlist_name(self):
        if hasattr(self, '_playlist_title') and self._playlist_title:
            return self._playlist_title
        url = self.url_input.text().strip()
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if "playlist" in path:
            return "Playlist"
        parts = path.split("/")
        return parts[-1] if parts else "Playlist"

    def on_show(self):
        self.url_input.setFocus()
