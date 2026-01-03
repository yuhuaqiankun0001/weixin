# WeixinLauncherPro (Multi-instance + Window Layout + Plugin UI)

## 你现在拥有的能力
- 多开启动：启动 N 个微信实例（是否真正“多开”取决于你的微信版本/策略）
- 窗口扫描与摆放：保存一个“基准窗口位置”，之后自动层叠/平铺摆放
- 首次定位向导：第一次运行，弹出向导选择 WeiXin.exe 与基准窗口
- 窗口编号：扫描到的窗口会显示为 “微信1/微信2/…” 便于选择与操作
- 插件系统：每个功能独立目录、独立文件调试，最终合并到同一界面（Notebook 页签）
- 插件独立调试入口：可单独启动某个插件 UI

---

## 运行（开发模式）
建议使用国内源：
```powershell
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python app.py
```

---

## 插件独立调试
```powershell
python debug_plugin.py hello
python debug_plugin.py scheduler
```

---

## 打包 EXE
运行：
```bat
build_exe.bat
```

---

## 插件开发规范
每个插件目录：`plugins/<name>/plugin.py`

必须提供：
- `create_plugin()`：返回插件对象
- 插件对象实现：
  - `init(ctx)`
  - `get_tab(parent) -> ttk.Frame`
  - `on_start()` / `on_stop()`

示例插件：
- `plugins/hello`
- `plugins/scheduler`

---

## 关于“定时发送消息”
示例插件目前默认做 **“聚焦窗口 + 复制消息到剪贴板（你手动粘贴发送）”** 的安全实现。
你后续如果要升级为更强的自动化发送，建议将发送实现封装为 sender 模块（可替换），避免把风险逻辑写死在 UI/调度层。
