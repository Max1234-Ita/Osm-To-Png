#!/usr/bin/env python3
"""
help_window.py
Manages the Help popup window, which displays a Markdown help file
based on the currently selected language (e.g. help_en.md, help_it.md, etc.)
Supports embedded images (from /help/images) converted to base64.
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import markdown
import base64
import re
from urllib.parse import urljoin
from urllib.request import pathname2url
from tkinterweb import HtmlFrame

from inifile_access import IniManager


class HelpWindow(tk.Toplevel):
    def __init__(self, master, help_file, title="Help"):
        """
        :param master: parent window
        :param help_file: Name of the help file, i.e. 'help_eng.md'
        :param title: window title
        """
        super().__init__(master)
        self.master = master
        self.helpfile = help_file

        self.title(title)
        self.geometry("700x500")
        self.minsize(500, 400)
        self.attributes("-topmost", True)

        # Window close behavior
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Main frame
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True)

        # HTML display area with margin
        self.html_view = HtmlFrame(frame, messages_enabled=False)
        self.html_view.pack(fill="both", expand=True, padx=(20, 8), pady=8)

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

        self.after(1000, lambda: self.attributes("-topmost", False))

    # ----------------------------------------------------------------------
    def _load_help_file(self):
        """Loads the Markdown help file in a background thread."""
        try:
            help_path = Path(f"help/{self.helpfile}").resolve()

            # Fallback to English help file
            if not help_path.exists():
                help_path = (Path("help") / "help_en.md").resolve()

            if not help_path.exists():
                html_content = (
                    f"<h3>Help file not found.<br>"
                    f"Please ensure the folder '/help' contains '{self.helpfile}' or 'help_en.md'.</h3>"
                )
            else:
                with open(help_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                # 🔹 Convert images to base64 inline
                # def embed_images_as_base64(md_text, base_dir):
                #     pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
                #
                #     def replacer(match):
                #         alt_text = match.group(1)
                #         img_rel_path = match.group(2)
                #         img_path = (base_dir / img_rel_path).resolve()
                #         if not img_path.exists():
                #             return f'<p><b>[Missing image: {img_rel_path}]</b></p>'
                #         ext = img_path.suffix.lower()
                #         mime = {
                #             ".png": "image/png",
                #             ".jpg": "image/jpeg",
                #             ".jpeg": "image/jpeg",
                #             ".gif": "image/gif",
                #             ".svg": "image/svg+xml"
                #         }.get(ext, "image/png")
                #         with open(img_path, "rb") as img_file:
                #             encoded = base64.b64encode(img_file.read()).decode("utf-8")
                #         return f'<img src="data:{mime};base64,{encoded}" alt="{alt_text}" style="max-width:100%; margin:8px 0;">'
                #
                #     return re.sub(pattern, replacer, md_text)
                # md_content = embed_images_as_base64(md_content, base_dir)

                def embed_local_images(md_text, base_dir):
                    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

                    def replacer(match):
                        alt_text = match.group(1)
                        rel_path = match.group(2)
                        img_path = (base_dir / rel_path).resolve()
                        if not img_path.exists():
                            return f'<p><b>[Missing image: {rel_path}]</b></p>'
                        # Usa percorso file:// compatibile
                        img_url = f"file:///{img_path.as_posix()}"
                        return f'<img src="{img_url}" alt="{alt_text}" style="max-width:100%; margin:8px 0;">'

                    return re.sub(pattern, replacer, md_text)

                base_dir = help_path.parent
                md_content = embed_local_images(md_content, base_dir)

                # Convert Markdown to HTML
                html_body = markdown.markdown(
                    md_content,
                    extensions=["tables", "fenced_code", "toc", "sane_lists"]
                )

                # Add basic styling
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            color: #222;
                            margin: 16px;
                            line-height: 1.5;
                        }}
                        h1, h2, h3 {{ color: #004080; }}
                        img {{ border: 1px solid #ccc; border-radius: 4px; }}
                        code {{
                            background: #f8f8f8;
                            padding: 2px 4px;
                            border-radius: 3px;
                        }}
                        pre {{
                            background: #f0f0f0;
                            padding: 8px;
                            border-radius: 5px;
                            overflow-x: auto;
                        }}
                    </style>
                </head>
                <body>{html_body}</body>
                </html>
                """

            # Base path for relative resources
            base_url = urljoin("file:", pathname2url(str(help_path.parent)) + "/")

            # Update the GUI safely from main thread
            self.after(0, lambda: self._update_html(html_content, base_url))

        except Exception as e:
            msg = f"Unable to read help file:\n{e}"
            print(msg)
            self.after(0, lambda e=e: messagebox.showerror("Error", msg))
            self.after(0, lambda: self._update_html("<h3>Error loading help file.</h3>", ""))

    # ----------------------------------------------------------------------
    def _update_html(self, html_content, base_url=""):
        """Updates HTML content inside the window (thread-safe)."""
        try:
            # Remove the loading label if still visible
            if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
                self.loading_label.destroy()

            # Display HTML with correct base URL
            self.html_view.load_html(html_content, base_url=base_url)

        except Exception as e:
            print(f"Error updating HTML: {e}")
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))

    # ----------------------------------------------------------------------
    def _on_close(self):
        """Closes the help window."""
        try:
            self.destroy()
        except Exception:
            pass
