from math import exp, atan
import random
from typing_extensions import override
from heapq import *

from rps.dataclass import Path, Dir, Point
from .aco import ACO


class IAACO(ACO):
    """
    参考文献:
    Miao C, Chen G, Yan C, et al. Path planning optimization of indoor mobile robot based on adaptive ant colony algorithm[J]. Computers & Industrial Engineering, 2021, 156: 107230.
    https://doi.org/10.1016/j.cie.2021.107230
    """

    def __init__(
        self,
        m: int = 50,
        nc: int = 30,
        alpha: float = 1,
        beta: float = 7,
        lambda_: float = 7,
        kappa: float = 0.9,
        sigma_1: float = 0.1,
        sigma_2: float = 0.9,
        delta_0: float = 0.15,
        Q: float = 2.5,
        Rs: float = 0.5,
        kL: float = 1,
        kS: float = 0,
        kE: float = 0,
    ) -> None:
        self.m = m
        self.nc = nc
        self.alpha = alpha
        self.beta = beta
        self.lambda_ = lambda_
        self.sigma_1 = sigma_1
        self.sigma_2 = sigma_2
        self.delta_0 = delta_0
        self.Q = Q
        self.kappa = kappa
        self.Rs = Rs
        self.kL = kL
        self.kS = kS
        self.kE = kE
        # 当前迭代次数
        self.iter_cnt = 0
        # 所有路径
        self.paths = [Path() for _ in range(m)]
        # 全局最优路径
        self.best_path: Path = Path()
        self.best_J = float("inf")
        self.min_t = 0.1

    @override
    def init_pher(self) -> None:
        self.t = {}
        for r in self.edges:
            self.t[r] = {s: self.Q for s in self.edges[r]}
        self.init_Di0()
        self.LSG = self.start * self.end

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

    @override
    def cal_H(self, r: Point, s: Point) -> float:
        epsilon = exp(-2 * (self.iter_cnt / self.nc) ** 2)
        Dij = self.edges[r][s]
        DjG = s * self.end
        return epsilon * 1 / (self.sigma_1 * Dij + self.sigma_2 * DjG)

    def cal_mu(self, r: Point, s: Point) -> float:
        """
        计算角度引导因子
        参考文献给出的公式为：μ(t) = 1 / cosφ = | yj - yG | / djG
        但这个公式有问题，在此处做了修改
        """
        if s == self.end:
            return 1
        return (s * self.end) / max(abs(s.y - self.end.y), abs(s.x - self.end.x))
        # return 1 / abs(s.y - self.end.y) / (s * self.end)

    def cal_xi(self, r: Point) -> float | int:
        """计算障碍物排除因子"""
        dib = self.di0[r]
        if dib > self.Rs:
            return 1
        if self.Rs <= dib <= self.Rs * 2:
            return self.Rs / dib
        return 0

    @override
    def cal_P(self, r: Point, s: Point) -> float:
        return (
            (self.t[r][s] ** self.alpha)
            * (self.cal_H(r, s) ** self.beta)
            * (self.cal_mu(r, s) ** self.lambda_)
            * self.cal_xi(r)
        )

    @override
    def allowed(self, r: Point) -> list[Point | None]:
        options = []
        for s in self.edges[r]:
            if s not in self.paths[self.k]:
                options.append(s)
        return options

    @override
    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        q0 = self.delta_0 * exp(-1 / 2 * (self.iter_cnt / self.nc) ** 2)
        q = random.random()
        if q <= q0:
            return max(allowed, key=lambda s: self.cal_P(r, s))
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    @override
    def tour(self, k: int) -> None:
        self.paths[k].clear()
        self.paths[k].valid = True
        r = self.start
        self.paths[k].append(r)
        while r != self.end:
            if s := self.state_trans(r):
                self.paths[k].append(s)
                r = s
            else:
                self.paths[k].valid = False
                return

    def cal_J(self, k: int) -> float:
        """计算第k条路径的多目标性能指标"""
        return (
            self.kL * self.cal_L(k) + self.kS * self.cal_S(k) + self.kE * self.cal_E(k)
        )

    def cal_L(self, k: int) -> float:
        """计算第k条路径的长度指标"""
        return self.paths[k].length

    def cal_S(self, k: int) -> float:
        """计算第k条路径的安全指标, 与最短路径无关, 故不考虑"""
        return 0

    def cal_E(self, k: int) -> float:
        """计算第k条路径的能耗指标, 与最短路径无关, 故不考虑"""
        return 0

    @override
    def iteration(self) -> None:
        self.iter_cnt += 1
        for self.k in range(self.m):
            self.tour(self.k)
        self.global_update()

    @override
    def is_end(self) -> bool:
        return self.iter_cnt == self.nc

    @override
    def global_update(self) -> None:
        pbs = Path()
        pws = Path()
        Jbest = float("inf")
        Jworst = 1
        # 寻找最优/最坏路径，更新rho
        for k in range(self.m):
            if self.paths[k].valid:
                J = self.cal_J(k)
                if J <= Jbest:
                    Jbest = J
                    pbs = self.paths[k]
                if J >= Jworst:
                    Jworst = J
                    pws = self.paths[k]
        rho = self.kappa * self.LSG / Jbest
        # 全局信息素更新
        for k in range(self.m):
            if self.paths[k].valid:
                delta_t = self.Q / self.paths[k].length
                for i, j in self.paths[k].get():
                    self.t[i][j] = (1 - rho) * self.t[i][j] + rho * delta_t
        # 最优/最坏路径信息素更新
        delta_t_pbs = self.Q / Jbest * (Jbest + Jworst) / 2
        delta_t_pws = -self.Q / Jworst
        for i, j in pbs.get():
            self.t[i][j] = (1 - rho) * self.t[i][j] + rho * delta_t_pbs
        for i, j in pws.get():
            self.t[i][j] = max((1 - rho) * self.t[i][j] + rho * delta_t_pws, self.min_t)
        # 更新全局最优路径
        if Jbest <= self.best_J:
            self.best_J = Jbest
            self.best_path = pbs.copy()
