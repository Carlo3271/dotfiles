#!/usr/bin/env python3
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


CSS = b"""
window {
  background: #060809;
  color: #f4f4f4;
  font-family: "Noto Sans", sans-serif;
  font-size: 10px;
}
.root {
  background: #060809;
}
.sidebar {
  background: #050607;
  border-right: 1px solid #1a1d20;
}
.side-button {
  background: #101316;
  border: 0;
  border-radius: 3px;
  color: #cfd4d8;
  padding: 4px;
  margin: 2px;
}
.side-button-active {
  background: #1db954;
  color: #001909;
}
.topbar {
  background: #0d0f10;
  border-bottom: 1px solid #22262a;
}
.search {
  background: #1c2024;
  color: #d8dde2;
  border: 0;
  border-radius: 12px;
  padding: 4px 10px;
}
.artist {
  background: #1a1414;
}
.artist-title {
  font-size: 31px;
  font-weight: 900;
  color: #ffffff;
}
.muted {
  color: #b8bdc2;
}
.green {
  color: #1ed760;
}
.section-title {
  font-size: 14px;
  font-weight: 800;
  color: #ffffff;
}
.album {
  background: #16191d;
  border-radius: 3px;
}
.album-title {
  color: #ffffff;
  font-weight: 700;
}
.cover-duvet {
  background-image: linear-gradient(135deg, #d8d8d8, #2d3035 48%, #0c0d0f);
  border: 1px solid #393d41;
}
.cover-twilight {
  background-image: linear-gradient(135deg, #18b7d5, #1f4b9d 48%, #e73d43);
  border: 1px solid #295276;
}
.player {
  background: #050607;
  border-top: 1px solid #1b1e21;
}
.progress trough {
  min-height: 3px;
  background: #404448;
}
.progress progress {
  min-height: 3px;
  background: #1ed760;
}
"""


class MusicWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="bôa - Duvet")
        self.set_default_size(430, 480)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.NONE)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.get_style_context().add_class("root")
        self.add(root)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        root.pack_start(body, True, True, 0)

        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        sidebar.set_size_request(38, -1)
        sidebar.set_margin_top(6)
        sidebar.set_margin_bottom(6)
        sidebar.get_style_context().add_class("sidebar")
        body.pack_start(sidebar, False, False, 0)

        for label, active in [("|||", False), ("+", False), ("du", False), ("la", False), ("vy", True), ("sp", False)]:
            b = Gtk.Label(label=label)
            b.get_style_context().add_class("side-button")
            if active:
                b.get_style_context().add_class("side-button-active")
            sidebar.pack_start(b, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        body.pack_start(main, True, True, 0)

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top.set_margin_left(8)
        top.set_margin_right(8)
        top.set_margin_top(6)
        top.set_margin_bottom(6)
        top.get_style_context().add_class("topbar")
        main.pack_start(top, False, False, 0)
        top.pack_start(Gtk.Label(label="...   <   >"), False, False, 0)
        search = Gtk.Label(label="What do you want to play?")
        search.set_xalign(0)
        search.get_style_context().add_class("search")
        top.pack_start(search, True, True, 0)
        top.pack_end(Gtk.Label(label="o"), False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main.pack_start(content, True, True, 0)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        left.set_size_request(210, -1)
        content.pack_start(left, False, False, 0)

        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        hero.set_margin_left(8)
        hero.set_margin_right(6)
        hero.set_margin_top(8)
        hero.set_margin_bottom(6)
        hero.get_style_context().add_class("artist")
        left.pack_start(hero, True, True, 0)
        duvet = Gtk.Label(label="")
        duvet.set_size_request(-1, 120)
        duvet.get_style_context().add_class("cover-duvet")
        hero.pack_start(duvet, False, False, 0)
        title = Gtk.Label(label="bôa")
        title.set_xalign(0)
        title.get_style_context().add_class("artist-title")
        hero.pack_start(title, False, False, 0)
        verified = Gtk.Label(label="Verified Artist")
        verified.set_xalign(0)
        verified.get_style_context().add_class("green")
        hero.pack_start(verified, False, False, 0)
        listeners = Gtk.Label(label="1,623,803 monthly listeners")
        listeners.set_xalign(0)
        listeners.get_style_context().add_class("muted")
        hero.pack_start(listeners, False, False, 0)

        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        action_row.set_margin_left(8)
        action_row.set_margin_right(8)
        left.pack_start(action_row, False, False, 6)
        action_row.pack_start(Gtk.Label(label="▶"), False, False, 0)
        action_row.pack_start(Gtk.Label(label="Follow"), False, False, 0)

        popular = Gtk.Label(label="Popular")
        popular.set_xalign(0)
        popular.set_margin_left(8)
        popular.get_style_context().add_class("section-title")
        left.pack_start(popular, False, False, 4)
        for i, track in enumerate([("1", "Duvet", "3:23"), ("2", "Twilight", "3:48")]):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.set_margin_left(8)
            row.set_margin_right(8)
            row.set_margin_top(3)
            row.pack_start(Gtk.Label(label=track[0]), False, False, 0)
            name = Gtk.Label(label=track[1])
            name.set_xalign(0)
            row.pack_start(name, True, True, 0)
            row.pack_end(Gtk.Label(label=track[2]), False, False, 0)
            left.pack_start(row, False, False, 0)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        right.set_margin_left(6)
        right.set_margin_right(8)
        right.set_margin_top(8)
        right.set_margin_bottom(8)
        content.pack_start(right, True, True, 0)
        right.pack_start(Gtk.Label(label="serial experiments lain"), False, False, 0)
        twilight = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        twilight.set_size_request(150, 150)
        twilight.get_style_context().add_class("cover-twilight")
        twilight.pack_end(Gtk.Label(label="twilight"), False, False, 12)
        right.pack_start(twilight, False, False, 0)
        album = Gtk.Label(label="Duvet")
        album.set_xalign(0)
        album.get_style_context().add_class("album-title")
        right.pack_start(album, False, False, 0)
        artist = Gtk.Label(label="bôa")
        artist.set_xalign(0)
        artist.get_style_context().add_class("muted")
        right.pack_start(artist, False, False, 0)
        right.pack_end(Gtk.Label(label="Related music videos"), False, False, 0)

        player = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        player.set_margin_left(8)
        player.set_margin_right(8)
        player.set_margin_top(6)
        player.set_margin_bottom(6)
        player.get_style_context().add_class("player")
        root.pack_end(player, False, False, 0)
        player.pack_start(Gtk.Label(label="Duvet\nbôa"), False, False, 0)
        player.pack_start(Gtk.Label(label="⏮  ⏸  ⏭"), True, True, 0)
        player.pack_end(Gtk.Label(label="0:10 ━━━━━━━ 3:23"), False, False, 0)


if __name__ == "__main__":
    win = MusicWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
