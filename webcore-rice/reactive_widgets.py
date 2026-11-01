#!/usr/bin/env python3
import cairo
import math
import random
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk, Pango


FALLBACK_WIDGET_ORIGIN = (1440, 0)
MATRIX_CHARS = "01$GXMZ?/#@_-=+<>"
SIGIL = [
    "G O D $ M A C K // 404",
    "<\\\\====[ WRONGSIDE.NET ]====//>",
    "        /\\        /\\",
    "   ____/  \\__G$__/  \\____",
    "  / __  __/\\____/\\__  __ \\",
    " /_/  \\/  / 404  \\  \\/  \\_\\",
    " \\ \\__/\\_/__NOISE__\\_/\\__/ /",
    "  \\____/  \\/====\\/  \\____/",
    "      /___/ DIALUP \\___\\",
    "    __\\___VOID.EXE___/__",
    "   /_/__SIGNAL_ROT__\\_\\",
    "<<<__________XP//STATIC__________>>>",
]


def run_text(command):
    try:
        return subprocess.check_output(
            command,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=1.2,
        ).strip()
    except Exception:
        return "n/a"


def connected_monitors():
    output = run_text("xrandr --query")
    monitors = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 3 or parts[1] != "connected":
            continue
        for part in parts[2:]:
            if "x" not in part or "+" not in part:
                continue
            try:
                size, x_pos, y_pos = part.split("+", 2)
                width, height = size.split("x", 1)
                monitors.append(
                    {
                        "name": parts[0],
                        "x": int(x_pos),
                        "y": int(y_pos),
                        "width": int(width),
                        "height": int(height),
                    }
                )
                break
            except ValueError:
                continue
    return monitors


def widget_origin():
    monitors = connected_monitors()
    for monitor in monitors:
        if monitor["name"] == "VGA-1":
            return monitor["x"], monitor["y"]
    if monitors:
        rightmost = max(monitors, key=lambda item: item["x"])
        return rightmost["x"], rightmost["y"]
    return FALLBACK_WIDGET_ORIGIN


def memory_line():
    return run_text("free -h | awk '/Mem:/ {print $3 \" / \" $2}'")


def disk_line():
    return run_text("df -h / | awk 'NR==2 {print $3 \" / \" $2 \" (\" $5 \")\"}'")


def top_lines():
    load = run_text("uptime | sed 's/^.*load average: //; s/, / /g'")
    mem = memory_line()
    temp = run_text("sensors | awk '/Package id 0:/ {gsub(/^\\+/, \"\", $4); print $4; exit}'")
    procs = run_text("ps -eo comm,%cpu,%mem --sort=-%cpu | awk 'NR>1 && NR<8 {printf \"%-13s %5s %5s\\n\", $1, $2, $3}'")
    return "\n".join(
        [
            "[setup]",
            "CPU load  " + load,
            "Memory    " + mem,
            "CPU temp  " + temp,
            "Uptime    " + run_text("uptime -p | sed 's/^up //'"),
            "",
            "process       cpu%  mem%",
            procs,
        ]
    )


def sigil_text():
    host = run_text("hostname")
    return "\n".join(
        SIGIL
        + [
            "",
            "user      carlo@" + host,
            "kernel    " + run_text("uname -r"),
            "wm        XFCE + WinTC Luna shell",
            "gpu       AMD Cedar / Radeon HD 5000",
            "memory    " + memory_line(),
            "disk      " + disk_line(),
            "uptime    " + run_text("uptime -p | sed 's/^up //'"),
            "sigil     sharp G$ monogram / 404 wrongside net",
            "status    ONLINE READY",
            "C:\\WINDOWS\\system32\\God$mack//404.exe",
        ]
    )


class Widget(Gtk.Window):
    def __init__(self, x, y, w, h, css_class, font_size=10):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        visual = Gdk.Screen.get_default().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_keep_below(True)
        self.stick()
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_default_size(w, h)
        self.move(x, y)

        self.label = Gtk.Label(xalign=0, yalign=0)
        self.label.set_selectable(False)
        self.label.set_line_wrap(False)
        self.label.set_ellipsize(Pango.EllipsizeMode.NONE)
        self.label.set_margin_top(8)
        self.label.set_margin_bottom(8)
        self.label.set_margin_start(10)
        self.label.set_margin_end(10)
        self.label.get_style_context().add_class(css_class)
        self.label.get_style_context().add_class(f"font-{font_size}")
        self.add(self.label)

        self.show_all()
        GLib.idle_add(self.make_click_through)
        GLib.timeout_add(1000, self.keep_down)

    def make_click_through(self):
        window = self.get_window()
        if window:
            window.input_shape_combine_region(cairo.Region(), 0, 0)
        return False

    def keep_down(self):
        self.set_keep_below(True)
        return True


