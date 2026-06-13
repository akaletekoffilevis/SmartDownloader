import os
import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango

import yt_dlp


OUTPUT_DIR = Path.home() / "Downloads" / "SmartDownloader"


# ─── yt-dlp helpers ────────────────────────────────────────────────────


def get_video_info(url: str):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extractor_retries": 1,
        "retries": 1,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_urls(urls: list[str], output_dir: str, fmt: str, cancel: list, progress_cb, done_cb):
    total = len(urls)

    def hook(d):
        if cancel[0]:
            raise Exception("Cancelled")
        if d["status"] == "downloading":
            pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
            try:
                pct = float(pct_str)
            except ValueError:
                pct = 0
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            GLib.idle_add(progress_cb, idx, total, pct, speed, eta)

    for idx, url in enumerate(urls, 1):
        if cancel[0]:
            break
        opts = {
            "format": fmt,
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [hook],
            "quiet": True,
            "no_warnings": True,
            "extractor_retries": 1,
            "retries": 3,
            "fragment_retries": 3,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception:
            pass
    GLib.idle_add(done_cb, not cancel[0])


# ─── Duration helper ───────────────────────────────────────────────────


def fmt_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}min"
    return f"{m}min {s:02d}s"


# ─── CSS ───────────────────────────────────────────────────────────────


CSS = """
window, .background { background-color: #1a1a2e; }
label { color: #e0e0e0; }
entry { 
    background-color: #16213e; color: #e0e0e0;
    border: 1px solid #0f3460; border-radius: 6px;
    padding: 8px 12px; font-size: 14px;
}
entry:focus { border-color: #10b981; }
button {
    background-color: #10b981; color: white; font-weight: bold;
    border: none; border-radius: 6px; padding: 8px 20px;
}
button:hover { background-color: #059669; }
button:disabled { background-color: #374151; color: #9ca3af; }
combobox { background-color: #16213e; color: #e0e0e0; }
combobox button { background-color: #16213e; color: #e0e0e0; }
progressbar { background-color: #16213e; border-radius: 4px; }
progressbar trough { background-color: #16213e; border: none; border-radius: 4px; }
progressbar progress { background-color: #10b981; border-radius: 4px; }
frame { border-color: #0f3460; }
checkbutton { color: #e0e0e0; }
scrollbar slider { background-color: #10b981; }
.title { font-size: 24px; font-weight: bold; color: #10b981; padding: 10px 0; }
.section { font-size: 14px; font-weight: bold; color: #94a3b8; padding: 5px 0; }
"""


# ─── Main App ──────────────────────────────────────────────────────────


