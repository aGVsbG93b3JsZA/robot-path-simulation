import random
from .aco import ACO
from ..gui import *

class AS(ACO):
    """
    标准蚁群算法

    参考文献:
    Dorigo M, Maniezzo V, Colorni A. Ant system: optimization by a colony of cooperating agents[J]. IEEE transactions on systems, man, and cybernetics, part b (cybernetics), 1996, 26(1): 29-41.
    https://ieeexplore.ieee.org/abstract/document/484436
    """
    def __init__(
        self, 
        m: int = 20,
        nc: int = 100,
        Q: int = 300,
        alpha: float = 1.0,
        beta: float = 0.2,
        rho: float = 0.6,
        t0: float = 10
        ):
        """
        参数:
            m (int): 蚂蚁数量
            nc (int): 最大迭代次数
            Q (int): 每次迭代信息素总增量
            alpha (float): 信息素重要度
            beta (float): 启发函数重要度
            rho (float): 信息素蒸发率
            t0 (float): 初始信息素
        """
        self.m = m
        self.nc = nc
        self.Q = Q
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.t0 = t0
        # 每只蚂蚁的路径
        self.paths = [Path() for _ in range(self.m)]
        # 每只蚂蚁的路径长度
        self.lens = [0] * self.m 
        # 当前迭代次数            
        self.iter_cnt = 0
        # 当前最优路径
        self.best_path = None
        self.best_len = float('inf')

    def init_pher(self):
        self.t = {}
        for r in self.edges:
            self.t[r] = {s:self.t0 for s in self.edges[r]}

    def is_end(self) -> bool:
        return self.iter_cnt == self.nc

    def cal_H(self, r:Point, s:Point) -> float:
        return 1 / self.edges[r][s]

    def cal_P(self, r:Point, s:Point) -> float:
        return self.t[r][s]**self.alpha * self.cal_H(r, s)**self.beta

    def cal_L(self, k:int):
        return self.paths[k].length()
    
    def state_trans(self, k:int, r:Point) -> Point|None:
        # 下一步可到达的点
        allowed = [s for s in self.edges[r] if s not in self.paths[k]]
        # 若无可达点，返回为空
        if not allowed:
            return
        # 根据概率函数返回一个点
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    def tour(self, k:int):
        # 清空相关变量
        self.paths[k].clear()
        self.lens[k] = 0
        # r表示当前点
        r = self.graph.start
        self.paths[k].append(r)
        while r != self.graph.end:
            # 获得下一个点s
            if s:= self.state_trans(k, r):
                self.paths[k].append(s)
                r = s
            # 遇到死角回退一步
            else:
                r = self.paths[k].pop()
        # 计算路径长度
        self.lens[k] = self.cal_L(k)
        # 判断路径是否更短
        if self.lens[k] <= self.best_len:
            self.best_path = self.paths[k]
            self.best_len = self.lens[k]

    def global_update(self):
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] *= self.rho
        for k in range(self.m):
            for r, s in self.paths[k].get():
                self.t[r][s] += self.Q / self.lens[k]

    def iteration(self):
        for k in range(self.m):
            self.tour(k)
        self.global_update()
        self.iter_cnt += 1
        