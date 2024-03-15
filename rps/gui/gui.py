import os
import random
import numpy as np
import matplotlib.pyplot as plt
from .point import Point
from .graph import Graph
from .path import Path


class Map:
    """
    具有GUI功能的地图, 可加载算法并显示路径
    
    属性:
        graph (Graph): 可选, 加载初始地图 
    """
    def __init__(self, graph:Graph=None):

        if graph is not None:
            self.graph = graph
            self.graph.edges = self.graph.get_all_edges()

        self.fig, self.ax = plt.subplots(figsize=(7,7))

    def load(self, name:str='default', path:str=Graph.SAVE_DIR):
        """
        加载本地地图文件, 默认路径为maps/
        
        参数:
            name (str): 地图名, 默认为'default'
            path (str): 地图文件夹路径, 默认为'maps'
        """
        name = name + '.npy'
        file = os.path.join(path, name)
        with open(file, 'rb') as f:
            graph = np.load(f)
        start = Point(len(graph[0])-1, 0)
        end = Point(0, len(graph)-1)
        self.graph = Graph(graph, start, end)
        self.graph.edges = self.graph.get_all_edges()
        self._draw_map()
        
    def random_map(self, size:tuple=(20,20), alpha:float=0.2):
        """
        生成随机地图
        
        参数:
            size (tuple): 表示地图尺寸: (width, length)
            alpha (float): 障碍物数/地图方格数, 0 < alpha < 1
        """
        start = Point(0, 0)
        end = Point(size[0]-1, size[1]-1)
        graph = Graph(np.zeros(size), start, end)
        # 生成下一点
        def random_move(point: Point):
            within_map = lambda p: p in graph
            steps = list(filter(within_map, [point+(0,1), point+(1,0)]))
            return random.choice(steps)
        # 随机生成一条通路
        path = set()
        pos = start
        while pos != end:
            path.add(pos)
            pos = random_move(pos)
        path.add(end)
        # 生成随机障碍物
        block_num = int(size[0] * size[1] * alpha)
        i = 0
        while i < block_num:
            block = Point(random.randrange(size[0]), random.randrange(size[1]))
            if (block not in path) and (block in graph):
                graph[block.x][block.y] = 1
                i += 1
        self.graph = graph
        self.graph.edges = self.graph.get_all_edges()
        self._draw_map()

    def apply(self, algorithm:object, show=False):
        """
        在地图上应用算法（静态）

        参数:
            algorithm (object): 实例化算法对象
            show (bool): 是否立即显示
        """
        algorithm.load_graph(self.graph)
        path = algorithm.search()
        self._draw_path(path)
        if show:
            self.show()

    def apply_real_time(self, algorithm:object):
        """
        在地图上应用算法（动态显示）

        参数:
            algorithm (objcet): 实例化算法对象
        """
        algorithm.load_graph(self.graph)   
        if algorithm.CLASS == 'ACO':
            self._aco_real_time(algorithm)
        elif algorithm.CLASS == 'A_STAR':
            self._astar_real_time(algorithm)

    def _astar_real_time(self, algorithm):
        """Dijkstra, A*算法动态显示"""
        with plt.ion():
            self.ax.set_title(algorithm.__class__.__name__)
            for point in algorithm.search_real_time():
                self.ax.plot(point.y, point.x, 'oy', markersize=350/max(self.graph.size))
                plt.pause(0.001)
            self._draw_path(algorithm.path, color=3)
        plt.show()   
        
    def _aco_real_time(self, algorithm):
        """蚁群算法动态显示"""
        with plt.ion():
            for path in algorithm.search_real_time():
                self.ax.clear()
                self._draw_map()
                self.ax.set_title(algorithm.__class__.__name__ + f'  iteration:{algorithm.iter_cnt}  len:{path.length:.2f}')
                self._draw_path(path, color=0)
                plt.pause(0.001)
        plt.show() 

    def _aoto_color(func):
        """装饰器，自动选择路径颜色"""
        i = 0
        def wrapper(self, *args, **kwargs):
            nonlocal i
            if 'color' not in kwargs:
                kwargs['color'] = i
                i += 1
            return func(self, *args, **kwargs)
        return wrapper
    
    @_aoto_color
    def _draw_path(self, path:Path, color:int=None):
        """绘制算法路径"""
        fmt = 'cbgrmyk'[color] + '-'
        for r, s in path.get():
            self.ax.plot([r.y, s.y], [r.x, s.x], fmt, lw=1)   
        
    def _draw_map(self):
        """绘制初始地图"""
        # 画网格
        for x in range(self.graph.length):
            self.ax.plot((x-0.5, x-0.5), (-0.5, self.graph.width-0.5), 'k', lw=0.2)
        for y in range(self.graph.width):
            self.ax.plot((-0.5, self.graph.length-0.5), (y-0.5, y-0.5), 'k', lw=0.2)
        # 显示地图
        self.ax.imshow(self.graph.graph, cmap='Greys', origin='lower')
        # 设置刻度
        self.ax.set_xticks(np.arange(0, self.graph.length+1, self.graph.length//20))
        self.ax.set_yticks(np.arange(0, self.graph.width+1, self.graph.width//20))
        # 放置起始点
        self.ax.plot(self.graph.start.y, self.graph.start.x, 'og', markersize=400/max(self.graph.size))
        self.ax.plot(self.graph.end.y, self.graph.end.x, 'Xr', markersize=400/max(self.graph.size))

    def show(self, save:bool=False):
        """
        显示GUI界面

        参数:
            save (bool): 是否保存此次地图, 默认不保存
        """
        plt.show()
        if save:
            self.graph.save(name='default')

