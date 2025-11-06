"""
coord_picker_bbox_draw_fixed.py

BBox interattivo con rettangolo blu iniziale, centrato sulla mappa,
spostabile e ridimensionabile (minimo 50×50 px).
"""

import math
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from tkintermapview import TkinterMapView
from inifile_access import IniManager
import globals


CONFIG_FILE = "config.ini"
CONFIG_SECTION = "coord_picker"
TILE_DL_SECTION = "tile_download"

try:
    configuration = IniManager(CONFIG_FILE)
except Exception:
    configuration = None


def clamp(n, a, b):
    return max(a, min(b, n))


class _MapViewerBBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coordinate picker – BBox interattivo")
        self.withdraw()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.minsize(800, 520)

        fontsize = int(configuration.getvalue("general", "fontsize", 14)) if configuration else 14
        self.ui_font = ("Arial", fontsize)

        # Topbar
        topbar = tk.Frame(self)
        topbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 3))
        ttk.Label(topbar, text="📍 Seleziona area").pack(side="left", padx=(4, 0))
        ttk.Button(topbar, text="?", width=3, command=lambda: webbrowser.open_new_tab(
            "https://www.openstreetmap.org/copyright")).pack(side="right", padx=(0, 4))

        # Map
        self.map_widget = TkinterMapView(self, corner_radius=0)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        # Overlay per rettangolo
        self.overlay = tk.Canvas(self.map_widget, highlightthickness=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Controls
        controls_frame = tk.Frame(self)
        controls_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        tk.Label(controls_frame, text="Zoom tile:", font=self.ui_font).pack(side="left", padx=(14, 0))
        self.zoom_entry = ttk.Entry(controls_frame, width=5, font=self.ui_font, justify="center")
        self.zoom_entry.insert(0, configuration.getvalue('tile_download', 'zoom') if configuration else "15")
        self.zoom_entry.pack(side="left", padx=6)
        ttk.Button(controls_frame, text="-", width=3, command=self.decrement_zoom).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="+", width=3, command=self.increment_zoom).pack(side="left", padx=2)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(4, 8))
        ttk.Button(btn_frame, text="OK", width=12, command=self.on_ok).pack(side="right", padx=8)
        ttk.Button(btn_frame, text="Annulla", width=12, command=self.on_cancel).pack(side="right")

        self.rect = None
        self.min_size = 50
        self._dragging = False
        self._drag_type = None

        # Caricamento mappa
        self.start_pos = (41.9028, 12.4964)
        self.start_zoom = int(configuration.getvalue(CONFIG_SECTION, "lastzoom", 15)) if configuration else 15
        self.after(300, self._init_map_safe)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.deiconify()

    def _init_map_safe(self):
        """Inizializza la mappa e crea il rettangolo solo quando pronta."""
        try:
            self.map_widget.set_tile_server("https://tile.openstreetmap.org/{z}/{x}/{y}.png")
            self.map_widget.set_position(*self.start_pos)
            self.map_widget.set_zoom(self.start_zoom)
        except Exception:
            self.after(200, self._init_map_safe)
            return

        # Attendi che la mappa abbia dimensioni utili
        if self.map_widget.winfo_width() < 100 or self.map_widget.winfo_height() < 100:
            self.after(200, self._init_map_safe)
            return

        self._init_default_rect()
        self.overlay.bind("<ButtonPress-1>", self._on_canvas_button)
        self.overlay.bind("<B1-Motion>", self._on_canvas_drag)
        self.overlay.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.after(300, self._refresh_overlay)

    # --- Rettangolo interattivo ---
    def _init_default_rect(self):
        w = self.map_widget.winfo_width()
        h = self.map_widget.winfo_height()
        size = 200
        cx, cy = w / 2, h / 2
        self.rect = {
            "left": cx - size / 2,
            "top": cy - size / 2,
            "right": cx + size / 2,
            "bottom": cy + size / 2,
            "handles": {}
        }
        self._draw_selection()

    def _draw_selection(self):
        self.overlay.delete("sel")
        if not self.rect:
            return
        l, t, r, b = self.rect["left"], self.rect["top"], self.rect["right"], self.rect["bottom"]
        self.overlay.create_rectangle(l, t, r, b, outline="#0077ff", width=2, tags="sel")
        hs = 8
        for tag, (hx, hy) in {"nw": (l, t), "ne": (r, t), "sw": (l, b), "se": (r, b)}.items():
            self.overlay.create_rectangle(hx - hs/2, hy - hs/2, hx + hs/2, hy + hs/2,
                                          fill="#ffffff", outline="#333333", tags=("sel", f"handle_{tag}"))

    def _point_on_handle(self, x, y):
        for tag in ("nw", "ne", "sw", "se"):
            c = self.overlay.coords(f"handle_{tag}")
            if c and c[0] <= x <= c[2] and c[1] <= y <= c[3]:
                return tag
        return None

    def _point_in_rect(self, x, y):
        l, t, r, b = self.rect["left"], self.rect["top"], self.rect["right"], self.rect["bottom"]
        return l <= x <= r and t <= y <= b

    def _on_canvas_button(self, e):
        handle = self._point_on_handle(e.x, e.y)
        if handle:
            self._dragging, self._drag_type = True, f"resize-{handle}"
        elif self._point_in_rect(e.x, e.y):
            self._dragging, self._drag_type = True, "move"
            self._orig = (self.rect["left"], self.rect["top"], self.rect["right"], self.rect["bottom"])
        self._start = (e.x, e.y)

    def _on_canvas_drag(self, e):
        if not self._dragging:
            return
        x, y = clamp(e.x, 0, self.overlay.winfo_width()), clamp(e.y, 0, self.overlay.winfo_height())
        if self._drag_type == "move":
            sx, sy = self._start
            dx, dy = x - sx, y - sy
            l0, t0, r0, b0 = self._orig
            w, h = r0 - l0, b0 - t0
            l = clamp(l0 + dx, 0, self.overlay.winfo_width() - w)
            t = clamp(t0 + dy, 0, self.overlay.winfo_height() - h)
            self.rect.update({"left": l, "top": t, "right": l + w, "bottom": t + h})
        elif self._drag_type.startswith("resize-"):
            dir = self._drag_type.split("-", 1)[1]
            l, t, r, b = self.rect["left"], self.rect["top"], self.rect["right"], self.rect["bottom"]
            min_sz = self.min_size
            if dir == "nw":
                l = clamp(x, 0, r - min_sz)
                t = clamp(y, 0, b - min_sz)
            elif dir == "ne":
                r = clamp(x, l + min_sz, self.overlay.winfo_width())
                t = clamp(y, 0, b - min_sz)
            elif dir == "sw":
                l = clamp(x, 0, r - min_sz)
                b = clamp(y, t + min_sz, self.overlay.winfo_height())
            elif dir == "se":
                r = clamp(x, l + min_sz, self.overlay.winfo_width())
                b = clamp(y, t + min_sz, self.overlay.winfo_height())
            self.rect.update({"left": l, "top": t, "right": r, "bottom": b})
        self._draw_selection()

    def _on_canvas_release(self, e):
        self._dragging = False
        self._drag_type = None

    def _refresh_overlay(self):
        self._draw_selection()
        self.after(500, self._refresh_overlay)

    # --- Zoom controls ---
    def increment_zoom(self):
        z = int(self.zoom_entry.get() or 15)
        z = min(z + 1, 22)
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, str(z))

    def decrement_zoom(self):
        z = int(self.zoom_entry.get() or 15)
        z = max(z - 1, 1)
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, str(z))

    # --- Confirm/cancel ---
    def on_ok(self):
        self.selection = self._get_bbox_latlon()
        self.destroy()

    def on_cancel(self):
        self.selection = None
        self.destroy()

    def _get_bbox_latlon(self):
        """Converti rettangolo in coordinate geografiche."""
        left, top, right, bottom = (
            self.rect["left"], self.rect["top"], self.rect["right"], self.rect["bottom"]
        )
        z = getattr(self.map_widget, "zoom", 15)
        c_lat, c_lon = self.map_widget.get_position()
        cx, cy = self.latlon_to_pixels(c_lat, c_lon, z)
        w, h = self.map_widget.winfo_width(), self.map_widget.winfo_height()
        half_w, half_h = w / 2, h / 2
        def px_to_latlon(px, py):
            gx, gy = cx - half_w + px, cy - half_h + py
            return self.pixels_to_latlon(gx, gy, z)
        top_left = px_to_latlon(left, top)
        bottom_right = px_to_latlon(right, bottom)
        return top_left, bottom_right

    # --- Mercator ---
    def latlon_to_pixels(self, lat, lon, zoom):
        lat_rad = math.radians(lat)
        map_size = 256 * (2 ** zoom)
        x = (lon + 180.0) / 360.0 * map_size
        y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * map_size
        return x, y

    def pixels_to_latlon(self, x, y, zoom):
        map_size = 256 * (2 ** zoom)
        lon = x / map_size * 360.0 - 180.0
        n = math.pi - 2.0 * math.pi * y / map_size
        lat = math.degrees(math.atan(math.sinh(n)))
        return lat, lon


def select_bbox():
    app = _MapViewerBBox()
    app.mainloop()
    return app.selection


if __name__ == "__main__":
    print(select_bbox())
