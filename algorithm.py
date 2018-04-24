import random
import math

from settings import *
from simulator import map as map_object
from simulator import robotlocation, frontier, robot

def action(map:map_object):
    map_grid_matrix = map.grid
    robot_amount = len(map.robots)
    allFrontiers = []
    robotLocations = getRobotLocation(map)
    # print(map_grid_matrix)
    # print("len(robotLocations):", len(robotLocations))
    for i in range(robot_amount):
        allFrontiers.append(findFrontiers(map_grid_matrix, robotLocations[i]))
    print("len(allFrontiers[0]):", len(allFrontiers[0]))
    if len(allFrontiers[0]) == 0:
        move_control = [random.randint(0,4) for i in range(robot_amount)]
    else:
        allFrontiersCopy = allFrontiers.copy()
        for i in range(robot_amount):
            # print("robot_anoumt", robot_amount)
            allFrontiers[i] = updateIndividualByBSO(robot_amount, i, allFrontiers, map_grid_matrix, robotLocations[i])
        move_control = []
        for i in range(robot_amount):
            move_control.append(directionSelect(allFrontiers[i], robotLocations[i]))
    # move_control = [random.randint(0,4) for i in range(robot_amount)]
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
                m_frontier = frontier(x, y, calculateDistance(map_grid_matrix, x, y, robotlocation))
                frontiers.append(m_frontier)
    print("frontiers:", len(frontiers))
    frontiers = frontierFilter(frontiers)
    print("newfrontiers:", len(frontiers))
    return frontiers

def frontierFilter(frontiers):
    lenghtoffrotiers = 10 
    newfrontiers = []
    if len(frontiers) >= lenghtoffrotiers:
        newfrontiers.append(frontiers[0])
        for i in  range(1, len(frontiers)):
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

#fitness function
def calculateDistance(map_grid_matrix, x, y, robotlocation):
    distance = 1/(math.hypot((x - robotlocation.x), (y - robotlocation.y)))
    # print("frontier", x, y)
    # print("robotlocation", robotlocation.x, robotlocation.y)
    # print("distance", distance)
    return distance

def updateIndividualByBSO(robot_amount, robotIndex, allFrontiers, map_grid_matrix, robotlocation):
    prob_one_cluster = 0.5
    frontiers = allFrontiers[robotIndex]
    # print("robotIndex", robotIndex)
    centerFrontier = findCenterFrontier(frontiers)
    # replace cluster center by at randomly generated center TODO
    
    for i in range(len(frontiers)):
        r_1 = random.random()
        indi_temp = frontier(0, 0, 0)
        if r_1 < prob_one_cluster: # update from self cluster
            if random.random() < 0.4:
                indi_temp = centerFrontier
            else:
                indi_1 = math.ceil(random.random() * (len(frontiers)-1))
                indi_temp = frontiers[indi_1]
        else:   # update throught other cluster
            cluster_1 = robotIndex
            while cluster_1 != robotIndex:
                cluster_1 = math.ceil(random.random() * (robot_amount - 1))
            # print("cluster_1:", cluster_1)
            frontiers_1 =  allFrontiers[cluster_1]
            centerFrontier_1 = findCenterFrontier(frontiers_1)
            indi_1 = math.ceil(random.random() * (len(frontiers_1)-1))
            indi = math.ceil(random.random() * (len(frontiers)-1))
            tem = random.random()
            if random.random() < 0.5:
                indi_temp.x = tem * centerFrontier.x + (1 - tem) * centerFrontier_1.x
                indi_temp.y = tem * centerFrontier.y + (1 - tem) * centerFrontier_1.y
            else:
                indi_temp.x = tem * frontiers[indi].x + (1 - tem) * frontiers_1[indi_1].x
                indi_temp.y = tem * frontiers[indi].y + (1 - tem) * frontiers_1[indi_1].y
        indi_temp.weight = calculateDistance(map_grid_matrix, indi_temp.x, indi_temp.y, robotlocation)
        if(frontiers[i].weight < indi_temp.weight):
            frontiers[i] = indi_temp
    return frontiers

def findCenterFrontier(frontiers):
    # print("len(frontiers):", len(frontiers))
    centerfrontier = frontiers[0]
    for i in range(len(frontiers)):
        if centerfrontier.weight < frontiers[i].weight:
            centerfrontier = frontiers[i]
    # print("centerfrontier.weight: ", centerfrontier.weight)
    return centerfrontier

def directionSelect(frontiers, robotlocation):
    rightWeight = 0
    leftWeight = 0
    upWeight = 0
    downWeight = 0
    for i in range(len(frontiers)):
        frontier = frontiers[i]
        # print("frontier", frontier.x, frontier.y)
        # print("robotlocation", robotlocation.x, robotlocation.y)
        angle = calc_angle(robotlocation.x, robotlocation.y, frontier.x, frontier.y)
        # print("angle:", angle)
        if angle > 45 and angle <= 175:
            downWeight += frontier.weight
        if (angle > 175 and angle <= 225):
            leftWeight += frontier.weight
        if (angle > 225 and angle <= 315):
            upWeight += frontier.weight
        if (angle > 315 and angle <= 360) or (angle > 0 and angle <= 45):
            rightWeight += frontier.weight
    print("leftWeight:", leftWeight)
    print("downWeight:", downWeight)
    print("rightWeight", rightWeight)
    print("upWeight:", upWeight)
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

'''
point_e frontier
point_s robot
north 360
west 90
south 180
east 270
'''
def calc_angle(x_point_s, y_point_s, x_point_e, y_point_e):
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