import random
from typing_extensions import override
from rps.dataclass import Path, Point, Dir
from .ant_system import AS


class IHMACO(AS):
    """
    参考文献:
    Cui J, Wu L, Huang X, et al. Multi-strategy adaptable ant colony optimization algorithm and its application in robot path planning[J]. Knowledge-Based Systems, 2024, 288: 111459.
    https://doi.org/10.1016/j.knosys.2024.111459
    """

    def __init__(
        self,
        m: int = 50,
        nc: int = 30,
        T0: float = 1,
        Q: float = 2.5,
        alpha: float = 1,
        beta: float = 7,
        rho: float = 0.2,
        t0: float = 1,
        w1: float = 0.5,
        w2: float = 1,
        epsilon_q=0.1,
    ):
        super().__init__(m, nc, Q, alpha, beta, rho, t0)
        self.T0 = T0
        self.w1 = w1
        self.w2 = w2
        self.epsilon_q = epsilon_q

    @override
    def init_pher(self):
        dST = self.start * self.end
        self.t = {}
        for i in self.edges:
            self.t[i] = {}
            dSi = self.start * i
            diT = i * self.end
            for j in self.edges[i]:
                dSj = self.start * j
                djT = j * self.end
                a = 1 if diT > djT else 0.5
                self.t[i][j] = a * (dST / (dSi + diT) + dST / (dSj + djT)) * self.t0

    @override
    def cal_P(self, r: Point, s: Point) -> float:
        return (
            self.t[r][s] ** self.alpha
            * self.cal_H(r, s) ** self.beta
            * self.omega(r, s)
            * self.T(r, s)
        )

    @override
    def cal_H(self, r: Point, s: Point) -> float:
        return 1 / (s * self.end)

    def omega(self, r: Point, s: Point) -> float:
        dir_ij: Dir = s - r
        dir_ST: Dir = self.end - self.start
        delta = dir_ST - dir_ij
        return (5 - delta) / 15

    def T(self, r: Point, s: Point) -> float:
        if self.path > s:
            return 2 * self.T0
        return self.T0

    @override
    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        q = random.random()
        if q < self.q0:
            s = max(allowed, key=lambda s: self.cal_P(r, s))
        else:
            weights = list(map(lambda s: self.cal_P(r, s), allowed))
            s = random.choices(allowed, weights=weights)[0]
        self.local_update(r, s)
        return s

    def fitness(self, path: Path):
        return self.w1 * path.length + self.w2 * path.turn_num

    @override
    def global_update(self):
        rho = self.rho * (1 + 0.2 * self.iter_cnt / self.nc)
        for i in self.edges:
            for j in self.edges[i]:
                self.t[i][j] *= 1 - rho
        for k in range(self.m):
            for i, j in self.paths[k].get():
                fitness = self.fitness(self.paths[k])
                self.t[i][j] += self.Q / fitness

    @override
    def iteration(self):
        self.iter_cnt += 1
        iter_best_path = Path(length=float("inf"), turn_num=float("inf"))
        cnt = 0
        self.q0 = 0.1 + 2 * (self.iter_cnt - 0.45 * self.nc) ** 2 / self.nc**2
        for self.k in range(self.m):
            if cnt > 0.5 * self.m:
                self.q0 = self.epsilon_q * self.q0
            self.tour(self.k)
            if self.path.valid and self.is_better_path(self.path, iter_best_path):
                iter_best_path = self.path
            else:
                cnt += 1
        if self.is_better_path(iter_best_path, self.best_path):
            self.best_path = iter_best_path.copy()
        self.global_update()
