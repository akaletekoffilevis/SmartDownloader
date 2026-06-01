from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QProgressBar, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication


class DownloadPage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._connected = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Téléchargement")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(8)

        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Collez un lien YouTube, TikTok, etc...")
        self.url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(self.url_input, 1)

        self.paste_btn = QPushButton("📋 Coller")
        self.paste_btn.setFixedWidth(100)
        self.paste_btn.clicked.connect(self._paste)
        url_layout.addWidget(self.paste_btn)

        self.detect_btn = QPushButton("🔍 Détecter")
        self.detect_btn.setFixedWidth(120)
        self.detect_btn.clicked.connect(self._detect)
        url_layout.addWidget(self.detect_btn)
        layout.addLayout(url_layout)

        self.info_frame = QFrame()
        self.info_frame.setObjectName("info_frame")
        self.info_frame.setVisible(False)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(8)

        self.video_title = QLabel("Titre de la vidéo")
        self.video_title.setObjectName("video_title")
        info_layout.addWidget(self.video_title)

        self.video_meta = QLabel("Durée | Auteur")
        self.video_meta.setObjectName("video_meta")
        info_layout.addWidget(self.video_meta)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        options_layout.addWidget(QLabel("Mode :"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Best Speed", "Meilleure qualité", "Audio seulement"])
        self.mode_combo.setFixedWidth(180)
        options_layout.addWidget(self.mode_combo)

        options_layout.addWidget(QLabel("Format :"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Auto", "720p", "1080p", "4K"])
        self.quality_combo.setFixedWidth(120)
        options_layout.addWidget(self.quality_combo)

        options_layout.addStretch()
        info_layout.addLayout(options_layout)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.dl_btn = QPushButton("⬇ Lancer le téléchargement")
        self.dl_btn.setObjectName("success")
        self.dl_btn.setMinimumHeight(50)
        self.dl_btn.clicked.connect(self._start_download)
        btn_row.addWidget(self.dl_btn, 1)

        self.oneclick_btn = QPushButton("⚡ 1-Clic")
        self.oneclick_btn.setObjectName("oneclick")
        self.oneclick_btn.setMinimumHeight(50)
        self.oneclick_btn.setFixedWidth(120)
        self.oneclick_btn.clicked.connect(lambda: self._start_download("best-speed"))
        btn_row.addWidget(self.oneclick_btn)
        info_layout.addLayout(btn_row)

        layout.addWidget(self.info_frame)

        progress_frame = QFrame()
        progress_frame.setObjectName("info_frame")
        p_layout = QVBoxLayout(progress_frame)
        p_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        p_layout.addWidget(self.progress_bar)

        status_layout = QHBoxLayout()
        self.speed_label = QLabel("")
        self.speed_label.setObjectName("subtitle")
        status_layout.addWidget(self.speed_label)
        self.eta_label = QLabel("")
        self.eta_label.setObjectName("subtitle")
        self.eta_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.eta_label)
        p_layout.addLayout(status_layout)

        ctrl_layout = QHBoxLayout()
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setVisible(False)
        self.pause_btn.clicked.connect(self._toggle_pause)
        ctrl_layout.addWidget(self.pause_btn)

        self.cancel_btn = QPushButton("✖ Annuler")
        self.cancel_btn.setObjectName("danger")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel)
        ctrl_layout.addWidget(self.cancel_btn)
        ctrl_layout.addStretch()
        p_layout.addLayout(ctrl_layout)

        layout.addWidget(progress_frame)

        queue_header = QHBoxLayout()
        queue_label = QLabel("File d'attente")
        queue_label.setObjectName("subtitle")
        queue_header.addWidget(queue_label)
        queue_header.addStretch()

        self.queue_count = QLabel("0 en attente")
        self.queue_count.setObjectName("subtitle")
        queue_header.addWidget(self.queue_count)

        clear_queue_btn = QPushButton("🗑 Vider")
        clear_queue_btn.setFixedWidth(80)
        clear_queue_btn.clicked.connect(self._clear_queue)
        queue_header.addWidget(clear_queue_btn)

        layout.addLayout(queue_header)

        self.queue_list = QScrollArea()
        self.queue_list.setObjectName("queue_area")
        self.queue_content = QWidget()
        self.queue_layout = QVBoxLayout(self.queue_content)
        self.queue_layout.setAlignment(Qt.AlignTop)
        self.queue_list.setWidget(self.queue_content)
        self.queue_list.setWidgetResizable(True)
        self.queue_list.setMinimumHeight(120)
        layout.addWidget(self.queue_list, 1)

        self._current_url = None
        self._is_paused = False

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

    def _paste(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
            self._detect()

    def _on_url_changed(self, text):
        text = text.strip()
        has_url = bool(text and (
            "youtube.com" in text.lower() or "youtu.be" in text.lower()
            or "tiktok" in text.lower() or "vimeo" in text.lower()
            or "twitter.com" in text.lower() or "x.com" in text.lower()
            or "instagram.com" in text.lower()
        ))
        self.detect_btn.setEnabled(has_url)

    def _detect(self):
        url = self.url_input.text().strip()
        if not url:
            return
        info = self.downloader.get_video_info(url)
        if "error" in info:
            self.video_title.setText(f"Erreur : {info['error']}")
            self.video_title.setObjectName("error_label")
            self.info_frame.setVisible(True)
            return

        title = info.get("title", url)
        duration = info.get("duration", 0)
        uploader = info.get("uploader", "")
        mins, secs = divmod(int(duration), 60)
        dur_str = f"{mins}:{secs:02d}" if duration else "Live"

        self.video_title.setText(title)
        self.video_meta.setText(f"⏱ {dur_str}  |  {uploader}")
        self.video_title.setObjectName("video_title")
        self.info_frame.setVisible(True)
        self._last_info = info

    def _start_download(self, force_mode=None):
        url = self.url_input.text().strip()
        if not url:
            return

        if force_mode:
            mode = force_mode
        else:
            mode_map = {
                "Best Speed": "best-speed",
                "Meilleure qualité": "best-quality",
                "Audio seulement": "audio",
            }
            mode = mode_map.get(self.mode_combo.currentText(), "best-speed")

        quality_map = {"Auto": 0, "720p": 720, "1080p": 1080, "4K": 2160}
        selected_height = quality_map.get(self.quality_combo.currentText(), 0)
        if selected_height > 0 and mode in ("best-speed", "best-quality"):
            mode = f"{mode}:{selected_height}"

        if not self.manager.can_download:
            self.manager.add_to_queue({
                "url": url,
                "title": self.video_title.text()[:50] if hasattr(self, '_last_info') else url[:50],
                "mode": mode,
                "status": "waiting"
            })
            self._refresh_queue()
            self.speed_label.setText("⏳ Ajouté à la file d'attente")
            self.speed_label.setObjectName("status_warning")
            return

        self._current_url = url
        if not self.manager.acquire_download(url):
            self.speed_label.setText("⚠ Déjà en cours de téléchargement")
            self.speed_label.setObjectName("status_warning")
            return
        self._connect_signals()

        self.dl_btn.setEnabled(False)
        self.oneclick_btn.setEnabled(False)
        self.dl_btn.setText("⏳ Téléchargement en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.pause_btn.setVisible(True)
        self.cancel_btn.setVisible(True)
        self.speed_label.setText("")
        self.eta_label.setText("")

        speed_limit = self.manager.config.get("speed_limit", 0)
        self.downloader.download(url, mode=mode, speed_limit=speed_limit)
        self._refresh_queue()

    def _on_progress(self, data):
        if data.get("url") != self._current_url:
            return
        percent = data.get("percent", 0)
        speed = data.get("speed", "")
        eta = data.get("eta", "")
        self.progress_bar.setValue(int(percent))
        self.speed_label.setText(f"⚡ Vitesse : {speed}" if speed else f"Téléchargement... {percent:.0f}%")
        if eta:
            self.eta_label.setText(f"⏱ Restant : {eta}")

    def _on_complete(self, data):
        if data.get("url") != self._current_url:
            return
        self._disconnect_signals()
        self._reset_ui()
        self.speed_label.setText("✅ Téléchargement terminé !")
        self.speed_label.setObjectName("status_success")
        self._current_url = None
        self._process_queue()

    def _on_error(self, data):
        if data.get("url") != self._current_url:
            return
        self._disconnect_signals()
        self._reset_ui()
        self.speed_label.setText(f"❌ Erreur : {data.get('error', 'Inconnue')}")
        self.speed_label.setObjectName("status_error")
        self._current_url = None
        self._process_queue()

    def _process_queue(self):
        next_item = self.manager.get_next_waiting()
        if next_item and self.manager.can_download:
            self.url_input.setText(next_item["url"])
            self._detect()
            QTimer.singleShot(500, lambda: self._start_download(next_item.get("mode")))
        self._refresh_queue()

    def _toggle_pause(self):
        if self._is_paused:
            self.downloader.resume()
            self.pause_btn.setText("⏸ Pause")
            self._is_paused = False
        else:
            self.downloader.pause()
            self.pause_btn.setText("▶ Reprendre")
            self._is_paused = True

    def _cancel(self):
        self.downloader.cancel()
        self._disconnect_signals()
        self._reset_ui()
        self.speed_label.setText("✖ Téléchargement annulé")
        self.speed_label.setObjectName("status_warning")
        self._current_url = None
        self._process_queue()

    def _reset_ui(self):
        self._is_paused = False
        self.dl_btn.setEnabled(True)
        self.oneclick_btn.setEnabled(True)
        self.dl_btn.setText("⬇ Lancer le téléchargement")
        self.pause_btn.setText("⏸ Pause")
        self.pause_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)

    def _refresh_queue(self):
        for i in reversed(range(self.queue_layout.count())):
            item = self.queue_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        state = self.manager.get_queue_state()
        waiting = state["waiting"]
        active_count = state["active_count"]

        self.queue_count.setText(f"{active_count} actif(s), {len(waiting)} en attente")

        for entry in waiting:
            status = entry.get("status", "")
            icon = "⏸"
            title = entry.get("title", "Inconnu")[:50]

            row = QHBoxLayout()
            row.setSpacing(8)

            label = QLabel(f"{icon} {title}")
            label.setObjectName("subtitle")
            label.setStyleSheet("padding: 4px 8px;")
            row.addWidget(label, 1)

            promote_btn = QPushButton("⬆")
            promote_btn.setFixedSize(28, 28)
            url = entry.get("url", "")
            promote_btn.clicked.connect(lambda checked, u=url: self._promote(u))
            row.addWidget(promote_btn)

            remove_btn = QPushButton("✖")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setObjectName("danger")
            remove_btn.clicked.connect(lambda checked, u=url: self._remove_from_queue(u))
            row.addWidget(remove_btn)

            container = QWidget()
            container.setLayout(row)
            self.queue_layout.addWidget(container)

    def _promote(self, url):
        self.manager.promote_in_queue(url)
        self._refresh_queue()

    def _remove_from_queue(self, url):
        self.manager.remove_from_queue(url)
        self._refresh_queue()

    def _clear_queue(self):
        self.manager.clear_waiting_queue()
        self._refresh_queue()

    def on_show(self):
        self._refresh_queue()
