import os
import threading
import subprocess
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QObject, Signal


class Downloader(QObject):
    progress_signal = Signal(dict)
    complete_signal = Signal(dict)
    error_signal = Signal(dict)

    FORMAT_RANK = {
        "av1": 0,
        "vp9": 1,
        "h264": 2,
    }

    @staticmethod
    def _ytdlp_path():
        venv_bin = Path(sys.prefix) / "bin"
        candidates = [
            venv_bin / "yt-dlp",
            Path("/usr/local/bin/yt-dlp"),
            Path("/usr/bin/yt-dlp"),
        ]
        for p in candidates:
            if p.exists():
                return str(p)
        return "yt-dlp"

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self._process = None
        self._paused = False
        self._cancelled = False
        self._lock = threading.Lock()
        self._process_ready = threading.Event()
        self._js_runtime_args = self._detect_js_runtime()

    @property
    def is_busy(self):
        with self._lock:
            return self._process_ready.is_set() or self._process is not None

    def _detect_js_runtime(self):
        for name, paths in [
            ("node", ["node", "/usr/bin/node", "/usr/local/bin/node"]),
            ("deno", ["deno", "/usr/bin/deno", "/usr/local/bin/deno"]),
            ("bun", ["bun", "/usr/bin/bun"]),
        ]:
            nvm_node = os.path.expanduser("~/.nvm/versions/node/*/bin/node")
            if name == "node":
                import glob
                nvm_versions = sorted(glob.glob(nvm_node), reverse=True)
                paths = nvm_versions + paths
            for p in paths:
                if os.path.exists(p) and os.access(p, os.X_OK):
                    return ["--js-runtimes", f"{name}:{p}"]
        return []

    def _select_format(self, url, mode="best-speed"):
        try:
            # Bug fix: Ensure height_limit is extracted correctly from any mode string
            base_mode = mode.split(":")[0]
            height_limit = 2160
            if ":" in mode:
                try:
                    height_limit = int(mode.split(":")[1])
                except ValueError:
                    pass

            result = subprocess.run(
                [self._ytdlp_path(), "-J", "--skip-download"] + self._js_runtime_args + [url],
                capture_output=True, text=True, timeout=30
            )
            info = json.loads(result.stdout) if result.stdout.strip() else {}
            if not isinstance(info, dict):
                info = {}
            formats = info.get("formats", [])
            if not formats:
                return f"bestvideo[height<={height_limit}]+bestaudio/best"

            if base_mode == "best-quality":
                return f"bestvideo[height<={height_limit}]+bestaudio/best"

            if base_mode == "audio":
                return "bestaudio/best"

            best_speed = self._pick_fastest_format(formats, height_limit=height_limit)
            return best_speed if best_speed else f"bestvideo[height<={height_limit}]+bestaudio/best"

        except Exception:
            return "bestvideo+bestaudio/best"

    def _pick_fastest_format(self, formats, height_limit=2160):
        scored = []
        for f in formats:
            codec = f.get("vcodec", "")
            height = f.get("height", 0) or 0
            tbr = f.get("tbr", 0) or 0

            if not codec or codec == "none":
                continue
            if height > height_limit:
                continue
            if height <= 0:
                continue
            if codec.startswith("av01"):
                codec_key = "av1"
            elif codec.startswith("vp9"):
                codec_key = "vp9"
            else:
                codec_key = "h264"

            score = self.FORMAT_RANK.get(codec_key, 99)
            scored.append((score, height, tbr, f.get("format_id")))

        scored.sort(key=lambda x: (x[0], -x[1], x[2]))
        if scored:
            best = scored[0]
            return f"{best[3]}+bestaudio/best"
        return None

    def get_video_info(self, url):
        try:
            result = subprocess.run(
                [self._ytdlp_path(), "-J", "--skip-download"] + self._js_runtime_args + [url],
                capture_output=True, text=True, timeout=30
            )
            info = json.loads(result.stdout) if result.stdout.strip() else {}
            if not isinstance(info, dict):
                return {"error": result.stderr.strip() or "Impossible de récupérer les informations"}
            is_playlist = bool(info.get("entries"))
            return {
                "title": info.get("title", "Inconnu"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
                "uploader": info.get("uploader", ""),
                "webpage_url": info.get("webpage_url", url),
                "formats": [
                    {
                        "format_id": f.get("format_id", ""),
                        "height": f.get("height", 0) or 0,
                        "ext": f.get("ext", ""),
                        "filesize": f.get("filesize", 0) or 0,
                        "tbr": f.get("tbr", 0) or 0,
                        "vcodec": f.get("vcodec", ""),
                        "acodec": f.get("acodec", ""),
                    }
                    for f in info.get("formats", [])
                    if f.get("vcodec") and f["vcodec"] != "none"
                ],
                "is_playlist": is_playlist,
                "entries": [
                    {
                        "title": e.get("title", ""),
                        "url": e.get("webpage_url", ""),
                        "duration": e.get("duration", 0),
                    }
                    for e in info.get("entries", [])
                ] if info.get("entries") else [],
            }
        except Exception as e:
            return {"error": str(e)}

    def download(self, url, output_dir=None, mode="best-speed",
                 speed_limit=0):
        if self._process_ready.is_set():
            self.error_signal.emit({"url": url, "error": "Un téléchargement est déjà en cours"})
            return None

        output_dir = output_dir or self.manager.get_download_dir()
        os.makedirs(output_dir, exist_ok=True)

        fmt = self._select_format(url, mode)

        cmd = [
            self._ytdlp_path(),
            "-f", fmt,
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            "--newline",
            "--progress",
            "--no-playlist",
            "--no-warnings",
        ] + self._js_runtime_args

        if mode == "best-speed":
            cmd += ["--concurrent-fragments", "5"]
        else:
            cmd += ["--concurrent-fragments", "3"]

        if speed_limit > 0:
            cmd += ["--limit-rate", f"{speed_limit}K"]

        if self.manager.config.get("auto_split_gb"):
            split_bytes = self.manager.config["auto_split_gb"] * 1073741824
            cmd += ["--max-filesize", str(split_bytes)]

        cmd += ["--retries", "10", "--fragment-retries", "10"]
        cmd += [url]

        thread = threading.Thread(
            target=self._run_download,
            args=(cmd, url, output_dir, mode),
            daemon=True
        )
        thread.start()
        return thread

    def _run_download(self, cmd, url, output_dir, mode="best-speed"):
        try:
            with self._lock:
                if self._cancelled:
                    return
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self._process_ready.set()

            progress_data = {"url": url}
            was_paused = False
            
            # Use stdout.readline() to avoid blocking issues on some systems
            while True:
                line = self._process.stdout.readline()
                if not line and self._process.poll() is not None:
                    break
                
                if self._cancelled:
                    self._process.terminate()
                    break

                if self._paused:
                    if not was_paused and sys.platform != "win32":
                        try:
                            self._process.send_signal(subprocess.signal.SIGSTOP)
                        except Exception: pass
                        was_paused = True
                    time.sleep(0.5)
                    continue
                else:
                    if was_paused and sys.platform != "win32":
                        try:
                            self._process.send_signal(subprocess.signal.SIGCONT)
                        except Exception: pass
                        was_paused = False

                parsed = self._parse_progress(line)
                if parsed:
                    progress_data.update(parsed)
                    self.progress_signal.emit(dict(progress_data))

            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()

            if self._cancelled:
                return

            if self._process.returncode == 0:
                title = progress_data.get("title", progress_data.get("filename", "Inconnu"))
                dl_type = "audio" if mode == "audio" else "video"
                self.manager.add_history({
                    "url": url,
                    "title": title,
                    "type": dl_type,
                    "status": "complete",
                    "path": output_dir,
                })
                self.complete_signal.emit({"url": url, "success": True, "title": title})
            else:
                self.error_signal.emit({"url": url, "error": "Échec du téléchargement"})

        except Exception as e:
            self.error_signal.emit({"url": url, "error": str(e)})
        finally:
            with self._lock:
                self._process = None
                self._process_ready.clear()
            self.manager.release_download(url)

    def _parse_progress(self, line):
        data = {}
        if "[download] Destination:" in line:
            path = line.split("Destination:")[-1].strip()
            data["filename"] = os.path.basename(path)
            name = os.path.splitext(data["filename"])[0]
            if name:
                data["title"] = name

        if "[download]" in line and "%" in line:
            match = re.search(r'([\d.]+)%', line)
            if match:
                data["percent"] = float(match.group(1))

            match = re.search(r'at\s+([\d.]+[\w/]+)', line)
            if match:
                data["speed"] = match.group(1)

            match = re.search(r'ETA\s+(\S+)', line)
            if match:
                data["eta"] = match.group(1)

        return data

    def pause(self):
        self._paused = True
        if self._process:
            try:
                self._process.send_signal(subprocess.signal.SIGSTOP)
            except ProcessLookupError:
                pass

    def resume(self):
        self._paused = False
        if self._process:
            try:
                self._process.send_signal(subprocess.signal.SIGCONT)
            except ProcessLookupError:
                pass

    def cancel(self):
        self._cancelled = True
        proc = self._process
        if proc:
            try:
                if self._paused:
                    proc.send_signal(subprocess.signal.SIGCONT)
                proc.terminate()
            except ProcessLookupError:
                pass

    def search(self, query, max_results=10):
        try:
            result = subprocess.run(
                [self._ytdlp_path(), "-J", "--skip-download"] + self._js_runtime_args +
                [f"ytsearch{max_results}:{query}"],
                capture_output=True, text=True, timeout=30
            )
            data = json.loads(result.stdout) if result.stdout.strip() else {}
            if not isinstance(data, dict):
                return {"error": result.stderr.strip() or "Aucun résultat"}
            entries = data.get("entries", [])
            results = []
            for e in entries:
                results.append({
                    "title": e.get("title", ""),
                    "url": e.get("webpage_url", ""),
                    "duration": e.get("duration", 0),
                    "thumbnail": e.get("thumbnail", ""),
                    "uploader": e.get("uploader", ""),
                    "views": e.get("view_count", 0),
                })
            return results
        except Exception as e:
            return {"error": str(e)}
