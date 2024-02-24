from rps.gui import Map, make_map
from rps.aco import MyAS, MyACO, AS, MAACO

if __name__ == '__main__':

    map = Map()
    # map.random_map((20, 20))
    map.load()
    # map.load()
    # alg = AS()
    # alg = MyAS(beta=10)
    alg = MyACO(beta=10)
    # alg = MAACO(t0=0.1)
    # map.apply(alg, show=True)
    map.apply_real_time(alg)
    # make_map(name='demo')s


