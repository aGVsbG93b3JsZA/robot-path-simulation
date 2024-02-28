from rps.gui import Map, make_map, Point
from rps.aco import *

if __name__ == '__main__':

    map = Map()
    # map.random_map((20, 20))
    map.load('demo')
    # map.load()
    # alg = MyAS(m=20, beta=20)
    # alg = MyACO()
    # alg = MAACO()
    alg = LRACO(alpha=20, beta=5, m1=20, m2=20, nc=20, q0=0.6)
    # map.apply(alg, show=True)
    map.apply_real_time(alg)
    # make_map(name='demo')s