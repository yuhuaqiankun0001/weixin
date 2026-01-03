from .ui import SchedulerTab


class SchedulerPlugin:
    id = "scheduler"
    name = "定时任务"
    version = "0.2.0"

    def init(self, ctx):
        self.ctx = ctx

    def get_tab(self, parent):
        self.tab = SchedulerTab(parent, self.ctx)
        return self.tab

    def on_start(self):
        pass

    def on_stop(self):
        pass


def create_plugin():
    return SchedulerPlugin()
