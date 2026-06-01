import json
import os
import threading
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"
HISTORY_FILE = DATA_DIR / "history.json"

DEFAULT_CONFIG = {
    "download_dir": str(Path.home() / "Downloads" / "SmartDownloader"),
    "max_concurrent": 2,
    "speed_limit": 0,
    "default_quality": "best",
    "default_mode": "best-speed",
    "theme": "dark",
    "language": "fr",
    "auto_split_gb": 2,
    "auto_download": False,
}


class Manager:
    def __init__(self):
        self._lock = threading.RLock()
        self._queue_lock = threading.RLock()
        self.config = self._load_config()
        self.history = self._load_history()
        self.queue = []
        self.active_downloads = []
        self._init_dirs()

    def _init_dirs(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(self.config["download_dir"], exist_ok=True)

    def _load_config(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
        except (json.JSONDecodeError, OSError):
            pass
        return dict(DEFAULT_CONFIG)

    def save_config(self):
        with self._lock:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def batch_update_config(self, changes):
        with self._lock:
            self.config.update(changes)
            self.save_config()

    def _load_history(self):
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
        except (json.JSONDecodeError, OSError):
            pass
        return []

    def _save_history(self):
        with self._lock:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history, f, indent=2)

    def clear_history(self):
        with self._lock:
            self.history.clear()
            self._save_history()

    def add_history(self, entry):
        entry["date"] = datetime.now().isoformat()
        entry["id"] = str(int(datetime.now().timestamp()))
        with self._lock:
            self.history.insert(0, entry)
            self._save_history()

    def get_history(self, filters=None):
        with self._lock:
            results = list(self.history)
        if filters:
            if filters.get("type"):
                results = [e for e in results if e.get("type") == filters["type"]]
            if filters.get("query"):
                q = filters["query"].lower()
                results = [e for e in results if q in e.get("title", "").lower()]
        return results

    def remove_history(self, entry_id):
        with self._lock:
            self.history = [e for e in self.history if e.get("id") != entry_id]
            self._save_history()

    def get_download_dir(self):
        return self.config["download_dir"]

    def set_download_dir(self, path):
        self.config["download_dir"] = path
        os.makedirs(path, exist_ok=True)
        self.save_config()

    @property
    def can_download(self):
        return len(self.active_downloads) < self.config["max_concurrent"]

    def acquire_download(self, url):
        with self._queue_lock:
            if url not in self.active_downloads:
                self.active_downloads.append(url)
                return True
            return False

    def release_download(self, url):
        with self._queue_lock:
            if url in self.active_downloads:
                self.active_downloads.remove(url)

    def get_queue_state(self):
        with self._queue_lock:
            return {
                "waiting": [q for q in self.queue if q.get("status") == "waiting"],
                "active_count": len(self.active_downloads),
            }

    def clear_waiting_queue(self):
        with self._queue_lock:
            self.queue = [q for q in self.queue if q.get("status") != "waiting"]

    def add_to_queue(self, item):
        with self._queue_lock:
            self.queue.append(item)

    def remove_from_queue(self, url):
        with self._queue_lock:
            self.queue = [q for q in self.queue if q.get("url") != url]

    def promote_in_queue(self, url):
        with self._queue_lock:
            for i, q in enumerate(self.queue):
                if q.get("url") == url:
                    self.queue.insert(0, self.queue.pop(i))
                    break

    def get_next_waiting(self):
        with self._queue_lock:
            for i, q in enumerate(self.queue):
                if q.get("status") == "waiting":
                    return self.queue.pop(i)
            return None
