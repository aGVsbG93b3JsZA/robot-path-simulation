"""
画布类
"""

import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from rps.dataclass import Point, Graph
from PySide6.QtCore import QRunnable, QThreadPool, Slot, Signal, QObject

from .worker import Runner
from .customs import ErrorMessageBox
from rps.config import DEFAULT_MAP_PATH, DEFAULT_MAP_NAME
from rps.utils.common import insert_record


class MainCanvas(FigureCanvasQTAgg):
    """
    Matplotlib画布类, 用于显示地图和路径
    """

    start_signal = Signal()
    finish_signal = Signal(int)
    result_signal = Signal(str, dict)

    def __init__(self, parent=None):
        self.parent = parent
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        super().__init__(self.fig)
        self.threadpool = QThreadPool()
        self.lines = {}
        self.graph = Graph()
        self.circles = []
        self.cids = []
        self.map_file = ""
        self.editing = False
        try:
            self.load(DEFAULT_MAP_NAME)
        except FileNotFoundError:
            pass
        self.finish_signal.connect(self.draw_result)

    def load(self, name=None, path=DEFAULT_MAP_PATH, file=None):
        """加载本地地图文件"""
        if file is None:
            self.map_file = os.path.join(path, name + ".npz")
        else:
            if not file.endswith(".npz"):
                file += ".npz"
            self.map_file = file
        self.parent.clear_results()
        self.graph.load(file=self.map_file)
        self.draw_map()

    def run_algorithm(self, alg, run_setting):
        """运行算法"""
        if self.graph.graph is None:
            ErrorMessageBox.show("No graph loaded")
            return
        name = run_setting["name"]
        if name in self.lines:
            ErrorMessageBox.show("Name already exists")
            return
        color = run_setting["color"]
        style = run_setting["style"]
        real_time = run_setting["real_time"]
        self.lines[name] = Line2D([], [], color=color, label=name, linestyle=style)
        self.line = self.lines[name]
        self.ax.add_line(self.line)
        self.alg = alg
        self.alg.load_graph(self.graph)
        self.runner = Runner(self)
        self.runner.set_task(self.alg, real_time)
        self.threadpool.start(self.runner)

    def stop_algorithm(self):
        """停止算法"""
        self.runner.stop()

    @Slot(int)
    def draw_result(self, stopped):
        """绘制结果"""
        for circle in self.circles:
            circle.remove()
        self.circles.clear()
        if not stopped:
            path = self.alg.best_path
            self.draw_path(path)
            name = self.line.get_label()
            data = {
                "class": self.alg.__class__.__name__,
                "length": self.alg.best_path.length,
                "turn_num": self.alg.best_path.turn_num,
                "history": (
                    self.alg.length_history
                    if hasattr(self.alg, "length_history")
                    else None
                ),
            }
            insert_record(
                data["class"], data["length"], data["turn_num"], data["history"]
            )
            self.result_signal.emit(name, data)
        else:
            self.clear_path(self.line.get_label())
        self.ax.set_title("")

    def draw_point(self, point):
        """绘制点"""
        x, y = point
        circle = Circle((y, x), 0.5, color=self.line.get_color(), fill=True)
        self.circles.append(circle)
        self.ax.add_patch(circle)
        self.draw()
        self.flush_events()

    def draw_path(self, path):
        """绘制路径"""
        if not path:
            return
        y, x = zip(*path)
        self.line.set_data(x, y)
        self.ax.legend()
        self.draw()
        self.flush_events()

    def draw_map(self):
        """绘制地图"""
        # 清空画布
        self.ax.clear()
        # 画网格
        for x in range(self.graph.length):
            self.ax.plot(
                (x - 0.5, x - 0.5), (-0.5, self.graph.width - 0.5), "k", lw=0.2
            )
        for y in range(self.graph.width):
            self.ax.plot(
                (-0.5, self.graph.length - 0.5), (y - 0.5, y - 0.5), "k", lw=0.2
            )
        # 显示地图
        self.ax.imshow(self.graph.graph, cmap="Greys", origin="lower")
        # 设置刻度
        self.ax.set_xticks(np.arange(0, self.graph.length, self.graph.length // 20))
        self.ax.set_yticks(np.arange(0, self.graph.width, self.graph.width // 20))
        # 放置起始点
        self.ax.add_patch(
            Rectangle(
                (self.graph.start.y - 0.5, self.graph.start.x - 0.5),
                1,
                1,
                color="g",
                fill=True,
            )
        )
        self.ax.add_patch(
            Rectangle(
                (self.graph.end.y - 0.5, self.graph.end.x - 0.5),
                1,
                1,
                color="r",
                fill=True,
            )
        )
        self.draw()
        self.flush_events()

    def clear_path(self, name):
        """清除路径"""
        if name != "all":
            self.lines[name].remove()
            self.lines.pop(name)
        else:
            for line in self.lines.values():
                line.remove()
            self.lines.clear()
        self.draw()
        self.flush_events()

    def clear(self):
        """清空画布"""
        self.ax.clear()
        self.draw()
        self.flush_events()
        self.lines.clear()

    def edit(self, file=None, width=None, length=None, new=False):
        """编辑地图"""
        self.parent.clear_results()
        self.clear()
        self.editing = True

        if file is None:
            file = self.map_file
        if width is None:
            width = self.graph.width
        if length is None:
            length = self.graph.length

        self.save_file = file
        self.edit_width = width
        self.edit_length = length

        if new:
            self.grid = np.zeros((width, length), dtype=int)
            self.grid[width // 2][length // 2] = 1
            self.edit_start = np.array([width - 1, 0])
            self.edit_end = np.array([0, length - 1])
        else:
            data = np.load(file)
            self.grid = data["graph"]
            self.edit_start = data["start"]
            self.edit_end = data["end"]

        for x in range(length):
            self.ax.plot((x - 0.5, x - 0.5), (-0.5, width - 0.5), "k", lw=0.2)
        for y in range(width):
            self.ax.plot((-0.5, length - 0.5), (y - 0.5, y - 0.5), "k", lw=0.2)

        self.start_dot = plt.Circle(
            (self.edit_start[1], self.edit_start[0]), 0.5, color="g"
        )
        self.end_dot = plt.Circle((self.edit_end[1], self.edit_end[0]), 0.5, color="r")
        self.ax.add_artist(self.end_dot)
        self.ax.add_artist(self.start_dot)

        self.im = self.ax.imshow(self.grid, cmap="Greys", origin="lower")
        self.ax.set_xticks(np.arange(0, length, max(1, length // 20)))
        self.ax.set_yticks(np.arange(0, width, max(1, width // 20)))

        self.draw()
        self.flush_events()

        self.cids.append(self.mpl_connect("button_press_event", self.onclick))
        self.cids.append(self.mpl_connect("key_press_event", self.on_key))

    @Slot()
    def save_edit(self):
        """保存编辑"""
        for cid in self.cids:
            self.mpl_disconnect(cid)
        self.cids.clear()
        np.savez(
            self.save_file, graph=self.grid, start=self.edit_start, end=self.edit_end
        )
        self.load(file=self.save_file)
        self.edit_width = None
        self.edit_length = None
        self.grid = None
        self.edit_start = None
        self.edit_end = None
        self.start_dot = None
        self.end_dot = None
        self.im = None
        self.editing = False

    def onclick(self, event):
        x = round(event.ydata)
        y = round(event.xdata)
        if (x == self.edit_start[0] and y == self.edit_start[1]) or (
            x == self.edit_end[0] and y == self.edit_end[1]
        ):
            return
        self.grid[x][y] = 1 - self.grid[x][y]
        self.im.set_data(self.grid)
        self.draw()
        self.flush_events()

    def on_key(self, event):
        if event.key == "1":
            x = round(event.ydata)
            y = round(event.xdata)
            if self.grid[x][y] == 1:
                return
            self.edit_start[0] = x
            self.edit_end[1] = y
            self.start_dot.center = (y, x)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        elif event.key == "2":
            x = round(event.ydata)
            y = round(event.xdata)
            if self.grid[x][y] == 1:
                return
            self.edit_end[0] = x
            self.edit_end[1] = y
            self.end_dot.center = (y, x)
            self.draw()
            self.flush_events()


class ShowDetailCanvas(FigureCanvasQTAgg):
    """
    显示路径长度变化的画布
    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        super().__init__(self.fig)

    def show_detail(self, data: dict):
        """显示路径长度变化"""
        self.ax.clear()
        for name in data:
            length = data[name]["history"]
            if length is None:
                continue
            self.ax.plot(range(len(length)), length, label=name)
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Length")
        self.ax.legend()
        self.draw()
        self.flush_events()
