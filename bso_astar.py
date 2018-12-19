import random
import math
import numpy as np

from settings import *
from simulator import Map as map_object
from simulator import RobotLocation, Frontier, Robot
from distance_calculator import astar_distance


def action(map: map_object):
    # initiallize
    map_grid_matrix = map.grid
    robot_amount = len(map.robots)
    allFrontiers = []
    centerfrontiers = []
    total_weights = []

    # robots' location
    robotLocations = getRobotLocation(map)
    # print(map_grid_matrix)
    # print("len(robotLocations):", len(robotLocations))

    # search the frontiers
    for i in range(robot_amount):
        allFrontiers.append(findFrontiers(map_grid_matrix, robotLocations[i]))
    # print("len(allFrontiers[0]):", len(allFrontiers[0]))

    # calculate the "centerfrontiers" and "total weights"
    if len(allFrontiers[0]) == 0:
        move_control = [random.randint(0, 4) for i in range(robot_amount)]
    else:
        [allFrontiers_sorted, centerfrontiers, total_weights] = calculate_allfrontiers(
            map_grid_matrix, allFrontiers, robotLocations)

        # update the frontiers by BSO, in order to emerge the collaberative behaviour
        for i in range(robot_amount):
            allFrontiers[i] = update_individuals_by_BSO(
                robot_amount, i, allFrontiers[i], allFrontiers_sorted, map_grid_matrix, robotLocations[i], centerfrontiers, total_weights)

        # generate the control comment by the weight of frontiers
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
        robot_location = RobotLocation(robot.x, robot.y)
        robotLocations.append(robot_location)
    return robotLocations


def findFrontiers(map_grid_matrix, robotlocation):
    frontiers = []
    for x in range(len(map_grid_matrix)):
        for y in range(len(map_grid_matrix[0])):
            if map_grid_matrix[x][y] == EXPLORATED_BOUND:
                m_frontier = Frontier(x, y, eichilide_distance(
                    map_grid_matrix, x, y, robotlocation), [robotlocation.x, robotlocation.y])
                frontiers.append(m_frontier)
    # print("frontiers:", len(frontiers))
    frontiers = frontierFilter(frontiers)
    # print("newfrontiers:", len(frontiers))
    return frontiers


def frontierFilter(frontiers):
    lenghtoffrotiers = 8
    newfrontiers = []
    if len(frontiers) >= lenghtoffrotiers:
        # remove 20% of the frontiers randomly
        remove_lenght = math.ceil(len(frontiers) * 0.2)
        for i in range(remove_lenght):
            index = math.ceil(random.random() * (len(frontiers) - 1))
            del(frontiers[index])

        # sort the frontiers by their weight, ascending order
        newfrontiers.append(frontiers[0])
        for i in range(1, len(frontiers)):
            temd_frontier = frontiers[i]
            index = len(newfrontiers) - 1
            for j in range(len(newfrontiers)):
                if newfrontiers[index - j].weight > temd_frontier.weight:
                    break
            newfrontiers.insert(index - 1, temd_frontier)

            # save only "lenghtoffrotiers" frontiers
            if len(newfrontiers) > lenghtoffrotiers:
                del(newfrontiers[lenghtoffrotiers])

    elif len(frontiers) > 0:
        newfrontiers = frontiers
        # sort the frontiers by their weight, ascending order
        newfrontiers.append(frontiers[0])
        for i in range(1, len(frontiers)):
            temd_frontier = frontiers[i]
            index = len(newfrontiers) - 1
            for j in range(len(newfrontiers)):
                if newfrontiers[index - j].weight > temd_frontier.weight:
                    break
            newfrontiers.insert(index - 1, temd_frontier)

    else:
        newfrontiers = frontiers

    return newfrontiers


def calculate_allfrontiers(map_grid_matrix, allFrontiers, robotLocations):
    allFrontiers_sorted = []
    centerfrontiers = []
    total_weights = []

    for i in range(len(allFrontiers)):
        frontiers = allFrontiers[i]
        frontiers_sorted = []
        robotlocation = robotLocations[i]

        # sort the frontiers with the astar distance
        frontiers_sorted.append(frontiers[0])
        [frontiers_sorted[0].weight, frontiers_sorted[0].dircetion] = calculate_distance(
            map_grid_matrix, frontiers_sorted[0].x, frontiers_sorted[0].y, robotlocation)
        total_weight = frontiers_sorted[0].weight
        for j in range(1, len(frontiers)):
            temd_frontier = frontiers[j]
            [temd_frontier.weight, temd_frontier.dircetion] = calculate_distance(
                map_grid_matrix, temd_frontier.x, temd_frontier.y, robotlocation)
            index = len(frontiers_sorted) - 1
            for z in range(len(frontiers_sorted)):
                if frontiers_sorted[index - z].weight > temd_frontier.weight:
                    break
            
            frontiers_sorted.insert(index - 1, temd_frontier)
            total_weight += frontiers_sorted[index - 1].weight

        allFrontiers_sorted.append(frontiers_sorted)
        centerfrontiers.append(frontiers_sorted[0])
        total_weights.append(total_weight)

    return allFrontiers_sorted, centerfrontiers, total_weights


