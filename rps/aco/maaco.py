from math import exp
import random
from typing_extensions import override
from rps.dataclass import Point, Path
from .ant_system import AS


class MAACO(AS):
    """
    参考文献:
    Wu L, Huang X, Cui J, et al. Modified adaptive ant colony optimization algorithm and its application for solving path planning of mobile robot[J]. Expert Systems with Applications, 2023, 215: 119410.
    https://doi.org/10.1016/j.eswa.2022.119410
    """

    def __init__(
        self,
        m: int = 50,
        nc: int = 30,
        Q: float = 2.5,
        alpha: float = 1,
        beta: float = 7,
        rho: float = 0.2,
        t0: float = 1,
        q0_initial: float = 0.5,
        a: float = 1,
        whmax: float = 0.9,
        whmin: float = 0.2,
    ):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.q0_initial = q0_initial
        self.a = a
        self.whmax = whmax
        self.whmin = whmin
        self.k0 = 0.7 * self.nc

    @override
    def init_pher(self) -> None:
        self.dst = self.start * self.end
        self.t = {}
        for i in self.edges:
            self.t[i] = {}
            t_initial = self.dst / (self.start * i + self.end * i) * self.t0
            for j in self.edges[i]:
                self.t[i][j] = t_initial

    @override
    def allowed(self, r: Point) -> list[Point | None]:
        options = []
        for s in self.edges[r]:
            if s not in self.path:
                options.append(s)
        dir = self.end - r
        options.sort(key=lambda s: dir - (s - r))
        return options[:3]

    @override
    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        q = random.random()
        if q <= self.q0:
            return max(allowed, key=lambda s: self.cal_P(r, s))
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    @override
    def cal_H(self, r: Point, s: Point) -> float:
        dsj = self.path.length + self.edges[r][s]
        djt = s * self.end
        k = 1  # 原论文中未给出k的值
        h = self.whmax - (self.whmax - self.whmin) * exp(-k * djt) / self.dst
        g = 1 - h
        ci = 1 - (self.path > s)
        return 1 / (g * dsj + h * djt + self.a * ci)

    @override
    def iteration(self):
        self.iter_cnt += 1
        if self.iter_cnt < self.k0:
            self.q0 = (self.nc - self.iter_cnt) / self.nc * self.q0_initial
        else:
            self.q0 = (
                self.iter_cnt - self.k0
            ) / self.nc * self.q0_initial + self.q0_initial / 2
        iter_best_path = Path(length=float("inf"), turn_num=float("inf"))
        for self.k in range(self.m):
            self.tour(self.k)
            if self.path.valid and self.is_better_path(self.path, iter_best_path):
                iter_best_path = self.path
        if self.is_better_path(iter_best_path, self.best_path):
            self.best_path = iter_best_path.copy()
        if iter_best_path.length != float("inf"):
            self.global_update()

    @override
    def global_update(self):
        t_max = (
            1 / (2 * (1 - self.rho)) * 1 / self.best_path.length
            + (1 / self.best_path.length)
        ) * 200
        t_min = t_max / 500
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] *= 1 - self.rho
        for k in range(self.m):
            for r, s in self.paths[k].get():
                self.t[r][s] += self.Q / self.paths[k].length
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] = max(t_min, min(t_max, self.t[r][s]))
