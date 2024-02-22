from .point import Point

class Path:
    """
    表示一条路径 (基于列表和集合存储，列表用于表示顺序，集合用于快速查找点)

    属性:
        path (list): 可选, 加载初始路径
    """
    def __init__(self, path:list=None):
        if path is None:
            self.path = []
            self.points = set()
        else:
            self.path = path
            self.points = set(path)

    def append(self, other):
        """添加一个路径点"""
        self.path.append(other)
        self.points.add(other)
    
    def pop(self) -> Point:
        """删除最后一个路径点, 返回前一个点"""
        self.path.pop()
        # self.points.discard(p)
        return self.path[-1]
    
    def length(self) -> float|int:
        """计算路径的长度"""
        dist = 0
        for r, s in self.get():
            dist += r * s
        return dist
    
    def turns(self) -> int:
        """计算路径的拐角数"""
        turn_num = 0
        turn = (0, 0)
        for r, s in self.get():
            if turn != (turn:=s-r):
                turn_num += 1
        return turn_num

    def __getitem__(self, i:int):
        return self.path[i]
    
    def __contains__(self, p:Point):
        return p in self.points

    def copy(self):
        """浅拷贝"""
        return Path(self.path.copy())
    
    def get(self):
        """依次产生所有两点子路径"""
        for i in range(len(self.path)-1):
            r, s = self.path[i], self.path[i+1]
            yield r, s
    
    def clear(self):
        """清空路径"""
        self.path.clear()
        self.points.clear()