def update_individuals_by_BSO(robot_amount, robotIndex, frontiers_1, allFrontiers_sorted, map_grid_matrix, robotlocation, centerfrontiers, total_weights):
    prob_one_cluster = 0.5  # 0.8
    frontiers_sorted_1 = allFrontiers_sorted[robotIndex]
    # print("robotIndex", robotIndex)

    # replace cluster center by at randomly generated center TODO
    # if random.random() < 0.2:
    #     cenIdx = math.ceil(random.random() * (len(allFrontiers) -1) )
    #     centerfrontiers[cenIdx] =

    for i in range(len(frontiers_1)):
        r_1 = random.random()
        indi_temp = frontiers_1[i]

        # update from self cluster
        if r_1 < prob_one_cluster:
            # select the claster center as a new candidate frontier
            if random.random() < 0.4:
                indi_temp = centerfrontiers[robotIndex]
            else:
                indi_1 = resampling(frontiers_sorted_1,
                                    total_weights[robotIndex])
                indi_temp = frontiers_sorted_1[indi_1]

            # replace the relative frontier
            if(frontiers_1[i].weight < indi_temp.weight):
                frontiers_1[i] = indi_temp

        # update throught other cluster
        else:
            # sclect another cluster randemly
            cluster_2 = robotIndex
            while cluster_2 != robotIndex:
                cluster_2 = math.ceil(random.random() * (robot_amount - 1))
            # print("cluster_2:", cluster_2)
            frontiers_sorted_2 = allFrontiers_sorted[cluster_2]
            # math.ceil(random.random() * (len(frontiers_2)-1))
            indi_2 = resampling(frontiers_sorted_2, total_weights[cluster_2])
            # math.ceil(random.random() * (len(frontiers)-1))
            indi_1 = resampling(frontiers_sorted_1, total_weights[robotIndex])
            if random.random() < 0.5:
                indi_temp = pick_from_two_cluster(
                    centerfrontiers[robotIndex], centerfrontiers[cluster_2], robotlocation)     # TODO this function need to be altered
            else:
                indi_temp = pick_from_two_cluster(
                    frontiers_sorted_1[indi_1], frontiers_sorted_2[indi_2], robotlocation)      # TODO this function need to be altered

            [indi_temp.weight, indi_temp.dircetion]= calculate_distance(
                map_grid_matrix, indi_temp.x, indi_temp.y, robotlocation)

            # replace the relative frontier directly
            frontiers_1[i] = indi_temp

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


def pick_from_two_cluster(frontier_W_1, frontier_W_2, robotlocation_W):
    reject_distance = 5
    indi_temp_R = Frontier(0, 0, 0, [0, 0])
    # print("frontier_W_1:", frontier_W_1.x, frontier_W_1.y)
    # print("frontier_W_2:", frontier_W_2.x, frontier_W_2.y)
    frontier_R_1 = Frontier(0, 0, 0, [0, 0])
    frontier_R_1.x = frontier_W_1.x - robotlocation_W.x
    frontier_R_1.y = frontier_W_1.y - robotlocation_W.y
    frontier_R_2 = Frontier(0, 0, 0, [0, 0])
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
    indi_temp_W = Frontier(0, 0, 0, [0, 0])
    indi_temp_W.x = indi_temp_R.x + robotlocation_W.x
    indi_temp_W.y = indi_temp_R.y + robotlocation_W.y
    # print("indi_temp_W:", indi_temp_W.x, indi_temp_W.y)
    return indi_temp_W


def eichilide_distance(map_grid_matrix, x, y, robotlocation):
    distance = math.hypot((x - robotlocation.x), (y - robotlocation.y))
    distance = 1 / distance
    return distance


def calculate_distance(map_grid_matrix, x, y, robotlocation):
    # convert list to array, and tackle the value
    map_array = np.array(map_grid_matrix)
    [rows, cols] = map_array.shape
    # print('rows:%d cols:%d', rows, cols)
    for i in range(rows):
        for j in range(cols):
            if(map_array[i, j] == UNEXPLARATION_AREA):
                map_array[i, j] = 1
            elif(map_array[i, j] == BLOCK_AREA):
                map_array[i, j] = 1
            else:
                map_array[i, j] = 0

    # calculate the distance by astar
    [distance, next_position] = astar_distance(
        map_array, (robotlocation.x, robotlocation.y), (x,  y))
    # print(distance)
    # print(next_position)

    distance = 1 / distance
    # print("frontier", x, y)
    # print("robotlocation", robotlocation.x, robotlocation.y)
    # print("distance", distance)
    return distance, next_position


def directionSelect(frontiers, robotlocation):
    rightWeight = 0
    leftWeight = 0
    upWeight = 0
    downWeight = 0
    for i in range(len(frontiers)):
        frontier = frontiers[i]
        print("frontier", frontier.direction[0], frontier.direction[0])
        print("next position:", frontier.direction)
        print("robotlocation", robotlocation.x, robotlocation.y)
        direction = calc_angle(robotlocation.x, robotlocation.y, frontier.direction[0], frontier.direction[0])
        print("direction:", direction)
        if direction > 45 and direction <= 175:
            downWeight += frontier.weight
        if (direction > 175 and direction <= 225):
            leftWeight += frontier.weight
        if (direction > 225 and direction <= 315):
            upWeight += frontier.weight
        if (direction > 315 and direction <= 360) or (direction > 0 and direction <= 45):
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
