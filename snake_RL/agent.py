from gameobjects import GameObject
from move import Move, Direction
import numpy
# Internal reward model, initialise to 0 for all 25 spaces.
model = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
# Discount
alpha = 0.8
# Learning rate
gamma = -0.04

# internal game stuff
foodposition = [0, 0]
wallposition = [0, 0]

# for initialising
start = True
score_internal = 0
step = 0

# [0,0] is top left

class Agent:

    def __init__(self):
        """" Constructor of the Agent, can be used to set up variables """

    def find_game_elements(self, board):
        global foodposition
        global wallposition
        for x in range(0, 5):
            for y in range(0, 5):
                if board[x][4 - y] == GameObject.FOOD:
                    model[x][4 - y] = 1
                #    print("[AGENT]: found FOOD at  x:" + str(x) + " y:" + str(4 - y))
                    foodposition = [x, 4 - y]
                elif board[x][4 - y] == GameObject.WALL:
                    model[x][4 - y] = -1
                #    print("[AGENT]: found WALL at  x:" + str(x) + " y:" + str(4 - y))
                    wallposition = [x, 4 - y]
                else: # empty space
                #    print("[AGENT]: found nothing at  x:" + str(x) + " y:" + str(4 - y))
                    pass

    def update_rewards(self):
        global step
        step = step + 1
        global foodposition
        global wallposition
        global model
        for x in range(0, 5):
            for y in range(0, 5):
                # food and walls get different updates.
                if not [x, 4 - y] == foodposition and not [x, 4 - y] == wallposition:
                    # punishment for not being a final state
                    model[x][4 - y] = model[x][4 - y] + gamma
                    # bonus for being close to a nice neighbour
                    neighbour_rewards = self.get_neighbour_rewards([x, 4 - y], False)
                    if max(neighbour_rewards[0], neighbour_rewards[1], neighbour_rewards[2], neighbour_rewards[3]) > model[x][4 - y]:
                        model[x][4 - y] = (model[x][4 - y] + alpha * max(neighbour_rewards[0], neighbour_rewards[1],
                                                                         neighbour_rewards[2], neighbour_rewards[3])) / 2


    def get_neighbour_rewards(self, pos, calledfornextmove):
        pos = list(pos)
        if calledfornextmove:
            #print("position according to neighbour rewards: " + str(pos))
            pass
        if 0 < pos[0] < 4:
            if 0 < pos[1] < 4:
                # not at an edge or corner
                return (model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] + 1],
                        model[pos[0]][pos[1] - 1])
            elif pos[1] == 0:
                # top edge
                return (model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] + 1],
                        -1000)
            else:
                # bottom edge
                return (model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        -1000,
                        -model[pos[0]][pos[1] - 1])
        elif pos[0] == 0:
            # left edge
            if pos[1] == 0:
                # topleft corner
                return (-1000,
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] + 1],
                        -1000)
            elif pos[1] == 4:
                # bottomleft corner
                return (-1000,
                        model[pos[0] + 1][pos[1]],
                        -1000,
                        model[pos[0]][pos[1] - 1])
            else:
                # just the left edge here
                return (-1000,
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] + 1],
                        model[pos[0]][pos[1] - 1])
        else:
            # right edge
            if pos[1] == 0:
                # topright corner
                return (model[pos[0] - 1][pos[1]],
                        -1000,
                        model[pos[0]][pos[1] + 1],
                        -1000)
            elif pos[1] == 4:
                # bottomright corner
                return (model[pos[0] - 1][pos[1]],
                        -1000,
                        -1000,
                        model[pos[0]][pos[1] - 1])
            else:
                # just the right edge here
                return (model[pos[0] - 1][pos[1]],
                        -1000,
                        model[pos[0]][pos[1] + 1],
                        model[pos[0]][pos[1] - 1])

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        # model initialisation
        global model
        global score_internal
        global start

        if score != score_internal:
            # Found the food! reset internal data by calling on_die
            self.on_die(head_position, board, score, body_parts)

        #for y in range(0, 5):
        #    print(str(str(model[0][y]) + "     ")[:6] + " " + str(str(model[1][y]) + "     ")[:6] + " " +
        #          str(str(model[2][y]) + "     ")[:6] + " " + str(str(model[3][y]) + "     ")[:6] + " " +
        #          str(str(model[4][y]) + "     ")[:6])
        #print()

        if start:
            self.find_game_elements(board)
        #    print("[AGENT]: Model - " + str(model))
            start = False
        self.update_rewards()
        possible_moves = self.get_neighbour_rewards(head_position, True)
        #print("[AGENT]: neighbour reward NORTH: " + str(possible_moves[3]))
        #print("[AGENT]: neighbour reward EAST: " + str(possible_moves[1]))
        #print("[AGENT]: neighbour reward SOUTH: " + str(possible_moves[2]))
        #print("[AGENT]: neighbour reward WEST: " + str(possible_moves[0]))
        #print()
        """ get_neighbour_rewards returns possible moves as follows:
            possible_moves[0] : WEST direction
            possible_moves[1] : EAST direction
            possible_moves[2] : SOUTH direction
            possible_moves[3] : NORTH direction"""
        possible_moves = list(possible_moves)
        while True:
            if len(possible_moves) == 1:
                break
            if max(possible_moves[0], possible_moves[1], possible_moves[2], possible_moves[3]) == possible_moves[0]:
                # GO WEST
                if direction == Direction.NORTH:
                    return Move.LEFT
                elif direction == Direction.EAST:
                    possible_moves[0] = -1000
                    continue
                elif direction == Direction.SOUTH:
                    return Move.RIGHT
                else:
                    return Move.STRAIGHT
            elif max(possible_moves[0], possible_moves[1], possible_moves[2], possible_moves[3]) == possible_moves[1]:
                # GO EAST
                if direction == Direction.NORTH:
                    return Move.RIGHT
                elif direction == Direction.EAST:
                    return Move.STRAIGHT
                elif direction == Direction.SOUTH:
                    return Move.LEFT
                else:
                    possible_moves[1] = -1000
                    continue
            elif max(possible_moves[0], possible_moves[1], possible_moves[2], possible_moves[3]) == possible_moves[2]:
                #GO SOUTH
                if direction == Direction.NORTH:
                    possible_moves[2] = -1000
                    continue
                elif direction == Direction.EAST:
                    return Move.RIGHT
                elif direction == Direction.SOUTH:
                    return Move.STRAIGHT
                else:
                    return Move.LEFT
            else:
                #GO NORTH
                if direction == Direction.NORTH:
                    return Move.STRAIGHT
                elif direction == Direction.EAST:
                    return Move.LEFT
                elif direction == Direction.SOUTH:
                    possible_moves[3] = -1000
                else:
                    return Move.RIGHT
        # for now...
        return Move.STRAIGHT

    def should_redraw_board(self):
        """
        This function indicates whether the board should be redrawn. Not drawing to the board increases the number of
        games that can be played in a given time. This is especially useful if you want to train you agent. The
        function is called before the get_move function.

        :return: True if the board should be redrawn, False if the board should not be redrawn.
        """
        return True

    def should_grow_on_food_collision(self):
        """
        This function indicates whether the snake should grow when colliding with a food object. This function is
        called whenever the snake collides with a food block. (False for RL)

        :return: True if the snake should grow, False if the snake should not grow
        """
        return False

    def on_die(self, head_position, board, score, body_parts):
        global start
        global model
        global foodposition
        global wallposition
        global score_internal
        global step
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.

        :param head_position: (x, y) position of the head at the moment of dying.

        :param board: two dimensional array representing the board of the game at the moment of dying. The board
        given does not include information about the snake, only the food position(s) and wall(s) are listed.

        :param score: score at the moment of dying.

        :param body_parts: the array of the locations of the body parts of the snake. The last element of this array
        represents the tail and the first element represents the body part directly following the head of the snake.
        When the snake runs in its own body the following holds: head_position in body_parts.
        """

        print("!!! --- !!! --- SCORE: " + str(score) + " --- !!! --- !!!")

        start = True
        score_internal = score
        model = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        foodposition = [0, 0]
        wallposition = [0, 0]
        step = 0
