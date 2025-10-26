import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import configparser
import os

import globals
from inifile_access import IniManager

class TileDownloadWindow:
    def __init__(self, total_tiles):
        self.config = IniManager("config.ini")
        uilang = self.config.getvalue('general', 'language')
        langpath =  Path(f'lang/ui_{uilang}.ini').resolve()
        self.ui = IniManager(langpath)
        self.inisection = "tile_download"

        self.windowtitle = self.ui.getvalue(self.inisection, "title")
        self.pausetext = self.ui.getvalue(self.inisection, "pause")
        self.resumetext = self.ui.getvalue(self.inisection, "resume")
        self.canceltext = self.ui.getvalue(self.inisection, "cancel")
        self.progresstest = self.ui.getvalue(self.inisection, "progress")
        # Crea root se non esiste
        self._own_root = False
        try:
            self.root = tk._default_root
        except Exception:
            self.root = None

        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # non mostrare root
            self._own_root = True

        # Crea finestra principale
        self.window = tk.Toplevel(self.root)
        self.window.title(self.windowtitle)
        self.window.attributes("-topmost", True)
        self.window.geometry("400x140")
        self._set_window_icon(self.window)
        self.window.resizable(False, False)
        self.total_tiles = total_tiles
        self.stopflag = False
        self.pauseflag = False

        # Label di stato principale
        self.label_status = ttk.Label(self.window, text="Download: 0.0%")
        self.label_status.pack(pady=(25, 10))

        # Progressbar
        self.progress = ttk.Progressbar(
            self.window,
            length=320,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=(5, 15))

        # Frame pulsanti
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)

        self.btn_pause = ttk.Button(
            btn_frame,
            text=self.pausetext,
            command=self.toggle_pause
        )
        self.btn_pause.pack(side="left", padx=8)

        self.btn_cancel = ttk.Button(
            btn_frame,
            text=self.canceltext,
            command=self.cancel_download
        )
        self.btn_cancel.pack(side="left", padx=8)

        # Blocca chiusura diretta (usa Annulla)
        self.window.protocol("WM_DELETE_WINDOW", self.cancel_download)

        self.window.attributes("-topmost", True)

        # Avvio aggiornamento periodico
        self.after_id = None
        self.window.after(100, self.refresh_status)

    def refresh_status(self, tile_count=None):
        """Aggiorna progressbar e testo leggendo DL_PROGRESS."""
        if self.stopflag:
            self.window.destroy()

        elif self.window.winfo_exists():
            if tile_count:
                try:
                    percent = round(float(tile_count / self.total_tiles * 100), 2)
                except Exception:
                    percent = 0.0

                percent = max(0.0, min(percent, 100.0))  # clamp
                prog = self.progresstest.replace('{n_tiles}', str(tile_count))
                prog = prog.replace('{tot_tiles}', str(self.total_tiles))
                prog = prog.replace('{perc}', f'{percent}%')
                self.progress["value"] = percent
                # self.label_status.config(text=f"{self.windowtitle}: {str(percent)}%")
                self.label_status.config(text=f"{prog}")
                if self.pauseflag:
                    self.label_status.config(text=f"{self.windowtitle}: {str(percent)}% -- ⏸")

            if not self.stopflag:
                self.window.after(100, self.refresh_status)
                self.window.update_idletasks()

        return self.stopflag, self.pauseflag


    def _set_window_icon(self, window):
        """
        Use a custom Icon for the program windows.
        Icon must be a .png or .ico file, in /resources dir.
        """
        try:
            window.iconbitmap(Path('resources') / globals.APP_ICON_ICO)  # formato Windows
        except Exception:
            try:
                icon = tk.PhotoImage(file=Path('resources') / globals.APP_ICON_PNG)
                window.iconphoto(False, icon)
            except Exception as e:
                print(f"Cannot set window icon: {e}")

    def toggle_pause(self):
        """Attiva/disattiva la pausa."""
        self.pauseflag = not self.pauseflag
        new_text = self.resumetext if self.pauseflag else self.pausetext
        self.btn_pause.config(text=new_text)

    def cancel_download(self):
        """Conferma e imposta STOP_FLAG."""
        cancelquestion = self.ui.getvalue('tile_download', 'confirm_cancel')
        cancelconfirmed = self.ui.getvalue('tile_download', 'cancel_confirmed')

        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(100, lambda: self.window.attributes("-topmost", False))

        # Disable buttons to prevent multi-click
        self.btn_cancel.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.window.update_idletasks()

        if messagebox.askyesno(title=self.windowtitle, message=cancelquestion):
            print('\n  >> Download interrupted by user <<\n')
            self.stopflag = True
            self.btn_cancel.config(state="disabled")
            self.btn_pause.config(state="disabled")
            self.label_status.config(text=cancelconfirmed)
            self.window.update_idletasks()
            # Destroy window after some time to allow the pending updates the to take place
            self.window.after(100, self.destroy)
            if self._own_root:
                self.root.quit()

        # Re-enable buttons
        # self.confirm_open = False
        if not self.stopflag:
            self.btn_cancel.config(state="normal")
            self.btn_pause.config(state="normal")

    def destroy(self):
        """Chiude in modo sicuro la finestra e cancella after() attivi."""
        # Cancella eventuali callback pendenti
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except tk.TclError:
                pass

        # Distrugge la finestra se esiste
        if self.window and self.window.winfo_exists():
            try:
                self.window.destroy()
            except tk.TclError:
                pass

        # Chiude la root se è stata creata internamente
        if self._own_root and self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except tk.TclError:
                pass