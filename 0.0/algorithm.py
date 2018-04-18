import random

from simulator import map as map_object

def action(map:map_object): # TODO
    '''

    '''
    map_grid_matrix = map.grid
    robot_amount = len(map.robots)
    return [random.randint(0,4) for i in range(robot_amount)]