import copy
import random
import configparser

import pygame
import tkinter as tk

from bso_astar import action
# from bso import action
from settings import *
from simulator import Map
from simulator import SimulatorStatus, Robot
from exceptions import OutsideBoundryError, ModeError
from gui import Application


class Simulator(object):
    def __init__(self, result_filename, gui=True, robot_init_filename=None, block_init_filename=None):
        self.result_filename = result_filename

        self.gui = gui

        self.configure()

        self.init_backend()

        self.init_map(robot_init_filename, block_init_filename)

    def flush(self):
        self.done = False
        self.block = False
        self.simulator_status = SimulatorStatus(self.cfg)
        self.map = copy.deepcopy(self.origin_map)

    def loop(self):
        while not (self.done or self.block):
            # self.screen.fill(BLACK)
            actions = action(copy.deepcopy(self.map))  # 避免算法部分不小心修改了map的属性
            real_action_this_interval = 0

            # set grid type
            for i, robot_i in enumerate(self.map.robots):
                self.map.grid[robot_i.x][robot_i.y] = EXPLORATED_AREA

                real_action_this_interval += robot_i.move(self.map, action=actions[i])
                self.map.grid[robot_i.x][robot_i.y] = ROBOT_AREA

            for robot_i in self.map.robots:
                view_real_area_i = robot_i.view_real_area(self.map.blocks,
                                                          self.map.grid_dimension)
                for j in view_real_area_i:
                    self.map.grid[j[0]][j[1]] = EXPLORATED_AREA

            for robot_i in self.map.robots:
                self.map.grid[robot_i.x][robot_i.y] = ROBOT_AREA

            self.map.view_real_exploration_bounds()

            if self.gui:
                # Draw the grid
                for row in range(int(self.cfg['MAP']['grid_row_dimension'])):
                    for column in range(int(self.cfg['MAP']['grid_column_dimension'])):
                        color = GREY
                        if self.map.grid[row][column] == ROBOT_AREA:
                            color = RED
                        elif self.map.grid[row][column] == BLOCK_AREA:
                            color = BLACK
                        elif self.map.grid[row][column] == EXPLORATED_AREA:
                            color = WHITE
                        elif self.map.grid[row][column] == EXPLORATED_BOUND:
                            color = BLUE
                        pygame.draw.rect(
                            self.screen, color,
                            [(int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['width'])) * column + int(
                                self.cfg['MAP']['margin']),
                             (int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['height'])) * row + int(
                                 self.cfg['MAP']['margin']), int(self.cfg['MAP']['width']), int(self.cfg['MAP']['height'])])

                # Limit to 60 frames per second
                self.clock.tick(CLOCK_TICK)

                # Go ahead and update the screen with what we've drawn.
                pygame.display.flip()

            self.update_simulator_status(real_action_this_interval)

    def load_elements_from_file(self, robot_init_filename, block_init_filename):
        map = Map((int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension'])))
        for x, y in map.get_blocks_init_place(block_init_filename):
            if not map.is_location_in_environment(x, y, (
            int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension']))):
                raise OutsideBoundryError('init block (x, y) not in map!')
            map.grid[x][y] = BLOCK_AREA
            map.blocks.append((x, y))

        for x, y in map.get_robot_init_place(robot_init_filename):
            if not map.is_location_in_environment(x, y, (
            int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension']))):
                raise OutsideBoundryError('init robot (x, y) not in map!')
            map.grid[x][y] = ROBOT_AREA
            map.robots.append(Robot(x, y))  # add robots
        return map

    def load_elements_by_click(self, robots_sequences, blocks_sequences):
        map = Map((int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension'])))
        for x, y in blocks_sequences:
            if not map.is_location_in_environment(x, y, (
            int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension']))):
                raise OutsideBoundryError('init block (x, y) not in map!')
            map.grid[x][y] = BLOCK_AREA
            map.blocks.append((x, y))

        for x, y in robots_sequences:
            if not map.is_location_in_environment(x, y, (
            int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension']))):
                raise OutsideBoundryError('init robot (x, y) not in map!')
            map.grid[x][y] = ROBOT_AREA
            map.robots.append(Robot(x, y))  # add robots
        return map

    def load_elements_by_random(self):
        map = Map((int(self.cfg['MAP']['grid_row_dimension']), int(self.cfg['MAP']['grid_column_dimension'])))
        count = 0
        while count <= int(self.cfg['MAP']['random_init_blocks_num']):
            x = random.randint(0, int(self.cfg['MAP']['grid_row_dimension']) - 1)
            y = random.randint(0, int(self.cfg['MAP']['grid_column_dimension']) - 1)
            if (x, y) not in map.blocks:
                count += 1
                map.grid[x][y] = BLOCK_AREA
                map.blocks.append((x, y))

        count = 0
        while count <= int(self.cfg['MAP']['random_init_robots_num']):
            x = random.randint(0, int(self.cfg['MAP']['grid_row_dimension']) - 1)
            y = random.randint(0, int(self.cfg['MAP']['grid_column_dimension']) - 1)
            if (x, y) not in map.blocks:
                count += 1
                map.grid[x][y] = ROBOT_AREA
                map.robots.append(Robot(x, y))  # add robots
        return map

    def update_simulator_status(self, real_action_this_interval):
        self.simulator_status.update_time()
        self.simulator_status.update_robot_route_length(real_action_this_interval)
        self.simulator_status.update_area_info(self.map)

        self.block = self.simulator_status.judge_blocking()
        self.done = self.simulator_status.judge_over(self.map)
        if self.done:
            self.simulator_status.update_status("success")
        if self.done or self.block:
            self.simulator_status.save_log(self.result_filename)
        print(self.simulator_status)  # for debug

    def init_backend(self):
        if self.gui:
            pygame.init()

            screen_height = int(self.cfg['MAP']['grid_row_dimension']) * (
                        int(self.cfg['MAP']['width']) + int(self.cfg['MAP']['margin']))
            screen_width = int(self.cfg['MAP']['grid_column_dimension']) * (
                        int(self.cfg['MAP']['height']) + int(self.cfg['MAP']['margin']))
            self.screen = pygame.display.set_mode([screen_width, screen_height])
            self.screen.fill(GREEN)

            pygame.display.set_caption(
                "Frontier-based Unknown Environment Exploration")
            self.clock = pygame.time.Clock()
            for row in range(int(self.cfg['MAP']['grid_row_dimension'])):
                for column in range(int(self.cfg['MAP']['grid_column_dimension'])):
                    pygame.draw.rect(
                        self.screen, GREY,
                        [(int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['width'])) * column + int(
                            self.cfg['MAP']['margin']),
                         (int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['height'])) * row + int(
                             self.cfg['MAP']['margin']), int(self.cfg['MAP']['width']), int(self.cfg['MAP']['height'])])

    def configure(self):
        if self.gui is True:
            root = tk.Tk()
            root.geometry("500x500")
            app = Application(master=root)
            app.mainloop()

        self.cfg = configparser.ConfigParser()
        self.cfg.read('settings.ini')
        self.mode = self.cfg['MODE']['mode']

    def init_map(self, robot_init_filename, block_init_filename):
        if self.mode == 'SELECTION' and self.gui:
            click_squences = {}
            selecting = True
            while selecting:
                self.clock.tick(60)

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        click_pos = event.pos
                        column = int((click_pos[0] - int(self.cfg['MAP']['margin'])) / (
                                    int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['width'])))
                        row = int((click_pos[1] - int(self.cfg['MAP']['margin'])) / (
                                    int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['height'])))
                        if 0 <= column < int(self.cfg['MAP']['grid_column_dimension']) and 0 <= row < int(
                                self.cfg['MAP']['grid_row_dimension']):
                            if event.button == LEFT_CLICK:
                                click_squences[(row, column)] = 'ROBOT'
                                pygame.draw.rect(
                                    self.screen, RED,
                                    [(int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['width'])) * column + int(
                                        self.cfg['MAP']['margin']),
                                     (int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['height'])) * row + int(
                                         self.cfg['MAP']['margin']), int(self.cfg['MAP']['width']),
                                     int(self.cfg['MAP']['height'])])
                            elif event.button == RIGHT_CLICK:
                                click_squences[(row, column)] = 'BLOCK'
                                pygame.draw.rect(
                                    self.screen, BLACK,
                                    [(int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['width'])) * column + int(
                                        self.cfg['MAP']['margin']),
                                     (int(self.cfg['MAP']['margin']) + int(self.cfg['MAP']['height'])) * row + int(
                                         self.cfg['MAP']['margin']), int(self.cfg['MAP']['width']),
                                     int(self.cfg['MAP']['height'])])

                    elif event.type == pygame.QUIT:
                        selecting = False

                pygame.display.update()

            robots_sequences = []
            blocks_sequences = []
            for k, v in click_squences.items():
                if v == 'ROBOT':
                    robots_sequences.append(k)
                elif v == 'BLOCK':
                    blocks_sequences.append(k)

            self.origin_map = self.load_elements_by_click(robots_sequences, blocks_sequences)

        elif self.mode == 'READFILE':
            self.origin_map = self.load_elements_from_file(robot_init_filename, block_init_filename)

        elif self.mode == 'RANDOM_INIT':
            self.origin_map = self.load_elements_by_random()

        else:
            raise ModeError('Mode no found!')

    def gui_exit(self):
        pygame.quit()
