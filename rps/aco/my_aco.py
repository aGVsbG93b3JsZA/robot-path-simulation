from math import ceil
import random
from .ant_system import AS
from ..gui import *


class MyACO(AS):
    
    def __init__(
        self, 
        m: int = 20, 
        nc: int = 100, 
        alpha: float = 2, 
        beta: float = 5, 
        t0: float = 1,
        m1: int = 5,
        m2: int = 10,
        q0: float = 0.8
        ):
        super().__init__(m, nc, alpha, beta, t0)
        self.record_path = RecordPath()
        self.m1 = m1
        self.m2 = m2
        self.gamma = 1
        self.q0 = q0


    def init_pher(self):
        self.t = {}
        for r in self.edges:
            self.t[r] = {}
            dr = self.start / r
            for s in self.edges[r]:
                self.t[r][s] = self.t0 / (dr + self.edges[r][s] + s * self.end)
    
    def cal_P(self, r: Point, s: Point) -> float:
        return self.t[r][s]**self.alpha

    def cal_elite_P(self, r:Point, s:Point, target:Point):
        return (1 / (self.edges[r][s] + s / target)) ** self.beta

    def get_start(self) -> Point:
        div = (len(self.record_path) - 1) / self.m2
        pos = int(div * (self.k-1))
        return self.record_path[pos]

    def get_target(self, r: Point) -> Point:
        """寻找目标点, 目标点为当前点到终点的某一点"""
        r_pos = self.record_path.index(r)
        end_pos = len(self.record_path) -1
        delta = end_pos - r_pos
        target_pos = r_pos + ceil(delta * self.gamma)
        # target_pos = r_pos + ceil(delta / 2)
        # target_pos = end_pos
        return self.record_path[target_pos]

    def local_update(self, path: Path):
        delta_t = self.record_path.dist(path[-1]) - self.record_path.dist(path[0]) - path.length
        # 新找的路径长度小于原有长度，更新信息素
        if delta_t > 0:
            for r, s in path.get():
                self.t[r][s] += delta_t

    def elite_state_trans(self, r:Point, target: Point):
        allowed = self.allowed(r)
        if not allowed:
            return
        if random.random() < self.q0:
            return max(allowed, key=lambda s: self.cal_elite_P(r, s, target))
        weights = list(map(lambda s: self.cal_elite_P(r, s, target), allowed))
        return random.choices(allowed, weights=weights)[0]


    def elite_tour(self, k:int):
        # r 表示当前点
        r = self.start
        # r = self.get_start()
        while r != self.end:
            self.paths[k].clear()
            self.paths[k].append(r)
            target = self.get_target(r)
            # print(r, end=' -> ')
            while True:
                # 获得下一个点 s
                if s:= self.elite_state_trans(r, target):
                    self.paths[k].append(s)
                    r = s
                    # 下一点在最短路径上, 更新信息素
                    if r in self.record_path:
                        self.local_update(self.paths[k])
                        break
                # 遇到死角回退一步
                else:
                    r = self.paths[k].pop()
        # print()


    def normal_tour(self, k:int):
        return super().tour(k)

    def global_update(self):
        if self.iter_cnt & 1:
            for r in self.t:
                for s in self.t[r]:
                    self.t[r][s] = 0.1
            for r, s in self.best_path.get():
                self.t[r][s] = self.t0
            self.record_path.load(self.best_path)
            
    def tour(self, k):
        if self.iter_cnt & 1:
            return self.normal_tour(k)
        return self.elite_tour(k)
    
    def iteration(self):
        self.iter_cnt += 1
        if self.iter_cnt & 1:
            self.m = self.m1
        else:
            # print('cnt:', self.iter_cnt)
            self.m = self.m2
            self.gamma = 1 - (self.iter_cnt-1) / self.nc
        for self.k in range(self.m):
            self.tour(self.k)
        self.global_update()



class TEST_ACO(AS):

    def __init__(
        self, 
        m = 30,
        alpha: float = 1, 
        beta: float = 5, 
        t0: float = 10
        ):
        super().__init__(m, alpha, beta, t0)
        # 利用队列模拟递归
        self.start_end_stack =[]
        # 用于记录每次递归信息素最大的点
        self.max_points = set()
        # 最终路径
        self.final_path = Path()
        self.min_t = 1
        # self.max_tao = 300

    def init_pher(self):
        self.tp = {}
        self.t = {}
        for r in self.edges:
            self.t[r] = {s:self.t0 for s in self.edges[r]}
            self.tp[r] = self.t0

    def load_graph(self, graph: Graph):
        self.start_end_stack.append((graph.start, graph.end))
        self.final_path.append(graph.start)
        self.max_points.add(graph.start)
        self.max_points.add(graph.end)
        return super().load_graph(graph)

    def cal_H(self, r: Point, s: Point) -> float:
        # return 1 / (s * self.end + self.paths[self.k].length + self.edges[r][s])
        return 1 / (s / self.end) / 2**0.5**(self.paths[self.k] > s)
    
    def diffuse(self, r: Point, delta_t:float):
        delta_t = delta_t / 2
        for s in self.edges[r]:
            self.tp[s] += delta_t / self.edges[r][s]

    def tour(self, k: int):
        super().tour(k)
        self.tour_update(k)

    def tour_update(self, k):
        """每只蚂蚁走完路径后更新信息素"""
        length = self.cal_L(k)
        ds = 0  # 起点到当前点的距离
        delta_t0 = (self.best_path.length - length) / self.m
        for r, s in self.paths[k].get():
            ds += self.edges[r][s]
            delta_t = delta_t0
            # delta_t = min(ds, length-ds) / (length ** 2) * delta_t0
            self.t[r][s] += delta_t
            self.t[r][s] = max(self.t[r][s], self.min_t)
            self.tp[s] += delta_t
            self.diffuse(s, delta_t)

    def global_update(self):
        # 寻找信息素最大的点
        options = set()
        for k in range(self.m):
            options |= self.paths[k].points
        options -= self.max_points
        max_point = max(options, key=lambda p: self.tp[p])
        self.max_points.add(max_point)
        # 递归入栈
        self.start_end_stack.append((max_point, self.end))   
        self.start_end_stack.append((self.start, max_point))
        
    def iteration(self):
        # 每次迭代前重新设置起始点
        self.start, self.end = self.start_end_stack.pop()
        # 设置蚂蚁数量
        self.m = round(self.start / self.end)
        # 若起始点为相邻点，跳过本次迭代
        if self.end in self.edges[self.start]:
            self.final_path.append(self.end)
            self.best_path = self.final_path
            self.iter_cnt += 1
            return 
        self.best_path.length = float('inf')
        super().iteration()
    
    def is_end(self) -> bool:
        if not self.start_end_stack:
            return True
        return False


class MyAS(AS):

    def __init__(self, m: int = 30, nc: int = 100, Q: int = 300, alpha: float = 1, beta: float = 10, rho: float = 0.5, t0: float = 20):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.min_t = 1
    
    def cal_H(self, r: Point, s: Point) -> float:
        # return 1 / (s / self.end) / 2**0.5**(self.paths[self.k] > s)
        return 1 / (s / self.end)
    
    def tour_update(self, k):
        for r, s in self.paths[k].get():
            delta_len = self.best_path.length - self.paths[k].length
            delta_len = delta_len if delta_len else -1
            self.t[r][s] += delta_len
            self.t[r][s] = max(self.min_t, self.t[r][s])

    def tour(self, k: int):
        super().tour(k)
        self.tour_update(k)


    def global_update(self):
        self.beta /= self.iter_cnt