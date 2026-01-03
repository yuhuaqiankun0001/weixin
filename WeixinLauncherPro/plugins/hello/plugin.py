from tkinter import ttk, messagebox


class HelloPlugin:
    id = "hello"
    name = "Hello"
    version = "0.2.0"

    def init(self, ctx):
        self.ctx = ctx

    def get_tab(self, parent):
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="这是一个示例插件，用于验证插件系统。").pack(anchor="w", padx=10, pady=10)
        ttk.Button(frame, text="Hello", command=self._hello).pack(anchor="w", padx=10, pady=6)
        ttk.Label(frame, text="你可以用 python debug_plugin.py hello 单独调试这个插件。").pack(anchor="w", padx=10, pady=6)
        return frame

    def _hello(self):
        self.ctx.log.info("Hello plugin clicked.")
        messagebox.showinfo("Hello", "插件系统工作正常。")

    def on_start(self):
        pass

    def on_stop(self):
        pass


def create_plugin():
    return HelloPlugin()
