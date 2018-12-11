import copy

import pygame

from algorithm import action
from settings import *
from simulator import Map
from simulator import OutsideBoundryError, SimulatorStatus, Robot


class Simulator(object):
    def __init__(self, result_filename):
        self.result_filename = result_filename

        pygame.init()

        screen_height = GRID_DIMENSION[0] * WIDTH + GRID_DIMENSION[0] + 1
        screen_width = GRID_DIMENSION[1] * HEIGHT + GRID_DIMENSION[1] + 1
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        pygame.display.set_caption(
            "Frontier-based Unknown Environment Exploration")

    def flush(self):
        self.done = False
        self.block = False

        self.clock = pygame.time.Clock()

        self.simulator_status = SimulatorStatus()

        self.map = Map(GRID_DIMENSION)

    def loop(self):
        while not (self.done or self.block):
            # self.screen.fill(BLACK)
            actions = action(copy.deepcopy(self.map))
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

    def load_elements(self, robot_init_filename, block_init_filename):  # replace init_map
        for x, y in self.map.get_robot_init_place(robot_init_filename):
            if not self.map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init robot (x, y) not in map!')
            self.map.grid[x][y] = ROBOT_AREA
            self.map.robots.append(Robot(x, y))  # add robots

        for x, y in self.map.get_blocks_init_place(block_init_filename):
            if not self.map.is_location_in_environment(x, y, GRID_DIMENSION):
                raise OutsideBoundryError('init block (x, y) not in map!')
            self.map.grid[x][y] = BLOCK_AREA
            self.map.blocks.append((x, y))

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
