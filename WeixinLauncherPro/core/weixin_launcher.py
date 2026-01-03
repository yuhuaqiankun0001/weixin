import os
import time
import subprocess


def launch_instances(exe_path: str, n: int, delay_ms: int):
    """Launch WeChat N times with delay. (Multi-instance behavior depends on WeChat build.)"""
    for _ in range(n):
        try:
            os.startfile(exe_path)
        except Exception:
            subprocess.Popen([exe_path], close_fds=True)
        time.sleep(max(0, delay_ms) / 1000.0)
