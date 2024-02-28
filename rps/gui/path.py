from .point import Point, LinkPoint

class Path:
    """
    表示一条路径 (基于列表和集合存储)

    属性:
        length (float): 路径长度 
        turn_num (int): 路径拐角数

    """
    def __init__(self, path:list=None):
        if path is None:
            self.path = []
            self.points = set()
        else:
            self.path = path
            self.points = set(path)
        self.length = 0
        self.turn_num = 0

    def append(self, other):
        """添加一个路径点"""
        if self.path:
            self.length += self.path[-1] * other
            self.turn_num += 1 - (self > other)
        self.path.append(other)
        self.points.add(other)

    def pop(self, vis:bool=True) -> Point:
        """删除最后一个路径点, 返回前一个点"""
        p = self.path.pop()
        self.turn_num -= 1 - (self > p)
        if not vis:
            self.points.discard(p)
        return self.path[-1]

    def __getitem__(self, i:int):
        return self.path[i]
    
    def __contains__(self, p:Point):
        return p in self.points
    
    def __iter__(self):
        return iter(self.path)
    
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
        cp = Path(self.path.copy())
        cp.turn_num = self.turn_num
        cp.length = self.length
        return cp
    
    def get(self):
        """依次生成路径上的两个点"""
        for i in range(len(self.path)-1):
            yield self.path[i], self.path[i+1]
    
    def clear(self):
        """清空路径"""
        self.path.clear()
        self.points.clear()
        self.length = 0
        self.turn_num = 0



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
    
    def load(self, path: Path | list):
        """加载外部路径"""
        self.clear()
        for point in path:
            self.append(point)

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

    def get(self):
        """依次生成路径上的两个点"""
        for i in range(len(self.path)-1):
            yield self.path[i], self.path[i+1]

    def __getitem__(self, i:int):
        return self.path[i]
    
    def __contains__(self, other:Point):
        return other in self.point_pos
    
    def __len__(self) -> int:
        return len(self.path)
    
    def clear(self) -> None:
        self.path.clear()
        self.point_pos.clear()
        self.point_len.clear()
        self.pos = 0
        self.length = 0




class LinkPath:
    """
    基于双向链表保存的路径, 同时支持关键字查找
    """
    def __init__(self) -> None:
        self.head = LinkPoint()
        self.rear = self.head
        self.elem = dict()
        self.length = 0

    def __getitem__(self, key: Point) -> LinkPoint:
        return self.elem[key]

    def append(self, other: Point):
        other = LinkPoint(other)
        self.length += self.rear * other
        other.front = self.rear
        other.length = self.length
        self.rear.next = other
        self.rear = other
        self.elem[other.point] = other

    def pop(self):
        self.length -= self.rear.front * self.rear
        lp = self.elem.pop(self.rear.point)
        self.rear = self.rear.front
        self.rear.next = None
        return lp.point


