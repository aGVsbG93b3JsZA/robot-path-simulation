import numpy as np
import matplotlib.pyplot as plt
import time
import os

def make_map(length:int=20, width:int=20, name:str=None, dir:str=None):
    """
    手动制作一张地图

    参数:
        width (int): 地图的宽度
        length (int): 地图的长度
        name (str): 地图的名字，若不传入，则为时间戳
        dir (str): 地图保存的文件夹路径，默认为 maps
    """
    
    if dir is None:
        dir = os.path.join(os.getcwd(), 'maps')
    if not os.path.exists(dir):
        os.mkdir(dir)

    fig, ax = plt.subplots(figsize=(10,7))

    # 初始化
    graph = np.zeros((width, length))
    graph[width//2][length//2] = 1

    # 画网格
    for x in range(length):
        ax.plot((x-0.5, x-0.5), (-0.5, width-0.5), 'k', lw=0.2)
    for y in range(width):
        ax.plot((-0.5, length-0.5), (y-0.5, y-0.5), 'k', lw=0.2)

    # x轴和y轴刻度
    ax.set_xticks(np.arange(0, length+1, length//20))
    ax.set_yticks(np.arange(0, width+1, width//20))

    # 显示地图
    im = ax.imshow(graph, cmap='Greys', origin='lower')

    # 点击地图刷新
    def onclick(event):
        x = round(event.ydata)
        y = round(event.xdata)
        graph[x][y] = 1 - graph[x][y]
        im.set_data(graph)
        fig.canvas.draw()
        fig.canvas.flush_events()

    fig.canvas.mpl_connect('button_press_event', onclick)

    # 显示地图
    plt.show()

    # 保存地图
    if name is None:
        name = str(int(time.time()))
    file = os.path.join(dir, name)
    np.save(file, graph)
    print(f'{name}已保存')

