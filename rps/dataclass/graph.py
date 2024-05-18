import os
from time import time
import numpy as np
from numpy.typing import NDArray
from .point import Point


# 相邻点距离
ADJ_DIST = 1
DIAG_DIST = 2**0.5

# 用于判断相邻点
ADJ = {(0, 1): 0b1000, (0, -1): 0b0100, (1, 0): 0b0010, (-1, 0): 0b0001}
DIAG = {0b1010: (1, 1), 0b1001: (-1, 1), 0b0110: (1, -1), 0b0101: (-1, -1)}


class Graph:
    """
    表示一张地图数据

    属性:
        graph: np.ndarray, 0和1构成的矩阵, 1表示障碍物, 0表示通路
        start: Point, 路径起始点
        end: Point, 路径目标点

    运算::

        假设 g: Graph, p: Point, x: int, y: int
        p in g -> bool      # 判断点p是否位于地图中且不为障碍物
        g[p] -> int         # 判断地图中的p点是否为通路(非障碍物)
        g[p] = 0 | 1        # 设置地图中点p的值
        g[x][y] -> int      # 判断地图中的点(x, y)是否为通路
        g[x][y] = 0 | 1     # 设置地图中点(x, y)的值
    """

    # 地图文件保存路径
    SAVE_DIR = os.path.join(os.getcwd(), "maps")

    def __init__(self, graph: NDArray = None, start=None, end=None):
        if graph is not None and start is not None and end is not None:
            self.graph = graph
            self.start = start
            self.end = end
            self.width = len(self.graph)
            self.length = len(self.graph[0])
            self.size = (self.width, self.length)
        self.edges = {}

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.graph[key]
        if isinstance(key, Point):
            return self.graph[key.x][key.y]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.graph[key] = value
        elif isinstance(key, Point):
            self.graph[key.x][key.y] = value

    def __contains__(self, point):
        if isinstance(point, Point):
            if 0 <= point.x < self.width and 0 <= point.y < self.length:
                if self.graph[point.x][point.y] == 0:
                    return True
        elif isinstance(point, tuple):
            if 0 <= point[0] < self.width and 0 <= point[1] < self.length:
                if self.graph[point[0]][point[1]] == 0:
                    return True
        return False

    def neighbors(self, point: Point):
        """
        获取某点的可达相邻点及距离

        参数:
            point (Point) : 图中的某一点

        生成:
            tuple[Point, float]: 下一点及距离
        """
        status = 0b0000
        for step in ADJ:
            neighbor_point = point + step
            if neighbor_point in self:
                status += ADJ[step]
                yield neighbor_point, ADJ_DIST
        for st in DIAG:
            if status & st:
                neighbor_point = point + DIAG[st]
                if neighbor_point in self:
                    yield neighbor_point, DIAG_DIST

    def load(self, name=None, path=SAVE_DIR, file=None):
        """
        从文件中加载地图

        参数:
            file (str): 地图文件路径
        """
        if name is not None and file is None:
            name = name + ".npz"
            file = os.path.join(path, name)
        data = np.load(file)
        self.graph = data["graph"]
        start = data["start"]
        end = data["end"]
        self.width = len(self.graph)
        self.length = len(self.graph[0])
        self.size = (self.width, self.length)
        self.start = Point(int(start[0]), int(start[1]))
        self.end = Point(int(end[0]), int(end[1]))
        self.edges = self.get_all_edges()

    def save(self, name=None, path=SAVE_DIR):
        """
        将当前地图保存至本地 (.npz格式)

        参数:
            name (str): 地图名（未传入则为时间戳）
            path (str): 保存路径名，默认为 maps
        """
        if not os.path.exists(path):
            os.mkdir(path)
        if name is None:
            name = str(int(time()))
        file = os.path.join(path, name)
        np.savez(
            file,
            graph=self.graph,
            start=[self.start.x, self.start.y],
            end=[self.end.x, self.end.y],
        )

    def get_all_edges(self) -> dict:
        """
        返回包含所有路径及距离的图

        返回:
            dict: 包含所有路径及长度的图
        """
        self.edges.clear()
        for i in range(self.width):
            for j in range(self.length):
                r = Point(i, j)
                if r in self:
                    self.edges[r] = {s: dist for s, dist in self.neighbors(r)}
        return self.edges
