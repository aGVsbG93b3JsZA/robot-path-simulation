from rps.dataclass import Point
from .ant_system import AS
import random


class ACS(AS):
    """
    参考文献:
    Dorigo M, Gambardella L M. Ant colony system: a cooperative learning approach to the traveling salesman problem[J]. IEEE Transactions on evolutionary computation, 1997, 1(1): 53-66.
    https://doi.org/10.1109/4235.585892
    """

    def __init__(
        self,
        m: int = 50,
        nc: int = 30,
        alpha: float = 0.1,
        beta: float = 0.2,
        rho: float = 0.1,
        t0: float = 1 / 800,
        q0: float = 0.3,
    ):
        """
        m (int): 蚂蚁数量
        nc (int): 最大迭代次数
        alpha (float): 全局信息素蒸发系数
        rho (float): 局部信息素蒸发系数
        beta (float): 启发函数幂系数
        t0 (float): 初始信息素
        q0 (float): 利用/探索阈值
        """
        super().__init__(m, nc, alpha, beta, rho, t0)
        self.q0 = q0

    def cal_P(self, r: Point, s: Point) -> float:
        return self.t[r][s] * self.cal_H(r, s) ** self.beta

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

    def local_update(self, r: Point, s: Point):
        self.t[r][s] *= 1 - self.rho
        self.t[r][s] += self.rho * self.t0

    def global_update(self):
        if self.best_path.length == float("inf"):
            return
        for r in self.edges:
            for s in self.edges[r]:
                self.t[r][s] *= 1 - self.alpha
        delta_t = 1 / self.best_path.length
        for r, s in self.best_path.get():
            self.t[r][s] += delta_t