class MatrixWidget(Widget):
    def __init__(self, origin_x, origin_y):
        super().__init__(origin_x + 36, origin_y + 44, 430, 250, "matrix", 10)
        GLib.timeout_add(120, self.tick)
        self.tick()

    def tick(self):
        width = 46
        height = 15
        lines = []
        for _ in range(height):
            line = "".join(random.choice(MATRIX_CHARS + "     ") for _ in range(width))
            lines.append(line)
        self.label.set_text("\n".join(lines))
        return True


class HtopWidget(Widget):
    def __init__(self, origin_x, origin_y):
        super().__init__(origin_x + 38, origin_y + 548, 420, 250, "htop", 10)
        GLib.timeout_add(1500, self.tick)
        self.tick()

    def tick(self):
        self.label.set_text(top_lines())
        return True


class SigilWidget(Widget):
    def __init__(self, origin_x, origin_y):
        super().__init__(origin_x + 560, origin_y + 86, 780, 410, "sigil", 11)
        GLib.timeout_add(2000, self.tick)
        self.tick()

    def tick(self):
        self.label.set_text(sigil_text())
        return True


class VisualizerWidget(Gtk.Window):
    def __init__(self, origin_x, origin_y):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.phase = random.random() * 10.0
        self.frame = 0
        self.width = 920
        self.height = 190
        visual = Gdk.Screen.get_default().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_keep_below(True)
        self.stick()
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_default_size(self.width, self.height)
        self.move(origin_x + 480, origin_y + 622)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(self.width, self.height)
        self.canvas.connect("draw", self.draw)
        self.add(self.canvas)
        self.show_all()
        GLib.idle_add(self.make_click_through)
        GLib.timeout_add(1000, self.keep_down)
        GLib.timeout_add(90, self.tick)

    def make_click_through(self):
        window = self.get_window()
        if window:
            window.input_shape_combine_region(cairo.Region(), 0, 0)
        return False

    def keep_down(self):
        self.set_keep_below(True)
        return True

    def tick(self):
        self.phase += 0.23
        self.frame = (self.frame + 1) % 10000
        self.canvas.queue_draw()
        return True

    def draw(self, _area, cr):
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        width = self.width
        height = self.height
        base_y = height * 0.48
        points = []
        for x in range(0, width, 8):
            t = self.phase + x * 0.014
            signal = math.sin(t) * 0.54
            signal += math.sin(t * 0.47 + self.phase * 0.9) * 0.31
            signal += math.sin(t * 1.73 - self.phase * 0.35) * 0.15
            points.append((x, base_y - signal * 52))

        for offset, alpha, line_width in ((9, 0.20, 10), (0, 0.68, 2.8), (-5, 0.24, 1.6)):
            cr.set_source_rgba(0.42, 1.0, 0.35, alpha)
            cr.set_line_width(line_width)
            cr.move_to(points[0][0], points[0][1] + offset)
            for x, y in points[1:]:
                cr.line_to(x, y + offset)
            cr.stroke()

        bar_count = 64
        bar_gap = 5
        bar_width = (width - bar_gap * (bar_count - 1)) / bar_count
        bottom = height - 18
        for band in range(bar_count):
            t = self.phase * 0.7 + band * 0.34
            value = (math.sin(t) + math.sin(t * 0.43 + 1.7) + 2.0) / 4.0
            value = max(0.0, min(1.0, value + random.uniform(-0.04, 0.04)))
            x = band * (bar_width + bar_gap)
            h = 12 + value * 55
            cr.set_source_rgba(0.58, 0.93, 1.0, 0.24 + value * 0.34)
            cr.rectangle(x, bottom - h, bar_width, h)
            cr.fill()

        cr.select_font_face("Lucida Console", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)
        cr.set_source_rgba(0.0, 0.08, 0.26, 0.70)
        cr.move_to(5, 19)
        cr.show_text("synth://wrongside.net/nohw  56k carrier  clock+sine+noise")
        cr.set_source_rgba(0.86, 1.0, 1.0, 0.72)
        cr.move_to(4, 18)
        cr.show_text("synth://wrongside.net/nohw  56k carrier  clock+sine+noise")
        return False


def main():
    css = b"""
    window { background: transparent; }
    label {
      background: transparent;
      color: rgba(215, 239, 255, 0.64);
      font-family: "Lucida Console", monospace;
      font-size: 10pt;
      font-weight: 700;
      text-shadow: 1px 1px 2px rgba(0, 24, 82, 0.92);
    }
    .font-11 {
      font-size: 11pt;
    }
    .font-9 {
      font-size: 9pt;
    }
    .matrix {
      color: rgba(118, 255, 83, 0.72);
      background: transparent;
    }
    .htop {
      color: rgba(255, 250, 218, 0.88);
      background: transparent;
    }
    .sigil {
      color: rgba(226, 246, 255, 0.86);
      background: transparent;
    }
    .visualizer {
      color: #76ff53;
      background: transparent;
    }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    origin_x, origin_y = widget_origin()
    MatrixWidget(origin_x, origin_y)
    HtopWidget(origin_x, origin_y)
    SigilWidget(origin_x, origin_y)
    VisualizerWidget(origin_x, origin_y)
    Gtk.main()


if __name__ == "__main__":
    main()
