from .point import Point, LinkPoint


class Path:
    """
    表示一条路径 (基于列表和集合存储)

    属性:
        valid (bool): 路径是否有效
        length (float): 路径长度
        turn_num (int): 路径拐角数

    """

    def __init__(self, path: list = None, length: float = 0, turn_num: int = 0):
        if path is None:
            self.path = []
            self.points = set()
        else:
            self.path = path
            self.points = set(path)
        self.length = length
        self.turn_num = turn_num
        self.valid = True

    def append(self, other):
        """添加一个路径点"""
        if self.path:
            self.length += self.path[-1] * other
            self.turn_num += 1 - (self > other)
        self.path.append(other)
        self.points.add(other)

    def pop(self, vis: bool = True) -> Point:
        """删除最后一个路径点, 返回前一个点"""
        p = self.path.pop()
        self.turn_num -= 1 - (self > p)
        if not vis:
            self.points.discard(p)
        return self.path[-1]

    def __getitem__(self, i: int):
        return self.path[i]

    def __contains__(self, p: Point):
        return p in self.points

    def __iter__(self):
        return iter(self.path)

    def __len__(self):
        return len(self.path)

    def __gt__(self, other: Point):
        """
        Path > Point
        判断下一点是否位于当前路径的方向上
        """
        if len(self.path) <= 1:
            return True
        return (other - self.path[-1]) == (self.path[-1] - self.path[-2])

    def __or__(self, other):
        """
        Path | Path
        返回两条路径的所有点集
        """
        return self.points | other.points

    def copy(self):
        return Path(self.path.copy(), length=self.length, turn_num=self.turn_num)

    def get(self):
        """依次生成路径上的两个点"""
        for i in range(len(self.path) - 1):
            yield self.path[i], self.path[i + 1]

    def clear(self, save_points=False):
        """清空路径"""
        self.path.clear()
        if not save_points:
            self.points.clear()
        self.length = 0
        self.turn_num = 0

    def __str__(self) -> str:
        return "->".join(map(str, self.path))


class LinkPath:
    """
    基于链表保存的路径, 同时支持关键字查找
    """

    def __init__(self) -> None:
        self.head = LinkPoint()
        self.rear = self.head
        self.elem = dict()
        self.length = 0
        self.turn_num = -1
        self.dir = Point(0, 0)
        self.valid = True

    def __getitem__(self, key: Point | LinkPoint) -> LinkPoint:
        if isinstance(key, LinkPoint):
            return self.elem[key.point]
        return self.elem[key]

    def __gt__(self, other: Point):
        if len(self.elem) > 1:
            return (other - self.rear.point) == self.dir
        return True

    def __len__(self):
        return len(self.elem) - 1

    def append(self, other: Point):
        if (dir := other - self.rear.point) != self.dir:
            self.turn_num += 1
            self.dir = dir
        other = LinkPoint(other)
        self.elem[other] = other
        self.rear.next = other
        self.length += self.rear * other
        self.rear = other

    def get(self, start: Point = None, end: Point = None):
        if start is None:
            start = self.head.next.point
        if end is None:
            end = self.rear.point
        start: LinkPoint = self.elem[start]
        while start != end:
            yield start.point, start.next.point
            start = start.next

    def __contains__(self, other: Point) -> bool:
        return other in self.elem


class RecordPath:
    """
    可快捷查找路径中的每个点的位置, 点到起点的距离
    """

    def __init__(self) -> None:
        # 保存路径点
        self.path = []
        # 保存路径点的位置
        self.point_pos = {}
        # 保存路径点到起点的长度
        self.point_len = {}
        # 当前位置
        self.pos = 0
        # 当前路径长度
        self.length = 0
        # 拐角数
        self.turn_num = 0

    def load(self, path: Path | LinkPath):
        """加载外部路径"""
        self.clear()
        if isinstance(path, Path):
            for point in path:
                self.append(point)
        elif isinstance(path, LinkPath):
            p = path.head.next
            while p != None:
                self.append(p.point)
                p = p.next
        self.turn_num = path.turn_num

    def append(self, other: Point):
        """添加路径点"""
        if self.path:
            self.length += self.path[-1] * other
        self.path.append(other)
        self.point_pos[other] = self.pos
        self.point_len[other] = self.length
        self.pos += 1

    def index(self, other: Point):
        """查找点的位置"""
        return self.point_pos[other]

    def dist(self, other: Point):
        """查找点到起点的距离"""
        return self.point_len[other]

    def get(self, start: Point = None, end: Point = None):
        """依次生成路径上的两个点"""
        if not self.path:
            return
        if start is None:
            start = self.path[0]
        if end is None:
            end = self.path[-1]
        for i in range(self.index(start), self.index(end)):
            yield self.path[i], self.path[i + 1]

    def __getitem__(self, i: int):
        return self.path[i]

    def __contains__(self, other: Point):
        return other in self.point_pos

    def __len__(self) -> int:
        return len(self.path)

    def __str__(self) -> str:
        return "->".join(map(str, self.path))

    def clear(self) -> None:
        self.path.clear()
        self.point_pos.clear()
        self.point_len.clear()
        self.pos = 0
        self.length = 0

    def check_turn(self, p: Point) -> bool:
        """检查某点是否为拐点"""
        if p == self.path[-1] or p == self.path[0]:
            return True
        pre, nxt = self.path[self.index(p) - 1], self.path[self.index(p) + 1]
        return (p - pre) != (nxt - p)
