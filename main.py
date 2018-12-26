# -*- coding: utf-8 -*-
import time
import configparser

from run_simulator import Simulator
from calculate import print_info

if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.read('settings.ini')

    robot_nums = [15, 20]
    environmen_nums = ['H', 'PL', 'WH']

    for environment_num in environmen_nums:
        for robot_num in robot_nums:
            run_time = time.asctime().split()
            filename = 'datas/' + ''.join(run_time).replace(":", "-") + '-robot_num_' + str(robot_num) + '_' + environment_num + '.csv'
            with open(filename, "w+") as f:
                f.write(
                    "run_time route_length status explorated_area unexplorated_area" +
                    "\n")

            robots_simulator = Simulator(filename, "init_data/robot_init_" + str(robot_num) + ".csv", "init_data/blocks_" + environment_num + ".csv")
            for i in range(int(cfg['TIME']['run_times'])):
                robots_simulator.flush()
                robots_simulator.loop()
            robots_simulator.gui_exit()

            print_info(filename, gedit=True)
