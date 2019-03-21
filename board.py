from enum import Enum
from exceptions import *
from trace import *
from printingDisabler import *
import copy

# The specifications tell us that there are 24 cards available to be placed on the board (shared between both players).
NBR_CARDS = 24
# The specifications tell us that there are a maximum of 60 moves, after which the game ends in a draw.
MAX_NBR_MOVES = 60

position_first_tile = None
position_second_tile = None
new_card = None

# lambda expressions shouldn't be assigned to variables in Python, should be translated to a function
# add_tuples = lambda tuple1, tuple2: tuple(x + y for x, y in zip(tuple1, tuple2))

def add_tuples(tuple1, tuple2):
    return tuple(x + y for x, y in zip(tuple1, tuple2))

def get_negative_tuple(tupleVar):
    return tuple(-x for x in tupleVar)

def all_values_positive(col1, row1, col2 = 1, row2 = 1):
    if col1 < 0 or row1 < 0 or col2 < 0 or row2 < 0:
        return False
    if col1 > Board.DIMENSIONS_X_Y[0] - 1 or row1 > Board.DIMENSIONS_X_Y[1] - 1 or col2 > Board.DIMENSIONS_X_Y[0] - 1 or row2 > Board.DIMENSIONS_X_Y[1] - 1:
        return False
    return True

class RecyclingMove:
    def __init__(self, card_to_swap, old_rot_code, new_rot_code,
                 position_card_1st_tile, position_card_2nd_tile, position_first_tile, position_second_tile):
        self.card_to_swap = card_to_swap
        self.old_rot_code = old_rot_code
        self.new_rot_code = new_rot_code
        self.position_card_1st_tile = position_card_1st_tile
        self.position_card_2nd_tile = position_card_2nd_tile
        self.position_first_tile = position_first_tile
        self.position_second_tile = position_second_tile

class RegularMove:
    def __init__(self, new_card, position_first_tile, position_second_tile, rotation_code):
        self.new_card = new_card
        self.position_first_tile = position_first_tile
        self.position_second_tile = position_second_tile
        self.rotation_code = rotation_code

def findMinimax(board, tracing, current_player):
    # Stores all possible level 2 moves after checking the level 3 moves that can result from them
    # and finding the one with the minimal heuristic.
    # The array is made up of tuples (heuristic, corresponding_heuristic)
    # We will iterate through this array until we find the move with the biggest heuristic as our next move.
    level2Array = []
    level3Nodes = 0

    if board.isInRecyclingPhase():
        for recycling_move in board.generate_valid_recycling_moves():
            board.swap_card_direct(recycling_move)
            level2Heuristic = board.heuristic_recycling_moves(recycling_move, current_player)
            """
                for level3_recycling_move in board.generate_valid_recycling_moves():
                    board.swap_card_direct(level3_recycling_move)
                    level3Heuristic = board.heuristic_recycling_moves(recycling_move, current_player)
                    if level3Heuristic < level2Heuristic:
                        level2Heuristic = level3Heuristic
                    board.put_back_card_direct(level3_recycling_move)
                    level3Nodes += 1
            """
            level2Array.append((level2Heuristic, recycling_move))
            # Restore the swapped card
            board.put_back_card_direct(recycling_move)
    else:
        # Generating the next moves we can do from the current state of the board.
        # Temporarily insert cards to it to check the heuristic cost of each move.
        for regular_move in board.generate_valid_regular_moves():
            board.insert_card_direct(regular_move)
            level2Heuristic = board.heuristic_regular_moves(regular_move, current_player)
            """
            # Again, generating next moves, the ones min is to play. Temporarily insert cards to the board.
            # Find the move with the smallest heuristic since min is playing.
            for level3move in board.generate_valid_regular_moves():
                board.insert_card_direct(level3move)
                level3Heuristic = board.heuristic_regular_moves(level3move, current_player)
                if level3Heuristic < level2Heuristic:
                    level2Heuristic = level3Heuristic
                board.remove_card(level3move)
                level3Nodes += 1
            """

            # We found the smallest heuristic cost out of all the level 3 moves.
            # We can append the level 2 move and its smallest resulting heuristic (since min is playing next)
            level2Array.append((level2Heuristic, regular_move))
            board.remove_card(regular_move)

    chosenHeuristic = level2Array[0][0]
    moveChosen = level2Array[0][1]
    for level2 in level2Array:
        if (level2[0] > chosenHeuristic):
            chosenHeuristic = level2[0]
            moveChosen = level2[1]

    if tracing != None:
        tracing.addLevel3(level3Nodes, chosenHeuristic)
        tracing.addLevel2(level2Array)

    return moveChosen


class Tile:
    """ A tile is identified by whether it is red or white and by whether the dot on it is filled or empty.
        Thus, we use the following legend:
        R = Red
        W = White
        F = Filled
        E = Empty
    """
    class Color(Enum):
        red = 'R'
        white = 'W'

    class DotState(Enum):
        filled = 'F'
        empty = 'E'

    def __init__(self, color, dotState, cardOwner):
        self.color = color
        self.dotState = dotState
        self.cardOwner = cardOwner

    def get_item_key(self, type_item):
        if type_item == Tile.Color:
            return self.color
        else:
            return self.dotState

    def __str__(self):
        # Note: We assume there is no more than 99 different ids
        return self.color.value + self.dotState.value + "%-2d" % self.cardOwner.id



class Side:

    def __init__(self, tile1, tile2):
        self.tile1 = tile1
        self.tile2 = tile2

    def __str__(self):
        return '||' + str(self.tile1) + '|' + str(self.tile2) + '||'


