import uuid
from tkinter import ttk, messagebox

from core.scheduler import Job
from core import windows
from .actions import focus_and_copy


class SchedulerTab(ttk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx = ctx
        self._build()

    def _build(self):
        frm = ttk.LabelFrame(self, text="定时任务（示例：定时聚焦某个微信窗口 + 复制消息到剪贴板）")
        frm.pack(fill="x", padx=10, pady=10)

        ttk.Label(frm, text="目标微信：").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.cmb = ttk.Combobox(frm, width=58, state="readonly")
        self.cmb.grid(row=0, column=1, sticky="w", padx=8, pady=6)
        ttk.Button(frm, text="刷新窗口", command=self.refresh_windows).grid(row=0, column=2, padx=8, pady=6)

        ttk.Label(frm, text="间隔(秒)：").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.spn_interval = ttk.Spinbox(frm, from_=5, to=86400, increment=5, width=12)
        self.spn_interval.set("60")
        self.spn_interval.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frm, text="消息内容：").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.ent_text = ttk.Entry(frm, width=70)
        self.ent_text.grid(row=2, column=1, columnspan=2, sticky="w", padx=8, pady=6)
        self.ent_text.insert(0, "示例：到点提醒我发这条消息")

        ttk.Button(frm, text="添加任务", command=self.add_job).grid(row=3, column=1, sticky="w", padx=8, pady=10)
        ttk.Button(frm, text="删除选中任务", command=self.remove_job).grid(row=3, column=2, sticky="w", padx=8, pady=10)

        lf = ttk.LabelFrame(self, text="任务列表")
        lf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree = ttk.Treeview(lf, columns=("id","interval","target","text"), show="headings", height=10)
        for c, t, w in [("id","ID",120), ("interval","间隔(秒)",90), ("target","目标",140), ("text","内容",540)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.refresh_windows()
        self.refresh_jobs()

    def refresh_windows(self):
        exe = self.ctx.cfg.exe_path
        cls = self.ctx.cfg.class_name
        ws = windows.list_numbered_wechat_windows(exe, cls)
        items = []
        for w in ws:
            title = w.get("title") or "(无标题)"
            items.append(f"{w['label']} | {w['hwnd']} | {title}")
        self.cmb["values"] = items
        if items:
            self.cmb.current(0)

    def refresh_jobs(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for j in self.ctx.scheduler.list_jobs():
            self.tree.insert("", "end", values=(j.job_id, j.interval_sec, "-", "(action)"))

    def add_job(self):
        if not self.cmb.get():
            messagebox.showinfo("提示", "请先刷新并选择目标微信窗口。")
            return
        try:
            interval = int(self.spn_interval.get())
        except Exception:
            messagebox.showinfo("提示", "间隔必须是整数秒。")
            return

        text = self.ent_text.get().strip()
        if not text:
            messagebox.showinfo("提示", "消息内容不能为空。")
            return

        parts = [p.strip() for p in self.cmb.get().split("|")]
        target_label = parts[0]
        hwnd = int(parts[1])

        job_id = str(uuid.uuid4())[:8]

        def action():
            focus_and_copy(self.ctx, hwnd, text)
            self.ctx.log.info(f"[{target_label} job {job_id}] executed.")

        self.ctx.scheduler.add_or_update(Job(job_id=job_id, interval_sec=interval, action=action, enabled=True))
        self.ctx.log.info(f"Added job {job_id} for {target_label} every {interval}s.")
        self.refresh_jobs()

    def remove_job(self):
        sel = self.tree.selection()
        if not sel:
            return
        job_id = self.tree.item(sel[0], "values")[0]
        self.ctx.scheduler.remove(job_id)
        self.ctx.log.info(f"Removed job {job_id}.")
        self.refresh_jobs()
