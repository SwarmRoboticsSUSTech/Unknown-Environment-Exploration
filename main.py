# -*- coding: utf-8 -*-
import time

from run_simulator import Simulator
from calculate import print_info
from settings import *


if __name__ == '__main__':
    run_time = time.asctime().split()
    filename = 'datas/' + ''.join(run_time).replace(":", "-") + '.csv'
    with open(filename, "w+") as f:
        f.write(
            "run_time route_length status explorated_area unexplorated_area" +
            "\n")

    robots_simulator = Simulator(filename)
    for i in range(RUN_TIMES):
        robots_simulator.flush()
        robots_simulator.loop()
    robots_simulator.gui_exit()

    print_info(filename)