class Card:
    class Orientation(Enum):
        right = 1
        down = 2
        left = 3
        up = 4

    NBR_ROTATION_CODES = 8
    # NOTE: The id system is probably not necessary, but it allows us
    # to identify the different cards placed on the board. For debugging purposes it will be quite useful. Also,
    # please do not call self.id_count but Card.id_count instead whenever you want to modify the value of the variable.
    id_count = 0

    def __init__(self, rotation_code=1):
        self.id = Card.id_count
        self.side1 = Side(Tile(Tile.Color.red, Tile.DotState.filled, self),
                          Tile(Tile.Color.white, Tile.DotState.empty, self))
        self.side2 = Side(Tile(Tile.Color.red, Tile.DotState.empty, self),
                          Tile(Tile.Color.white, Tile.DotState.filled, self))
        self.update_rotation_code(rotation_code)

    def update_rotation_code(self, rotation_code):
        self.rotationCode = rotation_code
        if self.rotationCode <= self.NBR_ROTATION_CODES / 2:
            self.activeSide = self.side1
            self.orientation = self.Orientation(self.rotationCode)
        else:
            self.activeSide = self.side2
            self.orientation = self.Orientation(self.rotationCode - self.NBR_ROTATION_CODES / 2)

    def get_tile_positions(self, position):
        if self.orientation == self.Orientation.right:
            return position, add_tuples(position, (1, 0))
        elif self.orientation == self.Orientation.left:
            return add_tuples(position, (1, 0)), position
        elif self.orientation == self.Orientation.up:
            return position, add_tuples(position, (0, 1))
        else:  # if self.orientation == self.Orientation.down:
            return add_tuples(position, (0, 1)), position

    def __str__(self):
        # NOTE: This specific "toString" method should only be used for debug purposes
        # return #"Info on player " + str(self.playerOwner) + "'s card:\n" + \
        return "Side 1: " + str(self.side1) + "\n" + \
               "Side 2: " + str(self.side2) + "\n" + \
               "Rotation Code: " + str(self.rotationCode) + "\n" + \
               "Active Side: " + ("Side 1" if self.activeSide == self.side1 else "Side 2") + "\n" + \
               "Orientation: " + str(self.orientation) + "\n"


