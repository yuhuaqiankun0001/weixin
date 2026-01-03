import os
import json
from dataclasses import dataclass, asdict
from typing import Optional

APP_NAME = "WeixinMultiLauncher"
CONFIG_FILE = "config.json"
DEFAULT_WEIXIN_PATH = r"C:\Program Files\Tencent\Weixin\WeiXin.exe"


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int


@dataclass
class AppConfig:
    exe_path: str = DEFAULT_WEIXIN_PATH
    class_name: str = ""
    base_rect: Optional[Rect] = None
    layout: str = "cascade"   # cascade / tile
    cascade_dx: int = 30
    cascade_dy: int = 30
    launch_delay_ms: int = 800


def _config_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def config_path() -> str:
    return os.path.join(_config_dir(), CONFIG_FILE)


def load_config() -> AppConfig:
    path = config_path()
    if not os.path.exists(path):
        return AppConfig()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cfg = AppConfig(**{k: v for k, v in raw.items() if k != "base_rect"})
        if raw.get("base_rect"):
            cfg.base_rect = Rect(**raw["base_rect"])
        return cfg
    except Exception:
        return AppConfig()


def save_config(cfg: AppConfig) -> None:
    raw = asdict(cfg)
    if cfg.base_rect is not None:
        raw["base_rect"] = asdict(cfg.base_rect)
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
