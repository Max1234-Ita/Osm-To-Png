#!/usr/bin/env python3
"""
coord_picker_v2a.py
Main application module (map viewer / bbox selector).

Key points:
- Uses a single shared IniManager instance (configuration).
- Passes shared configuration into SettingsForm so settings changes are applied immediately.
- Provides apply_runtime_settings() that the SettingsForm calls after saving (to update API key, tile server URLs, fonts, etc.).
- Default UI language file is ui_english.ini if config missing or invalid.
"""

import math
import sys
import tkinter as tk
import webbrowser
import requests
from pathlib import Path
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView

import globals
import lat_lon_tileid
import settings_form
from inifile_access import IniManager
from help_window import HelpWindow
from utils import is_hex, is_email

# Default UI filename used when config does not specify a language file
DEFAULT_LANG_UI_FILE = "ui_english.ini"
CONFIG_FILE = "config.ini"
CONFIG_SECTION = "coord_picker"
TILE_DL_SECTION = "tile_download"

# Shared configuration instance
configuration = IniManager(CONFIG_FILE)
# Expose to settings_form module if some parts still reference it
settings_form.shared_configuration = configuration

# Map styles
map_styles = globals.map_styles


def _resolve_lang_filename(config_value: str) -> str:
    """
    Accepts either a filename (ui_*.ini) or a short code (e.g. 'eng', 'ita')
    and returns the appropriate filename (ui_*.ini). If input is empty, returns default.
    """
    if not config_value:
        return DEFAULT_LANG_UI_FILE
    cfg = str(config_value).strip()
    if cfg.lower().endswith(".ini") and cfg.lower().startswith("ui_"):
        return cfg
    simple = cfg.lower()
    return f"ui_{simple}.ini"


