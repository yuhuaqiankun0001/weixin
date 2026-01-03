import os
import sys


def resource_base_dir() -> str:
    """Return base dir for resources (works for PyInstaller onefile)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts: str) -> str:
    return os.path.join(resource_base_dir(), *parts)
