import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, delay=750):
        """
        A simple Tooltip for Tkinter widgets
        :param widget:  Control with which the tooltip is associated
        :param text     Tooltip text
        :param delay    Pop-up delay (milliseconds
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self._after_id = None

        widget.bind("<Enter>", self.schedule_tip)
        widget.bind("<Leave>", self.hide_tip)

    def schedule_tip(self, event=None):
        """Timer to show the tooltip after selected delay."""
        self._after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        """Show the tooltip as foreground"""
        if self.tip_window or not self.text:
            # Tooltip already visible, avoid creating another
            return
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("tahoma", 9)
        )
        label.pack(ipadx=6, ipady=2)

    def hide_tip(self, event=None):
        """Hide the tooltip"""
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
