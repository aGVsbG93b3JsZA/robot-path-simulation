import os
import random
import numpy as np
import matplotlib.pyplot as plt
from .point import Point
from .graph import Graph
from .path import Path


class Map:
    """
    具有GUI功能的地图, 可加载算法并显示路径

    属性:
        graph (Graph): 可选, 加载初始地图
    """

    def __init__(self, graph: Graph = None, figsize: tuple = (7, 7)):

        if graph is not None:
            self.graph = graph
            self.graph.edges = self.graph.get_all_edges()

        self.fig, self.ax = plt.subplots(figsize=figsize)

    def load(self, name: str = "default", path: str = Graph.SAVE_DIR):
        """
        加载本地地图文件, 默认路径为maps/

        参数:
            name (str): 地图名, 默认为'default'
            path (str): 地图文件夹路径, 默认为'maps'
        """
        name = name + ".npz"
        file = os.path.join(path, name)
        data = np.load(file)
        graph = data["graph"]
        start = Point(int(data["start"][0]), int(data["start"][1]))
        end = Point(int(data["end"][0]), int(data["end"][1]))
        self.graph = Graph(graph, start, end)
        self.graph.edges = self.graph.get_all_edges()
        self._draw_map()

    def random_map(self, size: tuple = (20, 20), alpha: float = 0.2):
        """
        生成随机地图

        参数:
            size (tuple): 表示地图尺寸: (width, length)
            alpha (float): 障碍物数/地图方格数, 0 < alpha < 1
        """
        start = Point(0, 0)
        end = Point(size[0] - 1, size[1] - 1)
        graph = Graph(np.zeros(size), start, end)

        # 生成下一点
        def random_move(point: Point):
            within_map = lambda p: p in graph
            steps = list(filter(within_map, [point + (0, 1), point + (1, 0)]))
            return random.choice(steps)

        # 随机生成一条通路
        path = set()
        pos = start
        while pos != end:
            path.add(pos)
            pos = random_move(pos)
        path.add(end)
        # 生成随机障碍物
        block_num = int(size[0] * size[1] * alpha)
        i = 0
        while i < block_num:
            block = Point(random.randrange(size[0]), random.randrange(size[1]))
            if (block not in path) and (block in graph):
                graph[block.x][block.y] = 1
                i += 1
        self.graph = graph
        self.graph.edges = self.graph.get_all_edges()
        self._draw_map()

    def apply(self, algorithm: object, show=False, save_name=None, label=None):
        """
        在地图上应用算法（静态）

        参数:
            algorithm (object): 实例化的算法对象
            show (bool): 是否立即显示
        """
        algorithm.load_graph(self.graph)
        path = algorithm.search()
        print(f"Length: {path.length:.2f}")
        if label is None:
            label = algorithm.__class__.__name__
        self._draw_path(path, label=label)
        self.ax.legend()
        if save_name is not None:
            self.save_svg(name=save_name)
        if show:
            self.show()

    def apply_real_time(self, algorithm: object):
        """
        在地图上应用算法（动态显示）

        参数:
            algorithm (objcet): 实例化算法对象
        """
        algorithm.load_graph(self.graph)
        if algorithm.CLASS == "ACO":
            self._aco_real_time(algorithm)
        elif algorithm.CLASS == "A_STAR":
            self._astar_real_time(algorithm)

    def _astar_real_time(self, algorithm):
        """Dijkstra, A*算法动态显示"""
        with plt.ion():
            self.ax.set_title(algorithm.__class__.__name__)
            for point in algorithm.search_real_time():
                self.ax.plot(
                    point.y, point.x, "oy", markersize=350 / max(self.graph.size)
                )
                plt.pause(0.001)
            self._draw_path(algorithm.path, color=0)
        plt.show()

    def _aco_real_time(self, algorithm):
        """蚁群算法动态显示"""
        with plt.ion():
            for path in algorithm.search_real_time():
                self.ax.clear()
                self._draw_map()
                self.ax.set_title(
                    algorithm.__class__.__name__
                    + f"  iteration:{algorithm.iter_cnt}  length:{path.length:.2f}"
                )
                if path:
                    self._draw_path(path, color=0)
                    plt.pause(0.001)
        plt.show()

    def _draw_path(self, path: Path, color: int = None, label: str = None):
        """绘制算法路径"""
        x, y = zip(*path)
        if color is None:
            self.ax.plot(y, x, label=label)
        else:
            colors = ["r", "g", "b", "y", "m", "c"]
            self.ax.plot(y, x, colors[color])

    def _draw_map(self):
        """绘制初始地图"""
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
        self.ax.set_xticks(
            np.arange(0, self.graph.length, max(1, self.graph.length // 20))
        )
        self.ax.set_yticks(
            np.arange(0, self.graph.width, max(1, self.graph.width // 20))
        )
        # 画起点和终点
        self.ax.add_patch(
            plt.Circle(
                (self.graph.start.y, self.graph.start.x),
                0.5,
                color="g",
                fill=True,
                zorder=10,
            )
        )
        self.ax.add_patch(
            plt.Circle(
                (self.graph.end.y, self.graph.end.x),
                0.5,
                color="r",
                fill=True,
                zorder=10,
            )
        )

    def show(self, save_name=None):
        """
        显示GUI界面

        参数:
            save (bool): 是否保存此次地图, 默认不保存
        """
        plt.show()
        if save_name is not None:
            self.graph.save(name=save_name)

    def save_svg(self, name: str = "default", path: str = "images"):
        """
        保存地图为svg格式

        参数:
            name (str): 地图名, 默认为'default'
            path (str): 保存路径, 默认为'maps'
        """
        name = name + ".svg"
        file = os.path.join(path, name)
        if not os.path.exists(path):
            os.makedirs(path)
        plt.savefig(file, format="svg")
