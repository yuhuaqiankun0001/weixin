import importlib.util
import sys
import tkinter as tk
from tkinter import messagebox

REQUIRED_MODULES = ["psutil", "win32gui", "win32con", "win32process"]


def _show_error(msg: str) -> None:
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", msg)
        root.destroy()
    except Exception:
        print(msg, file=sys.stderr)


def _environment_ready() -> bool:
    if sys.platform != "win32":
        _show_error("本工具需在 Windows 上运行（依赖 win32 API）。")
        return False

    missing = [m for m in REQUIRED_MODULES if importlib.util.find_spec(m) is None]
    if missing:
        _show_error(
            "缺少依赖：{}\n请先运行 “pip install -r requirements.txt” 再启动。".format(", ".join(missing))
        )
        return False

    return True


def main():
    if not _environment_ready():
        sys.exit(1)

    from ui.main_window import run_app
    run_app()


if __name__ == "__main__":
    main()
