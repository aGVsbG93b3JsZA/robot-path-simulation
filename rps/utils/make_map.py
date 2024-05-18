import numpy as np
import matplotlib.pyplot as plt
import time
import os


def make_map(length: int = 20, width: int = 20, name: str = None, dir: str = None):
    """
    手动制作一张地图

    参数:
        width (int): 地图的宽度
        length (int): 地图的长度
        name (str): 地图的名字，若不传入，则为时间戳
        dir (str): 地图保存的文件夹路径，默认为 maps
    """

    if dir is None:
        dir = os.path.join(os.getcwd(), "maps")
    if not os.path.exists(dir):
        os.mkdir(dir)
    if name is None:
        name = str(int(time.time()))

    file = os.path.join(dir, name)

    fig, ax = plt.subplots(figsize=(7, 7))

    # 初始化
    if os.path.exists(file + ".npz"):
        data = np.load(file + ".npz")
        graph = data["graph"]
        start = data["start"]
        end = data["end"]
        width, length = graph.shape
    else:
        graph = np.zeros((width, length), dtype=int)
        graph[width // 2][length // 2] = 1
        start = np.array([width - 1, 0])
        end = np.array([0, length - 1])

    # 画网格
    for x in range(length):
        ax.plot((x - 0.5, x - 0.5), (-0.5, width - 0.5), "k", lw=0.2)
    for y in range(width):
        ax.plot((-0.5, length - 0.5), (y - 0.5, y - 0.5), "k", lw=0.2)

    # 画起点和终点
    start_dot = plt.Circle((start[1], start[0]), 0.5, color="g")
    end_dot = plt.Circle((end[1], end[0]), 0.5, color="r")
    ax.add_artist(end_dot)
    ax.add_artist(start_dot)

    # x轴和y轴刻度
    ax.set_xticks(np.arange(0, length + 1, length // 20))
    ax.set_yticks(np.arange(0, width + 1, width // 20))

    # 显示地图
    im = ax.imshow(graph, cmap="Greys", origin="lower")

    # 点击地图刷新
    def onclick(event):
        x = round(event.ydata)
        y = round(event.xdata)
        if (x == start[0] and y == start[1]) or (x == end[0] and y == end[1]):
            return
        graph[x][y] = 1 - graph[x][y]
        im.set_data(graph)
        fig.canvas.draw()
        fig.canvas.flush_events()

    # 按键事件
    def on_key(event):
        if event.key == "1":
            x = round(event.ydata)
            y = round(event.xdata)
            if graph[x][y] == 1:
                return
            start[0] = x
            start[1] = y
            start_dot.center = (y, x)
            fig.canvas.draw()
            fig.canvas.flush_events()
            print("start:", start)
        elif event.key == "2":
            x = round(event.ydata)
            y = round(event.xdata)
            if graph[x][y] == 1:
                return
            end[0] = x
            end[1] = y
            end_dot.center = (y, x)
            fig.canvas.draw()
            fig.canvas.flush_events()
            print("end:", end)

    # 连接事件
    fig.canvas.mpl_connect("button_press_event", onclick)
    fig.canvas.mpl_connect("key_press_event", on_key)

    # 显示地图
    plt.show()

    # 保存地图
    np.savez(file, graph=graph, start=start, end=end)
    print(f"{name}已保存")
