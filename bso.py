import random
import math
import numpy as np

from settings import *
from simulator import map as map_object
from simulator import robotlocation, frontier, robot
from distance_calculator import astar_distance


def action(map: map_object):
    map_grid_matrix = map.grid
    robot_amount = len(map.robots)
    allFrontiers = []
    centerfrontiers = []
    total_weights = []

    robotLocations = getRobotLocation(map)
    # print(map_grid_matrix)
    # print("len(robotLocations):", len(robotLocations))
    for i in range(robot_amount):
        allFrontiers.append(findFrontiers(map_grid_matrix, robotLocations[i]))
    # print("len(allFrontiers[0]):", len(allFrontiers[0]))
    if len(allFrontiers[0]) == 0:
        move_control = [random.randint(0, 4) for i in range(robot_amount)]
    else:
        calculate_allfrontiers(allFrontiers, centerfrontiers, total_weights)

        # allFrontiersCopy = allFrontiers.copy()

        for i in range(robot_amount):
            allFrontiers[i] = updateIndividualByBSO(
                robot_amount, i, allFrontiers, map_grid_matrix, robotLocations[i], centerfrontiers, total_weights)
        move_control = []
        for i in range(robot_amount):
            move_control.append(directionSelect(
                allFrontiers[i], robotLocations[i]))
    print("move_control:", move_control)
    return move_control


def getRobotLocation(map):
    robotLocations = []
    for i in range(len(map.robots)):
        robot = map.robots[i]
        robot_location = robotlocation(robot.x, robot.y)
        robotLocations.append(robot_location)
    return robotLocations


def findFrontiers(map_grid_matrix, robotlocation):
    frontiers = []
    for x in range(len(map_grid_matrix)):
        for y in range(len(map_grid_matrix[0])):
            if map_grid_matrix[x][y] == EXPLORATED_BOUND:
                m_frontier = frontier(x, y, calculateDistance(
                    map_grid_matrix, x, y, robotlocation))
                frontiers.append(m_frontier)
    # print("frontiers:", len(frontiers))
    frontiers = frontierFilter(frontiers)
    # print("newfrontiers:", len(frontiers))
    return frontiers


def frontierFilter(frontiers):
    lenghtoffrotiers = 10
    newfrontiers = []
    if len(frontiers) >= lenghtoffrotiers:
        remove_lenght = math.ceil(len(frontiers) * 0.2)
        for i in range(remove_lenght):
            index = math.ceil(random.random() * (len(frontiers) - 1))
            del(frontiers[index])
        newfrontiers.append(frontiers[0])
        for i in range(1, len(frontiers)):
            temd_frontier = frontiers[i]
            index = len(newfrontiers) - 1
            for j in range(len(newfrontiers)):
                if newfrontiers[index - j].weight > temd_frontier.weight:
                    break
            newfrontiers.insert(index - 1, temd_frontier)
            if len(newfrontiers) > lenghtoffrotiers:
                del(newfrontiers[lenghtoffrotiers])
    else:
        newfrontiers = frontiers
    return newfrontiers


def calculate_allfrontiers(allFrontiers, centerfrontiers, total_weights):
    for i in range(len(allFrontiers)):
        frontiers = allFrontiers[i]
        calculate_frontiers(frontiers, i, centerfrontiers, total_weights)


def calculate_frontiers(frontiers, index, centerfrontiers, total_weights):
    if len(centerfrontiers) <= index:
        centerfrontiers.append(frontier(0, 0, 0))
    if len(total_weights) <= index:
        total_weights.append(0)
    total_weight = 0
    centerfrontier = frontiers[0]
    for i in range(len(frontiers)):
        total_weight += frontiers[i].weight
        if centerfrontiers[index].weight < frontiers[i].weight:
            centerfrontier = frontiers[i]
    centerfrontiers[index] = centerfrontier
    total_weights[index] = total_weight

# fitness function TODO


