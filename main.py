import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from core.manager import Manager
from core.downloader import Downloader
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SmartDownloader")
    app.setOrganizationName("SmartDL")

    manager = Manager()
    downloader = Downloader(manager)

    window = MainWindow(manager, downloader)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
