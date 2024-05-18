from heapq import *
from collections import defaultdict
from rps.dataclass import Path, Graph


class MethodError(Exception):
    """算法不支持动态/静态显示"""


class A_Star_Base:

    CLASS = "A_STAR"

    def load_graph(self, graph: Graph):
        self.graph = graph
        self.edg = graph.edges  # 字典表示的图

    def search(self):
        raise MethodError(f"{self.__class__.__name__} doesn't support search")

    def search_real_time(self):
        raise MethodError(f"{self.__class__.__name__} doesn't support search real time")


class A_Star(A_Star_Base):

    def __init__(self) -> None:
        # 到起点的最短距离
        self.g = defaultdict(lambda: float("inf"))
        # 到终点的最短距离
        self.h = lambda p: p / self.graph.end
        # 启发函数
        self.f = lambda p: self.g[p] + self.h(p)
        # 已访问元素
        self.close = set()
        # 存放节点的父节点
        self.fa = {}
        # 生成的路径
        self.path = None

    def _search(self):
        self.g[self.graph.start] = 0
        open = []  # 待访问元素
        heappush(open, (0, self.graph.start))
        while open:
            _, r = heappop(open)
            if r in self.close:
                continue
            yield r
            if r == self.graph.end:
                self._get_path()
                return
            self.close.add(r)
            for s in self.edg[r]:
                if s in self.close:
                    continue
                if self.g[s] > self.g[r] + self.edg[r][s]:
                    self.g[s] = self.g[r] + self.edg[r][s]
                    self.fa[s] = r
                heappush(open, (self.f(s), s))

    def search(self, graph=None):
        if graph is not None:
            self.load_graph(graph)
        for _ in self._search():
            pass
        return self.path

    def search_real_time(self):
        return self._search()

    def _get_path(self):
        p = self.graph.end
        self.path = Path()
        self.path.append(p)
        start = self.graph.start
        while (p := self.fa[p]) != start:
            self.path.append(p)
        self.path.append(start)
        self.path.path.reverse()
        self.best_path = self.path