# UNEXPLARATION_AREA = 0
# ROBOT_AREA = 1
# BLOCK_AREA = 2
# EXPLORATED_AREA = 3
# EXPLORATED_BOUND = 4
def calculateDistance(map_grid_matrix, x, y, robotlocation):
    # # convert list to array, and tackle the value
    # map_array = np.array(map_grid_matrix)
    # [rows, cols] = map_array.shape
    # # print('rows:%d cols:%d', rows, cols)
    # for i in range(rows):
    #     for j in range(cols):
    #         if(map_array[i, j] == UNEXPLARATION_AREA):
    #             map_array[i, j] = 1
    #         elif(map_array[i, j] == BLOCK_AREA):
    #             map_array[i, j] = 1
    #         else:
    #             map_array[i, j] = 0

    distance = math.hypot((x - robotlocation.x), (y - robotlocation.y))
    # [distance, next_position] = astar_distance(map_array, (robotlocation.x, robotlocation.y), (x,  y))

    distance = 1 / distance
    # print("frontier", x, y)
    # print("robotlocation", robotlocation.x, robotlocation.y)
    # print("distance", distance)
    return distance


def updateIndividualByBSO(robot_amount, robotIndex, allFrontiers, map_grid_matrix, robotlocation, centerfrontiers, total_weights):
    prob_one_cluster = 0.5  # 0.8
    frontiers_1 = allFrontiers[robotIndex]
    # print("robotIndex", robotIndex)

    # replace cluster center by at randomly generated center TODO
    # if random.random() < 0.2:
    #     cenIdx = math.ceil(random.random() * (len(allFrontiers) -1) )
    #     centerfrontiers[cenIdx] =

    for i in range(len(frontiers_1)):
        r_1 = random.random()
        indi_temp = frontier(0, 0, 0)
        if r_1 < prob_one_cluster:  # update from self cluster
            if random.random() < 0.4:
                indi_temp = centerfrontiers[robotIndex]
            else:
                # math.ceil(random.random() * (len(frontiers)-1))
                indi_1 = resampling(frontiers_1, total_weights[robotIndex])
                indi_temp = frontiers_1[indi_1]
            indi_temp.weight = calculateDistance(
                map_grid_matrix, indi_temp.x, indi_temp.y, robotlocation)
            if(frontiers_1[i].weight < indi_temp.weight):
                frontiers_1[i] = indi_temp
                calculate_frontiers(frontiers_1, robotIndex,
                                    centerfrontiers, total_weights)
        else:   # update throught other cluster
            cluster_2 = robotIndex
            while cluster_2 != robotIndex:
                cluster_2 = math.ceil(random.random() * (robot_amount - 1))
            # print("cluster_2:", cluster_2)
            frontiers_2 = allFrontiers[cluster_2]
            # math.ceil(random.random() * (len(frontiers_2)-1))
            indi_2 = resampling(frontiers_2, total_weights[cluster_2])
            # math.ceil(random.random() * (len(frontiers)-1))
            indi_1 = resampling(frontiers_1, total_weights[robotIndex])
            if random.random() < 0.5:
                indi_temp = pick_two_cluster(
                    centerfrontiers[robotIndex], centerfrontiers[cluster_2], robotlocation)
            else:
                indi_temp = pick_two_cluster(
                    frontiers_1[indi_1], frontiers_2[indi_2], robotlocation)
            # print("robotlocation", robotlocation.x, robotlocation.y)
            indi_temp.weight = calculateDistance(
                map_grid_matrix, indi_temp.x, indi_temp.y, robotlocation)
            # if(frontiers_1[i].weight < indi_temp.weight):
            frontiers_1[i] = indi_temp
            calculate_frontiers(frontiers_1, robotIndex,
                                centerfrontiers, total_weights)
    return frontiers_1


def resampling(frontiers, total_weight):
    """
    low variance re-sampling
    """
    random_weight = random.random() * total_weight
    ind = 0
    weight_sum = frontiers[ind].weight
    for i in range(len(frontiers) - 1):
        if weight_sum > random_weight:
            return ind
        else:
            ind += 1
            weight_sum += frontiers[ind].weight
    return ind


