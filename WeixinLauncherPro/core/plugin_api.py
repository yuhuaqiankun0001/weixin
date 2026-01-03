import os
import importlib.util
from dataclasses import dataclass
from typing import Protocol, List
from tkinter import ttk

from core.context import AppContext
from core.paths import resource_path


class Plugin(Protocol):
    id: str
    name: str
    version: str

    def init(self, ctx: AppContext) -> None: ...
    def get_tab(self, parent) -> ttk.Frame: ...
    def on_start(self) -> None: ...
    def on_stop(self) -> None: ...


@dataclass
class LoadedPlugin:
    plugin: Plugin
    tab: ttk.Frame


def _load_plugin_module_from_file(mod_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(mod_name, file_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load spec: {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def load_single_plugin_from_dir(plugin_dir_name: str, ctx: AppContext) -> Plugin:
    """Load a single plugin by directory name under plugins/. For debug runner."""
    plugin_py = resource_path("plugins", plugin_dir_name, "plugin.py")
    if not os.path.isfile(plugin_py):
        raise FileNotFoundError(f"plugin.py not found: {plugin_py}")
    mod = _load_plugin_module_from_file(f"plugin_{plugin_dir_name}", plugin_py)
    if not hasattr(mod, "create_plugin"):
        raise RuntimeError("create_plugin() not found")
    plugin = mod.create_plugin()
    plugin.init(ctx)
    return plugin


class PluginHost:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.loaded: List[LoadedPlugin] = []

    def load_all(self, notebook: ttk.Notebook):
        plugins_dir = resource_path("plugins")
        if not os.path.isdir(plugins_dir):
            self.ctx.log.warn(f"plugins dir not found: {plugins_dir}")
            return

        for name in os.listdir(plugins_dir):
            plugin_py = os.path.join(plugins_dir, name, "plugin.py")
            if not os.path.isfile(plugin_py):
                continue

            try:
                mod = _load_plugin_module_from_file(f"plugin_{name}", plugin_py)
                if not hasattr(mod, "create_plugin"):
                    self.ctx.log.warn(f"{name} missing create_plugin()")
                    continue

                plugin = mod.create_plugin()
                plugin.init(self.ctx)
                tab = plugin.get_tab(notebook)
                notebook.add(tab, text=plugin.name)
                self.loaded.append(LoadedPlugin(plugin=plugin, tab=tab))
                self.ctx.log.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            except Exception as e:
                self.ctx.log.error(f"Load plugin failed: {name}: {e}")

    def start_all(self):
        for p in self.loaded:
            try:
                p.plugin.on_start()
            except Exception as e:
                self.ctx.log.error(f"Plugin start error: {p.plugin.name}: {e}")

    def stop_all(self):
        for p in self.loaded:
            try:
                p.plugin.on_stop()
            except Exception:
                pass
