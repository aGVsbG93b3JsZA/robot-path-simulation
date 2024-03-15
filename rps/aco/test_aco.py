from .ant_system import ACO, AS
from ..gui import Point, Dir, Path, RecordPath
from math import ceil
import random
from collections import defaultdict



class MHACO(ACO):
    def __init__(
        self, 
        m: int = 20, 
        nc: int = 25, 
        Q: float = 30, 
        alpha: float = 1, 
        beta1: float = 1, 
        beta2: float = 2, 
        rho: float = 0.5, 
        rho2: float = 0.2,
        t0: float = 1,
        q1: float = 0.5,
        q2: float = 0.5
        ):
        """
        m (int): 蚂蚁数量
        nc (int): 最大迭代次数
        Q (int): 信息素更新量
        alpha (float): 信息素权重幂系数
        beta1 (float): 蚁群1启发式函数权重幂系数
        beta2 (float): 蚁群2启发式函数权重幂系数
        rho (float): 全局信息素蒸发系数
        rho2 (float): 局部信息素蒸发系数
        t0 (float): 初始信息素
        q1 (float): 
        """
        self.m = m
        self.nc = nc
        self.Q = Q
        self.alpha = alpha
        self.beta1 = beta1
        self.beta2 = beta2
        self.rho = rho
        self.rho2 = rho2
        self.t0 = t0
        self.q1 = q1
        self.q2 = q2
        # 每只蚂蚁的路径
        self.paths = [Path() for _ in range(self.m)]
        # 当前蚂蚁的路径
        self.path: Path = None
        # 当前迭代次数            
        self.iter_cnt = 0
        # 当前最优路径
        self.best_path = Path()
        self.best_path.length = float('inf')
        self.last_best_path = self.best_path
        # 重载路径
        self.record_path = RecordPath()
        self.max_t = 10
        self.min_t = 1

    def init_pher(self):
        dist_0 = self.graph.width * self.graph.length
        self.dist = defaultdict(lambda: dist_0)
        self.dist[self.start] = 0
        self.t = {}
        for r in self.edges:
            self.t[r] = {s:self.t0 for s in self.edges[r]}

    def allowed(self, r: Point) -> list[Point|None]:
        options = []
        for s in self.edges[r]:
            if s not in self.paths[self.k]:
                options.append(s)
        return options

    def cal_H_1(self, r: Point, s: Point) -> float:
        """计算蚁群1启发函数"""
        res = (self.end - s) - (s - r)
        if self.path > s:
            res *= 2
        if s not in self.best_path:
            res *= 2
        return res
    
    def cal_H_2(self, r: Point, s: Point, target: Point) -> float:
        """计算蚁群2启发函数"""
        res = (target - s) - (s - r)
        # res **= 1 / (r / target)
        if self.path > s:
            res *= 2
        if s not in self.best_path:
            res *= 2
        return res
    
    def cal_P_1(self, r: Point, s: Point) -> float:
        """计算蚁群1概率"""
        return self.t[r][s]**self.alpha * self.cal_H_1(r, s)**self.beta1

    def cal_P_2(self, r:Point, s:Point, target:Point):
        """计算蚁群2概率"""
        return self.t[r][s]**self.alpha * self.cal_H_2(r, s, target)**self.beta2
    
    def state_trans_1(self, r: Point) -> Point:
        """蚁群1状态转移函数"""
        allowed = self.allowed(r)
        if not allowed:
            return
        if random.random() < self.q1:
            return max(allowed, key=lambda s: self.cal_P_1(r, s))
        else:
            weights = list(map(lambda s: self.cal_P_1(r, s), allowed))
            return random.choices(allowed, weights=weights)[0]
        
    def state_trans_2(self, r:Point, target: Point):
        """蚁群2状态转移函数"""
        allowed = self.allowed(r)
        if not allowed:
            return
        if random.random() < self.q2:
            return max(allowed, key=lambda s: self.cal_P_2(r, s, target))
        weights = list(map(lambda s: self.cal_P_2(r, s, target), allowed))
        return random.choices(allowed, weights=weights)[0]

    def path_is_better(self, path: Path) -> bool:
        """判断路径path是否为更优的路径"""
        if self.path.length < self.best_path.length:
            return True
        if self.path.length == self.best_path.length and self.path.turn_num < self.best_path.turn_num:
            return True
        return False

    def tour_1(self, k):
        """蚁群1进行路径探索"""
        self.path: Path = self.paths[k]
        self.path.clear()
        r = self.start
        self.path.append(r)
        # while True:
        #     if s:= self.state_trans_1(r):
        #         if s in self.best_path:
        #             pass
        #         pass
        #     else:
        #         self.path.clear()
        #         return
        while r != self.end:
            if s:= self.state_trans_1(r):
                # self.dist[s] = min(self.dist[s], self.dist[r] + self.edges[r][s])
                self.path.append(s)
                r = s
            else:
                self.path.clear()
                return
        if self.path_is_better(self.path):
            self.best_path = self.path.copy()

    def tour_2(self, k):
        """蚁群2进行路径探索"""
        self.path: Path = self.paths[k]
        r = self.start
        while r != self.end:
            self.path.clear()
            self.path.append(r)
            target = self.get_target(r)
            while True:
                if s:= self.state_trans_2(r, target):
                    self.path.append(s)
                    r = s
                    # 下一点在最短路径上, 更新信息素
                    if r in self.record_path:
                        self.local_update(self.path)
                        break
                else:
                    r = target
                    break

    def get_target(self, r: Point) -> Point:
        """蚁群2寻找目标点, 目标点为当前点到终点的某一点"""
        r_pos = self.record_path.index(r)
        end_pos = len(self.record_path) -1
        delta = end_pos - r_pos
        gamma = (self.m-self.k) / self.m
        # gamma = random.random()
        target_pos = r_pos + ceil(delta * gamma)
        return self.record_path[target_pos]

    def global_update_1(self) -> None:
        """蚁群1全局信息素更新"""
        if self.last_best_path != self.best_path:
            for r, s in self.last_best_path.get():
                self.t[r][s] = self.min_t
            self.last_best_path = self.best_path
        for r, s in self.best_path.get():
            self.t[r][s] = min(self.max_t, self.iter_cnt)

    def local_update(self, path: Path):
        """蚁群2局部信息素更新"""
        start = self.record_path.index(path[0])
        end = self.record_path.index(path[-1])
        delta_t = self.record_path.dist(path[-1]) - self.record_path.dist(path[0]) - path.length
        if delta_t > 0:
            # 惩罚原有路径
            while start != end:
                r = self.record_path[start]
                s = self.record_path[start+1]
                # self.t[r][s] *= self.rho2
                self.t[r][s] = self.min_t
                start += 1
            # 奖励新路径
            for r, s in path.get():
                # self.t[r][s] = max(self.max_t, self.t[r][s] + delta_t)
                self.t[r][s] = min(self.iter_cnt, self.max_t)

    def iteration(self) -> None:
        self.iter_cnt += 1
        if self.iter_cnt % 6 == 0:
            self.record_path.load(self.best_path)
            for self.k in range(self.m):
                self.tour_2(self.k)
        else:
            for self.k in range(self.m):
                self.tour_1(self.k)
            self.global_update_1()
    
    def is_end(self) -> bool:
        return self.iter_cnt == self.nc









