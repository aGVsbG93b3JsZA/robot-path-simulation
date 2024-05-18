import numpy as np
from typing_extensions import override
from rps.dataclass import Point, LinkPath, RecordPath
from .acs import ACS
import random
from math import ceil


def cos(vertex: Point, v1: Point, v2: Point) -> float:
    """
    计算两个向量的夹角余弦值
    """
    e1 = np.array([v1.x - vertex.x, v1.y - vertex.y])
    e2 = np.array([v2.x - vertex.x, v2.y - vertex.y])
    return np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))


class ACO0(ACS):
    """
    多异体蚁群算法第一部分优化
    """

    def __init__(
        self,
        m: int = 20,
        nc: int = 30,
        alpha: float = 4,
        beta: float = 4,
        rho: float = 0.8,
        t0: float = 1,
        q0: float = 0.7,
        a: float = 10,
    ):
        super().__init__(m, nc, alpha, beta, rho, t0, q0)
        self.a = a
        self.best_path = RecordPath()
        self.iter_best_path = self.best_path

    @override
    def init_pher(self):
        # 初始化最优路径
        self.best_path.length = 1e6
        self.best_path.turn_num = 1e6
        self.target = self.end
        # 初始化信息素
        super().init_pher()

    @override
    def cal_P(self, r: Point, s: Point) -> float:
        return (
            self.t[r][s] ** self.alpha
            * self.cal_H(r, s) ** self.beta
            * self.cal_F(r, s)
        )

    @override
    def cal_H(self, r: Point, s: Point) -> float:
        return self.a ** cos(r, s, self.target)

    def cal_F(self, r: Point, s: Point) -> float:
        """计算修正函数"""
        res = 1.5 ** (-1 * (s - r - self.path.dir))
        if s in self.best_path and r in self.best_path:
            res *= 2 ** (self.best_path.index(s) - self.best_path.index(r) - 1)
        return res

    def is_better_path(self, path, cmp_path) -> bool:
        """判断路径path是否为更优的路径"""
        if abs(path.length - cmp_path.length) < 0.1:
            return path.turn_num < cmp_path.turn_num
        return path.length < cmp_path.length

    @override
    def tour(self, k: int):
        self.begin = self.start
        self.path = LinkPath()
        r = self.start
        self.path.append(r)
        while r != self.end:
            if s := self.state_trans(r):
                self.path.append(s)
                r = s
            else:
                return
        if self.is_better_path(self.path, self.iter_best_path):
            self.iter_best_path = self.path

    @override
    def iteration(self):
        self.iter_cnt += 1
        for self.k in range(self.m):
            self.tour(self.k)
        if self.is_better_path(self.iter_best_path, self.best_path):
            self.best_path.load(self.iter_best_path)


class ACO1(ACO0):
    """
    多异体蚁群算法第二部分优化
    """

    def local_refine(self, path: LinkPath, start: Point, end: Point, start_len: float):
        """局部信息素更新"""
        best_local_length = self.best_path.dist(end) - self.best_path.dist(start)
        local_length = path.length - start_len

        if local_length < best_local_length:
            delta_t = 0
            for r, s in self.best_path.get(start, end):
                delta_t += self.t[r][s]
            delta_t /= local_length
            for r, s in path.get(start, end):
                self.t[r][s] += delta_t
        else:
            delta_t = best_local_length / local_length * self.t0
            for r, s in self.best_path.get(start, end):
                self.t[r][s] += delta_t

    def get_target(self, r: Point) -> Point:
        """获取目标导向点"""
        return self.end

    @override
    def tour(self, k: int):
        self.begin = self.start
        self.path = LinkPath()
        r = self.start
        self.path.append(r)
        while r != self.end:
            start = r  # 当前起点
            start_len = self.path.length  # 当前路径长路
            self.target = self.get_target(r)
            while True:
                if s := self.state_trans(r):
                    self.path.append(s)
                    r = s
                    if r in self.best_path:
                        self.local_refine(self.path, start, r, start_len)
                        break
                    elif r == self.end:
                        break
                else:
                    return
        if self.is_better_path(self.path, self.iter_best_path):
            self.iter_best_path = self.path