class Board:
    DIMENSIONS_X_Y = (8, 12)
    CONVERSION_LETTER_TO_NUMBER = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
                                   'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18,
                                   'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25}

    # Conversion board to be used for the application of the naive heuristic
    # Keys are represented by coordinate pairs.
    # Example: '24' represents coordinate (B,4). '512' represents coordinate (E,12).
    # The associated value is the numeric weight assigned to that coordinate (given by the prof)
    heuristic_board_conversion = dict()
    for i in range(0, DIMENSIONS_X_Y[0]):
        for j in range(0, DIMENSIONS_X_Y[1]):
            heuristic_board_conversion[(i, j)] = (i + 1) + j * 10

    def __init__(self, max_nbr_cards):
        # NOTE: Initially, the board is empty (no cards on it), so no tiles are on it either.
        # We illustrate a location on the board with no tile/card as a string (blank spaces).
        self.board = [[' ' * 4 for x in range(self.DIMENSIONS_X_Y[0])] for y in range(self.DIMENSIONS_X_Y[1])]
        self.nbr_cards = 0
        # There is at most maxNbrCards cards on the board and we have to ensure no one can insert cards (through the
        # methods we provide) when we reach that quota.
        self.max_nbr_cards = max_nbr_cards
        self.recycled_card = 23

    # Looping through the board
    # For all coordinates with a card placed on it, we determine if it's red/white and empty/filled
    # The coordinate is also used to find the positions 'weight' using the dict above
    # Based on the formula, the evaluation function is calculated
    def bad_heuristic_regular_moves_iteration_2(self):
        sum_empty_white = 0
        sum_full_white = 0
        sum_full_red = 0
        sum_empty_red = 0
        for x in range(0, self.DIMENSIONS_X_Y[0]):
            for y in range(0, self.DIMENSIONS_X_Y[1]):
                if isinstance(self.board[y][x],Tile):
                    coord_value = self.heuristic_board_conversion[(x, y)]
                    if self.board[y][x].color == Tile.Color.white and self.board[y][x].dotState == Tile.DotState.empty:
                        # "sum the coordinates of each white empty dot O "
                        sum_empty_white += coord_value
                    elif self.board[y][x].color == Tile.Color.white and self.board[y][x].dotState == Tile.DotState.filled:
                        # "sum the coordinates of each white full dot  • "
                        sum_full_white += coord_value
                    elif self.board[y][x].color == Tile.Color.red and self.board[y][x].dotState == Tile.DotState.filled:
                        # " sum the coordinates of each red full dot • "
                        sum_full_red += coord_value
                    elif self.board[y][x].color == Tile.Color.red and self.board[y][x].dotState == Tile.DotState.empty:
                        # " sum the coordinates of each red empty dot O "
                        sum_empty_red += coord_value
        evaluation_func = sum_empty_white + 3 * sum_full_white - 2 * sum_empty_red - 1.5 * sum_full_red
        return evaluation_func

    def heuristic_regular_moves(self, regular_move, current_player):
        enemy_player_type_item = Tile.DotState if current_player.typeItem == Tile.Color else Tile.Color
        array_colors_tiles = [regular_move.new_card.activeSide.tile1.color, regular_move.new_card.activeSide.tile2.color]
        array_dot_states_tiles = [regular_move.new_card.activeSide.tile1.dotState, regular_move.new_card.activeSide.tile2.dotState]

        return self.calculate_heuristic_inserted_tiles([regular_move.position_first_tile, regular_move.position_second_tile], current_player.typeItem)\
                    - 0.5 * self.calculate_heuristic_inserted_tiles([regular_move.position_first_tile, regular_move.position_second_tile], enemy_player_type_item)\
                    + self.calculate_heuristic_blocking([regular_move.position_first_tile, regular_move.position_second_tile], array_colors_tiles, array_dot_states_tiles, enemy_player_type_item)

    # Since the number of possible moves during the recycling phase and the regular phase are different,
    # the heuristic should be different as well (less costly when in recycling phase)
    def heuristic_recycling_moves(self, recycling_move, current_player):
        # For iteration 2, we use the same naive heuristic for both recyling moves and regular moves.
        return self.heuristic_regular_moves(RegularMove(recycling_move.card_to_swap, recycling_move.position_card_1st_tile,
                                                            recycling_move.position_card_2nd_tile, recycling_move.new_rot_code), current_player)

    class RecyclingMove:
        def __init__(self, card_to_swap, old_rot_code, new_rot_code,
                     position_card_1st_tile, position_card_2nd_tile, position_first_tile, position_second_tile):
            self.card_to_swap = card_to_swap
            self.old_rot_code = old_rot_code
            self.new_rot_code = new_rot_code
            self.position_card_1st_tile = position_card_1st_tile
            self.position_card_2nd_tile = position_card_2nd_tile
            self.position_first_tile = position_first_tile
            self.position_second_tile = position_second_tile

    class RegularMove:
        def __init__(self, new_card, position_first_tile, position_second_tile, rotation_code):
            self.new_card = new_card
            self.position_first_tile = position_first_tile
            self.position_second_tile = position_second_tile
            self.rotation_code = rotation_code

    def ai_move(self, tracing, current_player):
        with TogglePrintingOffGuard():
            aiMove = findMinimax(self, tracing, current_player)
            self.nbr_cards += 1
            Card.id_count += 1
            return self.swap_card_direct(aiMove) if isinstance(aiMove, RecyclingMove) else self.insert_card_direct(aiMove)

    def remove_card(self, regular_move):
        self.board[regular_move.position_first_tile[1]][regular_move.position_first_tile[0]] = ' ' * 4
        self.board[regular_move.position_second_tile[1]][regular_move.position_second_tile[0]] = ' ' * 4

    def convert_coordinate(self, letter_num_coordinate):
        """ Convert a coordinate in the form [A-Z] [0-9] (eg. A 2) (given as a tuple)
            to a coordinate in the current 2-dimensional array
            Note the letter is the column and the number is the row (so coordinate given as (column, row))
        """
        x_coord = self.convert_letter_to_num(letter_num_coordinate[0])
        if x_coord >= self.DIMENSIONS_X_Y[0]:
            raise OutOfBoundsException("ERROR: X coordinate " + str(letter_num_coordinate[0]) + " is out of bounds")
        y_coord = letter_num_coordinate[1] - 1
        if y_coord >= self.DIMENSIONS_X_Y[1] or y_coord < 0:
            raise OutOfBoundsException("ERROR: Y coordinate " + str(letter_num_coordinate[1]) + " is out of bounds")
        return x_coord, y_coord

    def convert_letter_to_num(self, letter):
        return self.CONVERSION_LETTER_TO_NUMBER[letter.upper()]

    def convert_num_to_letter(self, searched_number):
        for letter, number in self.CONVERSION_LETTER_TO_NUMBER.items():
            if number == searched_number:
                return letter

    def get_horizontal_rotation_codes(self):
        # Vertical orientation codes are odd integers
        return (rotationCode for rotationCode in range(1, Card.NBR_ROTATION_CODES + 1) if rotationCode % 2 == 1)

    def get_vertical_rotation_codes(self):
        # Vertical orientation codes are even integers
        return (rotationCode for rotationCode in range(1, Card.NBR_ROTATION_CODES + 1) if rotationCode % 2 == 0)

    def get_rotation_codes(self):
        return (rotationCode for rotationCode in range(1, Card.NBR_ROTATION_CODES + 1))

    def ask_for_input(self, player):
        inserted_tiles_pos = None
        while inserted_tiles_pos is None:
            inserted_tiles_pos = self.read_input(input(player + ", please enter " + ("a recycling move" if self.isInRecyclingPhase() else "a regular move") + ": "))
        return inserted_tiles_pos

    def read_input(self, input_std):
        """ Method used to try the read the input from the user.
            Return true if we were able to successfully and false otherwise.
        """
        args = input_std.split()
        if len(args) == 0:
            print("Enter a move.")
            return None
        if args[0] == "0":
            if len(args) != 4:
                print("Input error: Regular moves should have 4 arguments (not " + str(len(args)) + "):")
                print("0 orientationCode xCoord yCoord")
                print("Example: 0 5 A 2")
                return None
            return self.insert_card(args)
        else:
            if len(args) != 7:
                print("Input error: Swap moves should have 7 arguments (not " + str(len(args)) + "):")
                print("xCoordTile1 yCoordTile1 xCoordTile2 yCoordTile2 newOrientationCode newCoordX newCoordY")
                print("Example: F 2 F 3 3 A 2")
                return None
            return self.swap_card(args)

    def swap_card(self, args):
        # Check if you should recycle on this turn
        if not self.isInRecyclingPhase():
            print("Error: Cannot do a recycling move until " + str(self.max_nbr_cards) + " cards are on the board.\n" \
                                                                                  "Please do a normal move instead.")
            return None

        # Check if the first 4 inputs give you a position
        try:
            position_card_1st_tile = self.convert_coordinate((args[0], int(args[1])))
            card_1st_tile = self.board[position_card_1st_tile[1]][position_card_1st_tile[0]]
        except Exception:
            print(args[2] + " " + args[3] + " does not represent a valid position.")
            return None
        try:
            position_card_2nd_tile = self.convert_coordinate((args[2], int(args[3])))
            card_2nd_tile = self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]]
        except Exception:
            print(args[2] + " " + args[3] + " does not represent a valid position.")
            return None

        # Check if the position are tiles with cards on them
        if isinstance(card_1st_tile, str) or isinstance(card_2nd_tile, str):
            print("1 or both tile do not have a card on them.")
            return None

        # Checks if the tiles come from the same card
        if card_1st_tile.cardOwner != card_2nd_tile.cardOwner:
            print("The 2 tiles selected do not come from the same card. Choose 2 tiles from the same card.")
            return None
        # Otherwise, we ensured the identity of the card needing to be swapped
        card_to_swap = card_1st_tile.cardOwner

        # Checks to see if there is a tile used over the chosen card, so that the board won't become illegal
        if position_card_2nd_tile[0] == position_card_1st_tile[0]:
            if isinstance(self.board[max(position_card_1st_tile[1], position_card_2nd_tile[1]) + 1][position_card_1st_tile[0]],
                          Tile):
                print(
                    "You cannot move this card, it would leave the board in an illegal state. Please choose another card.")
                return None
        elif isinstance(self.board[position_card_1st_tile[1] + 1][position_card_1st_tile[0]], Tile) or isinstance(
                self.board[position_card_2nd_tile[1] + 1][position_card_2nd_tile[0]], Tile):
            print("You cannot move this card, it would leave the board in an illegal state. Please choose another card.")
            return None

        # Checks that the 5th argument is a rotation code
        try:
            input_rot_code = int(args[4])
        except ValueError:
            print("The 5th argument should be an integer and " + args[5] + " is not.")
            return None
        if input_rot_code <= 0 or input_rot_code > Card.NBR_ROTATION_CODES:
            print("Valid rotation codes range from 1 to " + str(Card.NBR_ROTATION_CODES) + ", " + "thus " +
                  str(input_rot_code) + " is out of range.")
            return None

        # Gets the new position of the card
        try:
            position_new_card = self.convert_coordinate((args[5], int(args[6])))
        except ValueError:
            print(args[5] + " " + args[6] + " does not represent a valid position.")
            return None


        recyclingMove = self.get_valid_recycling_move(card_to_swap, card_1st_tile, card_2nd_tile, input_rot_code, position_new_card,
                                                      position_card_1st_tile, position_card_2nd_tile)
        if recyclingMove is None:
            print ("This is not a valid recycling move")
            return None

        self.swap_card_direct(recyclingMove)

        # Make sure the same card can't be recycled twice
        self.recycled_card = card_to_swap

        return [recyclingMove.position_first_tile, recyclingMove.position_second_tile]

    def swap_card_direct(self, recyclingMove):
        recyclingMove.card_to_swap.update_rotation_code(recyclingMove.new_rot_code)
        self.board[recyclingMove.position_card_1st_tile[1]][recyclingMove.position_card_1st_tile[0]] = ' ' * 4
        self.board[recyclingMove.position_card_2nd_tile[1]][recyclingMove.position_card_2nd_tile[0]] = ' ' * 4
        self.board[recyclingMove.position_first_tile[1]][recyclingMove.position_first_tile[0]] = recyclingMove.card_to_swap.activeSide.tile1
        self.board[recyclingMove.position_second_tile[1]][recyclingMove.position_second_tile[0]] = recyclingMove.card_to_swap.activeSide.tile2
        return [recyclingMove.position_first_tile, recyclingMove.position_second_tile]

    # Method used to "cancel" a recycling move
    def put_back_card_direct(self, recyclingMove):
        recyclingMove.card_to_swap.update_rotation_code(recyclingMove.old_rot_code)
        self.board[recyclingMove.position_card_1st_tile[1]][recyclingMove.position_card_1st_tile[0]] = recyclingMove.card_to_swap.activeSide.tile1
        self.board[recyclingMove.position_card_2nd_tile[1]][recyclingMove.position_card_2nd_tile[0]] = recyclingMove.card_to_swap.activeSide.tile2
        self.board[recyclingMove.position_first_tile[1]][recyclingMove.position_first_tile[0]] = ' ' * 4
        self.board[recyclingMove.position_second_tile[1]][recyclingMove.position_second_tile[0]] = ' ' * 4

    def get_valid_recycling_move(self, card_to_swap, card_1st_tile, card_2nd_tile, input_rot_code, position_new_card,
                                 position_card_1st_tile, position_card_2nd_tile):
        # Makes sure the last card used isn't the one being played/swapped now
        if card_to_swap == self.recycled_card:
            print("You cannot move the card that was moved/played last turn. Please choose another card.")
            return None

        # Check if the card has the same rotation code and a different location, to be a legal recycle move
        if not(card_1st_tile.cardOwner.rotationCode == input_rot_code and position_new_card[0] == min(position_card_1st_tile[0], position_card_2nd_tile[0])
               and position_new_card[1] == min(position_card_1st_tile[1], position_card_2nd_tile[1])):
            self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = ' ' * 4
            self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = ' ' * 4
            old_rot_code_cache = card_to_swap.rotationCode
            card_to_swap.update_rotation_code(input_rot_code)
            position_first_tile, position_second_tile = card_to_swap.get_tile_positions(position_new_card)

            # The new position is tested for legality. Place the card back before returning,
            # whether it is an illegal move or not.
            if not self.card_location_is_valid_spot(position_first_tile, position_second_tile, card_to_swap):
                print("The location where you want to place your recycled card is not valid.")
                self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = card_1st_tile
                self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = card_2nd_tile
                card_to_swap.update_rotation_code(old_rot_code_cache)
                return None
            self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = card_1st_tile
            self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = card_2nd_tile
            card_to_swap.update_rotation_code(old_rot_code_cache)
            return RecyclingMove(card_to_swap, old_rot_code_cache, input_rot_code,
                                 position_card_1st_tile, position_card_2nd_tile,
                                 position_first_tile, position_second_tile)

        print("You cannot keep the same rotation and position.")
        return None

    def insert_card(self, input_args):
        """ Tries to insert card into the board from the inputArgs given by player.
            If it was successful in inserting it, it increments self.nbrCards by 1 and returns the new_card.
            Otherwise, it returns None.
        """
        # Ensure that an exception is thrown when we try to exceed the max number of cards to indicate failure
        if self.nbr_cards >= self.max_nbr_cards:
            print("Error: Cannot insert more than " + str(self.max_nbr_cards) + " cards on the board.\nPlease do a recycling "
                                                                         "move instead.")
            return None
        try:
            input_rot_code = int(input_args[1])
        except ValueError:
            print("The 2nd argument should be an integer and " + input_args[1] + " is not.")
            return None
        if input_rot_code <= 0 or input_rot_code > Card.NBR_ROTATION_CODES:
            print("Valid rotation codes range from 1 to " + str(Card.NBR_ROTATION_CODES) + ", " + "thus " +
                  str(input_rot_code) + " is out of range.")
            return None

        new_card = Card(input_rot_code)
        try:
            position_new_card = self.convert_coordinate((input_args[2], int(input_args[3])))
        except OutOfBoundsException as e:
            print(e.message)
            print(input_args[2] + " " + input_args[3] + " does not represent a valid position.")
            return None
        position_first_tile, position_second_tile = new_card.get_tile_positions(position_new_card)
        if not self.card_location_is_valid_spot(position_first_tile, position_second_tile, new_card):
            print("The location where you want to place your card is not valid.")
            return None

        self.board[position_first_tile[1]][position_first_tile[0]] = new_card.activeSide.tile1
        self.board[position_second_tile[1]][position_second_tile[0]] = new_card.activeSide.tile2

        self.nbr_cards += 1
        Card.id_count += 1

        return [position_new_card, position_second_tile]

    def insert_card_direct(self, regular_move):
        regular_move.new_card.update_rotation_code(regular_move.rotation_code)
        self.board[regular_move.position_first_tile[1]][regular_move.position_first_tile[0]] = regular_move.new_card.activeSide.tile1
        self.board[regular_move.position_second_tile[1]][regular_move.position_second_tile[0]] = regular_move.new_card.activeSide.tile2
        return (regular_move.position_first_tile, regular_move.position_second_tile)

    def card_location_is_valid_spot(self, tile_1_location, tile_2_location, new_card):
        """ Return whether or not the given location in the 2d-dimensional array is valid.
            To be valid, it has to:
            - 1- Be empty (no tiles already on it)
            - 2- Not be out of bounds (x and y not < 0, x < dimensions.x, y < dimensions.y)
            - 3- a: Be placed on row 1 (tile1location.y = 0) or
                 b: On top of cards that were already placed
            Used to check if we can put a new tile on that location or if it is illegal.
        """
        # This variable is used for condition 1:
        # Check whether both board locations are empty (no tile on neither of them)
        empty_locations = False
        try:
            empty_locations = not isinstance(self.board[tile_1_location[1]][tile_1_location[0]], Tile) and \
                             not isinstance(self.board[tile_2_location[1]][tile_2_location[0]], Tile)
        # Condition 2: Exception raised when at least one of the locations of the card is out of bounds
        except ValueError:
            print("Error: Both squares (tiles) that are part of the card being placed must not have empty tiles at the "
                  "bottom.")
            return False
        except IndexError:
            print("Error: One square is not on a board tile.")
            return False

        if not empty_locations:
            print("Error: The card would be placed on top of another card's segment(s).")
            return False

        # Condition 3a: Check whether the card is placed on row 1
        if tile_1_location[1] == 0 or tile_2_location[1] == 0:
            # Since we checked conditions 1, 2 and 3a, the card location is valid.
            return True
        # Condition 3b: Card has to be placed on top of other cards
        if new_card.orientation == Card.Orientation.right or new_card.orientation == Card.Orientation.left:
            tile1_location_y_under = tile_1_location[1] - 1
            tile2_location_y_under = tile_2_location[1] - 1

            occupied_locations = (isinstance(self.board[tile1_location_y_under][tile_1_location[0]], Tile) and
                                  isinstance(self.board[tile2_location_y_under][tile_2_location[0]], Tile))
            if not occupied_locations:
                print("Error: The card would hang over one or 2 empty cells, which is not allowed.")
                return False
            # Since we checked conditions 1, 2 and 3b, the card location is valid.
            return True
        else:  # if new_card.orientation == Card.Orientation.up or new_card.orientation == Card.Orientation.down:
            tile_location_under_y = min(tile_1_location[1], tile_2_location[1]) - 1
            if not isinstance(self.board[tile_location_under_y][tile_1_location[0]], Tile):
                print("Error: The card would hang over an empty cell, which is not allowed.")
                return False
            # Since we checked conditions 1, 2 and 3b, the card location is valid.
            return True

    def check_win_conditions(self, inserted_tiles_pos, type_item):
        if type_item == Tile.Color:
            types = (Tile.Color.white, Tile.Color.red)
        else:
            types = (Tile.DotState.empty, Tile.DotState.filled)
        offsets = [(0, -1), (1, 0), (1, 1), (1, -1)]
        for tile_pos in inserted_tiles_pos:
            for offset in offsets:
                for i in range(4):
                    start_pos = (tile_pos[0] - i * offset[0], tile_pos[1] - i * offset[1])
                    end_pos = (start_pos[0] + 3 * offset[0], start_pos[1] + 3 * offset[1])
                    if all_values_positive(start_pos[0], start_pos[1], end_pos[0], end_pos[1]):
                        for type in types:
                            if not isinstance(self.board[start_pos[1]][start_pos[0]], Tile):
                                continue
                            if self.board[start_pos[1]][start_pos[0]].get_item_key(type_item) != type:
                                    continue
                            if self.get_nbr_matching_tiles_in_offset_direction(start_pos, offset, type, type_item) >= 3:
                                return True
        return False

    def calculate_heuristic_inserted_tiles(self, inserted_tiles_pos, type_item):
        if type_item == Tile.Color:
            types = (Tile.Color.white, Tile.Color.red)
        else:
            types = (Tile.DotState.empty, Tile.DotState.filled)
        offsets = [(0, 1), (1, 0), (1, 1), (1, -1)]
        nbr_2_matching = 0
        nbr_3_matching = 0
        nbr_4_matching = 0
        for tile_pos in inserted_tiles_pos:
            for offset in offsets:
                for i in range(4):
                    start_pos = (tile_pos[0] - i * offset[0], tile_pos[1] - i * offset[1])
                    end_pos = (start_pos[0] + 3 * offset[0], start_pos[1] + 3 * offset[1])
                    if all_values_positive(start_pos[0], start_pos[1], end_pos[0], end_pos[1]):
                        for type in types:
                            nbr_matching_tiles = 0
                            if isinstance(self.board[start_pos[1]][start_pos[0]], Tile):
                                if self.board[start_pos[1]][start_pos[0]].get_item_key(type_item) != type:
                                    continue
                                else:
                                    nbr_matching_tiles += 1
                            nbr_matching_tiles += self.get_nbr_matching_tiles_in_offset_direction(start_pos, offset, type, type_item)
                            if nbr_matching_tiles == 1:
                                pass
                            elif nbr_matching_tiles == 2:
                                nbr_2_matching += 1
                            elif nbr_matching_tiles == 3:
                                nbr_3_matching += 1
                            elif nbr_matching_tiles == 4:
                                nbr_4_matching += 1
        return nbr_2_matching + 10 * nbr_3_matching + 1000 * nbr_4_matching

    def calculate_heuristic_blocking(self, inserted_tiles_pos, array_colors_tiles, array_dot_states_tiles, blocking_type_item):
        offsets = [(0, 1), (1, 0), (1, 1), (1, -1)]
        nbr_2_blocking = 0
        nbr_3_blocking = 0
        nbr_4_blocking = 0
        for i in range(0, len(inserted_tiles_pos)):
            for offset in offsets:
                if blocking_type_item == Tile.Color:
                    blocking_type = array_colors_tiles[i]
                else:
                    blocking_type = array_dot_states_tiles[i]
                nbr_blocked_tiles = self.get_nbr_blocking_tiles_in_offset_direction(inserted_tiles_pos[i], offset, blocking_type, blocking_type_item)
                if nbr_blocked_tiles <= 1:
                    pass
                elif nbr_blocked_tiles == 2:
                    nbr_2_blocking += 1
                elif nbr_blocked_tiles == 3:
                    nbr_3_blocking += 1
                elif nbr_blocked_tiles == 4:
                    nbr_4_blocking += 1
        return nbr_2_blocking + 10 * nbr_3_blocking + 1000 * nbr_4_blocking

    def get_nbr_blocking_tiles_in_offset_direction(self, tile_pos, offset, blocking_type, type_item):
        current_pos = tile_pos
        checked_tiles = 0
        while checked_tiles < 3:
            current_pos = add_tuples(current_pos, offset)
            if all_values_positive(current_pos[0], current_pos[1]) \
                and isinstance(self.board[current_pos[1]][current_pos[0]], Tile)\
                and self.board[current_pos[1]][current_pos[0]].get_item_key(type_item) != blocking_type:
                    checked_tiles += 1
            else:
                break

        return checked_tiles

    def get_nbr_matching_tiles_in_offset_direction(self, tile_pos, offset, type, type_item):
        nbr_consecutives = 0
        current_pos = tile_pos
        checked_tiles = 0
        while checked_tiles < 3:
            current_pos = add_tuples(current_pos, offset)
            if all_values_positive(current_pos[0], current_pos[1]) \
                and isinstance(self.board[current_pos[1]][current_pos[0]], Tile):
                # Check whether this tile is a blocking one or not
                if self.board[current_pos[1]][current_pos[0]].get_item_key(type_item) == type:
                    nbr_consecutives += 1
                # If it is a blocking tile, stop checking in the offset direction.
                else:
                    return 0
            checked_tiles += 1
        return nbr_consecutives

    def generate_valid_recycling_moves(self):
        cardOwnerPreviousTile = None
        cards_recycled_and_locations = dict()
        valid_tile_locations = list()
        # For all rows on the board, search upwards through the corresponding column
        # in order to find the highest nonempty tile of each column. This is because we can only recycle cards
        # that do not have anything on top of them.
        for i in range(0, self.DIMENSIONS_X_Y[0]):
            for j in range(0, self.DIMENSIONS_X_Y[1]):
                # If we found the highest tile on that column (i.e. the next highest tile is either an empty tile
                # or the very top of the board), then generate valid recycling moves that involve swapping it out.
                if isinstance(self.board[j][i], Tile) and \
                        (((j+1) == self.DIMENSIONS_X_Y[1]) or not isinstance(self.board[j + 1][i], Tile)):
                    card_to_recycle = self.board[j][i].cardOwner
                    # If we already checked the valid moves of that card, we can ignore it.
                    if card_to_recycle != cardOwnerPreviousTile:
                        cards_recycled_and_locations[card_to_recycle] = ((i, j), self.find_location_other_tile_of_card(card_to_recycle, (i, j)))
                    cardOwnerPreviousTile = card_to_recycle
                    # If the tile above the current one is not out of bounds, then
                    # we assume that it is a valid tile location, since it is, by definition, the
                    # first empty tile we encounter going upwards.
                    if j + 1 < self.DIMENSIONS_X_Y[1]:
                        valid_tile_locations.append((i, j+1))
                    # We should NOT search the tiles upwards from there.
                    break
                # If the column contains no tile, then the bottom position of the column
                # needs to be added as a valid tile location for the recycling move.
                if j == 0 and not isinstance(self.board[j][i], Tile):
                    valid_tile_locations.append((i, j))

        valid_recycling_moves = list()
        # Then, for each card that can be recycled, generate its valid next moves
        for card, locations in cards_recycled_and_locations.items():
            potential_valid_recycling_moves = self.generate_valid_recycling_moves_for_card(card, locations, valid_tile_locations)
            if potential_valid_recycling_moves != None:
                valid_recycling_moves.extend(potential_valid_recycling_moves)
        return valid_recycling_moves

    def find_location_other_tile_of_card(self, card, first_tile_position):
        if (first_tile_position[0] + 1) < self.DIMENSIONS_X_Y[0] \
                and isinstance(self.board[first_tile_position[1]][first_tile_position[0] + 1], Tile)\
                and self.board[first_tile_position[1]][first_tile_position[0] + 1].cardOwner == card:
            return (first_tile_position[0]+1, first_tile_position[1])
        if (first_tile_position[0] - 1) >= 0 \
                and isinstance(self.board[first_tile_position[1]][first_tile_position[0] - 1], Tile)\
                and self.board[first_tile_position[1]][first_tile_position[0] - 1].cardOwner == card:
            return (first_tile_position[0] - 1, first_tile_position[1])
        if (first_tile_position[1] + 1) < self.DIMENSIONS_X_Y[1] \
                and isinstance(self.board[first_tile_position[1] + 1][first_tile_position[0]], Tile) \
                and self.board[first_tile_position[1] + 1][first_tile_position[0]].cardOwner == card:
            return (first_tile_position[0], first_tile_position[1]+1)
        if (first_tile_position[1] - 1) >= 0 \
                and isinstance(self.board[first_tile_position[1] - 1][first_tile_position[0]], Tile)\
                and self.board[first_tile_position[1] - 1][first_tile_position[0]].cardOwner == card:
            return (first_tile_position[0], first_tile_position[1]-1)

    def generate_valid_recycling_moves_for_card(self, card, cardLocations, valid_tile_locations):
        recycling_moves = list()
        for new_card_location in valid_tile_locations:
            for rotation_code in self.get_rotation_codes():
                potential_valid_recycling_move = \
                    self.get_valid_recycling_move(card, card.activeSide.tile1, card.activeSide.tile2, rotation_code,
                                                  new_card_location, cardLocations[0], cardLocations[1])
                if potential_valid_recycling_move is not None:
                    recycling_moves.append(potential_valid_recycling_move)
        return recycling_moves

    def generate_valid_regular_moves(self):
        valid_regular_moves = list()
        new_card = Card(1) # We pass rotation_code but we are supposed to update the rotationCode later
        # For all rows on the board, search upwards through the corresponding column
        # in order to find the first empty tile.
        for i in range(0, self.DIMENSIONS_X_Y[0]):
            for j in range(0, self.DIMENSIONS_X_Y[1]):
                # If we found the first empty tile, try to insert a card from this position.
                if not isinstance(self.board[j][i], Tile):
                    potential_valid_moves = None
                    # If we are checking the very last column, then there is no need to check the "horizontal" moves
                    #  => they are invalid for sure.
                    if i == self.DIMENSIONS_X_Y[0] - 1:
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes(
                                                                        new_card,
                                                                        (i, j),
                                                                        self.get_vertical_rotation_codes())
                    # Similar logic applies to the very top row, the "vertical" moves
                    # are guaranteed to be invalid.
                    elif j == self.DIMENSIONS_X_Y[1] - 1:
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes(
                                                                        new_card,
                                                                        (i, j),
                                                                        self.get_horizontal_rotation_codes())
                    else:
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes(
                                                                        new_card,
                                                                        (i, j),
                                                                        self.get_rotation_codes())
                    if potential_valid_moves is not None:
                        valid_regular_moves.extend(potential_valid_moves)
                    # We should NOT search the tiles upwards from the first empty tile, since they are guaranteed to be invalid.
                    break
        return valid_regular_moves

    def generate_valid_regular_moves_from_pos_and_rot_codes(self, new_card, position, rotation_codes):
        regular_moves = []
        for rotation_code in rotation_codes:
            potential_regular_move = self.try_insert_card_in_new_board_AI(new_card, position, rotation_code)
            if potential_regular_move is not None:
                regular_moves.append(potential_regular_move)
        return regular_moves

    def try_insert_card_in_new_board_AI(self, new_card, position, rotation_code):
        new_card.update_rotation_code(rotation_code)
        position_first_tile, position_second_tile = new_card.get_tile_positions(position)
        if self.card_location_is_valid_spot(position_first_tile, position_second_tile, new_card):
            return RegularMove(new_card, position_first_tile, position_second_tile, rotation_code)
        else:
            return None

    def isInRecyclingPhase(self):
        # Returns whether or not the players have entered the recycling phase, meaning that only recycling moves
        # will be allowed from now on. This happens when all cards are placed on the board.
        return self.nbr_cards >= self.max_nbr_cards

    def __str__(self):
        output_str = '\n'
        row_index = 0
        for row in self.board:
            current_row_str = "%2d" % (row_index + 1) + ' '
            for colVal in row:
                current_row_str += '|' + str(colVal)
            current_row_str += '|\n'
            output_str = current_row_str + output_str
            row_index += 1

        output_str += ' ' * 5
        for row in range(self.DIMENSIONS_X_Y[0]):
            output_str += self.convert_num_to_letter(row) + ' ' * 4
        output_str += '\n\n'
        return output_str


