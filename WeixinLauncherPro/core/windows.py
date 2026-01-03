import os
import math
from typing import List, Dict, Optional

import psutil
import win32gui
import win32con
import win32process

from core.config import Rect


def _norm(p: str) -> str:
    try:
        return os.path.normcase(os.path.abspath(p))
    except Exception:
        return (p or "").lower()


def work_area():
    l, t, r, b = win32gui.SystemParametersInfo(win32con.SPI_GETWORKAREA)
    return l, t, r, b


def list_windows_by_exe(exe_path: str, class_name: str = "") -> List[Dict]:
    """List visible top-level windows that belong to the given exe path, optionally filtering by class name."""
    exe_norm = _norm(exe_path)
    out: List[Dict] = []

    def cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        cls = win32gui.GetClassName(hwnd)
        if class_name and cls != class_name:
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            p = psutil.Process(pid)
            if exe_norm and _norm(p.exe()) != exe_norm:
                return
        except Exception:
            return
        title = win32gui.GetWindowText(hwnd)
        out.append({"hwnd": int(hwnd), "pid": int(pid), "title": title, "class": cls})

    win32gui.EnumWindows(cb, None)

    # Sort to make numbering more stable:
    # 1) has title first, 2) pid, 3) hwnd
    out.sort(key=lambda x: (0 if x["title"] else 1, x["pid"], x["hwnd"]))
    return out


def list_numbered_wechat_windows(exe_path: str, class_name: str = "") -> List[Dict]:
    """Return windows with a stable sequential index: 微信1/微信2/..."""
    ws = list_windows_by_exe(exe_path, class_name)
    for i, w in enumerate(ws, start=1):
        w["index"] = i
        w["label"] = f"微信{i}"
    return ws


def focus(hwnd: int):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


def set_rect(hwnd: int, rect: Rect):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd, None,
        rect.x, rect.y, rect.w, rect.h,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )


def get_rect(hwnd: int) -> Rect:
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    return Rect(int(l), int(t), int(r - l), int(b - t))


def layout_cascade(base: Rect, count: int, dx: int, dy: int) -> List[Rect]:
    wa_l, wa_t, wa_r, wa_b = work_area()
    rects = []
    for i in range(count):
        x = max(wa_l, min(base.x + i * dx, wa_r - base.w))
        y = max(wa_t, min(base.y + i * dy, wa_b - base.h))
        rects.append(Rect(x, y, base.w, base.h))
    return rects


def layout_tile(base: Rect, count: int) -> List[Rect]:
    wa_l, wa_t, wa_r, wa_b = work_area()
    wa_w, wa_h = wa_r - wa_l, wa_b - wa_t
    cols = math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)
    cell_w = max(1, wa_w // cols)
    cell_h = max(1, wa_h // rows)
    w = min(base.w, cell_w)
    h = min(base.h, cell_h)

    rects = []
    for i in range(count):
        r = i // cols
        c = i % cols
        rects.append(Rect(wa_l + c * cell_w, wa_t + r * cell_h, w, h))
    return rects
