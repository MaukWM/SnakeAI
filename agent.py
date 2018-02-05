import math
import random
import copy
from queue import PriorityQueue

import numpy as np
import time

from gameobjects import GameObject
from move import Move, Direction

BOARD_SIZE = 25

class Node:
    def __init__(self, point, parent=None):
        self.point = point
        self.x = point[0]
        self.y = point[1]
        self.parent = parent
        self.h = 0
        self.g = 0
        self.f = 0

    def hasParent(self):
        return self.parent is None

    def path_to_parent(self):
        if self.parent is not None:
            # fucking gore code maar is beter dan tuple, tuple. Trust me on this one.
            return self.point + self.parent.path_to_parent()
        else:
            return self.point


def get_manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def a_star_search(start, goal, board):
    open_list = []
    closed_list = []

    start_node = Node(start)

    open_list.append(start_node)

    while not len(open_list) == 0:
        # find node with lowest f
        best_node = None
        best_node_f = math.inf
        for node in open_list:
            if node.f < best_node_f:
                best_node = node
                best_node_f = node.f

        # pop best_node off the open list
        open_list.remove(best_node)
        # print(best_node.x, best_node.y)

        node_north = None
        node_east = None
        node_west = None
        node_south = None

        # generate 4 successors
        if not (best_node.y >= BOARD_SIZE-1):
            node_south = Node((best_node.x, best_node.y+1), best_node)
        if not (best_node.y <= 0):
            node_north = Node((best_node.x, best_node.y-1), best_node)
        if not (best_node.x <= 0):
            node_west = Node((best_node.x-1, best_node.y), best_node)
        if not (best_node.x >= BOARD_SIZE-1):
            node_east = Node((best_node.x+1, best_node.y), best_node)

        successors = [node_north, node_south, node_west, node_east]

        for successor in successors:
            if successor is None:
                continue
            if successor.point == goal:
                return successor

            successor.g = 1
            successor.h = get_manhattan_distance(successor.point, goal)
            successor.f = successor.g + successor.h

            skip = False
            for node in open_list:
                if ((node.point == successor.point)): # and (node.f < successor.f)): what is commented out ruins lives
                    skip = True
                    break

            for node in closed_list:
                if ((node.point == successor.point)): # and (node.f < successor.f)): what is commented out ruins lives
                    skip = True
                    break

            if not skip:
                if successor.x != -1 and successor.x != BOARD_SIZE and successor.y != -1 and successor.y != BOARD_SIZE:
                    tile_object = board[successor.x][successor.y]
                    if (tile_object == GameObject.SNAKE_BODY) or (tile_object == GameObject.WALL) or (tile_object == GameObject.SNAKE_HEAD):
                        closed_list.append(successor)
                    elif (tile_object == GameObject.FOOD):
                        return successor
                    else:
                        open_list.append(successor)
                else:
                    closed_list.append(successor)

        closed_list.append(best_node)

        closed_list_num = len(closed_list)
        open_list_num = len(open_list)

        # print("closed list:", len(closed_list))
        # print("open list:", len(open_list))

    return None


