from dataclasses import dataclass
from core.config import AppConfig
from core.logger import Logger
from core.scheduler import Scheduler
from core import windows


@dataclass
class AppContext:
    cfg: AppConfig
    log: Logger
    scheduler: Scheduler
    windows: windows
