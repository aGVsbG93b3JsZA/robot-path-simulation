from rps.gui import Map, make_map
from rps.aco import *
from rps.classical import *

if __name__ == '__main__':

    map = Map()
    # map.random_map((100, 100))
    map.load('default')
    # map.load('3')
    # map.load('demo')
    # alg = ACS() 
    # alg = MAACO(nc=25)
    # alg = TestACO(nc=25)
    alg = MHACO(m=20, nc=25)
    # alg = LRACO(alpha=20, beta=5, m=50, m1=5, m2=20, nc=20, q0=0.6)
    # alg = Dijkstra()
    # alg = A_Star()
    # map.apply(alg, show=True)
    map.apply_real_time(alg)

    # make_map(length=20, width=20, name='4')