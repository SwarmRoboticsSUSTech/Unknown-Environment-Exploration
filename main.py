# -*- coding: utf-8 -*-
import time
import configparser

from run_simulator import Simulator
from calculate import print_info

if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.read('settings.ini')

    run_time = time.asctime().split()
    filename = 'datas/' + ''.join(run_time).replace(":", "-") + '.csv'
    with open(filename, "w+") as f:
        f.write(
            "run_time route_length status explorated_area unexplorated_area" +
            "\n")

    robots_simulator = Simulator(filename, "init_data/robot_init.csv", "init_data/blocks.csv")
    for i in range(int(cfg['TIME']['run_times'])):
        robots_simulator.flush()
        robots_simulator.loop()
    robots_simulator.gui_exit()

    print_info(filename, gedit=True)
