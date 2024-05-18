import os
import inspect
import rps.aco
import rps.classical
from datetime import datetime
from rps import conn, cursor
from rps.config import DEFAULT_MAP_PATH


def get_algs():
    """
    获取所有的算法
    """
    return rps.aco.__all__ + rps.classical.__all__


def get_class_init(cls):
    """
    获取类的初始化参数
    """
    signature = inspect.signature(cls.__init__)
    init_params = {}
    for name, param in signature.parameters.items():
        if param.default != inspect.Parameter.empty:
            init_params[name] = param.default
    return init_params


def get_files(path=DEFAULT_MAP_PATH, format="npz"):
    """获取地图文件列表"""
    files = os.listdir(path)
    return [f.split(".")[0] for f in files if f.endswith(format)]


def show_map(graph):
    """显示地图"""
    import matplotlib.pyplot as plt

    length, width = graph.shape
    plt.imshow(graph, cmap="Grays", origin="lower")
    for x in range(length):
        plt.plot((x - 0.5, x - 0.5), (-0.5, width - 0.5), "k", lw=0.2)
    for y in range(width):
        plt.plot((-0.5, length - 0.5), (y - 0.5, y - 0.5), "k", lw=0.2)
    plt.show()


def insert_record(name, length, turn_num, detail_length, time=None):
    """
    插入一条记录
    """
    if time is None:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if detail_length is None:
        detail_length = ""
    cursor.execute(
        "INSERT INTO run_record (name, length, turn_num, detail_length, time) VALUES ('{}', {}, {}, '{}', '{}')".format(
            name, length, turn_num, detail_length, time
        )
    )
    conn.commit()
