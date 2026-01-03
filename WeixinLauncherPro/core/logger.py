from dataclasses import dataclass
from typing import Callable


@dataclass
class Logger:
    sink: Callable[[str], None]

    def info(self, msg: str):
        self.sink(msg)

    def warn(self, msg: str):
        self.sink("[WARN] " + msg)

    def error(self, msg: str):
        self.sink("[ERROR] " + msg)
