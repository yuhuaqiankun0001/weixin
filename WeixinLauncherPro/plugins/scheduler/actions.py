import tkinter as tk


def focus_and_copy(ctx, hwnd: int, text: str):
    """Safer default action: focus target window + copy message to clipboard for manual paste/send."""
    try:
        ctx.windows.focus(hwnd)
    except Exception as e:
        ctx.log.error(f"focus failed: {e}")
        return

    try:
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        ctx.log.info("Message copied to clipboard (manual paste + send).")
    except Exception as e:
        ctx.log.error(f"clipboard failed: {e}")
