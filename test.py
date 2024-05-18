from rps.dataclass import Map
from rps.aco import *
from rps.classical import *
from rps.dataclass import *


def run():
    map = Map()
    map.load("test2")
    # map.save_svg("test")
    alg = MHACO(m=7, nc=20, a=10)
    map.apply_real_time(alg)

if __name__ == "__main__":
    run()
