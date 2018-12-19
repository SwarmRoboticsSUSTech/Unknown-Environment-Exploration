import pandas as pd
import itertools

from settings import *


class robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.previous_x = x
        self.previous_y = y

    def move(
            self,
            map,
            action=0,
    ):
        if action == 0:
            pass
        elif action == 1:  # left
            self.y -= 1
        elif action == 2:  # down
            self.x += 1
        elif action == 3:  # right
            self.y += 1
        elif action == 4:  # up
            self.x -= 1

        if robot.judge_valid_loaction(self.x, self.y, map.blocks,
                                      map.grid_dimension):
            self.previous_x = self.x
            self.previous_y = self.y
            return int(bool(action))
        else:
            self.x = self.previous_x
            self.y = self.previous_y
            return 0

    @staticmethod
    def judge_valid_loaction(x, y, blocks, grid_dimension):
        if (x, y) in blocks:
            return False
        else:
            return map.is_location_in_environment(x, y, grid_dimension)

    @staticmethod
    def view_raw_area(x, y):
        return [(x - 2, y), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                (x, y - 2), (x, y - 1), (x, y + 1), (x, y + 2), (x + 1, y - 1),
                (x + 1, y), (x + 1, y + 1), (x + 2, y)]

    def view_real_area(self, blocks, grid_dimension):
        # So silly.
        raw_area = set(robot.view_raw_area(self.x, self.y))

        # Avoid view area cross blocks
        if (self.x + 1, self.y) in blocks:
            raw_area.remove((self.x + 2, self.y))
        if (self.x - 1, self.y) in blocks:
            raw_area.remove((self.x - 2, self.y))
        if (self.x, self.y + 1) in blocks:
            raw_area.remove((self.x, self.y + 2))
        if (self.x, self.y - 1) in blocks:
            raw_area.remove((self.x, self.y - 2))
        raw_area_without_blocks = raw_area.difference(set(blocks))
        real_area = [
            i for i in raw_area_without_blocks
            if map.is_location_in_environment(i[0], i[1], grid_dimension)
        ]
        return real_area


class map:
    def __init__(self, grid_dimension):
        self.grid_dimension = grid_dimension
        self.grid = [[0 for x in range(grid_dimension[1])]
                     for y in range(grid_dimension[0])]
        self.robots = []
        self.blocks = []

    @staticmethod
    def get_robot_init_place(filename):
        df = pd.read_csv(filename)
        return [tuple(x) for x in df.values]

    @staticmethod
    def get_blocks_init_place(filename):
        df = pd.read_csv(filename)
        return [tuple(x) for x in df.values]

    def view_real_exploration_bounds(self):
        for x in range(self.grid_dimension[0]):
            for y in range(self.grid_dimension[1]):
                if self.grid[x][y] == UNEXPLARATION_AREA and self.judge_side_white(
                        x, y):
                    self.grid[x][y] = EXPLORATED_BOUND

    def judge_side_white(self, x, y):
        if x < 0 or y < 0 or x >= self.grid_dimension[0] or y >= self.grid_dimension[1]:
            raise OutsideBoundryError('(x, y) not in map!')
        if self.is_location_in_environment(
                x - 1, y,
                self.grid_dimension) and self.grid[x
                                                   - 1][y] == EXPLORATED_AREA:
            return True
        elif self.is_location_in_environment(
                x + 1, y,
                self.grid_dimension) and self.grid[x
                                                   + 1][y] == EXPLORATED_AREA:
            return True
        elif self.is_location_in_environment(
                x, y + 1,
                self.grid_dimension) and self.grid[x][y
                                                      + 1] == EXPLORATED_AREA:
            return True
        elif self.is_location_in_environment(
                x, y - 1,
                self.grid_dimension) and self.grid[x][y
                                                      - 1] == EXPLORATED_AREA:
            return True
        else:
            return False

    @staticmethod
    def is_location_in_environment(x, y, grid_dimension):
        if x < 0 or y < 0 or x >= grid_dimension[0] or y >= grid_dimension[1]:
            return False
        else:
            return True


class OutsideBoundryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return (repr(self.value))


class frontier:
    def __init__(self, row, column, weight, direction):
        self.weight = weight
        self.direction = direction
        self.x = row
        self.y = column


class robotlocation:
    def __init__(self, row, column):
        self.x = row
        self.y = column


class SimulatorStatus:
    def __init__(self):
        self.time = 0
        self.robot_route_length = 0
        self.block_time = 0
        self.final_status = "run"
        self.explorated_area = 0
        self.unexplorated_area = 0

    def update_time(self):
        self.time += 1

    def update_area_info(self, map: map):
        one_dimension_map = list(itertools.chain(*map.grid))
        self.explorated_area = one_dimension_map.count(3)
        self.unexplorated_area = one_dimension_map.count(
            0) + one_dimension_map.count(4)

    def update_robot_route_length(self, cost_this_interval):
        self.robot_route_length += cost_this_interval
        if cost_this_interval == 0:
            self.block_time += 1
        else:
            self.block_time = 0

    def update_status(self, status):  # TODO
        self.final_status = status

    @staticmethod
    def judge_over(map: map):
        one_dimension_map = list(itertools.chain(*map.grid))
        # print(one_dimension_map)
        if UNEXPLARATION_AREA not in one_dimension_map and EXPLORATED_BOUND not in one_dimension_map:
            return True
        else:
            return False

    def judge_blocking(self):
        if self.block_time >= BLOCK_TIME:
            self.final_status = "block"
            return True
        elif self.time >= DIE_TIME:
            self.final_status = "block"
            return True
        else:
            return False

    def __repr__(self):
        return "run time is " + str(
            self.time) + " " + "robots total route length is " + str(
                self.robot_route_length
            ) + " " + "status is " + self.final_status

    def save_log(self, filename):
        with open(filename, "a") as f:
            f.write(
                str(self.time) + " " + str(self.robot_route_length) + " " +
                self.final_status + " " + str(self.explorated_area) + " " +
                str(self.unexplorated_area) + "\n")
