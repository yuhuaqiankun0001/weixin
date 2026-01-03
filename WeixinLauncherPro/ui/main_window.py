import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.config import load_config, save_config
from core.logger import Logger
from core.scheduler import Scheduler
from core.context import AppContext
from core.plugin_api import PluginHost
from core import windows
from core.weixin_launcher import launch_instances
from ui.setup_wizard import SetupWizard


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("微信多开启动器 + 辅助功能（插件化）")
        self.geometry("980x640")
        self.resizable(False, False)

        self.cfg = load_config()

        self.txt_log = None
        self.logger = Logger(self._append_log)
        self.scheduler = Scheduler(self._append_log)
        self.scheduler.start()

        self.ctx = AppContext(cfg=self.cfg, log=self.logger, scheduler=self.scheduler, windows=windows)

        # first-run wizard if needed
        self.withdraw()
        if not self._ensure_config_ready():
            # user cancelled
            self.destroy()
            return
        self.deiconify()

        self._build_ui()

        # plugins
        self.host = PluginHost(self.ctx)
        self.host.load_all(self.notebook)
        self.host.start_all()

        self._append_log("Ready.")

    def _ensure_config_ready(self) -> bool:
        exe_ok = bool(self.cfg.exe_path) and os.path.exists(self.cfg.exe_path)
        if (not exe_ok) or (self.cfg.base_rect is None):
            wiz = SetupWizard(self, self.cfg)
            self.wait_window(wiz)
            return bool(getattr(wiz, "result_ok", False))
        return True

    def _append_log(self, msg: str):
        if not self.txt_log:
            return
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def _build_ui(self):
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        tab_base = ttk.Frame(self.notebook)
        self.notebook.add(tab_base, text="启动与摆放")

        frm = ttk.LabelFrame(tab_base, text="微信启动与窗口摆放")
        frm.pack(fill="x", padx=10, pady=10)

        self.var_exe = tk.StringVar(value=self.cfg.exe_path)
        self.var_class = tk.StringVar(value=self.cfg.class_name)
        self.var_n = tk.IntVar(value=2)
        self.var_delay = tk.IntVar(value=self.cfg.launch_delay_ms)
        self.var_layout = tk.StringVar(value=self.cfg.layout)
        self.var_dx = tk.IntVar(value=self.cfg.cascade_dx)
        self.var_dy = tk.IntVar(value=self.cfg.cascade_dy)

        ttk.Label(frm, text="WeiXin.exe：").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_exe, width=70).grid(row=0, column=1, sticky="w", padx=8, pady=6)
        ttk.Button(frm, text="浏览…", command=self._browse_exe).grid(row=0, column=2, padx=8, pady=6)
        ttk.Button(frm, text="首次定位向导", command=self._open_wizard).grid(row=0, column=3, padx=8, pady=6)

        ttk.Label(frm, text="ClassName（可选）：").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=self.var_class, width=70).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frm, text="多开 N：").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Spinbox(frm, from_=1, to=20, textvariable=self.var_n, width=8).grid(row=2, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frm, text="启动间隔(ms)：").grid(row=2, column=2, sticky="e", padx=8, pady=6)
        ttk.Spinbox(frm, from_=100, to=3000, increment=100, textvariable=self.var_delay, width=10).grid(row=2, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(frm, text="布局：").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Radiobutton(frm, text="层叠", variable=self.var_layout, value="cascade").grid(row=3, column=1, sticky="w", padx=8, pady=6)
        ttk.Radiobutton(frm, text="平铺", variable=self.var_layout, value="tile").grid(row=3, column=2, sticky="w", padx=8, pady=6)

        ttk.Label(frm, text="层叠偏移 dx/dy：").grid(row=3, column=3, sticky="e", padx=8, pady=6)
        ttk.Spinbox(frm, from_=0, to=200, textvariable=self.var_dx, width=6).grid(row=3, column=4, sticky="w", padx=(0,4), pady=6)
        ttk.Spinbox(frm, from_=0, to=200, textvariable=self.var_dy, width=6).grid(row=3, column=5, sticky="w", padx=4, pady=6)

        ttk.Button(frm, text="启动并摆放（基于已保存位置）", command=self.launch_and_arrange).grid(
            row=4, column=1, sticky="w", padx=8, pady=10
        )

        # Windows list panel
        wpanel = ttk.LabelFrame(tab_base, text="已扫描到的微信窗口（微信1/微信2/...）")
        wpanel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        bar = ttk.Frame(wpanel)
        bar.pack(fill="x", padx=8, pady=6)
        ttk.Button(bar, text="刷新窗口列表", command=self.refresh_windows).pack(side="left")
        ttk.Button(bar, text="聚焦选中窗口", command=self.focus_selected).pack(side="left", padx=8)
        ttk.Button(bar, text="设为基准位置并保存", command=self.set_selected_as_base).pack(side="left", padx=8)

        self.tree = ttk.Treeview(wpanel, columns=("idx","hwnd","title","class"), show="headings", height=10)
        for c, t, w in [("idx","编号",70), ("hwnd","HWND",120), ("title","标题",520), ("class","ClassName",180)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Log
        logf = ttk.LabelFrame(tab_base, text="日志")
        logf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_log = tk.Text(logf, height=10, wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)

        self.refresh_windows()

    def _open_wizard(self):
        wiz = SetupWizard(self, self.cfg)
        self.wait_window(wiz)
        if getattr(wiz, "result_ok", False):
            # reload cfg and refresh UI vars
            self.cfg = load_config()
            self.ctx.cfg = self.cfg
            self.var_exe.set(self.cfg.exe_path)
            self.var_class.set(self.cfg.class_name)
            self.var_layout.set(self.cfg.layout)
            self.refresh_windows()
            self.logger.info("Setup wizard completed and configuration reloaded.")

    def _browse_exe(self):
        p = filedialog.askopenfilename(
            title="选择 WeiXin.exe",
            filetypes=[("WeiXin.exe", "WeiXin.exe"), ("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if p:
            self.var_exe.set(p)

    def _persist_cfg(self):
        self.cfg.exe_path = self.var_exe.get().strip()
        self.cfg.class_name = self.var_class.get().strip()
        self.cfg.launch_delay_ms = int(self.var_delay.get())
        self.cfg.layout = self.var_layout.get()
        self.cfg.cascade_dx = int(self.var_dx.get())
        self.cfg.cascade_dy = int(self.var_dy.get())
        save_config(self.cfg)

    def refresh_windows(self):
        exe = self.var_exe.get().strip()
        cls = self.var_class.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not exe or not os.path.exists(exe):
            return
        ws = windows.list_numbered_wechat_windows(exe, cls)
        for w in ws:
            self.tree.insert("", "end", values=(w["label"], w["hwnd"], w.get("title") or "", w.get("class") or ""))

    def _selected_hwnd(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        return int(vals[1])

    def focus_selected(self):
        hwnd = self._selected_hwnd()
        if hwnd is None:
            messagebox.showinfo("提示", "请先选择一个窗口。")
            return
        try:
            windows.focus(hwnd)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def set_selected_as_base(self):
        hwnd = self._selected_hwnd()
        if hwnd is None:
            messagebox.showinfo("提示", "请先选择一个窗口。")
            return
        self.cfg.base_rect = windows.get_rect(hwnd)
        self._persist_cfg()
        self.logger.info(f"Saved base rect: {self.cfg.base_rect}")

    def launch_and_arrange(self):
        self._persist_cfg()
        if not self.cfg.base_rect:
            messagebox.showinfo("提示", "还没有保存基准位置。请先选择一个窗口并“设为基准位置并保存”。")
            return

        n = int(self.var_n.get())
        delay = int(self.var_delay.get())
        exe = self.cfg.exe_path
        cls = self.cfg.class_name

        self.logger.info(f"Launching {n} instance(s)...")
        launch_instances(exe, n, delay)

        self.logger.info("Scanning windows...")
        ws = windows.list_numbered_wechat_windows(exe, cls)
        targets = ws[:n]
        if not targets:
            messagebox.showinfo("提示", "未扫描到窗口。")
            return

        if self.cfg.layout == "tile":
            rects = windows.layout_tile(self.cfg.base_rect, len(targets))
        else:
            rects = windows.layout_cascade(self.cfg.base_rect, len(targets), self.cfg.cascade_dx, self.cfg.cascade_dy)

        for i, (w, r) in enumerate(zip(targets, rects), start=1):
            windows.set_rect(w["hwnd"], r)
            self.logger.info(f"[微信{i}] moved: {w.get('title','')} -> {r}")

        self.refresh_windows()

    def on_close(self):
        try:
            self.host.stop_all()
        except Exception:
            pass
        try:
            self.scheduler.stop()
        except Exception:
            pass
        self.destroy()


def run_app():
    app = MainWindow()
    if app.winfo_exists():
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()