class DotPlayer:
    def __init__(self):
        self.name = "player1 - dots"
        self.typeItem = Tile.DotState


class ColorPlayer:
    def __init__(self):
        self.name = "player2 - color"
        self.typeItem = Tile.Color

class GameInfo:
    def __init__(self, b, ai_player, current_player, other_player, p1, p2, tracing):
        self.board = b
        self.ai_player = ai_player
        self.current_player = current_player
        self.other_player = other_player
        self.p1 = p1
        self.p2 = p2
        self.tracing = tracing
        self.nbr_moves = 0

game_info = None

def set_up_game():
    b = Board(NBR_CARDS)

    p1 = DotPlayer()
    p2 = ColorPlayer()

    current_player = None
    other_player = None
    ai_player = None

    ai_input = input("Would you like to play against the AI? Enter Y for yes or N for no \n")
    while True:
        if len(ai_input) == 0:
            ai_input = input("Please enter Y or N \n")
        elif ai_input == 'Y' or ai_input == 'y':
            ai_mode = True
            break
        elif ai_input == 'N' or ai_input == 'n':
            ai_mode = False
            break
        else:
            ai_input = input("Invalid entry. Please try again \n")

    if ai_mode:
        tracing = None
        trace_input = input("Would you like to produce a trace of the minimax? Enter Y for yes or N for no \n" )
        while True:
            if len(trace_input) == 0:
                trace_input = input("Please enter Y or N \n")
            elif trace_input == 'Y' or trace_input == 'y':
                tracing = TraceFile()
                break
            elif trace_input == 'N' or trace_input == 'n':
                break
            else:
                trace_input = input("Invalid entry. Please try again \n")

        ai_first = None
        player_input = input("Would you like the AI to play first? Enter Y for yes or N for no \n")
        while True:
            if len(player_input) == 0:
                player_input = input("Please enter Y or N \n")
            elif player_input == 'Y' or player_input == 'y':
                ai_first = True
                break
            elif player_input == 'N' or player_input == 'n':
                ai_first = False
                break
            else:
                player_input = input("Invalid entry. Please try again \n")

        # Users decide which player they'd like to be
        user_input = input("Enter C if you'd like to play color, or D if you'd like to play dots \n")
        while True:
            if len(user_input) == 0:
                user_input = input("Please enter C or D \n")
            elif user_input == 'C' or user_input == 'c':
                current_player = p2
                other_player = p1
                if ai_first:
                    ai_player = p2
                else:
                    ai_player = p1
                break
            elif user_input == 'D' or user_input == 'd':
                current_player = p1
                other_player = p2
                if ai_first:
                    ai_player = p1
                else:
                    ai_player = p2
                break
            else:
                user_input = input("Invalid entry. Please try again \n")

    else:
        # Users decide which player they'd like to be
        user_input = input("Enter C if you'd like to play color, or D if you'd like to play dots \n")
        while True:
            if len(user_input) == 0:
                    user_input = input("Please enter C or D \n")
            elif user_input == 'C' or user_input == 'c':
                    current_player = p2
                    other_player = p1
                    break
            elif user_input == 'D' or user_input == 'd':
                    current_player = p1
                    other_player = p2
                    break
            else:
                user_input = input("Invalid entry. Please try again \n")
    global game_info
    game_info = GameInfo(b, ai_player, current_player, other_player, p1, p2, tracing)

