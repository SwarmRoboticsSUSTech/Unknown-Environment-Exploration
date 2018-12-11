import copy
import random

import pygame

from algorithm import action
from settings import *
from simulator import Map
from simulator import SimulatorStatus, Robot
from exceptions import OutsideBoundryError, ModeIllegalError


class Simulator(object):
    def __init__(self, result_filename, mode='SELECTION', robot_init_filename=None, block_init_filename=None):
        self.result_filename = result_filename
        self.mode = mode

        if mode not in ('SELECTION', 'RANDOM_INIT', 'READFILE'):
            raise ModeIllegalError('mode is illegal')

        pygame.init()

        screen_height = GRID_DIMENSION[0] * (WIDTH + MARGIN)
        screen_width = GRID_DIMENSION[1] * (HEIGHT + MARGIN)
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        pygame.display.set_caption(
            "Frontier-based Unknown Environment Exploration")
        self.clock = pygame.time.Clock()

        # Draw the backend
        for row in range(GRID_DIMENSION[0]):
            for column in range(GRID_DIMENSION[1]):
                pygame.draw.rect(
                    self.screen, GREY,
                    [(MARGIN + WIDTH) * column + MARGIN,
                     (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])

        click_squences = {}
        selection_mode = True
        while selection_mode:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    click_pos = event.pos
                    column = int((click_pos[0] - MARGIN) / (MARGIN + WIDTH))
                    row = int((click_pos[1] - MARGIN) / (MARGIN + HEIGHT))

                    if event.button == LEFT_CLICK:
                        click_squences[(row, column)] = 'ROBOT'
                        pygame.draw.rect(
                            self.screen, RED,
                            [(MARGIN + WIDTH) * column + MARGIN,
                             (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
                    elif event.button == RIGHT_CLICK:
                        click_squences[(row, column)] = 'BLOCK'
                        pygame.draw.rect(
                            self.screen, BLACK,
                            [(MARGIN + WIDTH) * column + MARGIN,
                             (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
                elif event.type == pygame.QUIT:
                    selection_mode = False

            pygame.display.update()

        if self.mode is 'SELECTION':
            robots_sequences = []
            blocks_sequences = []
            for k, v in click_squences.items():
                if v is 'ROBOT':
                    robots_sequences.append(k)
                elif v is 'BLOCK':
                    blocks_sequences.append(k)

            self.origin_map = self.load_elements_by_click(robots_sequences, blocks_sequences)

        elif self.mode is 'READFILE':
            self.origin_map = self.load_elements_from_file(robot_init_filename, block_init_filename)

        elif self.mode is 'RANDOM_INIT':
            self.origin_map = self.load_elements_by_random()

    def flush(self):
        self.done = False
        self.block = False
        self.simulator_status = SimulatorStatus()
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

            # Draw the grid
            for row in range(GRID_DIMENSION[0]):
                for column in range(GRID_DIMENSION[1]):
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
                        [(MARGIN + WIDTH) * column + MARGIN,
                         (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])

            # Limit to 60 frames per second
            self.clock.tick(CLOCK_TICK)

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            self.update_simulator_status(real_action_this_interval)

    @staticmethod
    def load_elements_from_file(robot_init_filename, block_init_filename):
        map = Map(GRID_DIMENSION)
        for x, y in map.get_blocks_init_place(block_init_filename):
            if not map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init block (x, y) not in map!')
            map.grid[x][y] = BLOCK_AREA
            map.blocks.append((x, y))

        for x, y in map.get_robot_init_place(robot_init_filename):
            if not map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init robot (x, y) not in map!')
            map.grid[x][y] = ROBOT_AREA
            map.robots.append(Robot(x, y))  # add robots
        return map

    @staticmethod
    def load_elements_by_click(robots_sequences, blocks_sequences):
        map = Map(GRID_DIMENSION)
        for x, y in blocks_sequences:
            if not map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init block (x, y) not in map!')
            map.grid[x][y] = BLOCK_AREA
            map.blocks.append((x, y))

        for x, y in robots_sequences:
            if not map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init robot (x, y) not in map!')
            map.grid[x][y] = ROBOT_AREA
            map.robots.append(Robot(x, y))  # add robots
        return map

    @staticmethod
    def load_elements_by_random():
        map = Map(GRID_DIMENSION)
        count = 0
        while count <= RANDOM_INIT_BLOCKS_NUM:
            x = random.randint(0, GRID_DIMENSION[0]-1)
            y = random.randint(0, GRID_DIMENSION[1]-1)
            if (x, y) not in map.blocks:
                count += 1
                map.grid[x][y] = BLOCK_AREA
                map.blocks.append((x, y))

        count = 0
        while count <= RANDOM_INIT_ROBOTS_NUM:
            x = random.randint(0, GRID_DIMENSION[0]-1)
            y = random.randint(0, GRID_DIMENSION[1]-1)
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

    def gui_exit(self):
        pygame.quit()
