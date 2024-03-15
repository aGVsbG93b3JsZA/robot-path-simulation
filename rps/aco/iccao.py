from math import exp, atan
import random
from heapq import *

from rps.gui import Path, Dir, Point
from .aco import ACO

class NewPath(Path):
    def __init__(self, path: list = None):
        super().__init__(path)
        # 路径变化的角度
        self.alpha = 0


class IAACO(ACO):

    def __init__(
        self,
        m: int = 20,
        nc: int = 100,
        alpha: float = 0.5,
        beta: float = 0.5,
        lambda_: float = 0.5,
        Q: float = 100,
        kappa: float = 0.5,
        q0: float = 0.5,
        ) -> None:
        """
        参数:
            m (int): 蚂蚁数量
            nc (int): 最大迭代次数
            alpha (float): 信息素权重系数
            beta (float): 启发函数权重系数
            lambda_ (float): 角度导向函数权重系数
            Q (float): 每条路径信息素增加总量
            kappa (float): 
            q0 (float): 伪随机算法阈值
        """
        self.m = m
        self.nc = nc
        self.alpha = alpha
        self.beta = beta
        self.lambda_ = lambda_
        self.Q = Q
        self.kappa = kappa
        self.q0 = q0
        # 当前迭代次数
        self.iter_cnt = 0
        # 所有路径
        self.paths = [Path() for _ in range(m)]

    def init_pher(self) -> None:
        self.t = {}
        for r in self.edges:
            self.t[r] = {s: 1 for s in self.edges[r]}
        self.init_Di0()

    def cal_Di0(self, i: Point) -> float:
        """计算点i到最近的障碍物的距离"""
        q = []
        vis = set()
        heappush(q, (0, i))
        while q:
            dist, r = heappop(q)
            if r not in self.graph:
                return dist
            vis.add(r)
            for dir in Dir.all_dirs():
                s = r + dir
                if s in vis:
                    continue
                dist = i * s
                heappush(q, (dist, s))            

    def init_Di0(self) -> None:
        """计算所有点的Di0"""
        self.di0 = {}
        for i in self.edges:
            self.di0[i] = self.cal_Di0(i)

    def cal_H(self, r: Point, s: Point) -> float:
        epsilon = exp(-2 * (self.iter_cnt / self.nc) ** 2)
        sigma1 = 0.5
        sigma2 = 1 - sigma1
        Dij = self.edges[r][s]
        DjG = self.s * self.end
        return epsilon * 1 / (sigma1 * Dij + sigma2 * DjG)
    
    def cal_mu(self, r: Point, s: Point) -> float:
        """计算角度引导因子"""
        return abs(s.y - self.end.y) / (s * self.end)
    
    def cal_xi(self, r: Point) -> float | int:
        """计算障碍物排除因子"""
        return 1

    def cal_P(self, r: Point, s: Point) -> float:
        return (self.t[r][s] ** self.alpha) * (self.cal_H(r, s) ** self.beta) * (self.cal_mu(r, s) ** self.lambda_) * self.cal_xi(r) 

    def allowed(self, r: Point) -> list[Point | None]:
        options = []
        for s in self.edges[r]:
            options.append(s)
        return options

    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        #  δ0 is the proportional coefficient, its value range is [0.1, 0.5];
        delata_0 = 0.5
        q0 = delata_0 * exp(-1/2 * (self.iter_cnt / self.nc) ** 2)
        q = random.random()
        if q <= q0:
            return max(allowed, key=lambda s: self.cal_P(r, s))
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    def tour(self, k:int) -> None:
        self.paths[k].clear()
        self.paths[k].valid = True
        r = self.start
        self.paths[k].append(r)
        while r != self.end:
            if s:= self.state_trans(s):
                self.paths[k].append(s)
                r = s
            else:
                self.paths[k].valid = False
                return


    def cal_L(self, k: int) -> float:
        return self.paths[k].length
    
    def cal_S(self, k: int) -> float:
        """计算第k条路径的安全指标"""
        Nrist = 1
        res = 0
        for p in self.paths[k][:-1]:
            res += self.di0[p]
        return res / Nrist

    def cal_alpha(r, s):
        """计算角度变量"""



    def cal_E(self, k: int) -> float:
        delta_1 = 0.5
        delta_2 = 1 - delta_1


    def cal_J(self):
        pass

    def cal_rho(self):
        pass
    

    def iteration(self, k: int) -> None:
        """
        find J best
        find J worst
        global_update
        """
        for self.k in range(self.m):
            self.tour(self.k)


    def global_update(self) -> None:
        """
        cal_rho
        update global pheromone on all effective paths by Equations
        update the pheromone on the optimal path by Equation
        update the pheromone on the worst path by Equation
        """
        for k in range(self.m):
            if self.paths[k].valid:
                for r, s in self.paths[k].get():
                    self.t[r][s]

