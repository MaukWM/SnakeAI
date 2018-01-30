import math
import random
import copy

import numpy as np

from gameobjects import GameObject
from move import Move, Direction


def get_manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class Agent:

    current_score = 0
    scores = []
    visited_nodes = []

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

        if score > self.current_score:
            self.visited_nodes = []

        self.current_score = score

        heuristic = []
        for x in range(len(board)):
            heuristic.append([])
            for y in range(len(board[x])):
                heuristic[x].append(0)

        food = []
        snek = (0,0)

        # find snek
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == GameObject.SNAKE_HEAD:
                    snek = (x,y)

        self.visited_nodes.append(snek)

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

        # calculate heuristic values to closest food
        for x in range(len(heuristic)):
            for y in range(len(heuristic[x])):
                heuristic[x][y] = 1 + get_manhattan_distance((x,y), best_food_coordinate)

        # print(board)

        best_move_value = math.inf
        best_move = Move.STRAIGHT
        if (direction == Direction.NORTH):
            # Move.LEFT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]-1][snek[1]] < best_move_value) and (board[snek[0]-1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]-1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]-1][snek[1]]
                        best_move = Move.LEFT
            # Move.STRAIGHT
            if snek[1] != 0:
                if (snek[0], snek[1]-1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]-1] < best_move_value) and (board[snek[0]][snek[1]-1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]-1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]-1]
                        best_move = Move.STRAIGHT
            # Move.RIGHT
            if snek[0] != 24:
                if (snek[0]+1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]+1][snek[1]] < best_move_value) and (board[snek[0]+1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]+1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]+1][snek[1]]
                        best_move = Move.RIGHT

        elif (direction == Direction.SOUTH):
            # Move.LEFT
            if snek[0] != 24:
                if (snek[0]+1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]+1][snek[1]] < best_move_value) and (board[snek[0]+1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]+1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]+1][snek[1]]
                        best_move = Move.LEFT
            # Move.STRAIGHT
            if snek[1] != 24:
                if (snek[0], snek[1] + 1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]+1] < best_move_value) and (board[snek[0]][snek[1]+1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]+1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]+1]
                        best_move = Move.STRAIGHT
            # Move.RIGHT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]-1][snek[1]] < best_move_value) and (board[snek[0]-1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]-1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]-1][snek[1]]
                        best_move = Move.RIGHT

        elif (direction == Direction.WEST):
            # Move.LEFT
            if snek[1] != 24:
                if (snek[0], snek[1]+1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]+1] < best_move_value) and (board[snek[0]][snek[1]+1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]+1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]+1]
                        best_move = Move.LEFT
            # Move.STRAIGHT
            if snek[0] != 0:
                if (snek[0]-1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]-1][snek[1]] < best_move_value) and (board[snek[0]-1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]-1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]-1][snek[1]]
                        best_move = Move.STRAIGHT
            # Move.RIGHT
            if snek[1] != 0:
                if (snek[0], snek[1] - 1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]-1] < best_move_value) and (board[snek[0]][snek[1]-1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]-1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]-1]
                        best_move = Move.RIGHT

        elif (direction == Direction.EAST):
            # Move.LEFT
            if snek[1] != 0:
                if (snek[0], snek[1] - 1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]-1] < best_move_value) and (board[snek[0]][snek[1]-1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]-1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]-1]
                        best_move = Move.LEFT
            # Move.STRAIGHT
            if snek[0] != 24:
                if (snek[0]+1, snek[1]) not in self.visited_nodes:
                    if (heuristic[snek[0]+1][snek[1]] < best_move_value) and (board[snek[0]+1][snek[1]] is not GameObject.SNAKE_BODY) and (board[snek[0]+1][snek[1]] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]+1][snek[1]]
                        best_move = Move.STRAIGHT
            # Move.RIGHT
            if snek[1] != 24:
                if (snek[0], snek[1] + 1) not in self.visited_nodes:
                    if (heuristic[snek[0]][snek[1]+1] < best_move_value) and (board[snek[0]][snek[1]+1] is not GameObject.SNAKE_BODY) and (board[snek[0]][snek[1]+1] is not GameObject.WALL):
                        best_move_value = heuristic[snek[0]][snek[1]+1]
                        best_move = Move.RIGHT

        return best_move




        # create route

        # save route

        # perform route


        # x = random.randint(1,3)
        # if (x==1):
        #     return Move.STRAIGHT
        # elif (x==2):
        #     return Move.RIGHT
        # else:
        #     return Move.LEFT

    def on_die(self):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """
        self.scores.append(self.current_score)

        print(self.scores)
        print("average: ", np.average(self.scores))

        pass
