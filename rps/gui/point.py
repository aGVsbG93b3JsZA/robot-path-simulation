class Point:
    """
    表示地图中某个点

    属性:
        x: 该点x坐标
        y: 该点y坐标

    运算::

        假设 p1: Point, p2: Point
        p1 == p2 -> bool    # 判断两点坐标是否相等
        p1 + p2 -> Point    # 两点坐标相加，返回一个新点
        p1 - p2 -> tuple    # 两点坐标相减，返回一个元祖
        p1 * p2 -> float    # 计算两点欧几里得距离
        p1 / p2 -> float    # 计算两点对角线距离
    """

    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    def __str__(self):
        return f'Point({self.x}, {self.y})'

    def __eq__(self, other):
        if isinstance(other, Point):
            if self.x == other.x and self.y == other.y:
                return True
        return False

    def __lt__(self, other):
        return self

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return (self.x-other.x, self.y-other.y)
    
    def __mul__(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5
    
    def __truediv__(self, other):
        l = abs(self.x - other.x)
        w = abs(self.y - other.y)
        if w > l:
            l, w = w, l
        return 2**0.5 * w + l - w

    def __hash__(self):
        return hash((self.x, self.y))