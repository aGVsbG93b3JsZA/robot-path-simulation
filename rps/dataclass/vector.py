class Dir:
    """
    表示一个方向向量

    方向共有8种, 即方格图中可以移动的8种方向::

        Dir(1, 0)       # x轴正方向
        Dir(1, 1)       # 直线 y = x (x > 0)
        Dir(1, -1)      # 直线 y = -x (x > 0)
        Dir(0, 1)       # y轴正方向
        Dir(-1, 1)      # 直线 y = -x (x < 0)
        Dir(-1, 0)      # x轴负方向
        Dir(-1, -1)     # 直线 y = x (x < 0)
        Dir(0, -1)      # y轴负方向

    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"Dir({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __sub__(self, other) -> bool:
        if self == other:
            return 0
        return 4 - (abs(other.x + self.x) + abs(other.y + self.y))

    def left(self):
        """将方向逆时针旋转45度"""
        x = self.x + (self.x == 0 or self.x == self.y) * -self.y
        y = self.y + (self.y == 0 or self.x == -self.y) * self.x
        return Dir(x, y)

    def right(self):
        """将方向顺时针旋转45度"""
        x = self.x + (self.x == 0 or self.x == -self.y) * self.y
        y = self.y + (self.y == 0 or self.x == self.y) * -self.x
        return Dir(x, y)

    @classmethod
    def all_dirs(cls):
        """生成所有8个方向向量"""
        yield from [
            Dir(1, 0),
            Dir(1, 1),
            Dir(1, -1),
            Dir(0, 1),
            Dir(-1, 1),
            Dir(-1, 0),
            Dir(-1, -1),
            Dir(0, -1),
        ]
