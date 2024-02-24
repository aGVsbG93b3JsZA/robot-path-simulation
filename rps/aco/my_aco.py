from rps.gui import Graph, Point
from .ant_system import AS
from ..gui import *
from collections import deque


class MyACO(AS):

    def __init__(self, m: int = 30, nc: int = 100, Q: int = 300, alpha: float = 1, beta: float = 0.2, rho: float = 0.5, t0: float = 10):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        # 利用队列模拟递归栈
        self.start_end_stack = deque()
        # 用于记录每次递归信息素最大的点
        self.max_point = None
        self.max_t = 0
        # 最终路径
        self.final_path = Path()

    def init_pher(self):
        self.tp = {}
        self.t = {}
        for r in self.edges:
            self.t[r] = {s:self.t0 for s in self.edges[r]}
            self.tp[r] = self.t0

    def load_graph(self, graph: Graph):
        self.start_end_stack.append((graph.start, graph.end))
        self.final_path.append(graph.start)
        return super().load_graph(graph)

    def cal_H(self, r: Point, s: Point) -> float:
        turn = self.paths[self.k] > s
        return 1 / (s * self.end) * 2**0.5**turn

    def diffuse(self, r: Point, delta_t:float):
        for s in self.edges[r]:
            self.tp[s] += delta_t / self.edges[r][s]

    def global_update(self):
        self.max_t = 0
        # 信息素蒸发
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] *= self.rho
            self.tp[r] *= self.rho
        # 更新信息素
        for k in range(self.m):
            for r, s in self.paths[k].get():
                delta_t = self.Q / self.paths[k].length
                self.t[r][s] += delta_t
                self.tp[s] += delta_t
                self.diffuse(s, delta_t/2)
                # 更新信息素最大的点
                if self.tp[s] > self.max_t and (s != self.end):
                    self.max_t = self.tp[s]
                    self.max_point = s
        self.start_end_stack.appendleft((self.max_point, self.end))   
        self.start_end_stack.appendleft((self.start, self.max_point))
        
    def iteration(self):
        # 每次迭代前重新设置起始点
        self.start, self.end = self.start_end_stack.popleft()
        # 若起始点为相邻点，跳过本次迭代
        if self.end in self.edges[self.start]:
            self.final_path.append(self.end)
            self.best_path = self.final_path
            self.iter_cnt += 1
            return 
        self.best_len = float('inf')
        return super().iteration()
    
    def is_end(self) -> bool:
        if not self.start_end_stack:
            return True
        return False



















class MyAS(AS):

    def __init__(self, m: int = 30, nc: int = 100, Q: int = 300, alpha: float = 1, beta: float = 0.2, rho: float = 0.5, t0: float = 10):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.avg_len = 0
        self.sum_len = 0
        self.tour_cnt = 0
        self.min_t = 1

    
    def cal_H(self, r: Point, s: Point) -> float:
        return 1 / (s / self.end) / 2**0.5**(self.paths[self.k] > s)

    def tour_update(self, k):
        for r, s in self.paths[k].get():
            delta_len = self.paths[k].length - self.best_path.length
            delta_len = delta_len if delta_len else -1
            self.t[r][s] += delta_len
            self.t[r][s] = max(self.min_t, self.t[r][s])


    def tour(self, k: int):
        self.tour_cnt += 1
        super().tour(k)
        self.tour_update(k)


    def global_update(self):
        # self.best_path = self.paths[0]
        pass