class SmartDownloader(Gtk.Window):
    def __init__(self):
        super().__init__(title="SmartDownloader")
        self.set_default_size(800, 600)
        self.set_border_width(20)
        self._media = None
        self._download_thread = None
        self._cancel = [False]

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self._build_ui()

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(vbox)

        # ── Title ──
        title = Gtk.Label(label="SmartDownloader")
        title.set_name("title")
        title.get_style_context().add_class("title")
        vbox.pack_start(title, False, False, 0)

        # ── URL row ──
        url_box = Gtk.Box(spacing=10)
        vbox.pack_start(url_box, False, False, 0)

        self._url_entry = Gtk.Entry()
        self._url_entry.set_placeholder_text("Coller l'URL YouTube / playlist ici...")
        self._url_entry.set_hexpand(True)
        self._url_entry.connect("activate", lambda e: self._detect())
        url_box.pack_start(self._url_entry, True, True, 0)

        self._detect_btn = Gtk.Button(label="Détecter")
        self._detect_btn.connect("clicked", lambda b: self._detect())
        url_box.pack_start(self._detect_btn, False, False, 0)

        # ── Info area (scrollable) ──
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled, True, True, 0)

        self._info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._info_box.set_margin_start(5)
        self._info_box.set_margin_end(5)
        scrolled.add(self._info_box)

        # ── Progress area ──
        self._progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.pack_start(self._progress_box, False, False, 0)

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_show_text(False)
        self._progress_box.pack_start(self._progress_bar, False, False, 0)

        prog_row = Gtk.Box(spacing=10)
        self._progress_box.pack_start(prog_row, False, False, 0)

        self._progress_label = Gtk.Label(label="")
        prog_row.pack_start(self._progress_label, True, True, 0)

        self._cancel_btn = Gtk.Button(label="Annuler")
        self._cancel_btn.connect("clicked", lambda b: self._cancel())
        prog_row.pack_end(self._cancel_btn, False, False, 0)

        self._progress_box.set_visible(False)

    # ── Actions ─────────────────────────────────────────────────────

    def _set_detecting(self, active: bool):
        self._url_entry.set_sensitive(not active)
        self._detect_btn.set_sensitive(not active)
        self._detect_btn.set_label("Détection..." if active else "Détecter")

    def _detect(self):
        url = self._url_entry.get_text().strip()
        if not url:
            return
        self._set_detecting(True)
        self._clear_info()
        thread = threading.Thread(target=self._detect_thread, args=(url,), daemon=True)
        thread.start()

    def _detect_thread(self, url: str):
        try:
            info = get_video_info(url)
            GLib.idle_add(self._show_info, info)
        except Exception as e:
            GLib.idle_add(self._show_error, str(e))
        finally:
            GLib.idle_add(lambda: self._set_detecting(False))

    def _clear_info(self):
        for w in self._info_box.get_children():
            w.destroy()
        self._media = None

    def _show_error(self, err: str):
        self._clear_info()
        lbl = Gtk.Label(label=f"Erreur : {err}")
        lbl.set_name("error")
        self._info_box.pack_start(lbl, False, False, 0)
        self.show_all()

    def _show_info(self, info: dict):
        self._clear_info()
        self._media = info

        is_playlist = bool(info.get("entries"))
        if is_playlist:
            self._show_playlist(info)
        else:
            self._show_video(info)
        self.show_all()

    def _show_video(self, info: dict):
        title = info.get("title", "Inconnu")
        duration = info.get("duration", 0)
        dur_str = fmt_duration(duration) if duration else "?"

        lbl_title = Gtk.Label(label=title)
        lbl_title.set_xalign(0)
        lbl_title.set_line_wrap(True)
        lbl_title.set_markup(f"<b>{GLib.markup_escape_text(title)}</b>")
        self._info_box.pack_start(lbl_title, False, False, 0)

        lbl_dur = Gtk.Label(label=f"Durée : {dur_str}")
        lbl_dur.set_xalign(0)
        lbl_dur.set_margin_start(10)
        self._info_box.pack_start(lbl_dur, False, False, 0)

        # Format selector
        fmt_box = Gtk.Box(spacing=10)
        fmt_box.set_margin_top(15)
        fmt_box.set_margin_start(10)
        self._info_box.pack_start(fmt_box, False, False, 0)

        fmt_box.pack_start(Gtk.Label(label="Format :"), False, False, 0)

        self._fmt_store = Gtk.ListStore(str, str)
        for label, val in [
            ("Meilleure qualité (4K)", "bestvideo[height<=2160]+bestaudio/best"),
            ("Meilleure qualité (1080p)", "bestvideo[height<=1080]+bestaudio/best"),
            ("Meilleure qualité (720p)", "bestvideo[height<=720]+bestaudio/best"),
            ("Audio seulement (MP3)", "bestaudio/best"),
        ]:
            self._fmt_store.append([label, val])

        self._fmt_combo = Gtk.ComboBox.new_with_model(self._fmt_store)
        renderer = Gtk.CellRendererText()
        self._fmt_combo.pack_start(renderer, True)
        self._fmt_combo.add_attribute(renderer, "text", 0)
        self._fmt_combo.set_active(1)
        fmt_box.pack_start(self._fmt_combo, False, False, 0)

        dl_btn = Gtk.Button(label="Télécharger")
        dl_btn.set_margin_top(20)
        dl_btn.set_margin_bottom(10)
        dl_btn.connect("clicked", lambda b: self._download_video())
        self._info_box.pack_start(dl_btn, False, False, 0)

    def _show_playlist(self, info: dict):
        entries = [e for e in info.get("entries", []) if e]
        title = info.get("title", "Playlist")

        lbl = Gtk.Label(label=f"Playlist : {title} ({len(entries)} vidéos)")
        lbl.set_xalign(0)
        lbl.set_markup(f"<b>{GLib.markup_escape_text(title)}</b> ({len(entries)} vidéos)")
        self._info_box.pack_start(lbl, False, False, 0)

        lbl2 = Gtk.Label(label="Sélectionner les vidéos à télécharger :")
        lbl2.set_xalign(0)
        lbl2.set_margin_start(10)
        lbl2.set_margin_top(10)
        self._info_box.pack_start(lbl2, False, False, 0)

        # Select-all
        self._select_all_cb = Gtk.CheckButton(label="Tout sélectionner")
        self._select_all_cb.set_active(True)
        self._select_all_cb.set_margin_start(15)
        self._select_all_cb.connect("toggled", self._toggle_all)
        self._info_box.pack_start(self._select_all_cb, False, False, 0)

        self._check_buttons = []
        for e in entries:
            dur = fmt_duration(e.get("duration", 0)) if e.get("duration") else "?"
            cb = Gtk.CheckButton(label=f"{e.get('title', 'Inconnu')[:80]} ({dur})")
            cb.set_active(True)
            cb.set_margin_start(25)
            self._info_box.pack_start(cb, False, False, 0)
            self._check_buttons.append(cb)

        dl_btn = Gtk.Button(label="Télécharger la sélection")
        dl_btn.set_margin_top(20)
        dl_btn.set_margin_bottom(10)
        dl_btn.connect("clicked", lambda b: self._download_playlist(entries))
        self._info_box.pack_start(dl_btn, False, False, 0)

    def _toggle_all(self, cb):
        val = cb.get_active()
        for c in self._check_buttons:
            c.set_active(val)

    def _get_format(self) -> str:
        if hasattr(self, "_fmt_combo"):
            tree_iter = self._fmt_combo.get_active_iter()
            if tree_iter:
                return self._fmt_store[tree_iter][1]
        return "bestvideo[height<=1080]+bestaudio/best"

    def _download_video(self):
        if not self._media:
            return
        fmt = self._get_format()
        url = self._media.get("webpage_url", self._url_entry.get_text().strip())
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._cancel = [False]
        self._show_progress_area(1)
        self._download_thread = threading.Thread(
            target=download_urls,
            args=([url], str(OUTPUT_DIR), fmt, self._cancel, self._on_progress, self._on_done),
            daemon=True,
        )
        self._download_thread.start()

    def _download_playlist(self, entries: list):
        selected = [
            e.get("webpage_url") or e.get("url")
            for e, cb in zip(entries, self._check_buttons)
            if cb.get_active()
        ]
        if not selected:
            return
        fmt = "bestvideo[height<=1080]+bestaudio/best"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._cancel = [False]
        self._show_progress_area(len(selected))
        self._download_thread = threading.Thread(
            target=download_urls,
            args=(selected, str(OUTPUT_DIR), fmt, self._cancel, self._on_progress, self._on_done),
            daemon=True,
        )
        self._download_thread.start()

    def _show_progress_area(self, total: int):
        self._download_total = total
        self._progress_bar.set_fraction(0)
        self._progress_label.set_text("Préparation...")
        self._cancel_btn.set_sensitive(True)
        self._progress_box.set_visible(True)

    def _on_progress(self, idx: int, total: int, pct: float, speed: str, eta: str):
        overall = ((idx - 1) + pct / 100) / total
        self._progress_bar.set_fraction(overall)
        text = f"[{idx}/{total}] {pct:.1f}%"
        if speed:
            text += f" — {speed}"
        if eta:
            text += f" — ETA {eta}"
        self._progress_label.set_text(text)

    def _on_done(self, success: bool):
        self._progress_bar.set_fraction(1.0 if success else 0.0)
        self._progress_label.set_text("Téléchargement terminé !" if success else "Annulé")
        self._cancel_btn.set_sensitive(False)

    def _cancel(self):
        self._cancel[0] = True
        self._cancel_btn.set_sensitive(False)
        self._progress_label.set_text("Annulation...")


# ─── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SmartDownloader()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
