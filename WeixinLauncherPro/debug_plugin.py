"""Standalone plugin UI runner.

Usage:
  python debug_plugin.py hello
  python debug_plugin.py scheduler

This will load plugins/<name>/plugin.py and render its tab in a simple window.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox

from core.config import load_config
from core.logger import Logger
from core.scheduler import Scheduler
from core.context import AppContext
from core import windows
from core.plugin_api import load_single_plugin_from_dir


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_plugin.py <plugin_name>")
        sys.exit(1)

    plugin_name = sys.argv[1].strip()
    root = tk.Tk()
    root.title(f"Plugin Debug - {plugin_name}")
    root.geometry("900x560")

    txt = tk.Text(root, height=10, wrap="word")
    txt.pack(side="bottom", fill="x")

    def sink(msg: str):
        txt.insert("end", msg + "\n")
        txt.see("end")

    cfg = load_config()
    logger = Logger(sink)
    scheduler = Scheduler(sink)
    scheduler.start()
    ctx = AppContext(cfg=cfg, log=logger, scheduler=scheduler, windows=windows)

    try:
        plugin = load_single_plugin_from_dir(plugin_name, ctx)
    except Exception as e:
        messagebox.showerror("Load failed", str(e))
        root.destroy()
        return

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)
    tab = plugin.get_tab(nb)
    nb.add(tab, text=plugin.name)

    def on_close():
        try:
            plugin.on_stop()
        except Exception:
            pass
        try:
            scheduler.stop()
        except Exception:
            pass
        root.destroy()

    try:
        plugin.on_start()
    except Exception:
        pass

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
