import importlib.util
import sys

REQUIRED_MODULES = ["psutil", "win32gui", "win32con", "win32process"]


def _show_error(msg: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", msg)
        root.destroy()
    except Exception:
        # Fallback to stderr if tkinter is unavailable or fails.
        print(msg, file=sys.stderr)


def _environment_ready() -> bool:
    # tkinter is a hard requirement; check early so we can show a clear message in headless environments.
    if importlib.util.find_spec("tkinter") is None:
        _show_error("缺少 tkinter 图形界面支持。请安装带 tkinter 的 Python 版本。")
        return False

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
