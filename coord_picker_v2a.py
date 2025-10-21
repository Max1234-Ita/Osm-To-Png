
import math
import sys
import tkinter as tk
import webbrowser
import requests
import markdown
from tkhtmlview import HTMLLabel
from pathlib import Path
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView

import globals
from settings_form import SettingsForm
from inifile_access import IniManager


LANG = 'ita'
LANG_SHORT = 'it'
CONFIG_FILE = "config.ini"
CONFIG_SECTION = "coord_picker"
TILE_DL_SECTION = "tile_download"
configuration = IniManager(CONFIG_FILE)

# ============================
# Available map styles
# ============================
map_styles = globals.map_styles

# ============================
# UI localization
# ============================
def load_ui_strings(lang_code="ita"):
    """
    Loads the User Interface strings from the corresponding .ini file (ui_eng.ini, ui_ita.ini, etc.
    :param lang_code:   Language code, i.e. eng for English, ita for Italian.
                        A file ui_{lang_code}.ini must exist in lang directory
    :return:            The UI strings for the Main and Settings form, as list
    """
    ui_file = Path('lang') / f"ui_{lang_code}.ini"

    try:
        ui_config = IniManager(ui_file)
    except Exception:
        print(f"Error while loading file '{ui_file.name}' ")
        sys.exit(-99)

    keys = [
        "window_title", "loading_message", "style_label", "zoom_label",
        "zoom_map_label", "tiles_label", "search_label", "search_button",
        "ok_button", "cancel_button", "osm_attribution", "select_location_title",
        "select_location_prompt", "select_button", "not_found_message",
        "error_message", "help_button", "help_title", "help_file",
        "preview_button"
    ]
    setting_keys = [
        'title', 'font_label', 'apikey_label', 'email_label', 'language_label',
        'ok_button', 'cancel_button', 'restart_message', 'apikey_tooltip',
        'osmmail_tooltip',
    ]
    ui = {k: ui_config.getvalue("user_interface", k, f"[{k}]") for k in keys}
    setting_ui = {k: ui_config.getvalue("settings_form", k, f"[{k}]") for k in setting_keys}
    return ui, setting_ui


