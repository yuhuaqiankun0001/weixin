import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, List


@dataclass
class Job:
    job_id: str
    interval_sec: int
    action: Callable[[], None]
    enabled: bool = True


class Scheduler:
    """A tiny in-process scheduler for plugins."""

    def __init__(self, on_log: Callable[[str], None]):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._log = on_log

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._log("Scheduler started.")

    def stop(self):
        self._stop.set()
        self._log("Scheduler stopped.")

    def add_or_update(self, job: Job):
        with self._lock:
            self._jobs[job.job_id] = job

    def remove(self, job_id: str):
        with self._lock:
            self._jobs.pop(job_id, None)

    def list_jobs(self) -> List[Job]:
        with self._lock:
            return list(self._jobs.values())

    def _run(self):
        last_run: Dict[str, float] = {}
        while not self._stop.is_set():
            now = time.time()
            jobs = self.list_jobs()
            for j in jobs:
                if not j.enabled:
                    continue
                prev = last_run.get(j.job_id, 0.0)
                if now - prev >= j.interval_sec:
                    try:
                        j.action()
                    except Exception as e:
                        self._log(f"[Scheduler] job {j.job_id} error: {e}")
                    last_run[j.job_id] = now
            time.sleep(0.3)
