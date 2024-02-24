from math import exp
import random
from ..gui import Point
from .ant_system import AS

class MAACO(AS):
    """
    参考文献:
    Wu L, Huang X, Cui J, et al. Modified adaptive ant colony optimization algorithm and its application for solving path planning of mobile robot[J]. Expert Systems with Applications, 2023, 215: 119410.
    https://www.sciencedirect.com/science/article/abs/pii/S0957417422024290
    """
    def __init__(
        self, 
        m: int = 50, 
        nc: int = 100, 
        Q: float = 2.5, 
        alpha: float = 1, 
        beta: float = 7, 
        rho: float = 0.2, 
        t0: float = 1,
        q0: float = 0.5,
        a: float = 1,
        whmax: float = 0.9,
        whmin: float = 0.2
        ):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.q0_initial = q0
        self.a = a
        self.whmax = whmax
        self.whmin = whmin
        self.k0 = 0.7 * self.nc

    def init_pher(self) -> None:
        self.dst = self.start * self.end
        self.t = {}
        for i in self.edges:
            t_initial = self.dst / (self.start * i + self.end * i) * self.t0
            self.t[i] = {j: t_initial for j in self.edges[i]}

    def allowed(self, r: Point) -> list[Point | None]:
        options = []
        for s in self.edges[r]:
            if s not in self.paths[self.k]:
                options.append(s)
        if len(options) <= 3:
            return options
        dir = self.end - r
        allowed_dirs = [dir, dir.left(), dir.right()]
        filter_rule = lambda s: (s - r) in allowed_dirs
        options = list(filter(filter_rule, options))
        return options

    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        q = random.random()
        if q <= self.q0:
            return max(allowed, key=lambda s: self.cal_P(r, s))
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    def cal_H(self, r: Point, s: Point) -> float:
        dsj = self.edges[r][s]
        djt = s * self.end
        k = 1
        h = self.whmax - (self.whmax - self.whmin) * exp((-k * djt)/self.dst)
        g = 1 - h
        ci = self.paths[k].length + 1 - (self.paths[self.k] > s)
        return 1 / (g * dsj + h * djt + self.a * ci)

    def update_q0(self) -> None:
        if self.iter_cnt < self.k0:
            self.q0 = (self.nc - self.iter_cnt) / self.nc * self.q0_initial
        else:
            self.q0 = (self.iter_cnt - self.k0) / self.nc * self.q0_initial + self.q0_initial / 2

    def iteration(self) -> None:
        self.iter_cnt += 1
        self.update_q0()
        for self.k in range(self.m):
            self.tour(self.k)
        self.global_update()

    def global_update(self):
        t_max = 1 / (2 * (1 - self.rho)) * 1 / self.best_path.length + (1 / self.best_path.length) * 200
        t_min = t_max / 500
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] *= 1 - self.rho
                self.t[r][s] = max(self.t[r][s], t_min)
        for k in range(self.m):
            for r, s in self.paths[k].get():
                self.t[r][s] += self.Q / self.paths[k].length
                self.t[r][s] = min(self.t[r][s], t_max)
        
