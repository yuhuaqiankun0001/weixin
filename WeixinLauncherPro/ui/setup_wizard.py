import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.config import AppConfig, save_config
from core import windows


class SetupWizard(tk.Toplevel):
    """First-run setup wizard: choose WeiXin.exe and pick a base window rect."""

    def __init__(self, master, cfg: AppConfig):
        super().__init__(master)
        self.title("首次定位向导")
        self.geometry("760x520")
        self.resizable(False, False)
        self.cfg = cfg
        self.result_ok = False

        self.var_exe = tk.StringVar(value=cfg.exe_path)
        self.var_class = tk.StringVar(value=cfg.class_name)
        self.var_layout = tk.StringVar(value=cfg.layout)

        self._build()
        self.grab_set()
        self.transient(master)

    def _build(self):
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        nb = ttk.Notebook(outer)
        nb.pack(fill="both", expand=True)

        tab1 = ttk.Frame(nb)
        tab2 = ttk.Frame(nb)
        tab3 = ttk.Frame(nb)
        nb.add(tab1, text="1) 选择程序")
        nb.add(tab2, text="2) 选择基准窗口")
        nb.add(tab3, text="3) 完成")

        # Tab1
        g1 = ttk.LabelFrame(tab1, text="选择 WeiXin.exe 路径")
        g1.pack(fill="x", padx=10, pady=10)

        ttk.Label(g1, text="WeiXin.exe：").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(g1, textvariable=self.var_exe, width=62).grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Button(g1, text="浏览…", command=self._browse).grid(row=0, column=2, padx=8, pady=8)

        ttk.Label(g1, text="窗口 ClassName（可选）：").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(g1, textvariable=self.var_class, width=62).grid(row=1, column=1, sticky="w", padx=8, pady=8)

        ttk.Label(tab1, text="提示：下一步前请确保至少打开了一个微信窗口（便于扫描并选基准位置）。").pack(anchor="w", padx=12, pady=(0, 10))

        # Tab2
        g2 = ttk.LabelFrame(tab2, text="扫描并选择一个“基准窗口”（用于后续自动摆放）")
        g2.pack(fill="both", expand=True, padx=10, pady=10)

        toolbar = ttk.Frame(g2)
        toolbar.pack(fill="x", padx=8, pady=6)
        ttk.Button(toolbar, text="刷新扫描", command=self._refresh).pack(side="left")
        ttk.Button(toolbar, text="从选中窗口自动填充 ClassName", command=self._fill_class).pack(side="left", padx=8)

        self.tree = ttk.Treeview(g2, columns=("idx","hwnd","title","class"), show="headings", height=12)
        for c, t, w in [("idx","编号",60), ("hwnd","HWND",110), ("title","标题",380), ("class","ClassName",180)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        tip = ttk.Label(g2, text="选择一个窗口后点击“设为基准并保存”。")
        tip.pack(anchor="w", padx=8, pady=(0, 8))

        btns = ttk.Frame(g2)
        btns.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(btns, text="设为基准并保存", command=self._save_base).pack(side="left")

        # Tab3
        g3 = ttk.LabelFrame(tab3, text="布局与完成")
        g3.pack(fill="x", padx=10, pady=10)
        ttk.Label(g3, text="默认布局：").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Radiobutton(g3, text="层叠", variable=self.var_layout, value="cascade").grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Radiobutton(g3, text="平铺", variable=self.var_layout, value="tile").grid(row=0, column=2, sticky="w", padx=8, pady=8)

        ttk.Label(tab3, text="点击“完成”后进入主界面。").pack(anchor="w", padx=12, pady=(6, 10))

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="取消", command=self._cancel).pack(side="right")
        ttk.Button(footer, text="完成", command=self._finish).pack(side="right", padx=8)

        self._refresh()

    def _browse(self):
        p = filedialog.askopenfilename(
            title="选择 WeiXin.exe",
            filetypes=[("WeiXin.exe", "WeiXin.exe"), ("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if p:
            self.var_exe.set(p)

    def _refresh(self):
        exe = self.var_exe.get().strip()
        cls = self.var_class.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not exe:
            return
        ws = windows.list_numbered_wechat_windows(exe, cls)
        for w in ws:
            self.tree.insert("", "end", values=(w["label"], w["hwnd"], w.get("title") or "", w.get("class") or ""))

    def _get_selected_hwnd(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        return int(vals[1])

    def _fill_class(self):
        hwnd = self._get_selected_hwnd()
        if hwnd is None:
            messagebox.showinfo("提示", "请先选择一个窗口。")
            return
        # class name is in the list already; we can read it:
        sel = self.tree.selection()[0]
        vals = self.tree.item(sel, "values")
        cls = vals[3]
        if cls:
            self.var_class.set(cls)

    def _save_base(self):
        exe = self.var_exe.get().strip()
        if not exe:
            messagebox.showinfo("提示", "请先选择 WeiXin.exe。")
            return
        hwnd = self._get_selected_hwnd()
        if hwnd is None:
            messagebox.showinfo("提示", "请先选择一个窗口。")
            return
        self.cfg.exe_path = exe
        self.cfg.class_name = self.var_class.get().strip()
        self.cfg.base_rect = windows.get_rect(hwnd)
        save_config(self.cfg)
        messagebox.showinfo("提示", "已保存基准位置。你可以切到“完成”页点击完成。")

    def _finish(self):
        exe = self.var_exe.get().strip()
        if not exe or not os.path.exists(exe):
            messagebox.showinfo("提示", "WeiXin.exe 路径无效，请重新选择。")
            return
        self.cfg.exe_path = exe
        self.cfg.class_name = self.var_class.get().strip()
        self.cfg.layout = self.var_layout.get().strip() or "cascade"
        if not self.cfg.base_rect:
            messagebox.showinfo("提示", "还未保存基准位置，请在第2步选择窗口并保存。")
            return
        save_config(self.cfg)
        self.result_ok = True
        self.destroy()

    def _cancel(self):
        self.result_ok = False
        self.destroy()
