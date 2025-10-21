
import tkinter as tk
from tkinter import ttk, messagebox
from inifile_access import IniManager
from tooltip import ToolTip

class SettingsForm(tk.Toplevel):
    def __init__(self, master, ui_strings, config_path="config.ini"):
        # [+] and [-] buttons
        def dec_font():
            try:
                val = int(self.fontsize.get())
                if val > 8:
                    self.fontsize.set(str(val - 1))
            except ValueError:
                self.fontsize.set("14")

        def inc_font():
            try:
                val = int(self.fontsize.get())
                if val < 48:
                    self.fontsize.set(str(val + 1))
            except ValueError:
                self.fontsize.set("14")

        super().__init__(master)
        self.ui = ui_strings
        form_title = self.ui.get("title", "Settings")  # fallback di sicurezza
        self.title(form_title)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Window settings
        self.transient(master)   # Connect window to parent
        self.grab_set()          # Capture input from main window
        self.focus_force()       # force focus and window to foreground
        self.lift()

        width, height = 360, 180
        self.update_idletasks()

        # Get coordinates of main window
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_w = master.winfo_width()
        master_h = master.winfo_height()

        # Get map center
        x = master_x + (master_w // 2) - (width // 2)
        y = master_y + (master_h // 2) - (height // 2)

        # Set Window geometry and Icon
        self.geometry(f"{width}x{height}+{x}+{y}")
        try:
            master.set_window_icon(self)
        except Exception:
            pass

        self.ui = ui_strings
        self.config = IniManager(config_path)

        # Get current values
        self.fontsize = tk.StringVar(value=self.config.getvalue("general", "fontsize", "14"))
        self.apikey = tk.StringVar(value=self.config.getvalue("tile_download", "apikey", ""))
        self.email = tk.StringVar(value=self.config.getvalue("tile_download", "osm_email", ""))
        self.language = tk.StringVar(value=self.config.getvalue("general", "language", "ita"))

        # ===== UI Layout =====
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Font size
        font_frame = ttk.Frame(frm)
        font_frame.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text=self.ui["font_label"]).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frm, textvariable=self.fontsize, width=4, justify="center").grid(row=0, column=1, sticky="w", pady=5)
        ttk.Button(font_frame, text="-", width=3, command=dec_font).pack(side="left", padx=(40, 1))
        ttk.Button(font_frame, text="+", width=3, command=inc_font).pack(side="left", padx=(1, 4))

        # ===== API Key =====
        ttk.Label(frm, text=self.ui["apikey_label"]).grid(row=1, column=0, sticky="w", pady=4)
        api_entry = ttk.Entry(frm, textvariable=self.apikey, width=35)
        api_entry.grid(row=1, column=1, sticky="ew", pady=4)
        ToolTip(api_entry, ui_strings['apikey_tooltip'])

        # Email
        ttk.Label(frm, text=self.ui["email_label"]).grid(row=2, column=0, sticky="w", pady=4)
        email_entry = ttk.Entry(frm, textvariable=self.email, width=35)
        email_entry.grid(row=2, column=1, sticky="ew", pady=4)
        ToolTip(email_entry, ui_strings["osmmail_tooltip"])

        # Language
        ttk.Label(frm, text=self.ui["language_label"], justify="center").grid(row=3, column=0, sticky="w", pady=5)
        lang_combo = ttk.Combobox(frm, textvariable=self.language, values=["ita", "eng"], width=4, state="readonly")
        lang_combo.grid(row=3, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        ttk.Button(btn_frame, text=self.ui["ok_button"], command=self.save_settings, width=10).pack(side="right", padx=8)
        ttk.Button(btn_frame, text=self.ui["cancel_button"], command=self.destroy, width=10).pack(side="right")

        for i in range(2):
            frm.columnconfigure(i, weight=1)


    def save_settings(self):
        """Save to config.ini and recommend program restart"""
        try:
            self.config.setvalue("general", "fontsize", self.fontsize.get())
            self.config.setvalue("general", "language", self.language.get())
            self.config.setvalue("tile_download", "apikey", self.apikey.get())
            self.config.setvalue("tile_download", "osm_email", self.email.get())
            messagebox.showinfo(
                self.ui["title"],
                self.ui.get("restart_message", "")
            )
        except Exception as e:
            msg = self.config.getvalue('settings_form', 'save_error')
            messagebox.showerror(self.ui["title"], f"{msg}:\n{e}")
        self.destroy()
