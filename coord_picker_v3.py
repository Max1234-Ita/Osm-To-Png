# #!/usr/bin/env python3
# """
# coord_picker_v3.py
# Interactive map viewer with draggable rectangular overlay for bounding box selection.
# Overlay is implemented as a semi-transparent PNG image placed over the map.
# """
#
# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkintermapview import TkinterMapView
# from pathlib import Path
# import threading
# import requests
# from PIL import Image, ImageTk
# import markdown
# from tkhtmlview import HTMLLabel
# from inifile_access import IniManager
#
#
# class _MapViewerBBox(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.withdraw()  # show only after initialization
#         self.title("Coordinate Picker")
#         self.geometry("1000x700")
#         self.resizable(True, True)
#         self.protocol("WM_DELETE_WINDOW", self._on_cancel)
#
#         # Load config
#         self.config_file = Path("config.ini")
#         self.ini = IniManager(self.config_file)
#         self.language = self.ini.getvalue("general", "language") or "ita"
#         self.fontsize = int(self.ini.getvalue("general", "fontsize") or 14)
#         self.ui = self._load_ui_strings()
#
#         # Map styles
#         self.APIkey = self.ini.getvalue("tile_download", "apikey") or ""
#         self.map_styles = {
#             "Mapnik": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
#             "Cycle": f"https://tile.thunderforest.com/cycle/{{z}}/{{x}}/{{y}}.png?apikey={self.APIkey}",
#             "Transport": f"https://tile.thunderforest.com/transport/{{z}}/{{x}}/{{y}}.png?apikey={self.APIkey}",
#             "Outdoors": f"https://tile.thunderforest.com/outdoors/{{z}}/{{x}}/{{y}}.png?apikey={self.APIkey}",
#             "Landscape": f"https://tile.thunderforest.com/landscape/{{z}}/{{x}}/{{y}}.png?apikey={self.APIkey}",
#             "Atlas": f"https://tile.thunderforest.com/atlas/{{z}}/{{x}}/{{y}}.png?apikey={self.APIkey}"
#         }
#
#         # Layout
#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(1, weight=1)
#
#         self._create_topbar()
#         self._create_mapview()
#         self._create_bottom_bar()
#
#         # Overlay control
#         self.overlay_enabled = False
#         self.overlay_label = None
#         self.overlay_image = None
#         self.drag_data = {"x": 0, "y": 0}
#
#         # Show after initialization
#         self.after(500, self._show_centered)
#
#     # --------------------------------------------------------------------------------------
#     def _load_ui_strings(self):
#         ui_file = Path("lang") / f"ui_{self.language.lower()}.ini"
#         ui_ini = IniManager(ui_file)
#         return ui_ini.getsection("user_interface")
#
#     # --------------------------------------------------------------------------------------
#     def _create_topbar(self):
#         top_frame = ttk.Frame(self)
#         top_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=4)
#         top_frame.columnconfigure(5, weight=1)
#
#         # Map style
#         ttk.Label(top_frame, text=self.ui.get("map_style", "Stile mappa:"), font=("Segoe UI", self.fontsize)).grid(row=0, column=0)
#         self.selected_style = tk.StringVar(value="Mapnik")
#         ttk.Combobox(top_frame, textvariable=self.selected_style, values=list(self.map_styles.keys()), width=15).grid(row=0, column=1, padx=4)
#
#         # Tile zoom
#         ttk.Label(top_frame, text=self.ui.get("tile_zoom", "Zoom tile:"), font=("Segoe UI", self.fontsize)).grid(row=0, column=2, padx=4)
#         self.zoom_entry = ttk.Entry(top_frame, width=4, justify="center")
#         self.zoom_entry.insert(0, "15")
#         self.zoom_entry.grid(row=0, column=3)
#         ttk.Button(top_frame, text="+", width=2, command=lambda: self._adjust_zoom(1)).grid(row=0, column=4)
#         ttk.Button(top_frame, text="-", width=2, command=lambda: self._adjust_zoom(-1)).grid(row=0, column=5)
#
#         # Search
#         self.search_var = tk.StringVar()
#         ttk.Entry(top_frame, textvariable=self.search_var, width=30).grid(row=0, column=6, padx=4)
#         ttk.Button(top_frame, text=self.ui.get("search_button", "Cerca"), command=self._search_location).grid(row=0, column=7)
#         ttk.Button(top_frame, text="?", width=3, command=self._show_help).grid(row=0, column=8, padx=(12, 0))
#
#         # Select Area
#         ttk.Button(top_frame, text=self.ui.get("select_area_button", "🟦 Seleziona area"), command=self._toggle_overlay).grid(row=0, column=9, padx=(20, 0))
#
#         # Preview
#         ttk.Button(top_frame, text=self.ui.get("preview_button", "Anteprima"), command=self._show_preview).grid(row=0, column=10, padx=4)
#
#     # --------------------------------------------------------------------------------------
#     def _create_mapview(self):
#         self.map_frame = ttk.Frame(self)
#         self.map_frame.grid(row=1, column=0, sticky="nsew")
#         self.map_frame.rowconfigure(0, weight=1)
#         self.map_frame.columnconfigure(0, weight=1)
#
#         self.map_widget = TkinterMapView(self.map_frame, width=800, height=600, corner_radius=0)
#         self.map_widget.grid(row=0, column=0, sticky="nsew")
#         self.map_widget.set_tile_server(self.map_styles["Mapnik"])
#         self.map_widget.set_position(41.9028, 12.4964)  # Roma
#         self.map_widget.set_zoom(6)
#
#         # Overlay attribution + zoom label
#         self.attribution_label = tk.Label(self.map_frame, text="© OpenStreetMap Contributors",
#                                           bg="silver", fg="white", font=("Segoe UI", self.fontsize - 2))
#         self.attribution_label.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-6)
#
#         self.zoom_label = tk.Label(self.map_frame, text="Zoom: 6",
#                                    bg="silver", fg="white", font=("Segoe UI", self.fontsize - 2))
#         self.zoom_label.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)
#
#         # Update zoom text
#         def _update_zoom(e=None):
#             z = self.map_widget.get_zoom()
#             self.zoom_label.config(text=f"Zoom: {z}")
#
#         self.map_widget.bind("<ButtonRelease-1>", _update_zoom)
#         self.map_widget.bind("<MouseWheel>", _update_zoom)
#
#     # --------------------------------------------------------------------------------------
#     def _create_bottom_bar(self):
#         bottom = ttk.Frame(self)
#         bottom.grid(row=2, column=0, sticky="ew", padx=10, pady=4)
#         bottom.columnconfigure(2, weight=1)
#
#         ttk.Button(bottom, text=self.ui.get("ok_button", "OK"), command=self._on_ok).pack(side="right", padx=5)
#         ttk.Button(bottom, text=self.ui.get("cancel_button", "Annulla"), command=self._on_cancel).pack(side="right")
#
#         self.tile_label = ttk.Label(bottom, text=self.ui.get("tile_estimate", "Tile stimate: 0"), font=("Segoe UI", self.fontsize))
#         self.tile_label.pack(side="left")
#
#     # --------------------------------------------------------------------------------------
#     def _show_centered(self):
#         """Show window centered after init."""
#         self.update_idletasks()
#         w = self.winfo_width()
#         h = self.winfo_height()
#         x = (self.winfo_screenwidth() // 2) - (w // 2)
#         y = (self.winfo_screenheight() // 2) - (h // 2)
#         self.geometry(f"{w}x{h}+{x}+{y}")
#         self.deiconify()
#
#     # --------------------------------------------------------------------------------------
#     def _toggle_overlay(self):
#         if not self.overlay_enabled:
#             try:
#                 img_path = Path("resources") / "overlay_rect.png"
#                 img = Image.open(img_path).convert("RGBA")
#                 self.overlay_image = ImageTk.PhotoImage(img)
#                 self.overlay_label = tk.Label(self.map_frame, image=self.overlay_image, bg=None, borderwidth=0)
#                 self.overlay_label.place(relx=0.5, rely=0.5, anchor="center")
#                 self.overlay_label.bind("<Button-1>", self._start_drag)
#                 self.overlay_label.bind("<B1-Motion>", self._do_drag)
#                 self.overlay_enabled = True
#             except Exception as e:
#                 messagebox.showerror("Errore", f"Impossibile caricare overlay PNG:\n{e}")
#         else:
#             if self.overlay_label:
#                 self.overlay_label.destroy()
#             self.overlay_label = None
#             self.overlay_enabled = False
#
#     def _start_drag(self, event):
#         self.drag_data["x"] = event.x
#         self.drag_data["y"] = event.y
#
#     def _do_drag(self, event):
#         dx = event.x - self.drag_data["x"]
#         dy = event.y - self.drag_data["y"]
#         x = self.overlay_label.winfo_x() + dx
#         y = self.overlay_label.winfo_y() + dy
#         self.overlay_label.place(x=x, y=y)
#
#     # --------------------------------------------------------------------------------------
#     def _adjust_zoom(self, delta):
#         try:
#             z = int(self.zoom_entry.get())
#             z = max(1, min(22, z + delta))
#             self.zoom_entry.delete(0, tk.END)
#             self.zoom_entry.insert(0, str(z))
#         except ValueError:
#             pass
#
#     # --------------------------------------------------------------------------------------
#     def _show_help(self):
#         help_file = self.ui.get("help_file", "help_it.md")
#         help_path = Path("lang") / help_file
#         if not help_path.exists():
#             messagebox.showerror("Errore", f"File di aiuto mancante:\n{help_path}")
#             return
#
#         top = tk.Toplevel(self)
#         top.title(self.ui.get("help_title", "Guida"))
#         top.geometry("700x500")
#         top.attributes("-topmost", True)
#
#         with open(help_path, "r", encoding="utf-8") as f:
#             html_content = markdown.markdown(f.read())
#
#         html_view = HTMLLabel(top, html=html_content, background="white", width=100)
#         html_view.pack(fill="both", expand=True)
#
#     # --------------------------------------------------------------------------------------
#     def _search_location(self):
#         query = self.search_var.get().strip()
#         if not query:
#             return
#         threading.Thread(target=self._do_search, args=(query,), daemon=True).start()
#
#     def _do_search(self, query):
#         try:
#             url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
#             headers = {"User-Agent": "PyOSM"}
#             resp = requests.get(url, headers=headers, timeout=10)
#             data = resp.json()
#             if not data:
#                 messagebox.showinfo("Ricerca", "Nessun risultato trovato.")
#                 return
#             lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
#             self.map_widget.set_position(lat, lon)
#         except Exception as e:
#             messagebox.showerror("Errore ricerca", str(e))
#
#     # --------------------------------------------------------------------------------------
#     def _show_preview(self):
#         try:
#             lat, lon = self.map_widget.get_position()
#             zoom = int(self.zoom_entry.get())
#             style = self.selected_style.get()
#             tile_url = self.map_styles[style]
#
#             popup = tk.Toplevel(self)
#             popup.title(self.ui.get("preview_button", "Anteprima"))
#             popup.geometry("400x300")
#             popup.attributes("-topmost", True)
#
#             preview_map = TkinterMapView(popup, width=400, height=300, corner_radius=0)
#             preview_map.pack(fill="both", expand=True)
#             preview_map.set_tile_server(tile_url)
#             preview_map.set_position(lat, lon)
#             preview_map.set_zoom(zoom)
#         except Exception as e:
#             messagebox.showerror("Errore", f"Impossibile mostrare anteprima:\n{e}")
#
#     # --------------------------------------------------------------------------------------
#     def _on_ok(self):
#         lat, lon = self.map_widget.get_position()
#         zoom = self.map_widget.get_zoom()
#         style = self.selected_style.get()
#         self.result = [(lat, lon), (lat, lon), style, zoom]
#         self.destroy()
#
#     def _on_cancel(self):
#         self.result = None
#         self.destroy()
#
#
# # ====================================================================================================
# def select_bbox():
#     app = _MapViewerBBox()
#     app.mainloop()
#     return getattr(app, "result", None)
