#!/usr/bin/env python3
"""
help_window.py
Gestisce la finestra popup di Aiuto (Help Window), che mostra un file Markdown
in base alla lingua selezionata (es. help_it.md, help_en.md, ecc.)
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import markdown
from tkhtmlview import HTMLLabel


class HelpWindow(tk.Toplevel):
    def __init__(self, master, lang_code="it", title="Help"):
        """
        :param master: finestra principale (parent)
        :param lang_code: codice lingua, es. "it", "en"
        :param title: titolo finestra
        """
        super().__init__(master)
        self.master = master
        self.lang_code = lang_code.lower()
        self.title(title)
        self.geometry("700x500")
        self.minsize(500, 400)
        self.attributes("-topmost", True)

        # Comportamento di chiusura
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Frame principale
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True)

        # Scrollbar + area HTML
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.html_view = HTMLLabel(
            frame,
            html="<h3>Caricamento in corso...</h3>",
            background="white",
            font=("Arial", 12)
        )
        self.html_view.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.html_view.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.html_view.yview)

        # Barra inferiore con pulsante Chiudi (✖)
        bottom_frame = tk.Frame(self, bg="#f0f0f0")
        bottom_frame.pack(fill="x", side="bottom")
        close_btn = tk.Button(bottom_frame, text="✖", width=4, command=self._on_close, font=("Arial", 12))
        close_btn.pack(side="right", padx=10, pady=5)

        # 🔹 Etichetta di caricamento (centrata sulla finestra)
        self.loading_label = tk.Label(
            self,
            text="⏳ Caricamento in corso...",
            font=("Arial", 11),
            bg="white",
            fg="gray30"
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

        # Caricamento del file in background
        threading.Thread(target=self._load_help_file, daemon=True).start()

    # ------------------------------------------------------------------------------------
    def _load_help_file(self):
        """Carica il file markdown corrispondente alla lingua impostata in un thread separato."""
        try:
            # Percorso: ./help/help_<lang>.md
            help_path = Path("help") / f"help_{self.lang_code}.md"
            help_path = help_path.resolve()

            # fallback su inglese
            if not help_path.exists():
                help_path = (Path("help") / "help_en.md").resolve()

            if not help_path.exists():
                html_content = f"<h3>File di aiuto non trovato:<br>{help_path}</h3>"
            else:
                with open(help_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                html_content = markdown.markdown(
                    md_content,
                    extensions=["tables", "fenced_code", "toc", "sane_lists"]
                )

            # Aggiorna la GUI nel main thread
            self.after(0, lambda: self._update_html(html_content))

        except Exception as e:
            msg = f"Impossibile leggere il file di aiuto:\n{e}"
            print(msg)
            self.after(0, lambda: messagebox.showerror("Errore", msg))
            self.after(0, lambda: self._update_html("<h3>Errore nel caricamento del file di aiuto.</h3>"))

    # ------------------------------------------------------------------------------------
    def _update_html(self, html_content):
        """Aggiorna il contenuto HTML nella finestra (main thread safe)."""

        # 🔹 Rimuovi la label di caricamento, se esiste
        if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
            self.loading_label.destroy()

        # Aggiorna il contenuto HTML
        self.html_view.set_html(html_content)

        try:
            self.html_view.set_html(html_content)
        except Exception as e:
            print(f"Errore aggiornamento HTMLLabel: {e}")

    # ------------------------------------------------------------------------------------
    def _on_close(self):
        """Chiude la finestra di help"""
        try:
            self.destroy()
        except Exception:
            pass