class Agent:

    trial = 0
    current_score = 0
    scores = []
    path = []
    times = []

    def get_move(self, board, score, turns_alive, turns_to_starve, direction):
        """This function behaves as the 'brain' of the snake. You only need to change the code in this function for
        the project. Every turn the agent needs to return a move. This move will be executed by the snake. If this
        functions fails to return a valid return (see return), the snake will die (as this confuses its tiny brain
        that much that it will explode). The starting direction of the snake will be North.

        :param board: A two dimensional array representing the current state of the board. The upper left most
        coordinate is equal to (0,0) and each coordinate (x,y) can be accessed by executing board[x][y]. At each
        coordinate a GameObject is present. This can be either GameObject.EMPTY (meaning there is nothing at the
        given coordinate), GameObject.FOOD (meaning there is food at the given coordinate), GameObject.WALL (meaning
        there is a wall at the given coordinate. TIP: do not run into them), GameObject.SNAKE_HEAD (meaning the head
        of the snake is located there) and GameObject.SNAKE_BODY (meaning there is a body part of the snake there.
        TIP: also, do not run into these). The snake will also die when it tries to escape the board (moving out of
        the boundaries of the array)

        :param score: The current score as an integer. Whenever the snake eats, the score will be increased by one.
        When the snake tragically dies (i.e. by running its head into a wall) the score will be reset. In other
        words, the score describes the score of the current (alive) worm.

        :param turns_alive: The number of turns (as integer) the current snake is alive.

        :param turns_to_starve: The number of turns left alive (as integer) if the snake does not eat. If this number
        reaches 1 and there is not eaten the next turn, the snake dies. If the value is equal to -1, then the option
        is not enabled and the snake can not starve.

        :param direction: The direction the snake is currently facing. This can be either Direction.NORTH,
        Direction.SOUTH, Direction.WEST, Direction.EAST. For instance, when the snake is facing east and a move
        straight is returned, the snake wil move one cell to the right.

        :return: The move of the snake. This can be either Move.LEFT (meaning going left), Move.STRAIGHT (meaning
        going straight ahead) and Move.RIGHT (meaning going right). The moves are made from the viewpoint of the
        snake. This means the snake keeps track of the direction it is facing (North, South, West and East).
        Move.LEFT and Move.RIGHT changes the direction of the snake. In example, if the snake is facing north and the
        move left is made, the snake will go one block to the left and change its direction to west.
        """

        skip = False

        if (score > self.current_score):
            self.path = []
        self.current_score = score


        # find snek
        snek = (0, 0)
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == GameObject.SNAKE_HEAD:
                    snek = (x, y)

        if len(self.path) == 0:

            food = []

            # find food
            for x in range(len(board)):
                for y in range(len(board[x])):
                    if board[x][y] == GameObject.FOOD:
                        food.append((x,y,get_manhattan_distance(snek, (x,y))))

            best_food = math.inf
            best_food_coordinate = (0,0)
            for x in range(len(food)):
                if food[x][2] < best_food:
                    best_food = food[x][2]
                    best_food_coordinate = (food[x][0], food[x][1])

            # print("Food:", best_food_coordinate)

            start_time = time.time() * 1000
            a_star_node = a_star_search(snek, best_food_coordinate, board)
            end_time = time.time() * 1000
            total_time = end_time-start_time
            self.times.append(total_time)


            if a_star_node is None:
                skip = True

            else:
                raw_sauce = a_star_node.path_to_parent()

                # ignore the following lines, please...
                for to_be_tuple_coordinate in range(len(raw_sauce)//2):
                    self.path.append((raw_sauce[2*to_be_tuple_coordinate], raw_sauce[2*to_be_tuple_coordinate+1]))

                # we do this to remove the starting position from the sequence
                self.path.pop()
                # print("Current path:", self.path)

        if skip:
            self.path = []

            x = random.randint(1, 3)
            if (x == 1):
                return Move.STRAIGHT
            elif (x == 2):
                return Move.RIGHT
            else:
                return Move.LEFT


        next_step = self.path.pop()

        if (direction == Direction.NORTH):
            # Move.LEFT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) == next_step:
                    return Move.LEFT
            # Move.STRAIGHT
            if snek[1] != 0:
                if (snek[0], snek[1]-1) == next_step:
                    return Move.STRAIGHT
            # Move.RIGHT
            if snek[0] != (BOARD_SIZE-1):
                if (snek[0]+1, snek[1]) == next_step:
                    return Move.RIGHT

        elif (direction == Direction.SOUTH):
            # Move.LEFT
            if snek[0] != (BOARD_SIZE-1):
                if (snek[0]+1, snek[1]) == next_step:
                    return Move.LEFT
            # Move.STRAIGHT
            if snek[1] != (BOARD_SIZE-1):
                if (snek[0], snek[1] + 1) == next_step:
                    return Move.STRAIGHT
            # Move.RIGHT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) == next_step:
                    return Move.RIGHT

        elif (direction == Direction.WEST):
            # Move.LEFT
            if snek[1] != (BOARD_SIZE-1):
                if (snek[0], snek[1]+1) == next_step:
                    return Move.LEFT
            # Move.STRAIGHT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) == next_step:
                    return Move.STRAIGHT
            # Move.RIGHT
            if snek[1] != 0:
                if (snek[0], snek[1] - 1) == next_step:
                    return Move.RIGHT

        elif (direction == Direction.EAST):
            # Move.LEFT
            if snek[1] != 0:
                if (snek[0], snek[1] - 1) == next_step:
                    return Move.LEFT
            # Move.STRAIGHT
            if snek[0] != (BOARD_SIZE-1):
                if (snek[0]+1, snek[1]) == next_step:
                    return Move.STRAIGHT
            # Move.RIGHT
            if snek[1] != (BOARD_SIZE-1):
                if (snek[0], snek[1] + 1) == next_step:
                    return Move.RIGHT

        x = random.randint(1, 3)
        if (x == 1):
            return Move.STRAIGHT
        elif (x == 2):
            return Move.RIGHT
        else:
            return Move.LEFT


    def on_die(self):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """
        self.scores.append(self.current_score)
        self.trial += 1

        self.path = []

        print(self.scores)
        print("average on trial ", self.trial, ":", np.average(self.scores))
        print("Average time to find path:", np.average(self.times))

        pass
