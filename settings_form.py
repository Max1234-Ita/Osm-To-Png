#!/usr/bin/env python3
"""
settings_form.py
Manages the application's settings window.

Features:
- Scans ./lang for ui_*.ini files and reads [info] -> language as display name.
- Presents a combobox with language full names and saves the selected *filename*
  (e.g. ui_english.ini) into config.ini [general]->language.
- Accepts a shared IniManager instance (shared_config) so that changes are applied
  immediately to the same in-memory config used by the main app.
- Accepts an optional on_change_callback(master) which is called after settings are written.
- Window is modal for 1 second, then released. On OK the window is destroyed, then
  the change callback is run (via master.after) and finally an info box is shown.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import configparser
from inifile_access import IniManager
from tooltip import ToolTip


DEFAULT_UI_FILENAME = "ui_english.ini"


class SettingsForm(tk.Toplevel):
    def __init__(self, master, ui_strings, config_path="config.ini", shared_config: IniManager = None, on_change_callback=None):
        """
        :param master: parent window
        :param ui_strings: dictionary with UI strings (from loaded UI file)
        :param config_path: path to config.ini (used only if shared_config is None)
        :param shared_config: optional IniManager instance to share with caller
        :param on_change_callback: optional callback function to call after save (signature: callback())
        """
        # inner helpers for + / - font buttons
        def dec_font():
            try:
                val = int(self.fontsize.get())
                if val > 8:
                    self.fontsize.set(str(val - 1))
            except Exception:
                self.fontsize.set("14")

        def inc_font():
            try:
                val = int(self.fontsize.get())
                if val < 48:
                    self.fontsize.set(str(val + 1))
            except Exception:
                self.fontsize.set("14")

        super().__init__(master)
        self.ui = ui_strings
        self.on_change_callback = on_change_callback

        # Title & geometry settings
        form_title = self.ui.get("title", "Settings")
        self.title(form_title)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Modal for 1 second, then release
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()
        self.after(1000, self.grab_release)

        # center relative to master
        width, height = 360, 180
        self.update_idletasks()
        try:
            master_x = master.winfo_x()
            master_y = master.winfo_y()
            master_w = master.winfo_width()
            master_h = master.winfo_height()
            x = master_x + (master_w // 2) - (width // 2)
            y = master_y + (master_h // 2) - (height // 2)
        except Exception:
            x, y = 100, 100
        self.geometry(f"{width}x{height}+{x}+{y}")

        # try setting icon
        try:
            master.set_window_icon(self)
        except Exception:
            pass

        # Use shared config if provided; otherwise create our own
        if shared_config:
            self.config = shared_config
        else:
            self.config = IniManager(config_path)

        # Load current values
        self.fontsize = tk.StringVar(value=self.config.getvalue("general", "fontsize", "14"))
        self.apikey = tk.StringVar(value=self.config.getvalue("tile_download", "apikey", ""))
        self.email = tk.StringVar(value=self.config.getvalue("tile_download", "osm_email", ""))
        self.language = tk.StringVar()

        # -----------------------------------------------------------------------------------------------------------
        # Discover available languages in ./lang directory
        lang_dir = Path("lang").resolve()
        lang_error = "Please check the '/lang' directory exists"
        lang_reinstall = "or reinstall the application."
        if not lang_dir.exists():
            messagebox.showerror(
                self.ui.get("title", "Error"), f"Cannot find language directory. {lang_error}, {lang_reinstall}"
            )
            self.destroy()
            return

        self.lang_map = {}  # display name -> filename
        filelist = list(lang_dir.glob("ui_*.ini"))
        for f in filelist:
            cfg = IniManager(f)
            lang_name = cfg.getvalue("info", "language")
            if lang_name:
                self.lang_map[lang_name] = f.name
                self.lang_map[lang_name.lower()] = f.name

        if not self.lang_map:
            messagebox.showerror(
                self.ui.get("title", "Error"),
                f"Cannot find any valid language file. {lang_error}, {lang_reinstall}"
            )
            self.destroy()
            return

        # Determine current language file saved in config
        current_language = self.config.getvalue("general", "language", "english")
        current_langfile = f"ui_{current_language}.ini".lower()

        # Set combobox selection based on filename
        for display_name, fname in self.lang_map.items():
            if fname == current_langfile:
                self.language.set(display_name)
                break
        else:
            messagebox.showerror(
                self.ui.get("title", "Error"),
                f"Unable to find language file: '{current_langfile}'. Please check the '/lang' directory {lang_reinstall}"
            )
            self.destroy()
            return

        # -----------------------------------------------------------------------------------------------------------
        # Build UI layout
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Font size row
        font_frame = ttk.Frame(frm)
        font_frame.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(frm, text=self.ui.get("font_label", "Font size")).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frm, textvariable=self.fontsize, width=4, justify="center").grid(row=0, column=1, sticky="w", pady=5)
        ttk.Button(font_frame, text="-", width=3, command=dec_font).pack(side="left", padx=(40, 1))
        ttk.Button(font_frame, text="+", width=3, command=inc_font).pack(side="left", padx=(1, 4))

        # API key
        ttk.Label(frm, text=self.ui.get("apikey_label", "API Key")).grid(row=1, column=0, sticky="w", pady=4)
        api_entry = ttk.Entry(frm, textvariable=self.apikey, width=35)
        api_entry.grid(row=1, column=1, sticky="ew", pady=4)
        ToolTip(api_entry, ui_strings.get("apikey_tooltip", "Enter your API key."))

        # Email
        ttk.Label(frm, text=self.ui.get("email_label", "E-mail")).grid(row=2, column=0, sticky="w", pady=4)
        email_entry = ttk.Entry(frm, textvariable=self.email, width=35)
        email_entry.grid(row=2, column=1, sticky="ew", pady=4)
        ToolTip(email_entry, ui_strings.get("osmmail_tooltip", "Your OSM contact e-mail."))

        # Language combobox
        available_languages = []
        for k in list(self.lang_map.keys()):
            add_it = True
            for q in available_languages:
                if q.lower() == k:
                    add_it = False
                    break
            if add_it:
                available_languages.append(k)
        ttk.Label(frm, text=self.ui.get("language_label", "Language"), justify="center").grid(row=3, column=0, sticky="w", pady=5)
        lang_combo = ttk.Combobox(
            frm,
            textvariable=self.language,
            values=list(available_languages),
            width=12,
            state="readonly"
        )
        lang_combo.grid(row=3, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))
        ttk.Button(btn_frame, text=self.ui.get("ok_button", "OK"), command=self.save_settings, width=10).pack(side="right", padx=8)
        ttk.Button(btn_frame, text=self.ui.get("cancel_button", "Cancel"), command=self.destroy, width=10).pack(side="right")

        for i in range(2):
            frm.columnconfigure(i, weight=1)

    # -----------------------------------------------------------------------------------------------------------

    def save_settings(self):
        """Save settings to config (via shared IniManager), write to disk, then close and call callback."""
        try:
            # store values in config instance
            self.config.setvalue("general", "fontsize", self.fontsize.get())

            #  TODO - Cleanup
            # map display language name back to filename and store filename
            # lang_file = self.lang_map.get(self.language.get())
            # if not lang_file:
            #     messagebox.showerror(
            #         self.ui.get("title", "Error"),
            #         "Selected language file not found. Please check your '/lang' directory."
            #     )
            #     return

            # self.config.setvalue("general", "language", lang_file)
            self.config.setvalue("general", "language", self.language.get())
            self.config.setvalue("tile_download", "apikey", self.apikey.get())
            self.config.setvalue("tile_download", "osm_email", self.email.get())

            # try to persist to disk if IniManager supports it
            if hasattr(self.config, "write"):
                try:
                    self.config.write()
                except Exception:
                    # if write fails silently, try save
                    if hasattr(self.config, "save"):
                        self.config.save()
            elif hasattr(self.config, "save"):
                self.config.save()

            # Save done on shared instance. Now close the settings window, then run callback and show message.
            # We must call the callback via master.after because self.destroy() will remove this widget.
            master = self.master

            # Destroy settings window first
            try:
                self.destroy()
            except Exception:
                pass

            # Run callback (if any) after a short delay on the master (so master is active)
            if self.on_change_callback:
                try:
                    master.after(100, lambda: self._safe_run_callback(self.on_change_callback))
                except Exception:
                    # fallback synchronous call
                    try:
                        self.on_change_callback()
                    except Exception:
                        pass

            # Show restart info after a short delay so that the message box appears in front
            try:
                master.after(300, lambda: messagebox.showinfo(
                    self.ui.get("title", "Settings"),
                    self.ui.get("restart_message", "Please restart the application to apply language changes.")
                ))
            except Exception:
                # final fallback - just show immediately (rare)
                messagebox.showinfo(
                    self.ui.get("title", "Settings"),
                    self.ui.get("restart_message", "Please restart the application to apply language changes.")
                )

        except Exception as e:
            msg = self.ui.get("save_error", "Error saving settings")
            messagebox.showerror(self.ui.get("title", "Settings"), f"{msg}:\n{e}")
            try:
                self.destroy()
            except Exception:
                pass

    def _safe_run_callback(self, cb):
        try:
            cb()
        except Exception as e:
            print(f"SettingsForm on_change_callback error: {e}")

    # -----------------------------------------------------------------
    @staticmethod
    def check_and_prompt(master, ui_strings, config_path="config.ini", shared_config: IniManager = None, on_change_callback=None):
        """
        If savedir in [tile_download] is empty, show settings form. Returns True if shown.
        Accepts shared_config and callback optional parameters to ensure the same shared instance is used.
        """
        config = shared_config if shared_config else IniManager(config_path)
        savedir = config.getvalue("tile_download", "savedir", "").strip()
        if not savedir:
            messagebox.showwarning(
                ui_strings.get("title", "Settings"),
                ui_strings.get("missing_savedir_message", "Please configure the save folder before continuing.")
            )
            SettingsForm(master, ui_strings, config_path=config_path, shared_config=config, on_change_callback=on_change_callback)
            return True
        return False