def pick_two_cluster(frontier_W_1, frontier_W_2, robotlocation_W):
    reject_distance = 5
    indi_temp_R = frontier(0, 0, 0)
    # print("frontier_W_1:", frontier_W_1.x, frontier_W_1.y)
    # print("frontier_W_2:", frontier_W_2.x, frontier_W_2.y)
    frontier_R_1 = frontier(0, 0, 0)
    frontier_R_1.x = frontier_W_1.x - robotlocation_W.x
    frontier_R_1.y = frontier_W_1.y - robotlocation_W.y
    frontier_R_2 = frontier(0, 0, 0)
    frontier_R_2.x = frontier_W_2.x - robotlocation_W.x
    frontier_R_2.y = frontier_W_2.y - robotlocation_W.y
    # print("frontier_R_1:", frontier_R_1.x, frontier_R_1.y)
    # print("frontier_R_2:", frontier_R_2.x, frontier_R_2.y)

    ff_distance = math.hypot(
        (frontier_R_1.x - frontier_R_2.x), (frontier_R_1.y - frontier_R_2.y))
    # print("ff_distance:", ff_distance)
    if ff_distance < reject_distance:
        if ff_distance != 0:
            indi_temp_R.x = frontier_R_1.x * \
                (reject_distance * 2 / ff_distance)
            indi_temp_R.y = frontier_R_1.y * \
                (reject_distance * 2 / ff_distance)
        else:
            indi_temp_R.x = frontier_R_1.x * 4
            indi_temp_R.y = frontier_R_1.y * 4
    else:
        indi_temp_R.x = frontier_R_1.x
        indi_temp_R.y = frontier_R_1.y
    # print("indi_temp_R:", indi_temp_R.x, indi_temp_R.y)
    indi_temp_W = frontier(0, 0, 0)
    indi_temp_W.x = indi_temp_R.x + robotlocation_W.x
    indi_temp_W.y = indi_temp_R.y + robotlocation_W.y
    # print("indi_temp_W:", indi_temp_W.x, indi_temp_W.y)
    return indi_temp_W


def directionSelect(frontiers, robotlocation):
    rightWeight = 0
    leftWeight = 0
    upWeight = 0
    downWeight = 0
    for i in range(len(frontiers)):
        frontier = frontiers[i]
        # print("frontier", frontier.x, frontier.y)
        # print("robotlocation", robotlocation.x, robotlocation.y)
        angle = calc_angle(robotlocation.x, robotlocation.y,
                           frontier.x, frontier.y)
        # print("angle:", angle)
        if angle > 45 and angle <= 175:
            downWeight += frontier.weight
        if (angle > 175 and angle <= 225):
            leftWeight += frontier.weight
        if (angle > 225 and angle <= 315):
            upWeight += frontier.weight
        if (angle > 315 and angle <= 360) or (angle > 0 and angle <= 45):
            rightWeight += frontier.weight
    # print("leftWeight:", leftWeight)
    # print("downWeight:", downWeight)
    # print("rightWeight", rightWeight)
    # print("upWeight:", upWeight)
    maxWeight = 0
    if maxWeight < leftWeight:
        action = 1
        maxWeight = leftWeight
    if maxWeight < downWeight:
        action = 2
        maxWeight = downWeight
    if maxWeight < rightWeight:
        action = 3
        maxWeight = rightWeight
    if maxWeight < upWeight:
        action = 4
        maxWeight = upWeight
    return action


def calc_angle(x_point_s, y_point_s, x_point_e, y_point_e):
    """
    point_e frontier
    point_s robot
    north 360
    west 90
    south 180
    east 270
    """
    angle = 0
    y_se = y_point_e - y_point_s
    x_se = x_point_e - x_point_s
    if x_se == 0 and y_se > 0:
        angle = 360
    if x_se == 0 and y_se < 0:
        angle = 180
    if y_se == 0 and x_se > 0:
        angle = 90
    if y_se == 0 and x_se < 0:
        angle = 270
    if x_se > 0 and y_se > 0:
        angle = math.atan(x_se/y_se)*180/math.pi
    elif x_se < 0 and y_se > 0:
        angle = 360 + math.atan(x_se/y_se)*180/math.pi
    elif x_se < 0 and y_se < 0:
        angle = 180 + math.atan(x_se/y_se)*180/math.pi
    elif x_se > 0 and y_se < 0:
        angle = 180 + math.atan(x_se/y_se)*180/math.pi
    return angle
