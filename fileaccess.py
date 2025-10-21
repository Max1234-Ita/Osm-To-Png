# Manages a File Selection prompt (GUI)

import os
from tkinter import filedialog, messagebox

def select_output_file(
        initial_dir: str = os.getcwd(),
        default_name: str = 'Untitled.png',
        default_extension=None,
        filetypes=None,
        prompt='Save file',
        confirm_overwrite=True
) -> str | None:
    """
    Shows a Save File dialog
    :param initial_dir:         Initial postion (directory path)
    :param default_name:        Default name for the file to save
    :param default_extension:   i.e. '.png'
    :param filetypes:           Allowed file types, i.e. [('All files', '*.*')]
    :param prompt:              Dialog title
    :param confirm_overwrite:   Ask to overwrite existing files

    :return str | None: Full path of selected file, or  None if the user cancels.
    """
    try:
        # Open the Save File dialog
        file_path = filedialog.asksaveasfilename(
            title=prompt,
            defaultextension=default_extension,
            initialdir=initial_dir,
            initialfile=default_name,
            filetypes=filetypes,                       # i.e. [("PNG pictures", "*.png")],
            confirmoverwrite=confirm_overwrite
        )

        if not file_path:
            # If user cancels
            return None

        # Check if save directory exists
        save_dir = os.path.dirname(file_path)
        if not os.path.exists(save_dir):
            messagebox.showerror("Error", f"Target directory does not exist:\n {save_dir}")
            return None

        return file_path

    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la selezione del file:\n{e}")
        return None
