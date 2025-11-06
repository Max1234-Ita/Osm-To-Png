#!/usr/bin/env python3
"""
help_window.py
Manages the Help popup window, which displays a Markdown help file
based on the currently selected language (e.g. help_en.md, help_it.md, etc.)
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import markdown
from tkhtmlview import HTMLLabel

from inifile_access import IniManager

class HelpWindow(tk.Toplevel):
    def __init__(self, master, help_file, title="Help"):
        """
        :param master: parent window
        :param help_file: Name of the help file, i.e. 'help_eng.md'
        :param title: window title
        """
        self.helpfile = help_file

        super().__init__(master)
        self.master = master
        # self.lang_code = lang_code.lower()
        self.title(title)
        self.geometry("700x500")
        self.minsize(500, 400)
        self.attributes("-topmost", True)

        cfg = IniManager('config.ini')

        # Window close behavior
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Main frame
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True)

        # Scrollbar + HTML area
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # HTML display area with left margin
        self.html_view = HTMLLabel(
            frame,
            html="<h3>Loading help file...</h3>",
            background="white",
            font=("Arial", 12)
        )
        self.html_view.pack(side="left", fill="both", expand=True, padx=(20, 8), pady=8)
        self.html_view.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.html_view.yview)

        # Bottom bar with Close (✖) button
        bottom_frame = tk.Frame(self, bg="#f0f0f0")
        bottom_frame.pack(fill="x", side="bottom")
        close_btn = tk.Button(bottom_frame, text="✖", width=4, command=self._on_close, font=("Arial", 12))
        close_btn.pack(side="right", padx=10, pady=5)

        # Centered loading label
        self.loading_label = tk.Label(
            self,
            text="⏳ Loading help content...",
            font=("Arial", 11),
            bg="white",
            fg="gray30"
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

        # Load help file asynchronously
        threading.Thread(target=self._load_help_file, daemon=True).start()

    # ----------------------------------------------------------------------
    def _load_help_file(self):
        """Loads the Markdown help file in a background thread."""
        try:
            # Expected path: ./help/help_<lang>.md
            # help_path = Path("help") / f"help_{self.lang_code}.md"
            # help_path = help_path.resolve()
            help_path = Path(f"help/{self.helpfile}").resolve()

            # Fallback to English help file
            if not help_path.exists():
                help_path = (Path("help") / "help_en.md").resolve()

            if not help_path.exists():
                html_content = (
                    f"<h3>Help file not found.<br>"
                    f"Please ensure the folder '/help' contains 'help_{self.lang_code}.md' or 'help_en.md'.</h3>"
                )
            else:
                with open(help_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                html_content = markdown.markdown(
                    md_content,
                    extensions=["tables", "fenced_code", "toc", "sane_lists"]
                )

            # Update the GUI safely from main thread
            self.after(0, lambda: self._update_html(html_content))

        except Exception as e:
            msg = f"Unable to read help file:\n{e}"
            print(msg)
            self.after(0, lambda: messagebox.showerror("Error", msg))
            self.after(0, lambda: self._update_html("<h3>Error loading help file.</h3>"))

    # ----------------------------------------------------------------------
    def _update_html(self, html_content):
        """Updates HTML content inside the window (thread-safe)."""
        try:
            # Remove the loading label if still visible
            if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
                self.loading_label.destroy()

            # Update HTML view
            self.html_view.set_html(html_content)

        except Exception as e:
            print(f"Error updating HTMLLabel: {e}")
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    # ----------------------------------------------------------------------
    def _on_close(self):
        """Closes the help window."""
        try:
            self.destroy()
        except Exception:
            pass