def load_ui_strings(lang_ui_filename: str = DEFAULT_LANG_UI_FILE):
    """
    Loads UI strings using IniManager from ./lang/<lang_ui_filename>.
    On failure shows an English error and exits.
    """
    lang_path = Path("lang") / lang_ui_filename
    if not lang_path.exists():
        messagebox.showerror(
            "Error",
            f"Unable to find language file: please ensure '/lang' contains '{lang_ui_filename}' or reinstall the application."
        )
        sys.exit(-1)

    try:
        ui_config = IniManager(lang_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading language file '{lang_ui_filename}':\n{e}")
        sys.exit(-2)

    ui_keys = ui_config.getkeys("user_interface")
    setting_keys = ui_config.getkeys("settings_form")
    ui = {k: ui_config.getvalue("user_interface", k, f"[{k}]") for k in ui_keys}
    setting_ui = {k: ui_config.getvalue("settings_form", k, f"[{k}]") for k in setting_keys}
    return ui, setting_ui, ui_config


class _MapViewerBBox(tk.Tk):
    def __init__(self):
        super().__init__()

        self.selection = None
        self.tile_preview_minimap = None
        self.help_window = None
        self._prev_position = (0, 0)
        self.preview_window = None
        self.preview_zoom_label = None
        self.help_file = None

        # Read API and first_run flag from shared configuration
        self.config = configuration  # shared instance
        self.apikey = self.config.getvalue(TILE_DL_SECTION, "apikey", "")
        self.first_run = self.config.getvalue(TILE_DL_SECTION, "savedir", "") == ""

        # Hide while initializing
        self.withdraw()

        # Geometry & layout basics
        self.grid_rowconfigure(4, minsize=60)
        self.grid_columnconfigure(0, weight=1)
        self.minsize(800, 500)

        # Restore geometry
        win_w = self.config.getvalue(CONFIG_SECTION, "win_width", "")
        win_h = self.config.getvalue(CONFIG_SECTION, "win_height", "")
        try:
            if win_w and win_h:
                self.geometry(f"{int(win_w)}x{int(win_h)}")
            else:
                self.geometry("950x750")
        except Exception:
            self.geometry("950x750")
        self._center_window()

        # Load UI language file (config may contain filename or code)
        cfg_lang_value = self.config.getvalue("general", "language", DEFAULT_LANG_UI_FILE)
        lang_ui_file = _resolve_lang_filename(cfg_lang_value)
        self.lang_file = Path("lang") / lang_ui_file

        if not self.lang_file.exists():
            messagebox.showerror(
                "Error",
                f"Unable to find language file: please ensure '/lang' contains '{lang_ui_file}' or reinstall the application."
            )
            self.destroy()
            sys.exit(1)

        self.ui, self.settings_ui, self.ui_configuration = load_ui_strings(lang_ui_file)

        # Determine short language code (info -> lang)
        self.lang_short = self.ui_configuration.getvalue("info", "lang", "en")

        # Fonts
        fontsize = int(self.config.getvalue("general", "fontsize", 14))
        self.ui_font = ("Arial", fontsize)
        self.small_font = ("Arial", max(8, fontsize - 2))

        # Title & icon
        self.title(self.ui.get("window_title", "Map Viewer"))
        self.set_window_icon(self)

        # Top bar
        topbar = tk.Frame(self)
        topbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 2))
        self.location_label = ttk.Label(topbar, text="📍 ...", anchor="w")
        self.location_label.pack(side="left", padx=(5, 0))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.minsize(950, 650)

        help_btn = ttk.Button(topbar, text="?", width=3, command=self.show_help)
        help_btn.pack(side="right", padx=(0, 5))
        settings_btn = ttk.Button(topbar, text="⚙️", width=3, command=self.open_settings)
        settings_btn.pack(side="right", padx=(0, 5))

        # Map widget
        self.map_widget = TkinterMapView(self, corner_radius=0, highlightthickness=1, highlightbackground="#22dd22", borderwidth=2)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        self.after(200, self.init_map)
        self.last_center = None
        self.after(300, self.check_map_position)

        # left click callback
        self.map_widget.add_left_click_map_command(lambda coords: self.update_location_label())
        self.after(1000, self.update_location_label)

        # Controls
        controls_frame = tk.Frame(self)
        controls_frame.grid(row=2, column=0, sticky="ew", pady=4, padx=10)
        tk.Label(controls_frame, text=f'{self.ui.get("style_label", "Style")}:', font=self.ui_font).pack(side="left")

        # Prepare tile servers mapping (apply API key)
        self._rebuild_tile_servers()

        default_style = "Mapnik (OSM)"
        map_style = self.config.getvalue(TILE_DL_SECTION, "style", default_style)
        self.selected_style = tk.StringVar(value=map_style)

        style = ttk.Style()
        style.configure("Custom.TMenubutton", font=self.ui_font)
        style.configure("Custom.TButton", font=self.ui_font)

        style_menu = ttk.OptionMenu(controls_frame, self.selected_style, map_style, *self.tile_servers.keys(), command=self.on_style_change)
        style_menu.pack(side="left", padx=5)
        style_menu.configure(style="Custom.TMenubutton")

        # Tile zoom entry
        tk.Label(controls_frame, text=f'{self.ui.get("zoom_label", "Tile zoom")}:', font=self.ui_font).pack(side="left", padx=(20, 0))
        self.zoom_entry = ttk.Entry(controls_frame, width=5, font=self.ui_font, justify="center")
        self.tilezoom = self.config.getvalue(TILE_DL_SECTION, "zoom", "")
        self.zoom_entry.insert(0, self.tilezoom)
        self.zoom_entry.pack(side="left", padx=5)
        ttk.Button(controls_frame, text="-", width=3, command=self.decrement_zoom, style="Custom.TButton").pack(side="left", padx=2)
        ttk.Button(controls_frame, text="+", width=3, command=self.increment_zoom, style="Custom.TButton").pack(side="left", padx=2)
        self.tiles_label = tk.Label(controls_frame, text=f"{self.ui.get('tiles_label', 'Tiles')}: n/a", font=self.ui_font)
        self.tiles_label.pack(side="left", padx=(15, 10))

        # Search & preview
        search_frame = tk.Frame(self)
        search_frame.grid(row=3, column=0, sticky="ew", pady=4, padx=10)
        tk.Label(search_frame, text=f'{self.ui.get("search_label", "Search")}:', font=self.ui_font).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30, font=self.ui_font)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_location())

        search_btn = ttk.Button(search_frame, text=self.ui.get("search_button", "Search"), command=self.search_location, style="Custom.TButton")
        search_btn.pack(side="left", padx=5)
        preview_btn = ttk.Button(search_frame, text=self.ui.get("preview_button", "Preview"), command=self.show_preview, style="Custom.TButton")
        preview_btn.pack(side="left", padx=(10, 5))

        # OK/Cancel
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, sticky="ew", pady=8)
        ttk.Button(btn_frame, text=self.ui.get("ok_button", "OK"), command=self.on_ok, width=12, style="Custom.TButton").pack(side="right", padx=10)
        ttk.Button(btn_frame, text=self.ui.get("cancel_button", "Cancel"), command=self.on_cancel, width=12, style="Custom.TButton").pack(side="right")

        # Overlays
        self.zoom_overlay = tk.Label(self.map_widget, text=f"{self.ui.get('zoom_map_label','Zoom')}: 15", font=self.small_font, bg="#f0f0f0", anchor="e", relief="flat")
        self.zoom_overlay.place(relx=0.99, rely=0.01, anchor="ne")
        self.osm_overlay = tk.Label(self.map_widget, text=self.ui.get("osm_attribution", "© OSM"), font=(self.ui_font[0], max(10, self.ui_font[1] - 2)), fg="gray30", bg="#f0f0f0", relief="flat", cursor="hand2")
        self.osm_overlay.place(relx=0.99, rely=0.99, anchor="se")
        self.osm_overlay.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.openstreetmap.org/copyright"))

        self._center_window()

        # Restore start pos/zoom
        last_pos = self.config.getvalue(CONFIG_SECTION, "lastposition", "")
        last_zoom = self.config.getvalue(CONFIG_SECTION, "lastzoom", "")
        self.start_pos = (41.9028, 12.4964)
        self.start_zoom = int(last_zoom or 15)
        if last_pos:
            try:
                lat, lon = map(float, last_pos.split(","))
                self.start_pos = (lat, lon)
            except Exception:
                pass

        self.start_location_updates()
        self.deiconify()

        if self.first_run:
            self.show_help()
            # Open settings passing the shared config and a callback to apply runtime changes
            self.open_settings()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------
    # Runtime settings application
    # ---------------------------
    def apply_runtime_settings(self):
        """
        Called after settings are saved. Update runtime values which don't require restart:
        - API key (update tile_servers)
        - Font sizes (update some widgets)
        - Any other runtime values we want to refresh immediately
        """
        try:
            # Re-read values from the shared configuration instance
            self.apikey = self.config.getvalue(TILE_DL_SECTION, "apikey", "")
            fontsize = int(self.config.getvalue("general", "fontsize", 14))
            self.ui_font = ("Arial", fontsize)
            self.small_font = ("Arial", max(8, fontsize - 2))

            # Rebuild tile servers to apply new API key
            self._rebuild_tile_servers()

            # If current selected style still exists, re-apply it's tile server
            current_style = self.selected_style.get()
            url = self.tile_servers.get(current_style)
            if url:
                try:
                    self.map_widget.set_tile_server(url)
                except Exception:
                    pass

            # Update fonts on a small selection of widgets (best-effort)
            try:
                # labels that are easy to update
                self.location_label.config(font=self.ui_font)
                self.tiles_label.config(font=self.ui_font)
                self.zoom_overlay.config(font=self.small_font)
                self.osm_overlay.config(font=(self.ui_font[0], max(10, self.ui_font[1] - 2)))
            except Exception:
                pass

        except Exception as e:
            print(f"apply_runtime_settings error: {e}")

    def _rebuild_tile_servers(self):
        """Rebuild the tile_servers mapping substituting {APIKEY} with the current key."""
        self.tile_servers = {
            name: url.replace("{APIKEY}", (self.apikey or ""))
            for name, url in map_styles.items()
        }

    # ---------------------------
    # Window utilities & persistence
    # ---------------------------
    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _save_settings(self, returninfo=None):
        if not returninfo:
            returninfo = self._get_return_info()
        center_lat = str(returninfo[5][0])
        center_lon = str(returninfo[5][1])
        zoom_val_map = str(returninfo[4])
        zoom_val_entry = str(returninfo[3])
        self.config.setvalue(CONFIG_SECTION, "lastposition", f"{center_lat},{center_lon}")
        self.config.setvalue(CONFIG_SECTION, "lastzoom", zoom_val_map)
        self.config.setvalue(CONFIG_SECTION, "win_width", self.winfo_width())
        self.config.setvalue(CONFIG_SECTION, "win_height", self.winfo_height())
        self.config.setvalue(TILE_DL_SECTION, "zoom", zoom_val_entry)
        style_name = self.selected_style.get()
        self.config.setvalue(TILE_DL_SECTION, "style", style_name)
        # Persist
        if hasattr(self.config, "write"):
            try:
                self.config.write()
            except Exception:
                if hasattr(self.config, "save"):
                    self.config.save()
        elif hasattr(self.config, "save"):
            self.config.save()

    def _get_return_info(self):
        center_lat, center_lon = self.map_widget.get_position()
        zoom_val_map = getattr(self.map_widget, "zoom", 15)
        zoom_map = round(float(zoom_val_map))
        try:
            zoom_val_entry = self.zoom_entry.get()
            zoom_entry = round(float(zoom_val_entry))
        except Exception:
            zoom_entry = 15

        w, h = self.map_widget.winfo_width(), self.map_widget.winfo_height()
        cx, cy = self.latlon_to_pixels(center_lat, center_lon, zoom_val_map)
        half_w, half_h = w / 2.0, h / 2.0
        tl_x, tl_y = cx - half_w, cy - half_h
        br_x, br_y = cx + half_w, cy + half_h
        tl_lat, tl_lon = self.pixels_to_latlon(tl_x, tl_y, zoom_map)
        br_lat, br_lon = self.pixels_to_latlon(br_x, br_y, zoom_map)
        top_lat, bottom_lat = max(tl_lat, br_lat), min(tl_lat, br_lat)
        left_lon, right_lon = min(tl_lon, br_lon), max(tl_lon, br_lon)

        style_name = self.selected_style.get()
        return_info = [
            (top_lat, left_lon),
            (bottom_lat, right_lon),
            style_name,
            str(zoom_entry),
            str(zoom_map),
            (center_lat, center_lon),
        ]
        return return_info

    # ---------------------------
    # Tile preview
    # ---------------------------
    def show_preview(self):
        def _on_close():
            self.preview_window = None
            self.tile_preview_minimap = None
            self.preview_zoom_label = None
            popup.destroy()

        try:
            lat, lon = self.map_widget.get_position()
            zoom_target = int(self.zoom_entry.get() or 15)
            style_name = self.selected_style.get()
            tile_server = self.tile_servers.get(style_name, list(self.tile_servers.values())[0])

            if self.preview_window and tk.Toplevel.winfo_exists(self.preview_window):
                self.tile_preview_minimap.set_tile_server(tile_server)
                self.tile_preview_minimap.set_position(lat, lon)
                self.tile_preview_minimap.set_zoom(zoom_target)
                if getattr(self, "preview_zoom_label", None):
                    self.preview_zoom_label.config(text=f"Tile zoom: {zoom_target}")
                return

            main_w, main_h = self.winfo_width(), self.winfo_height()
            preview_w, preview_h = max(400, main_w // 2), max(300, main_h // 2)

            popup = tk.Toplevel(self)
            popup.title(self.ui.get("preview_button", "Preview"))
            popup.geometry(f"{preview_w}x{preview_h}")
            popup.attributes("-topmost", True)
            popup.lift()
            popup.focus_force()
            self.preview_window = popup
            self.set_window_icon(self.preview_window)

            mini_map = TkinterMapView(popup, width=preview_w, height=preview_h, corner_radius=0)
            mini_map.pack(fill="both", expand=True)
            mini_map.set_tile_server(tile_server)
            mini_map.set_position(lat, lon)
            mini_map.set_zoom(zoom_target)
            self.tile_preview_minimap = mini_map

            font_family = self.ui_font[0]
            font_size = max(8, self.ui_font[1] - 2)
            self.preview_zoom_label = tk.Label(mini_map, text=f"Tile zoom: {zoom_target}", bg="#333333", fg="white", font=(font_family, font_size), padx=6, pady=2, relief="ridge", borderwidth=1)
            self.preview_zoom_label.place(relx=0.98, rely=0.02, anchor="ne")
            self.preview_zoom_label.lift()

            self._preview_last_zoom = zoom_target

            def poll_preview_zoom():
                if not (self.preview_window and tk.Toplevel.winfo_exists(self.preview_window)):
                    return
                try:
                    current_zoom = round(mini_map.zoom)
                    if current_zoom != getattr(self, "_preview_last_zoom", None):
                        self._preview_last_zoom = current_zoom
                        if getattr(self, "preview_zoom_label", None):
                            self.preview_zoom_label.config(text=f"Zoom: {current_zoom}")
                        self.zoom_entry.delete(0, "end")
                        self.zoom_entry.insert(0, str(current_zoom))
                except Exception:
                    pass
                self.after(250, poll_preview_zoom)

            poll_preview_zoom()

            def on_main_zoom_change(event=None):
                try:
                    new_zoom = int(self.zoom_entry.get() or 15)
                    if abs(mini_map.zoom - new_zoom) >= 1:
                        mini_map.set_zoom(new_zoom)
                        if getattr(self, "preview_zoom_label", None):
                            self.preview_zoom_label.config(text=f"Zoom: {new_zoom}")
                        self._preview_last_zoom = new_zoom
                except Exception:
                    pass

            self.zoom_entry.bind("<FocusOut>", on_main_zoom_change)
            popup.protocol("WM_DELETE_WINDOW", _on_close)

        except Exception as e:
            messagebox.showerror("Error", f"Preview error:\n{e}")

    # ---------------------------
    # Help
    # ---------------------------
    def show_help(self):
        if hasattr(self, "help_window") and self.help_window and tk.Toplevel.winfo_exists(self.help_window):
            try:
                self.help_window.lift()
                self.help_window.focus_force()
                return
            except Exception:
                pass

        try:
            help_file = self.ui_configuration.getvalue("info", "help_file", "").strip()
            # help_language = self.ui_configuration.getvalue("info", "lang", "en").strip().lower()

            if help_file:
                help_path = Path(f'help/{help_file}').resolve()
                if not help_path.exists():
                    help_path = Path(f'help/help_eng.md').resolve()
            else:
                # Use English by default
                help_path = Path(f'help/help_eng.md').resolve()

            if not help_path.exists():
                messagebox.showerror("Error", f"Help file not found: '{help_path}'.")
                return

            self.help_window = HelpWindow(self, help_file=help_file, title=self.ui.get("help_title", "Help"))
            self.set_window_icon(self.help_window)

        except Exception as e:
            messagebox.showerror("Error", f"Unable to open help window:\n{e}")

    # ---------------------------
    # Reverse geocoding
    # ---------------------------
    def get_nearest_place_name(self, lat, lon, email=None, language="en"):
        errmessage = self.ui_configuration.getvalue('user_interface', 'geocoding_failed', 'Unknown locality')
        try:
            params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "addressdetails": 1, "accept-language": language}
            headers = {"User-Agent": f"CoordPickerApp ({email or 'anonymous'})"}
            url = "https://nominatim.openstreetmap.org/reverse"
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            address = data.get("address", {})

            city = (address.get("city") or address.get("town") or address.get("village") or address.get("hamlet") or address.get("municipality"))
            region = (address.get("state") or address.get("region") or address.get("county"))
            country = address.get("country")
            parts = [p for p in (city, region, country) if p]
            if parts:
                return ", ".join(parts)
            return errmessage

        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return errmessage

    # ---------------------------
    # Other utilities (icons, map init, zoom, search, etc.)
    # ---------------------------

    def set_window_icon(self, window):
        try:
            window.iconbitmap(Path('resources') / globals.APP_ICON_ICO)
        except Exception:
            try:
                icon = tk.PhotoImage(file=Path('resources') / globals.APP_ICON_PNG)
                window.iconphoto(False, icon)
            except Exception as e:
                print(f"Cannot set window icon: {e}")

    def init_map(self):
        try:
            default_key = self.selected_style.get()
            server_url = self.tile_servers.get(default_key) or next(iter(self.tile_servers.values()))
            self.map_widget.set_tile_server(server_url)
            self.map_widget.set_position(*self.start_pos)
            self.map_widget.set_zoom(self.start_zoom)
            self.after(200, self.update_zoom_label)
            self.after(1000, self.update_tile_estimate)
            self.lift_overlays()
        except Exception as e:
            print(f"init_map error: {e}")

    def update_location_label(self):
        try:
            lat, lon = self.map_widget.get_position()
            email = self.config.getvalue(TILE_DL_SECTION, "osm_email", "")
            lang_code = self.ui_configuration.getvalue("info", "lang", "en")
            place = self.get_nearest_place_name(lat, lon, email, language=lang_code)
            self.location_label.config(text=f"{place}")
        except Exception as e:
            print(f"Location update error: {e}")
            self.location_label.config(text="...")
        finally:
            try:
                self.config.setvalue(CONFIG_SECTION, 'lastposition', f'{lat},{lon}')
            except Exception:
                pass

    def start_location_updates(self):
        self.update_location_label()
        self.after(5000, self.start_location_updates)

    def lift_overlays(self):
        try:
            self.zoom_overlay.lift()
            self.osm_overlay.lift()
        except Exception:
            pass
        self.after(500, self.lift_overlays)

    def on_style_change(self, selected):
        url = self.tile_servers.get(selected)
        if url:
            self.map_widget.set_tile_server(url)
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            self.show_preview()

    def increment_zoom(self):
        try:
            val = int(self.zoom_entry.get() or 15)
        except Exception:
            val = 15
        val = min(val + 1, 22)
        self.zoom_entry.delete(0, tk.END)
        self.zoom_entry.insert(0, str(val))
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            self.show_preview()

    def decrement_zoom(self):
        try:
            val = int(self.zoom_entry.get() or 15)
        except Exception:
            val = 15
        val = max(val - 1, 1)
        self.zoom_entry.delete(0, tk.END)
        self.zoom_entry.insert(0, str(val))
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            self.show_preview()

    def update_zoom_label(self):
        zoom_mappa = int(getattr(self.map_widget, "zoom", 15))
        self.zoom_overlay.config(text=f"{self.ui.get('zoom_map_label','Zoom')}: {zoom_mappa}")
        self.after(200, self.update_zoom_label)

    def update_tile_estimate(self):
        try:
            zoom_current = getattr(self.map_widget, "zoom", 15)
            zoom_target = int(self.zoom_entry.get())
            if not (1 <= zoom_target <= 22):
                raise ValueError
            w = max(1, self.map_widget.winfo_width())
            h = max(1, self.map_widget.winfo_height())
            info = self._get_return_info()
            min_xy = lat_lon_tileid.latlon_to_tile(info[0][0], info[0][1], int(info[3]))
            max_xy = lat_lon_tileid.latlon_to_tile(info[1][0], info[1][1], int(info[3]))
            total_tiles = (max_xy[0] - min_xy[0] + 1) * (max_xy[1] - min_xy[1] + 1)
            size_mb = (total_tiles * globals.tilesize_kb) / 1024.0
            self.tiles_label.config(text=f"{self.ui.get('tiles_label','Tiles')}: {total_tiles} (~{size_mb:.1f} MB)")
        except Exception:
            self.tiles_label.config(text=f"{self.ui.get('tiles_label','Tiles')}: n/a")
        finally:
            self.after(1000, self.update_tile_estimate)

    def search_location(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 10}
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": "TkinterMapApp"}, timeout=10)
            data = resp.json()
            if not data:
                messagebox.showinfo(self.ui.get("search_button", "Search"), self.ui.get("not_found_message", "Not found"))
                return
            if len(data) == 1:
                lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
                self.center_map(lat, lon)
            else:
                self.select_from_multiple(data)
        except Exception as e:
            messagebox.showerror(self.ui.get("search_button", "Search"), f"{self.ui.get('error_message','Error')}: {e}")

    def open_settings(self):
        """
        Open SettingsForm, passing the shared configuration and a callback to apply runtime changes.
        """
        # pass shared config and on_change callback
        settings_form.SettingsForm(self, self.settings_ui, config_path=CONFIG_FILE, shared_config=self.config, on_change_callback=self.apply_runtime_settings)

    def center_map(self, lat, lon):
        cur_zoom = getattr(self.map_widget, "zoom", 15)
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(cur_zoom)

    def select_from_multiple(self, results):
        popup = tk.Toplevel(self)
        popup.title(self.ui.get("select_location_title", "Select location"))
        popup.geometry("480x320")
        popup.minsize(480, 320)
        tk.Label(popup, text=f'{self.ui.get("select_location_prompt", "Select")}:', font=self.ui_font).pack(pady=5)
        listbox = tk.Listbox(popup, font=self.ui_font)
        for it in results:
            listbox.insert(tk.END, it.get("display_name", ""))
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        def select_location():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            lat, lon = float(results[idx]["lat"]), float(results[idx]["lon"])
            self.center_map(lat, lon)
            popup.destroy()

        ttk.Button(popup, text=self.ui.get("select_button", "Select"), command=select_location, style="Custom.TButton").pack(pady=5)
        listbox.bind("<Double-1>", lambda e: select_location())

    def on_ok(self):
        """Conferma la selezione bbox e avvia il download, previa validazione dei parametri."""
        try:
            # Check if required email/API/additional info is provided
            style_name = self.selected_style.get()
            osm_email = self.config.getvalue("tile_download", "osm_email", "").strip()
            api_key = self.config.getvalue("tile_download", "apikey", "").strip()

            provider_info = globals.styles_info.get(style_name, None)
            if isinstance(provider_info, list):
                provider_name = provider_info[0].lower()
            else:
                raise NameError

            if provider_name == "openstreetmap":
                # Validate email for OSM tiles
                if not is_email(osm_email):
                    invalid_osm_email_msg = self.ui.get("invalid_osm_email", "Invalid Openstreetmap email.")
                    messagebox.showwarning("", invalid_osm_email_msg)
                    self.open_settings()
                    return

            elif provider_name == "thunderforest":
                # Validate API key for Thunderforest tiles
                if not api_key or not is_hex(api_key):
                    invalid_api_key_msg = self.ui.get("invalid_thunderforest_key", "Invalid Thunderforest API key.")
                    messagebox.showwarning("", invalid_api_key_msg)
                    self.open_settings()
                    return
            else:
                pass    # Case trap - for debug only

            selection = self._get_return_info()
            self.selection = selection
            self._save_settings(selection)
            self.destroy()

        except NameError:
            messagebox.showerror("#Error #", f"Provider info not found for map style {style_name}")
        except Exception as e:
            messagebox.showerror("Errore", f"Error in setting validation :\n{e}")

    def check_map_position(self):
        current_center = (0, 0)
        try:
            current_center = self.map_widget.get_position()
            if self.last_center != current_center:
                self.last_center = current_center
                self.on_map_moved(current_center)
        except Exception:
            pass
        if current_center != self._prev_position:
            print(f'Position: {current_center}')
            self._prev_position = current_center
        self.after(500, self.check_map_position)

    def on_map_moved(self, coords):
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            lat, lon = coords
            try:
                self.tile_preview_minimap.set_position(lat, lon)
            except Exception:
                pass

    def on_cancel(self):
        self._save_settings()
        self.selection = None
        self.destroy()

    def on_close(self):
        try:
            self._save_settings()
        except Exception as e:
            print(f"Error saving config on close: {e}")
        finally:
            self.destroy()

    # Mercator conversions
    def latlon_to_pixels(self, lat, lon, zoom):
        lat_rad = math.radians(lat)
        map_size = 256.0 * (2.0 ** zoom)
        x = (lon + 180.0) / 360.0 * map_size
        y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * map_size
        return x, y

    def pixels_to_latlon(self, x, y, zoom):
        map_size = 256.0 * (2.0 ** zoom)
        lon = x / map_size * 360.0 - 180.0
        n = math.pi - 2.0 * math.pi * y / map_size
        lat = math.degrees(math.atan(math.sinh(n)))
        return lat, lon


def select_bbox():
    app = _MapViewerBBox()
    app.mainloop()
    return app.selection


if __name__ == "__main__":
    result = select_bbox()
    print("Result:", result)
