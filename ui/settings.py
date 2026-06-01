from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QSpinBox, QGroupBox, QFormLayout,
    QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt


class SettingsPage(QWidget):
    def __init__(self, manager, downloader):
        super().__init__()
        self.manager = manager
        self.downloader = downloader
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Paramètres")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addSpacing(8)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        dl_group = QGroupBox("Téléchargement")
        dl_form = QFormLayout(dl_group)
        dl_form.setSpacing(12)

        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        dir_layout.addWidget(self.dir_input, 1)
        browse_btn = QPushButton("📁 Parcourir")
        browse_btn.setFixedWidth(120)
        browse_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(browse_btn)
        dl_form.addRow("Dossier DL :", dir_layout)

        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setMinimum(1)
        self.concurrent_spin.setMaximum(5)
        self.concurrent_spin.setFixedWidth(80)
        dl_form.addRow("DL simultanés :", self.concurrent_spin)

        self.speed_spin = QSpinBox()
        self.speed_spin.setMinimum(0)
        self.speed_spin.setMaximum(100000)
        self.speed_spin.setSuffix(" KB/s")
        self.speed_spin.setSpecialValueText("Illimité")
        speed_help = QLabel("(0 = illimité)")
        speed_help.setObjectName("help_text")
        dl_form.addRow("Limite vitesse :", self.speed_spin)

        self.split_spin = QSpinBox()
        self.split_spin.setMinimum(0)
        self.split_spin.setMaximum(10)
        self.split_spin.setSuffix(" Go")
        self.split_spin.setSpecialValueText("Désactivé")
        dl_form.addRow("Split auto :", self.split_spin)

        self.auto_dl_check = QCheckBox("Télécharger automatiquement les liens détectés")
        dl_form.addRow("", self.auto_dl_check)

        scroll_layout.addWidget(dl_group)

        quality_group = QGroupBox("Qualité par défaut")
        quality_form = QFormLayout(quality_group)
        quality_form.setSpacing(12)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Best Speed", "Meilleure qualité", "Audio seulement"])
        quality_form.addRow("Mode :", self.mode_combo)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Auto", "720p", "1080p", "4K"])
        quality_form.addRow("Qualité :", self.quality_combo)

        scroll_layout.addWidget(quality_group)

        appearance_group = QGroupBox("Apparence")
        appearance_form = QFormLayout(appearance_group)
        appearance_form.setSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        appearance_form.addRow("Thème :", self.theme_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Français", "English"])
        appearance_form.addRow("Langue :", self.lang_combo)

        scroll_layout.addWidget(appearance_group)

        scroll_layout.addStretch()

        layout.addWidget(scroll_content, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setObjectName("success")
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _load_settings(self):
        cfg = self.manager.config
        self.dir_input.setText(cfg.get("download_dir", ""))
        self.concurrent_spin.setValue(cfg.get("max_concurrent", 2))
        self.speed_spin.setValue(cfg.get("speed_limit", 0))
        self.split_spin.setValue(cfg.get("auto_split_gb", 2))

        mode = cfg.get("default_mode", "best-speed")
        mode_map = {"best-speed": 0, "best-quality": 1, "audio": 2}
        self.mode_combo.setCurrentIndex(mode_map.get(mode, 0))

        q = cfg.get("default_quality", "best")
        q_map = {"best": 0, "720p": 1, "1080p": 2, "2160p": 3}
        self.quality_combo.setCurrentIndex(q_map.get(q, 0))

        theme = cfg.get("theme", "dark")
        self.theme_combo.setCurrentIndex(0 if theme == "dark" else 1)

        lang = cfg.get("language", "fr")
        self.lang_combo.setCurrentIndex(0 if lang == "fr" else 1)

        self.auto_dl_check.setChecked(cfg.get("auto_download", False))

    def _save_settings(self):
        self.manager.batch_update_config({
            "download_dir": self.dir_input.text(),
            "max_concurrent": self.concurrent_spin.value(),
            "speed_limit": self.speed_spin.value(),
            "auto_split_gb": self.split_spin.value(),
            "default_mode": {0: "best-speed", 1: "best-quality", 2: "audio"}[self.mode_combo.currentIndex()],
            "default_quality": {0: "best", 1: "720p", 2: "1080p", 3: "2160p"}[self.quality_combo.currentIndex()],
            "theme": "dark" if self.theme_combo.currentIndex() == 0 else "light",
            "language": "fr" if self.lang_combo.currentIndex() == 0 else "en",
            "auto_download": self.auto_dl_check.isChecked(),
        })

        main_window = self.window()
        if hasattr(main_window, "apply_theme"):
            main_window.apply_theme()

    def _browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Choisir le dossier")
        if path:
            self.dir_input.setText(path)

    def on_show(self):
        self._load_settings()
