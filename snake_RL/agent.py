from gameobjects import GameObject
from move import Move, Direction
import numpy
# Internal reward model, initialise to 0 for all 25 spaces.
model = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
# Discount
gamma = 1
# Learning rate
alpha = -0.04

# for initialising
start = True
score_internal = 0


class Agent:

    def __init__(self):
        """" Constructor of the Agent, can be used to set up variables """

    def find_game_elements(self, board):
        for x in range(0, 5):
            for y in range(0, 5):
                if board[x][y] == GameObject.FOOD:
                    model[x][y] = 1
                    print("[AGENT]: found FOOD at  x:" + str(x) + " y:" + str(y))
                elif board[x][y] == GameObject.WALL:
                    model[x][y] = -1
                    print("[AGENT]: found WALL at  x:" + str(x) + " y:" + str(y))
                else:
                    print("[AGENT]: found nothing at  x:" + str(x) + " y:" + str(y))

    def get_reward(self, state, coordinates):
        if state == GameObject.FOOD:
            # Food has a reward of 1
            return 1
        elif state == GameObject.WALL:
            # Walls have a reward of -1
            return -1
        else:
            # Empty space, return reward from model
            return self.model[coordinates[0]][coordinates[1]]

    def update_rewards(self):
        global model
        for x in range(0, 5):
            for y in range(0, 5):
                # food and walls don't get updates.
                if not model[x][y] == 1 and not model[x][y] == -1:
                    # punishment for not being a final state
                    model[x][y] = model[x][y] + alpha
                    # bonus for being close to a nice neighbour
                    neighbour_rewards = self.get_neighbour_rewards([x, y])
                    model[x][y] = model[x][y] + gamma * max(neighbour_rewards[0], neighbour_rewards[1],
                                                            neighbour_rewards[2], neighbour_rewards[3])

    def get_neighbour_rewards(self, pos):
        if 0 < pos[0] < 4:
            if 0 < pos[1] < 4:
                # not at an edge or corner
                return [model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] - 1],
                        model[pos[0]][pos[1] + 1]]
            elif pos[1] == 0:
                # bottom edge
                return [model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        -1,
                        model[pos[0]][pos[1] + 1]]
            else:
                # top edge
                return [model[pos[0] - 1][pos[1]],
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] - 1],
                        -1]
        elif pos[0] == 0:
            # left edge
            if pos[1] == 0:
                # bottomleft corner
                return [-1,
                        model[pos[0] + 1][pos[1]],
                        -1,
                        model[pos[0]][pos[1] + 1]]
            elif pos[1] == 4:
                # topleft corner
                return [-1,
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] - 1],
                        -1]
            else:
                # just the left edge here
                return [-1,
                        model[pos[0] + 1][pos[1]],
                        model[pos[0]][pos[1] - 1],
                        model[pos[0]][pos[1] + 1]]
        else:
            # right edge
            if pos[1] == 0:
                # bottomright corner
                return [model[pos[0] - 1][pos[1]],
                        -1,
                        -1,
                        model[pos[0]][pos[1] + 1]]
            elif pos[1] == 4:
                # topright corner
                return [model[pos[0] - 1][pos[1]],
                        -1,
                        model[pos[0]][pos[1] - 1],
                        -1]
            else:
                # just the right edge here
                return [model[pos[0] - 1][pos[1]],
                        -1,
                        model[pos[0]][pos[1] - 1],
                        model[pos[0]][pos[1] + 1]]

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        # model initialisation
        global start
        global score_internal
        if start:
            self.find_game_elements(board)
            print("[AGENT]: Model - " + str(model))
            start = False
        self.update_rewards()
        possible_moves = self.get_neighbour_rewards(head_position)
        """ get_neighbour_rewards returns possible moves as follows:
            possible_moves[0] : WEST direction
            possible_moves[1] : EAST direction
            possible_moves[2] : SOUTH direction
            possible_moves[3] : NORTH direction"""
        while True:
            if max(possible_moves) == possible_moves[0]:
                # GO WEST
                if direction == Direction.NORTH:
                    return Move.LEFT
                elif direction == Direction.EAST:
                    #to avoid loops, pop west from possible_moves
                    possible_moves.remove(possible_moves[0])
                    continue
                elif direction == Direction.SOUTH:
                    return Move.RIGHT
                else:
                    return Move.STRAIGHT
            elif max(possible_moves) == possible_moves[1]:
                # GO EAST
                if direction == Direction.NORTH:
                    return Move.RIGHT
                elif direction == Direction.EAST:
                    return Move.STRAIGHT
                elif direction == Direction.SOUTH:
                    return Move.LEFT
                else:
                    possible_moves.remove(possible_moves[1])
                    continue
            elif max(possible_moves) == possible_moves[2]:
                #GO SOUTH
                if direction == Direction.NORTH:
                    possible_moves.remove(possible_moves[2])
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
                    possible_moves.remove(possible_moves[3])
                    continue
                else:
                    return Move.RIGHT
        return Move.STRAIGHT
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
        When the snake tragically dies (i.e. by running its head into a wall) the score will be reset. In ohter
        words, the score describes the score of the current (alive) worm.

        :param turns_alive: The number of turns (as integer) the current snake is alive.

        :param turns_to_starve: The number of turns left alive (as integer) if the snake does not eat. If this number
        reaches 1 and there is not eaten the next turn, the snake dies. If the value is equal to -1, then the option
        is not enabled and the snake can not starve.

        :param direction: The direction the snake is currently facing. This can be either Direction.NORTH,
        Direction.SOUTH, Direction.WEST, Direction.EAST. For instance, when the snake is facing east and a move
        straight is returned, the snake wil move one cell to the right.

        :param head_position: (x,y) of the head of the snake. The following should always hold: board[head_position[
        0]][head_position[1]] == GameObject.SNAKE_HEAD.

        :param body_parts: the array of the locations of the body parts of the snake. The last element of this array
        represents the tail and the first element represents the body part directly following the head of the snake.

        :return: The move of the snake. This can be either Move.LEFT (meaning going left), Move.STRAIGHT (meaning
        going straight ahead) and Move.RIGHT (meaning going right). The moves are made from the viewpoint of the
        snake. This means the snake keeps track of the direction it is facing (North, South, West and East).
        Move.LEFT and Move.RIGHT changes the direction of the snake. In example, if the snake is facing north and the
        move left is made, the snake will go one block to the left and change its direction to west.
        """

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