class TestACO(AS):

    def __init__(
        self, 
        m: int = 20, 
        nc: int = 100, 
        Q: float = 300, 
        alpha: float = 1, 
        beta: float = 1, 
        rho: float = 0.5, 
        t0: float = 1/30,
        q0: float = 0.5
        ):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.q0 = q0
        
    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        q = random.random()
        if q < self.q0:
            return max(allowed, key=lambda s: self.cal_P(r, s))
        else:
            weights = list(map(lambda s: self.cal_P(r, s), allowed))
            return random.choices(allowed, weights=weights)[0]

    def init_pher(self):
        self.vis = set()
        self.dist = {}
        self.h = {}
        for r in self.edges:
            self.h[r] = {s:self.t0 for s in self.edges[r]}
        self.dist[self.end] = 0
        self.edges[self.end][self.end] = 0
        self.dfs_end(self.end, self.end)
        # return super().init_pher()
        self.t = self.h
    

    def dfs_end(self, s: Point, fa: Point):
        self.vis.add(s)
        if s == self.start:
            return
        self.dist[s] = self.dist[fa] + self.edges[s][fa]
        dir: Dir = self.start - s
        for r in dir.towards_points(s):
            if r in self.graph:
                self.h[r][s] = 1 / (self.edges[r][s] + self.dist[s])
                if r not in self.vis:                
                    self.dfs_end(r, s)
    
    def dfs_start(self, r: Point):
        if r in self.vis:
            pass
        dir: Dir = self.end - r
        for s in dir.towards_points(r):
            self.dfs_start(s)
        

    def cal_H(self, r: Point, s: Point) -> float:
        res = 1
        if (s - r) == (self.end - r):
            res *= 1.5
        if self.path > s:
            res *= 1.5
        return res



