from typing import Generator
from rps.dataclass import Point, Graph, Path


class ACO:
    """
    蚁群算法基类

    参考文献:
    Dorigo M, Birattari M, Stutzle T. Ant colony optimization[J]. IEEE computational intelligence magazine, 2006, 1(4): 28-39.
    https://doi.org/10.1109/MCI.2006.329691

    含外部调用的接口函数，以及蚁群算法内部函数定义

    常用变量名::

        alpha: float        # 信息素重要度
        belta: float        # 启发函数重要度
        rho: float          # 信息素蒸发率, 0 < rho < 1
        m: int              # 蚂蚁数量
        k: int              # 表示第k只蚂蚁
        nc: int             # 最大迭代次数
        t: dict             # 信息素
        t0: float           # 初始信息素（若初始为平均分配）
        Q: float            # 每条路径分配的信息素总量
        q: float            # 利用/探索因子, 0 < q < 1
        q0: float           # 0-1随机值, 用于和q比较
        r: Point            # 当前点
        s: Point            # 下一点

        paths: list[Path]   # 所有蚂蚁的路径
        iter_cnt: int       # 当前的迭代次数
        best_path: Path     # 当前为止的最佳路径
        graph: Graph        # 地图数据
        edges: dict         # 包含所有边及长度
    """

    CLASS = "ACO"

    def load_graph(self, graph: Graph) -> None:
        """加载一张地图，并设置初始信息素"""
        self.graph = graph
        self.edges = graph.edges
        self.start = graph.start
        self.end = graph.end
        self.init_pher()

    def search(self, graph=None, return_path=True):
        """执行算法，返回一条最终路径"""
        if graph is not None:
            self.load_graph(graph)
        self.length_history = []
        self.converge = 1
        while not self.is_end():
            self.iteration()
            if self.length_history and self.length_history[-1] != self.best_path.length:
                self.converge = self.iter_cnt
            self.length_history.append(self.best_path.length)
        if return_path:
            return self.best_path
        return self.best_path.length, self.best_path.turn_num, self.converge

    def search_real_time(self) -> Generator[Path, None, None]:
        """执行算法，每次迭代产生一条实时路径"""
        self.length_history = []
        self.converge = 1
        while not self.is_end():
            self.iteration()
            if self.length_history and self.length_history[-1] != self.best_path.length:
                self.converge = self.iter_cnt
            self.length_history.append(self.best_path.length)
            yield self.best_path

    def init_pher(self) -> None:
        """设置初始信息素及其他参数"""

    def tour(self, k: int) -> None:
        """第k只蚂蚁寻找一次路径"""

    def cal_L(self, k: int) -> float:
        """计算第k只蚂蚁的路径长度"""

    def cal_H(self, r: Point, s: Point) -> float:
        """计算从当前点r到下一点s的启发函数值"""

    def cal_P(self, r: Point, s: Point) -> float:
        """计算从当前点r到下一点s的概率"""

    def allowed(self, r: Point) -> list[Point | None]:
        """从当前点r可以到达的所有下一点"""

    def state_trans(self, r: Point) -> Point:
        """从当前点r选择出下一点s"""

    def local_update(self, r: Point, s: Point):
        """局部信息素更新(可选)"""

    def global_update(self) -> None:
        """全局信息素更新"""

    def iteration(self) -> None:
        """所有蚂蚁完成一次路径探索，为一次迭代"""

    def is_end(self) -> bool:
        """判断是否结束"""
