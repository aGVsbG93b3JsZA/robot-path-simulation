from .point import Point

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

    def pop(self) -> Point:
        """删除最后一个路径点, 返回前一个点"""
        p = self.path.pop()
        self.turn_num -= 1 - (self > p)
        # self.points.discard(p)
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

