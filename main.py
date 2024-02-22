from rps.gui import Map
from rps.aco import AS


if __name__ == '__main__':

    map = Map()
    map.load()
    print(map.graph.start)
    print(map.graph.end)
    alg = AS()
    map.apply_real_time(alg)