def game_loop():
    global game_info

    nbr_moves = 0
    while nbr_moves < MAX_NBR_MOVES:
        if game_info.ai_player != None and game_info.current_player == game_info.ai_player:
            inserted_tiles_pos = game_info.board.ai_move(game_info.tracing, game_info.current_player)
        else:
            inserted_tiles_pos = game_info.board.ask_for_input(game_info.current_player.name)
        print(game_info.board)
        if game_info.board.nbr_cards >= 4:
            # Even if the other player wins at the same time as the current player, the current player has
            # the priority.
            # (i.e. The current players wins even if both players won simultaneously,
            # because the current player was the one to play the winning move)
            if game_info.board.check_win_conditions(inserted_tiles_pos, game_info.current_player.typeItem):
                print(game_info.current_player.name + " wins the game!!!")
                return
            if game_info.board.check_win_conditions(inserted_tiles_pos, game_info.other_player.typeItem):
                print(game_info.other_player.name + " wins the game!!!")
                return
        # We switch to the other player
        game_info.other_player = game_info.current_player
        game_info.current_player = game_info.p1 if game_info.current_player == game_info.p2 else game_info.p2
        nbr_moves += 1
    print (str(MAX_NBR_MOVES) + " moves have been played. Thus, the game ends in a DRAW!! Congratulations to both players!")


# main
#set_up_game()
#game_loop()



