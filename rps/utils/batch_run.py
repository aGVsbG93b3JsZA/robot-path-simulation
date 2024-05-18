import numpy as np
import pandas as pd
import tqdm
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor


def batch_run(alg, graph, num, worker=4, return_average=True):
    """
    连续运行算法num次, 返回平均路径长度, 平均转弯次数, 平均收敛次数
    """
    results = []
    tasks = []
    with ProcessPoolExecutor(worker) as executor:
        for _ in range(num):
            _alg = deepcopy(alg)
            tasks.append(executor.submit(_alg.search, graph=graph, return_path=False))
        for i, res in enumerate(tasks):
            try:
                results.append(res.result())
            except Exception as e:
                print(e)
    if not return_average:
        return results
    total_length = sum([r[0] for r in results])
    total_turn = sum([r[1] for r in results])
    total_converge = sum([r[2] for r in results])
    return total_length / num, total_turn / num, total_converge / num


def param_test(alg, graph, param, value_range, batch, worker=4):
    """
    测试参数对算法的影响
    """
    for value in tqdm.tqdm(value_range, desc=f"{alg.__class__.__name__}:{param}"):
        setattr(alg, param, value)
        res = batch_run(alg, graph, batch, worker)
        yield value, res


def alg_test(alg, graph, batch_num, worker=4):
    """
    测试蚁群算法
    """
    results = batch_run(alg, graph, batch_num, worker, return_average=False)
    length, turn, converge = zip(*results)
    length = np.array(length)
    turn = np.array(turn)
    converge = np.array(converge)
    best_length = length.min()
    best_turn = turn.min()
    best_converge = converge.min()
    mean_length = length.mean()
    mean_turn = turn.mean()
    mean_converge = converge.mean()
    std_length = length.std()
    std_turn = turn.std()
    std_converge = converge.std()
    index = alg.__class__.__name__
    return pd.Series(
        name=index,
        data={
            "Best Length": best_length,
            "Mean Length": mean_length,
            "Std Length": std_length,
            "Best Turn": best_turn,
            "Mean Turn": mean_turn,
            "Std Turn": std_turn,
            "Best Converge": best_converge,
            "Mean Converge": mean_converge,
            "Std Converge": std_converge,
        },
    )


def classical_test(alg, graph):
    """
    测试经典算法
    """
    path = alg.search(graph)
    length = path.length
    turn_num = path.turn_num
    return pd.Series(
        name=alg.__class__.__name__,
        data={
            "Best Length": length,
            "Mean Length": length,
            "Std Length": 0,
            "Best Turn": turn_num,
            "Mean Turn": turn_num,
            "Std Turn": 0,
            "Best Converge": None,
            "Mean Converge": None,
            "Std Converge": None,
        },
    )
