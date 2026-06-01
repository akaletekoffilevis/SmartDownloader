import os
import sys
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class HistoryPage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Historique")
        title.setObjectName("title")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tout", "Vidéo", "Audio"])
        self.filter_type.setFixedWidth(130)
        self.filter_type.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(QLabel("Type :"))
        filter_layout.addWidget(self.filter_type)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher dans l'historique...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, 1)

        self.clear_btn = QPushButton("🗑 Tout effacer")
        self.clear_btn.setObjectName("danger")
        self.clear_btn.clicked.connect(self._clear_all)
        filter_layout.addWidget(self.clear_btn)

        layout.addLayout(filter_layout)

        self.count_label = QLabel("")
        self.count_label.setObjectName("subtitle")
        layout.addWidget(self.count_label)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

    def _load_history(self):
        self.list.clear()
        filters = {}
        type_filter = self.filter_type.currentText()
        if type_filter == "Vidéo":
            filters["type"] = "video"
        elif type_filter == "Audio":
            filters["type"] = "audio"
        query = self.search_input.text().strip()
        if query:
            filters["query"] = query

        entries = self.manager.get_history(filters)
        self.count_label.setText(f"{len(entries)} entrée(s)")

        for entry in entries:
            title = entry.get("title", "Inconnu")
            date = entry.get("date", "")[:19].replace("T", " ")
            status = entry.get("status", "unknown")
            entry_type = entry.get("type", "video")
            entry_id = entry.get("id", "")

            item = QListWidgetItem()
            widget = QWidget()
            wlayout = QHBoxLayout(widget)
            wlayout.setContentsMargins(8, 4, 8, 4)

            icon = "🎬" if entry_type == "video" else "🎵"
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            title_label = QLabel(f"{icon} {title[:70]}")
            title_label.setObjectName("history_title")
            info_layout.addWidget(title_label)

            meta = f"📅 {date}  |  {status}"
            meta_label = QLabel(meta)
            meta_label.setObjectName("subtitle")
            info_layout.addWidget(meta_label)

            wlayout.addLayout(info_layout, 1)

            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(4)

            open_btn = QPushButton("📂 Ouvrir")
            open_btn.setFixedSize(80, 32)
            open_btn.clicked.connect(lambda checked, e=entry: self._open_folder(e))
            actions_layout.addWidget(open_btn)

            redl_btn = QPushButton("🔄 Re-DL")
            redl_btn.setFixedSize(80, 32)
            redl_btn.clicked.connect(lambda checked, e=entry: self._redownload(e))
            actions_layout.addWidget(redl_btn)

            del_btn = QPushButton("✖")
            del_btn.setFixedSize(32, 32)
            del_btn.setObjectName("danger")
            del_btn.clicked.connect(lambda checked, eid=entry_id: self._delete_entry(eid))
            actions_layout.addWidget(del_btn)

            wlayout.addLayout(actions_layout)

            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

    def _apply_filters(self):
        self._load_history()

    def _clear_all(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            "Effacer tout l'historique ?\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.manager.clear_history()
            self._load_history()

    def _open_folder(self, entry):
        path = entry.get("path", "")
        if path and os.path.isdir(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
            except Exception:
                pass

    def _redownload(self, entry):
        url = entry.get("url", "")
        if url:
            parent = self.window()
            if hasattr(parent, "_navigate"):
                if hasattr(parent, "pages") and "download" in parent.pages:
                    dl_page = parent.pages["download"]
                    dl_page.url_input.setText(url)
                    dl_page._detect()
                parent._navigate("download")

    def _delete_entry(self, entry_id):
        self.manager.remove_history(entry_id)
        self._load_history()

    def on_show(self):
        self._load_history()
