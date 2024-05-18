import random
from typing_extensions import override
from .aco import ACO
from rps.dataclass import *


class AS(ACO):
    """
    标准蚁群算法

    参考文献:
    Dorigo M, Maniezzo V, Colorni A. Ant system: optimization by a colony of cooperating agents[J]. IEEE transactions on systems, man, and cybernetics, part b (cybernetics), 1996, 26(1): 29-41.
    https://doi.org/10.1109/3477.484436
    """

    def __init__(
        self,
        m: int = 20,
        nc: int = 30,
        Q: float = 300,
        alpha: float = 1.0,
        beta: float = 0,
        rho: float = 0.5,
        t0: float = 10,
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
        self.k = 0
        # 每只蚂蚁的路径
        self.paths = [Path() for _ in range(self.m)]
        # 当前蚂蚁的路径
        self.path: Path = None
        # 当前迭代次数
        self.iter_cnt = 0
        # 当前最优路径
        self.best_path = Path(length=float("inf"), turn_num=float("inf"))

    @override
    def init_pher(self):
        self.t = {}
        for r in self.edges:
            self.t[r] = {s: self.t0 for s in self.edges[r]}

    @override
    def is_end(self) -> bool:
        return self.iter_cnt == self.nc

    @override
    def cal_H(self, r: Point, s: Point) -> float:
        return 1 / self.edges[r][s]

    @override
    def cal_P(self, r: Point, s: Point) -> float:
        return self.t[r][s] ** self.alpha * self.cal_H(r, s) ** self.beta

    @override
    def allowed(self, r: Point) -> list[Point | None]:
        options = []
        for s in self.edges[r]:
            if s not in self.path:
                options.append(s)
        return options

    @override
    def state_trans(self, r: Point) -> Point | None:
        allowed = self.allowed(r)
        if not allowed:
            return
        weights = list(map(lambda s: self.cal_P(r, s), allowed))
        return random.choices(allowed, weights=weights)[0]

    @override
    def tour(self, k: int):
        # 当前路径
        self.path = self.paths[k]
        # 清空路径
        self.path.clear()
        self.path.valid = True
        # r表示当前点
        r = self.start
        self.path.append(r)
        while r != self.end:
            # 获得下一个点s
            if s := self.state_trans(r):
                self.path.append(s)
                r = s
            # 遇到死角, 提前结束
            else:
                self.path.clear()
                self.path.valid = False

    @override
    def global_update(self):
        for r in self.t:
            for s in self.t[r]:
                self.t[r][s] *= self.rho
        for k in range(self.m):
            for r, s in self.paths[k].get():
                self.t[r][s] += self.Q / self.paths[k].length

    def is_better_path(self, path: Path, cmp_path: Path) -> bool:
        """判断path是否比cmp_path更优"""
        if abs(path.length - cmp_path.length) < 0.1:
            return path.turn_num < cmp_path.turn_num
        return path.length < cmp_path.length

    @override
    def iteration(self):
        self.iter_cnt += 1
        iter_best_path = Path(length=float("inf"), turn_num=float("inf"))
        for self.k in range(self.m):
            self.tour(self.k)
            if self.path.valid and self.is_better_path(self.path, iter_best_path):
                iter_best_path = self.path
        if self.is_better_path(iter_best_path, self.best_path):
            self.best_path = iter_best_path.copy()
        self.global_update()
