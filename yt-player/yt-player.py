#!/usr/bin/env python3
"""
HyperCam 2 Style Music Player — XP/Y2K Aesthetic
YouTube Music integration via ytmusicapi + mpv
"""

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gdk, GLib, Gtk, Pango, Gst

from ytmusicapi import YTMusic

# Initialize GStreamer
Gst.init(None)

# Paths
HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "yt-player"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
AUTH_FILE = CONFIG_DIR / "auth.json"
CACHE_DIR = CONFIG_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Colors
XP_BLUE = (0.0, 0.33, 0.89, 0.95)
BEIGE = (0.93, 0.92, 0.88, 0.95)
GREEN = (0.0, 0.60, 0.0, 1.0)
GREEN_DIM = (0.0, 0.40, 0.0, 0.9)
RED_TUNNEL = (0.85, 0.15, 0.05, 0.9)
BLACK = (0.0, 0.0, 0.0, 1.0)


class TunnelVisualizer(Gtk.DrawingArea):
    """Red swirling tunnel visualizer like the 2000s screensaver."""

    def __init__(self, width=720, height=360):
        super().__init__()
        self.width = width
        self.height = height
        self.phase = 0.0
        self.frame = 0
        self.audio_level = 0.0
        self.set_size_request(width, height)
        GLib.timeout_add(33, self.tick)  # ~30fps

    def tick(self):
        self.phase += 0.12
        self.frame = (self.frame + 1) % 10000
        self.queue_draw()
        return True

    def draw(self, _area, cr):
        w = self.width
        h = self.height
        cx, cy = w / 2, h / 2

        # Black background
        cr.set_source_rgba(*BLACK)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Red tunnel rings - audio reactive
        max_radius = min(w, h) * 0.45
        audio_boost = 1.0 + self.audio_level * 0.5
        
        for i in range(50, 0, -1):
            t = self.phase + i * 0.15
            radius = max_radius * (i / 50.0) * audio_boost
            twist = math.sin(t * 0.7) * 0.4 + math.cos(t * 0.3) * 0.3
            
            # Red-orange gradient
            r = 0.7 + 0.3 * math.sin(t)
            g = 0.05 + 0.1 * math.cos(t * 0.5)
            b = 0.0
            alpha = 0.15 + 0.4 * (i / 50.0)
            
            cr.set_source_rgba(r, g, b, alpha)
            cr.arc(cx + twist * 30, cy + twist * 20, radius, 0, 2 * math.pi)
            cr.fill()

        # Central black hole with glow
        cr.set_source_rgba(*BLACK)
        cr.arc(cx, cy, max_radius * 0.2, 0, 2 * math.pi)
        cr.fill()
        
        # White center dot
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.arc(cx, cy, 3, 0, 2 * math.pi)
        cr.fill()

        return False


class PlayerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("HyperCam 2")
        self.set_default_size(720, 540)
        self.set_resizable(True)
        self.set_decorated(False)
        self.set_keep_above(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)

        # State
        self.playing = False
        self.current_track = None
        self.mpv_process = None
        self.ytmusic = None
        self.search_results = []
        self.current_index = 0
        self.pipeline = None
        self.audio_probe = None

        # Build UI
        self.build_ui()
        self.connect("destroy", Gtk.main_quit)

        # Init YouTube Music
        self.init_ytmusic()

    def build_ui(self):
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # Title bar (XP Luna style)
        title_bar = self.create_title_bar()
        main_box.pack_start(title_bar, False, False, 0)

        # Content area
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.pack_start(content, True, True, 0)

        # Visualizer
        self.visualizer = TunnelVisualizer(720, 360)
        content.pack_start(self.visualizer, True, True, 0)

        # Control panel (black background, green text)
        controls = self.create_controls()
        content.pack_start(controls, False, False, 0)

        # Status bar
        self.status_bar = Gtk.Label(label="Ready — authenticate YouTube Music to start")
        self.status_bar.set_margin_start(8)
        self.status_bar.set_margin_end(8)
        self.status_bar.set_margin_top(4)
        self.status_bar.set_margin_bottom(4)
        self.status_bar.modify_font(Pango.FontDescription("Tahoma 8"))
        main_box.pack_start(self.status_bar, False, False, 0)

    def create_title_bar(self):
        """XP Luna blue title bar."""
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_box.set_margin_top(4)
        title_box.set_margin_bottom(4)
        title_box.set_margin_start(8)
        title_box.set_margin_end(8)

        # Icon + Title
        title_label = Gtk.Label(label="Unregistered HyperCam 2")
        title_label.modify_font(Pango.FontDescription("Tahoma 9"))
        title_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.Color(255, 255, 255))
        title_box.pack_start(title_label, True, True, 0)

        # Window controls
        close_btn = Gtk.Button(label="×")
        close_btn.set_size_request(20, 20)
        close_btn.modify_font(Pango.FontDescription("Tahoma 10"))
        close_btn.connect("clicked", lambda w: Gtk.main_quit())
        title_box.pack_end(close_btn, False, False, 0)

        return title_box

    def create_controls(self):
        """Bottom control panel with green text on black."""
        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        controls.set_margin_start(8)
        controls.set_margin_end(8)
        controls.set_margin_top(8)
        controls.set_margin_bottom(8)

        # Info row
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.artist_label = Gtk.Label(label="Artist: Not connected")
        self.artist_label.set_halign(Gtk.Align.START)
        self.artist_label.modify_font(Pango.FontDescription("Tahoma 9"))
        self.artist_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 153, 0))
        info_box.pack_start(self.artist_label, True, True, 0)

        self.time_label = Gtk.Label(label="00:00")
        self.time_label.modify_font(Pango.FontDescription("Tahoma 9"))
        self.time_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 153, 0))
        info_box.pack_end(self.time_label, False, False, 0)

        controls.pack_start(info_box, False, False, 0)

        # Buttons row
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        btn_box.set_halign(Gtk.Align.CENTER)

        prev_btn = Gtk.Button(label="⏮")
        prev_btn.set_size_request(36, 28)
        prev_btn.connect("clicked", self.prev_track)
        btn_box.pack_start(prev_btn, False, False, 0)

        self.play_btn = Gtk.Button(label="▶")
        self.play_btn.set_size_request(42, 32)
        self.play_btn.connect("clicked", self.toggle_play)
        btn_box.pack_start(self.play_btn, False, False, 0)

        stop_btn = Gtk.Button(label="⏹")
        stop_btn.set_size_request(36, 28)
        stop_btn.connect("clicked", self.stop_playback)
        btn_box.pack_start(stop_btn, False, False, 0)

        next_btn = Gtk.Button(label="⏭")
        next_btn.set_size_request(36, 28)
        next_btn.connect("clicked", self.next_track)
        btn_box.pack_start(next_btn, False, False, 0)

        vol_label = Gtk.Label(label="Vol:")
        vol_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 153, 0))
        btn_box.pack_start(vol_label, False, False, 4)

        self.volume_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.volume_scale.set_range(0, 100)
        self.volume_scale.set_value(70)
        self.volume_scale.set_size_request(80, 20)
        self.volume_scale.connect("value-changed", self.set_volume)
        btn_box.pack_start(self.volume_scale, False, False, 0)

        fs_btn = Gtk.Button(label="⛶")
        fs_btn.set_size_request(28, 28)
        fs_btn.connect("clicked", self.toggle_fullscreen)
        btn_box.pack_end(fs_btn, False, False, 0)

        controls.pack_start(btn_box, False, False, 0)

        # Search row
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search YouTube Music...")
        self.search_entry.connect("activate", self.do_search)
        search_box.pack_start(self.search_entry, True, True, 0)

        search_btn = Gtk.Button(label="Search")
        search_btn.connect("clicked", self.do_search)
        search_box.pack_start(search_btn, False, False, 0)

        auth_btn = Gtk.Button(label="Auth")
        auth_btn.connect("clicked", self.auth_ytmusic)
        search_box.pack_end(auth_btn, False, False, 0)

        controls.pack_start(search_box, False, False, 0)

        return controls

    def init_ytmusic(self):
        """Initialize YouTube Music API."""
        try:
            if AUTH_FILE.exists():
                import json
                auth_data = json.loads(AUTH_FILE.read_text())
                self.ytmusic = YTMusic(auth=auth_data)
                self.status_bar.set_text("YouTube Music: connected (premium)")
            else:
                self.ytmusic = YTMusic()
                self.status_bar.set_text("YouTube Music: not authenticated (limited)")
        except Exception as e:
            self.status_bar.set_text(f"YouTube Music error: {e}")

    def auth_ytmusic(self, _widget):
        """Authenticate with YouTube Music premium account."""
        dialog = Gtk.MessageDialog(
            flags=0,
            message_type=Gtk.MessageType.INFO,
            text="YouTube Music Authentication",
            secondary_text=(
                "Authenticated via browser cookies.\n\n"
                f"Auth file: {AUTH_FILE}\n\n"
                "If auth expires, update cookies from Firefox and restart."
            )
        )
        dialog.set_transient_for(self)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.run()
        dialog.destroy()

    def do_search(self, _widget=None):
        """Search YouTube Music."""
        query = self.search_entry.get_text().strip()
        if not query or not self.ytmusic:
            return

        try:
            results = self.ytmusic.search(query, filter="songs", limit=10)
            self.search_results = results
            self.current_index = 0
            if results:
                self.play_track(results[0])
        except Exception as e:
            self.status_bar.set_text(f"Search error: {e}")

    def play_track(self, track):
        """Play a track via mpv."""
        if self.mpv_process:
            self.mpv_process.terminate()
            self.mpv_process = None

        video_id = track.get("videoId")
        if not video_id:
            return

        url = f"https://music.youtube.com/watch?v={video_id}"
        title = track.get("title", "Unknown")
        artist = track.get("artists", [{}])[0].get("name", "Unknown")
        album = track.get("album", {}).get("name", "")

        self.artist_label.set_text(f"Artist: {artist}")
        self.status_bar.set_text(f"Playing: {title}" + (f" — {album}" if album else ""))

        # Start mpv with IPC
        try:
            self.mpv_process = subprocess.Popen(
                ["mpv", "--no-video", "--input-ipc-server=/tmp/mpv-ytplayer.sock", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.playing = True
            self.play_btn.set_label("⏸")
            GLib.timeout_add(1000, self.update_time)
        except Exception as e:
            self.status_bar.set_text(f"Playback error: {e}")

    def toggle_play(self, _widget):
        """Play/pause."""
        if not self.mpv_process:
            if self.search_results:
                self.play_track(self.search_results[self.current_index])
            return

        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect("/tmp/mpv-ytplayer.sock")
            if self.playing:
                sock.sendall(b'{ "command": ["set_property", "pause", true] }')
                self.play_btn.set_label("▶")
            else:
                sock.sendall(b'{ "command": ["set_property", "pause", false] }')
                self.play_btn.set_label("⏸")
            sock.close()
            self.playing = not self.playing
        except Exception:
            pass

    def stop_playback(self, _widget):
        """Stop playback."""
        if self.mpv_process:
            self.mpv_process.terminate()
            self.mpv_process = None
        self.playing = False
        self.play_btn.set_label("▶")
        self.time_label.set_text("00:00")
        self.status_bar.set_text("Stopped")

    def prev_track(self, _widget):
        """Previous track."""
        if self.search_results and self.current_index > 0:
            self.current_index -= 1
            self.play_track(self.search_results[self.current_index])

    def next_track(self, _widget):
        """Next track."""
        if self.search_results and self.current_index < len(self.search_results) - 1:
            self.current_index += 1
            self.play_track(self.search_results[self.current_index])

    def set_volume(self, _widget):
        """Set mpv volume."""
        try:
            import socket
            vol = int(self.volume_scale.get_value())
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect("/tmp/mpv-ytplayer.sock")
            sock.sendall(f'{{ "command": ["set_property", "volume", {vol}] }}'.encode())
            sock.close()
        except Exception:
            pass

    def update_time(self):
        """Update time display from mpv."""
        if not self.mpv_process or not self.playing:
            return True
        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect("/tmp/mpv-ytplayer.sock")
            sock.sendall(b'{ "command": ["get_property", "time-pos"] }')
            data = sock.recv(1024)
            sock.close()
            if data:
                resp = json.loads(data)
                pos = resp.get("data", 0)
                m, s = divmod(int(pos), 60)
                self.time_label.set_text(f"{m:02d}:{s:02d}")
        except Exception:
            pass
        return True

    def toggle_fullscreen(self, _widget):
        """Toggle fullscreen."""
        if self.get_window().get_state() & Gdk.WindowState.FULLSCREEN:
            self.unfullscreen()
        else:
            self.fullscreen()


def main():
    win = PlayerWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
