import math
import numpy
from heapq import heappush, heappop


def heuristic_cost_estimate(neighbor, goal):
    x = neighbor[0] - goal[0]
    y = neighbor[1] - goal[1]
    return abs(x) + abs(y)


def dist_between(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path


# astar function returns a list of points (shortest path)
def astar(array, start, goal):

    # 8个方向 (1, 1),(1, -1), (-1, 1), (-1, -1)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic_cost_estimate(start, goal)}

    openSet = []
    heappush(openSet, (fscore[start], start))   # 往堆中插入一条新的值

    # while openSet is not empty
    while openSet:
        # current := the node in openSet having the lowest fScore value
        current = heappop(openSet)[1]   # 从堆中弹出fscore最小的节点

        if current == goal:
            return reconstruct_path(came_from, current)

        close_set.add(current)

        for i, j in directions:      # 对当前节点的 8 个相邻节点一一进行检查
            neighbor = current[0] + i, current[1] + j

            # 判断节点是否在地图范围内，并判断是否为障碍物
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1:   # 1为障碍物
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            # Ignore the neighbor which is already evaluated.
            if neighbor in close_set:
                continue

            #  The distance from start to a neighbor via current
            tentative_gScore = gscore[current] + \
                dist_between(current, neighbor)

            # Discover a new node
            if neighbor not in [i[1] for i in openSet]:
                heappush(openSet, (fscore.get(neighbor, numpy.inf), neighbor))
            # This is not a better path.
            elif tentative_gScore >= gscore.get(neighbor, numpy.inf):
                continue

            # This path is the best until now. Record it!
            came_from[neighbor] = current
            gscore[neighbor] = tentative_gScore
            fscore[neighbor] = tentative_gScore + \
                heuristic_cost_estimate(neighbor, goal)

    return False


# def eichilide_distance():
#     distance = math.hypot((x - robotlocation.x), (y - robotlocation.y))
#     return distance


def astar_distance(map_array, start, goal):
    path = astar(map_array, start, goal)
    if(path != False):
        # reture the lenght of this path and the next position expected to move
        return len(path), path[-2]

    return 1, start


if __name__ == "__main__":
    nmap = numpy.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    path = astar(nmap, (0, 0), (10, 13))
    print(path[-2])

    for i in range(len(path)):
        nmap[path[i]] = 100

    print(nmap)