# ============================
# Main Class
# ============================
class _MapViewerBBox(tk.Tk):
    def __init__(self):
        global LANG, LANG_SHORT
        super().__init__()
        self.selection = None
        self.tile_preview_minimap = None
        self.help_window = None
        self._prev_position = (0, 0)
        self.apikey = configuration.getvalue(TILE_DL_SECTION, "apikey")

        # Language & Font
        LANG = configuration.getvalue("general", "language", "ita")
        self.lang_file = Path('lang') / f'ui_{LANG}.ini'
        fontsize = int(configuration.getvalue("general", "fontsize", 14))
        self.ui_configuration = IniManager(self.lang_file)
        self.ui, self.settings_ui = load_ui_strings(LANG)
        LANG_SHORT = self.ui_configuration.getvalue('info', 'lang')
        self.ui_font = ("Arial", fontsize)
        self.small_font = ("Arial", max(8, fontsize - 2))
        self.title(self.ui["window_title"])
        self.set_window_icon(self)

        # Restore initial form geometry
        win_w = configuration.getvalue(CONFIG_SECTION, "win_width")
        win_h = configuration.getvalue(CONFIG_SECTION, "win_height")
        if win_w and win_h:
            try:
                self.geometry(f"{int(win_w)}x{int(win_h)}")
            except Exception:
                self.geometry("950x750")
        else:
            self.geometry("950x750")

        # ===== Top bar (settings & Help buttons) =====
        topbar = tk.Frame(self)
        topbar.pack(fill="x", anchor="ne", padx=10, pady=(5, 2))

        # Current location label (to the left, on top bar)
        self.location_label = ttk.Label(topbar, text="📍 ...", anchor="w")
        self.location_label.pack(side="left", padx=(5, 0))

        # Help button (text == "?")
        help_btn = ttk.Button(topbar, text="?", width=3, command=self.show_help)
        help_btn.pack(side="right", padx=(0, 5))

        # Settings button
        settings_btn = ttk.Button(topbar, text="⚙️", width=3, command=self.open_settings)
        settings_btn.pack(side="right", padx=(0, 5))


        # Map Widget
        self.map_widget = TkinterMapView(
            self,
            width=950,
            height=650,
            corner_radius=0,
            highlightthickness = 1,
            highlightbackground = "#22dd22",
            borderwidth=2
        )
        self.map_widget.pack(fill="both", expand=True)
        self.after(200, self.init_map)
        self.last_center = None
        self.after(300, self.check_map_position)

        # ===== Callback for location update =====
        self.map_widget.add_left_click_map_command(lambda coords: self.update_location_label())
        self.after(1000, self.update_location_label)  # Update on program start

        # User Controls (Style, Tile zoom, etc.
        controls_frame = tk.Frame(self)
        controls_frame.pack(fill="x", pady=4, padx=10)
        tk.Label(controls_frame, text=self.ui["style_label"], font=self.ui_font).pack(side="left")

        # Tile servers (available for selection in dropdown menu)
        self.tile_servers = {
            name: url.replace("{APIKEY}", self.apikey or "")
            for name, url in map_styles.items()
        }
        default_style = "Mapnik (OSM)"
        map_style = configuration.getvalue('tile_download', 'style')
        if not map_style:
            map_style = default_style
        self.selected_style = tk.StringVar(value=map_style)

        style = ttk.Style()
        style.configure("Custom.TMenubutton", font=self.ui_font)
        style.configure("Custom.TButton", font=self.ui_font)

        style_menu = ttk.OptionMenu(controls_frame, self.selected_style, map_style,
                                    *self.tile_servers.keys(), command=self.on_style_change)
        style_menu.pack(side="left", padx=5)
        style_menu.configure(style="Custom.TMenubutton")

        # Tile Zoom entry (with buttons); Retrieve initial values from config.ini
        tk.Label(controls_frame, text=self.ui["zoom_label"], font=self.ui_font).pack(side="left", padx=(20, 0))
        self.zoom_entry = ttk.Entry(controls_frame, width=5, font=self.ui_font, justify="center")
        tilezoom=configuration.getvalue('tile_download', 'zoom')
        self.zoom_entry.insert(0, tilezoom)
        self.zoom_entry.pack(side="left", padx=5)
        ttk.Button(controls_frame, text="-", width=3, command=self.decrement_zoom, style="Custom.TButton").pack(side="left", padx=2)
        ttk.Button(controls_frame, text="+", width=3, command=self.increment_zoom, style="Custom.TButton").pack(side="left", padx=2)
        self.tiles_label = tk.Label(controls_frame, text=f"{self.ui['tiles_label']} n/a", font=self.ui_font)
        self.tiles_label.pack(side="left", padx=(15, 10))

        # Search, Preview & Help
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", pady=4, padx=10)

        tk.Label(search_frame, text=self.ui["search_label"], font=self.ui_font).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30, font=self.ui_font)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_location())

        # Search button
        search_btn = ttk.Button(search_frame, text=self.ui["search_button"], command=self.search_location,
                                style="Custom.TButton")
        search_btn.pack(side="left", padx=5)

        # Preview Tiles button
        self.preview_window = None
        preview_btn = ttk.Button(search_frame, text=self.ui["preview_button"], command=self.show_preview,
                                 style="Custom.TButton")
        preview_btn.pack(side="left", padx=(10, 5))

        # Help button ([ ? ])
        help_btn = ttk.Button(search_frame, text="?", width=3, command=self.show_help, style="Custom.TButton")
        help_btn.pack(side="left", padx=(10, 5))
        self.bind("<F1>", lambda e: self.show_help())

        # OK/Cancel buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=8)
        ttk.Button(btn_frame, text=self.ui["ok_button"], command=self.on_ok, width=12, style="Custom.TButton").pack(side="right", padx=10)
        ttk.Button(btn_frame, text=self.ui["cancel_button"], command=self.on_cancel, width=12, style="Custom.TButton").pack(side="right")

        # Overlay labels (current map zoom and attribution)
        self.zoom_overlay = tk.Label(self.map_widget, text=f"{self.ui['zoom_map_label']} 15",
                                     font=self.small_font, bg="#f0f0f0", anchor="e", relief="flat")
        self.zoom_overlay.place(relx=0.99, rely=0.01, anchor="ne")
        self.osm_overlay = tk.Label(self.map_widget, text=self.ui["osm_attribution"],
                                    font=(self.ui_font[0], max(10, self.ui_font[1] - 2)),
                                    fg="gray30", bg="#f0f0f0", relief="flat", cursor="hand2")
        self.osm_overlay.place(relx=0.99, rely=0.99, anchor="se")
        self.osm_overlay.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.openstreetmap.org/copyright"))

        # # ===== Scale meter bar =====
        # self.scale_bar = tk.Label(self.map_widget, text="", bg="#0000aa",
        #     fg="white", font=(self.ui_font[0], max(10, self.ui_font[1] - 2)), padx=6, pady=2)
        # self.scale_bar.place(relx=0.02, rely=0.96, anchor="sw")  # angolo in basso a sinistra
        # self.scale_bar.lift()

        # Set map view center to saved position
        last_pos = configuration.getvalue(CONFIG_SECTION, "lastposition")
        last_zoom = configuration.getvalue(CONFIG_SECTION, "lastzoom")
        self.start_pos = (41.9028, 12.4964)
        self.start_zoom = int(last_zoom or 15)
        if last_pos:
            try:
                lat, lon = map(float, last_pos.split(","))
                self.start_pos = (lat, lon)
            except Exception:
                pass
        self.start_location_updates()

    def _save_settings(self, returninfo=None):
        if not returninfo:
            returninfo = self._get_return_info()
        center_lat = str(returninfo[5][0])
        center_lon = str(returninfo[5][1])
        zoom_val_map = str(returninfo[4])
        zoom_val_entry = str(returninfo[3])
        configuration.setvalue(CONFIG_SECTION, "lastposition", f"{center_lat},{center_lon}")
        configuration.setvalue(CONFIG_SECTION, "lastzoom", zoom_val_map)
        configuration.setvalue(CONFIG_SECTION, "win_width", self.winfo_width())
        configuration.setvalue(CONFIG_SECTION, "win_height", self.winfo_height())
        configuration.setvalue(TILE_DL_SECTION, "zoom", zoom_val_entry)
        style_name = self.selected_style.get()
        configuration.setvalue(TILE_DL_SECTION, "style", style_name)

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

    # ========== Preview ==========
    def show_preview(self):
        """Opens a minimap showing a preview of the tile details set in the Tile Zoom control."""
        def _on_close():
            # Destroy the minimap viewer if the Close button is clicked
            self.preview_window = None
            self.tile_preview_minimap = None
            popup.destroy()

        try:
            lat, lon = self.map_widget.get_position()
            zoom_target = int(self.zoom_entry.get() or 15)
            style_name = self.selected_style.get()
            tile_server = self.tile_servers.get(style_name, list(self.tile_servers.values())[0])

            if self.preview_window and tk.Toplevel.winfo_exists(self.preview_window):
                # Update the minimap, if it already exists
                self.tile_preview_minimap.set_tile_server(tile_server)
                self.tile_preview_minimap.set_position(lat, lon)
                self.tile_preview_minimap.set_zoom(zoom_target)
                return
            else:
                # Create a new popup (always in foreground)
                main_w, main_h = self.winfo_width(), self.winfo_height()
                preview_w, preview_h = max(400, main_w // 2), max(300, main_h // 2)

                popup = tk.Toplevel(self)
                popup.title(self.ui.get("preview_button", "Preview"))
                popup.geometry(f"{preview_w}x{preview_h}")
                popup.attributes("-topmost", True)
                popup.lift()
                popup.focus_force()
                # -----------------------------------------------------

                self.preview_window = popup

                mini_map = TkinterMapView(popup, width=preview_w, height=preview_h, corner_radius=0)
                mini_map.pack(fill="both", expand=True)
                mini_map.set_tile_server(tile_server)
                mini_map.set_position(lat, lon)
                mini_map.set_zoom(zoom_target)
                self.tile_preview_minimap = mini_map

                # Set the reference to be destroyed when minimap is closed
                popup.protocol("WM_DELETE_WINDOW", _on_close)

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile mostrare l'anteprima:\n{e}")

    # ----- Metodi -----
    def show_help(self):
        """Show the Help Window."""
        def _on_close():
            self.help_window.destroy()
            self.help_window = None

        if hasattr(self, "help_window") and self.help_window and tk.Toplevel.winfo_exists(self.help_window):
            try:
                self.help_window.lift()
                self.help_window.focus_force()
                return
            except Exception:
                pass

        self.help_window = tk.Toplevel(self)
        self.help_window.title(self.ui["help_title"])
        self.help_window.geometry("640x480")
        self.help_window.attributes("-topmost", True)

        # Load the Help file, based on selected language (if not found, use the English help)
        help_file = self.ui.get("help_file", "help/help_eng.md")
        content = f"<h3>File *'{Path(help_file).resolve()}'* not found.</h3>"
        try:
            with open(Path(help_file).resolve(), "r", encoding="utf-8") as f:
                content = f.read()
                # Convert markdown to HTML before displaying the contents
                if help_file.lower().endswith(".md"):
                    try:
                        html_content = markdown.markdown(
                            content,
                            extensions=["tables", "fenced_code", "toc"]
                        )
                    except ImportError:
                        # Markdown not installed
                        print('Markdown module not present, please install it. Help will be shown as basic Text.')
                        html_content = "<pre>" + content + "</pre>"
                else:
                    html_content = content
        except FileNotFoundError:
            html_content = content

        # Show the text in window
        html_label = HTMLLabel(self.help_window, html=html_content, background="white")
        html_label.pack(fill="both", expand=True)

        self.help_window.protocol("WM_DELETE_WINDOW", _on_close)



    def get_nearest_place_name(self, lat, lon, email=None, language="it"):
        """
        Do some Reverse-Geocoding.
        Uses Nominatim to retrieve the name od the nearest city/village,
        :return     Place name, Region, Country
        """
        errmessage = self.ui_configuration.getvalue('user_interface', 'geocoding_failed', 'Unknown locality')
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 10,  # OSM Admin Level. See https://wiki.openstreetmap.org/wiki/Key:admin_level for more info
                "addressdetails": 1,
                "accept-language": language
            }
            headers = {
                "User-Agent": f"CoordPickerApp ({email or 'anonymous'})"
            }
            url = "https://nominatim.openstreetmap.org/reverse"
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            address = data.get("address", {})

            # Get main address parts
            city = (
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    address.get("hamlet") or
                    address.get("municipality")
            )
            region = (
                    address.get("state") or
                    address.get("region") or
                    address.get("county")
            )
            country = address.get("country")

            parts = [p for p in [city, region, country] if p]
            if parts:
                return ", ".join(parts)
            return errmessage

        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return errmessage


    def set_window_icon(self, window):
        """
        Use a custom Icon for the program windows.
        Icon must be a .png or .ico file, in /resources dir.
        """
        try:
            window.iconbitmap(Path('resources') / 'osm2png.ico')  # formato Windows
        except Exception:
            try:
                icon = tk.PhotoImage(file=Path('resources') / "osm2png.png")
                window.iconphoto(False, icon)
            except Exception as e:
                print(f"Impossibile impostare l'icona finestra: {e}")

    def init_map(self):
        # Initialize the map after loading; Set default Zoom & Tile Server
        default_key = self.selected_style.get()
        server_url = self.tile_servers.get(default_key) or next(iter(self.tile_servers.values()))
        self.map_widget.set_tile_server(server_url)
        self.map_widget.set_position(*self.start_pos)
        self.map_widget.set_zoom(self.start_zoom)
        self.after(200, self.update_zoom_label)
        self.after(1000, self.update_tile_estimate)
        self.lift_overlays()

    def update_location_label(self):
        """Updates the Place name label"""
        try:
            lat, lon = self.map_widget.get_position()
            email = configuration.getvalue("tile_download", "osm_email", "")
            lang = configuration.getvalue("general", "language", "it")
            place = self.get_nearest_place_name(lat, lon, email,language=LANG_SHORT)
            self.location_label.config(text=f"{place}")
        except Exception as e:
            print(f"Errore aggiornamento località: {e}")
            self.location_label.config(text="...")
        finally:
            # Also update current position in config.ini
            configuration.setvalue('coord_picker', 'lastposition', f'{lat},{lon}')


    def start_location_updates(self):
        # Set auto-update for location label
        self.update_location_label()
        self.after(5000, self.start_location_updates)

    def lift_overlays(self):
        # Keeps overlay text in foreground
        try:
            self.zoom_overlay.lift()
            self.osm_overlay.lift()
        except Exception:
            pass
        self.after(500, self.lift_overlays)

    def on_style_change(self, selected):
        # Update the Tile Preview minimap if the main map is moved
        url = self.tile_servers.get(selected)
        if url:
            self.map_widget.set_tile_server(url)
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            self.show_preview()

    def increment_zoom(self):
        # Increment zoom of downloaded tiles by 1 when the [ + ] button is clicked
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
        # Decrement zoom of downloaded tiles by 1 when the [ - ] button is clicked
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
        self.zoom_overlay.config(text=f"{self.ui['zoom_map_label']} {zoom_mappa}")
        # self.update_scale_bar()
        self.after(200, self.update_zoom_label)

    # def update_scale_bar(self):
    #     """Aggiorna lo scalimetro in base allo zoom attuale e alla latitudine."""
    #     try:
    #         zoom = self.map_widget.zoom
    #         center = self.map_widget.get_position()
    #         lat = center[0]
    #
    #         # Calcolo approssimativo della lunghezza in metri per pixel
    #         meters_per_pixel = 156543.03392 * cos(lat * pi / 180) / (2 ** zoom)
    #         bar_meters = meters_per_pixel * 100  # 100 px di lunghezza barra
    #
    #         # Arrotonda a valori significativi (50, 100, 200, 500, 1000, ecc.)
    #         nice_values = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    #         display_value = min(nice_values, key=lambda x: abs(x - bar_meters))
    #
    #         # Aggiorna testo e ridimensiona
    #         if display_value >= 1000:
    #             text = f"{display_value / 1000:.0f} km"
    #         else:
    #             text = f"{display_value:.0f} m"
    #
    #         self.scale_bar.config(text=text)
    #     except Exception:
    #         pass


    def update_tile_estimate(self):
        # Estimates the number of tiles to download to cover the window area with specified zoom level
        try:
            zoom_current = getattr(self.map_widget, "zoom", 15)
            zoom_target = int(self.zoom_entry.get())
            if not (1 <= zoom_target <= 22):
                raise ValueError

            w = max(1, self.map_widget.winfo_width())
            h = max(1, self.map_widget.winfo_height())
            # Number of horizontal/vertical tiles @ zoom_target factor
            width_tiles = (w / 256.0) * (2 ** (zoom_target - zoom_current))     # TODO - adapt to support 512x512 tiles
            height_tiles = (h / 256.0) * (2 ** (zoom_target - zoom_current))
            total_tiles = math.ceil(abs(width_tiles) * abs(height_tiles))

            # Estimate total download size (average tile size is specified in globals.py)
            size_mb = (total_tiles * globals.tilesize_kb) / 1024.0
            self.tiles_label.config(text=f"{self.ui['tiles_label']} {total_tiles} (~{size_mb:.1f} MB)")
        except Exception:
            self.tiles_label.config(text=f"{self.ui['tiles_label']} n/a")
        finally:
            self.after(1000, self.update_tile_estimate)

    def search_location(self):
        # Uses Nominatim to search for a specified city or village
        query = self.search_entry.get().strip()
        if not query:
            return
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 10}
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": "TkinterMapApp"}, timeout=10)
            data = resp.json()
            if not data:
                messagebox.showinfo(self.ui["search_button"], self.ui["not_found_message"])
                return
            if len(data) == 1:
                lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
                self.center_map(lat, lon)
            else:
                self.select_from_multiple(data)
        except Exception as e:
            messagebox.showerror(self.ui["search_button"], f"{self.ui['error_message']} {e}")

    def open_settings(self):
        """Open the Settings form"""
        SettingsForm(self, self.settings_ui, CONFIG_FILE)

    def center_map(self, lat, lon):
        # Center map view on specified coordinates
        cur_zoom = getattr(self.map_widget, "zoom", 15)
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(cur_zoom)

    def select_from_multiple(self, results):
        # Allows to select location from a list
        popup = tk.Toplevel(self)
        popup.title(self.ui["select_location_title"])
        popup.geometry("480x320")
        popup.minsize(480, 320)
        tk.Label(popup, text=self.ui["select_location_prompt"], font=self.ui_font).pack(pady=5)

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

        ttk.Button(popup, text=self.ui["select_button"], command=select_location, style="Custom.TButton").pack(pady=5)
        listbox.bind("<Double-1>", lambda e: select_location())

    def on_ok(self):
        selection = self._get_return_info()
        self.selection = selection
        self._save_settings(selection)
        self.destroy()

    def check_map_position(self):
        """Checks if main map center has been moved"""
        current_center=(0,0)
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
        # repeat every 500 ms
        self.after(500, self.check_map_position)

    def on_map_moved(self, coords):
        """Update the Preview map."""
        if getattr(self, "preview_window", None) and tk.Toplevel.winfo_exists(self.preview_window):
            lat, lon = coords
            try:
                self.tile_preview_minimap.set_position(lat, lon)
                # self.update_scale_bar()
            except Exception:
                pass

    def on_cancel(self):
        self._save_settings()
        self.selection = None
        self.destroy()

    # mercator conversions
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
    print("Risultato:", result)
