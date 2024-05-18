from heapq import *
from collections import defaultdict
from rps.dataclass import Path
from .a_star import A_Star_Base


class Dijkstra(A_Star_Base):

    def __init__(self):
        # 各点与起始点距离
        self.d = defaultdict(lambda: float("inf"))
        # 存储各点的父节点
        self.fa = {}
        # 已访问节点
        self.vis = set()
        # 生成的路径
        self.path = None

    def _search(self):
        q = []  # 用于存储小根堆
        self.d[self.graph.start] = 0
        heappush(q, (0, self.graph.start))
        while q:
            d0, r = heappop(q)
            if r in self.vis:
                continue
            yield r
            self.vis.add(r)
            if r == self.graph.end:
                self._get_path()
                return
            for s in self.edg[r]:
                if self.edg[r][s] + d0 < self.d[s]:
                    self.d[s] = d0 + self.edg[r][s]
                    self.fa[s] = r
                    heappush(q, (self.d[s], s))

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

    def search(self, graph=None):
        if graph is not None:
            self.load_graph(graph)
        for _ in self._search():
            pass
        return self.path

    def search_real_time(self):
        return self._search()