class ACO2(ACO1):
    """
    多异体蚁群算法第三部分优化
    """

    def __init__(
        self,
        m: int = 20,
        nc: int = 30,
        alpha: float = 4,
        beta: float = 4,
        rho: float = 0.8,
        t0: float = 1,
        q0: float = 0.7,
        a: float = 10,
        alpha_2: float = 2,
        beta_2: float = 4,
        alpha_3: float = 2,
        beta_3: float = 2,
    ):
        super().__init__(m, nc, alpha, beta, rho, t0, q0, a)
        self.alpha_2 = alpha_2
        self.beta_2 = beta_2
        self.alpha_3 = alpha_3
        self.beta_3 = beta_3
        self.group_opt = [1, 2, 1, 1, 3, 1]

    @override
    def get_target(self, r: Point) -> Point:
        if self.group == 1:
            return self.end
        else:
            if not self.best_path:
                return self.end
            if self.group == 2:
                o = (self.m - self.k) / self.m
            else:
                o = random.random()
            r_pos = self.best_path.index(r)
            end_pos = len(self.best_path) - 1
            delta = end_pos - r_pos
            target_pos = r_pos + ceil(delta * o)
            return self.best_path[target_pos]

    @override
    def cal_P(self, r: Point, s: Point) -> float:
        if self.group == 1:
            return (
                self.t[r][s] ** self.alpha
                * self.cal_H(r, s) ** self.beta
                * self.cal_F(r, s)
            )
        elif self.group == 2:
            return (
                self.t[r][s] ** self.alpha_2
                * self.cal_H(r, s) ** self.beta_2
                * self.cal_F(r, s)
            )
        else:
            return (
                self.t[r][s] ** self.alpha_3
                * self.cal_H(r, s) ** self.beta_3
                * self.cal_F(r, s)
            )

    @override
    def iteration(self):
        self.begin = self.start
        self.iter_cnt += 1
        self.group = self.group_opt[self.iter_cnt % 6]
        for self.k in range(self.m):
            self.tour(self.k)
        if self.is_better_path(self.iter_best_path, self.best_path):
            self.best_path.load(self.iter_best_path)


class ACO3(ACO2):
    """
    多异体蚁群算法第四部分优化(总优化)
    """

    def __init__(
        self,
        m: int = 7,
        nc: int = 30,
        alpha: float = 4,
        beta: float = 4,
        rho: float = 0.8,
        t0: float = 1,
        q0: float = 0.7,
        a: float = 10,
        alpha_2: float = 2,
        beta_2: float = 4,
        alpha_3: float = 2,
        beta_3: float = 2,
    ):
        super().__init__(
            m, nc, alpha, beta, rho, t0, q0, a, alpha_2, beta_2, alpha_3, beta_3
        )
        self.best_paths = [RecordPath() for _ in range(3)]
        self.iter_best_paths = [
            self.best_paths[0],
            self.best_paths[1],
            self.best_paths[2],
        ]

    @override
    def init_pher(self):
        for i in range(3):
            self.best_paths[i].length = 1e6
            self.best_paths[i].turn_num = 1e6
        self.target = self.end
        self.ts = [{} for _ in range(3)]
        for r in self.edges:
            for t in range(3):
                self.ts[t][r] = {s: self.t0 for s in self.edges[r]}

    @override
    def cal_F(self, r: Point, s: Point) -> float:
        res = self.ts[0][r][s] + self.ts[1][r][s]
        res = self.t[r][s] / res
        return res * super().cal_F(r, s)

    @override
    def iteration(self):
        self.iter_cnt += 1
        self.group = self.group_opt[self.iter_cnt % 6]
        for self.k in range(self.m):
            for self.tribe in range(3):
                self.t = self.ts[self.tribe]
                self.best_path = self.best_paths[self.tribe]
                self.tour(self.k)
        self.global_update()

    @override
    def tour(self, k: int):
        self.begin = self.start
        self.path = LinkPath()
        r = self.start
        self.path.append(r)
        while r != self.end:
            start = r
            start_len = self.path.length
            self.target = self.get_target(r)
            while True:
                if s := self.state_trans(r):
                    self.path.append(s)
                    r = s
                    if r in self.best_path:
                        self.local_refine(self.path, start, r, start_len)
                        break
                    elif r == self.end:
                        break
                else:
                    return
        if self.is_better_path(self.path, self.iter_best_paths[self.tribe]):
            self.iter_best_paths[self.tribe] = self.path

    @override
    def global_update(self):
        for tribe in range(3):
            if self.is_better_path(self.iter_best_paths[tribe], self.best_paths[tribe]):
                self.best_paths[tribe].load(self.iter_best_paths[tribe])
        self.best_path = min(self.best_paths, key=lambda x: (x.length, x.turn_num))


class MHACO(ACO3):
    """
    多异体蚁群算法
    """
