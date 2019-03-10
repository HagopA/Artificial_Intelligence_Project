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

def all_values_positive(col1, row1, col2, row2):
    if col1 < 0 or row1 < 0 or col2 < 0 or row2 < 0:
        return False
    if col1 > Board.DIMENSIONS_X_Y[0] - 1 or row1 > Board.DIMENSIONS_X_Y[1] - 1 or col2 > Board.DIMENSIONS_X_Y[0] - 1 or row2 > Board.DIMENSIONS_X_Y[1] - 1:
        return False
    return True


def findMinimax(board, tracing):
    level2Array = []
    level3Nodes = 0
    for move in board.generate_valid_next_moves():
        board.insert_card_direct(move[0], move[1])
        level2Heuristic = 1000000
        for level3move in board.generate_valid_next_moves():
            board.insert_card_direct(level3move[0], level3move[1])
            level3Heuristic = board.heuristic()
            if level3Heuristic < level2Heuristic:
                level2Heuristic = level3Heuristic
            board.removeCard(level3move[0], level3move[1])
            level3Nodes += 1
        if level2Heuristic == 1000000:
            level2Heuristic = board.heuristic()
        level2Array.append([level2Heuristic, move])
        board.removeCard(move[0], move[1])

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

    def __init__(self, color, dotState, cardOwner, rotationCode):
        self.color = color
        self.dotState = dotState
        self.cardOwner = cardOwner
        self.rotationCode = rotationCode

    def get_item_key(self, type_item):
        if type_item == Tile.Color:
            return self.color
        else:
            return self.dotState

    def __str__(self):
        # Note: We assume there is no more than 99 different ids
        return self.color.value + self.dotState.value + "%-2d" % self.cardOwner



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

    def __init__(self, rotation_code=1, id=-1):
        if id == -1:
            self.id = Card.id_count
        else:
            self.id = id
        self.side1 = Side(Tile(Tile.Color.red, Tile.DotState.filled, self.id, rotation_code),
                          Tile(Tile.Color.white, Tile.DotState.empty, self.id, rotation_code))
        self.side2 = Side(Tile(Tile.Color.red, Tile.DotState.empty, self.id, rotation_code),
                          Tile(Tile.Color.white, Tile.DotState.filled, self.id, rotation_code))
        self.rotationCode = rotation_code
        if self.rotationCode <= self.NBR_ROTATION_CODES / 2:
            self.activeSide = self.side1
            self.orientation = self.Orientation(self.rotationCode)
        else:
            self.activeSide = self.side2
            self.orientation = self.Orientation(self.rotationCode - self.NBR_ROTATION_CODES / 2)
        if id == -1:
            self.id = Card.id_count
        else:
            self.id = id

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
        self.nbrCards = 0
        # There is at most maxNbrCards cards on the board and we have to ensure no one can insert cards (through the
        # methods we provide) when we reach that quota.
        self.maxNbrCards = max_nbr_cards
        self.recycled_card = 23

    # Looping through the board
    # For all coordinates with a card placed on it, we determine if it's red/white and empty/filled
    # The coordinate is also used to find the positions 'weight' using the dict above
    # Based on the formula, the evaluation function is calculated
    def heuristic(self):
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

    def ai_move(self, tracing):
        aiMove = findMinimax(self, tracing)
        self.nbrCards += 1
        Card.id_count += 1
        return self.insert_card_direct(aiMove[0], aiMove[1])

    def removeCard(self, new_card, position):

        position_first_tile, position_second_tile = new_card.get_tile_positions(position)
        self.board[position_first_tile[1]][position_first_tile[0]] = ' ' * 4
        self.board[position_second_tile[1]][position_second_tile[0]] = ' ' * 4

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
            inserted_tiles_pos = self.read_input(input(player + ", please enter coordinates: "))
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
            print("Error: Cannot do a recycling move until " + str(self.maxNbrCards) + " cards are on the board.\n" \
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

        # Checks to see if there is a tile used over the chosen card, so that the board won't become illegal
        if position_card_2nd_tile[0] == position_card_1st_tile[0]:
            if isinstance(self.board[max(position_card_1st_tile[1], position_card_2nd_tile[1]) + 1][position_card_1st_tile[0]],
                          Tile):
                print(
                    "You cannot move this card, it would leave the board in an illegal state. Please choose another card.")
                return None
        elif isinstance(self.board[position_card_1st_tile[1] + 1][position_card_1st_tile[0]], Tile) or isinstance(
                self.board[position_card_2nd_tile[1] + 1][position_card_2nd_tile[0]], Tile):
            print(
                "You cannot move this card, it would leave the board in an illegal state. Please choose another card.")
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

        if self.isValidRecyclingMove(card_1st_tile, card_2nd_tile, input_rot_code, position_new_card,
                                        position_card_1st_tile, position_card_2nd_tile):
            self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = ' ' * 4
            self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = ' ' * 4
            self.board[position_first_tile[1]][position_first_tile[0]] = new_card.activeSide.tile1
            self.board[position_second_tile[1]][position_second_tile[0]] = new_card.activeSide.tile2

        # Make sure the same card can't be recycled twice
        self.recycled_card = card_1st_tile.cardOwner

        return [position_first_tile, position_second_tile]

    def isValidRecyclingMove(self, card_1st_tile, card_2nd_tile, input_rot_code, position_new_card,
                             position_card_1st_tile, position_card_2nd_tile):
        global position_first_tile
        global position_second_tile
        global new_card

        # Makes sure the last card used isn't the one being played now
        if card_1st_tile.cardOwner == self.recycled_card:
            print("You cannot move the card that was moved/played last turn. Please choose another card.")
            return False

        # Check if the card has the same rotation code and a different location, to be a legal recycle move
        if not(card_1st_tile.rotationCode == input_rot_code and position_new_card[0] == min(position_card_1st_tile[0], position_card_2nd_tile[0])
               and position_new_card[1] == min(position_card_1st_tile[1], position_card_2nd_tile[1])):
            self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = ' ' * 4
            self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = ' ' * 4
            new_card = Card(input_rot_code, card_1st_tile.cardOwner)
            position_first_tile, position_second_tile = new_card.get_tile_positions(position_new_card)

            # The new position is tested for legality. Place the card back before returning,
            # whether it is an illegal move or not.
            if not self.card_location_is_valid_spot(position_first_tile, position_second_tile, new_card):
                print("The location where you want to place your recycled card is not valid.")
                self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = card_1st_tile
                self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = card_2nd_tile
                return False
            self.board[position_card_1st_tile[1]][position_card_1st_tile[0]] = card_1st_tile
            self.board[position_card_2nd_tile[1]][position_card_2nd_tile[0]] = card_2nd_tile

            return True

        print("You cannot keep the same rotation and position.")
        return False

    def insert_card(self, input_args):
        """ Tries to insert card into the board from the inputArgs given by player.
            If it was successful in inserting it, it increments self.nbrCards by 1 and returns the newCard.
            Otherwise, it returns None.
        """
        # Ensure that an exception is thrown when we try to exceed the max number of cards to indicate failure
        if self.nbrCards >= self.maxNbrCards:
            print("Error: Cannot insert more than " + str(self.maxNbrCards) + " cards on the board.\nPlease do a recycling "
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

        self.nbrCards += 1
        Card.id_count += 1

        return [position_new_card, position_second_tile]

    def insert_card_direct(self, new_card, position):
        position_first_tile, position_second_tile = new_card.get_tile_positions(position)
        self.board[position_first_tile[1]][position_first_tile[0]] = new_card.activeSide.tile1
        self.board[position_second_tile[1]][position_second_tile[0]] = new_card.activeSide.tile2
        return (position_first_tile, position_second_tile)

    def check_four_consecutive(self, tile_pos, offset, type_item):
        """ Check whether or not there are 4 consecutive tiles with the same state of the type item
            from tilePos in the direction of the offset (offset can be seen as a normalized direction vector).
        """
        nbr_consecutives = 1
        current_pos = tile_pos
        while nbr_consecutives < 4:
            next_pos = add_tuples(current_pos, offset)
            if not all_values_positive(next_pos[0], next_pos[1], current_pos[0], current_pos[1]):
                return False
            if isinstance(self.board[tile_pos[1]][tile_pos[0]], Tile) \
                and isinstance(self.board[next_pos[1]][next_pos[0]], Tile) \
                and self.board[tile_pos[1]][tile_pos[0]].get_item_key(type_item) == \
                    self.board[next_pos[1]][next_pos[0]].get_item_key(type_item):
                    nbr_consecutives += 1
            else:
                break
            current_pos = next_pos
        return nbr_consecutives >= 4

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
        else:  # if newCard.orientation == Card.Orientation.up or newCard.orientation == Card.Orientation.down:
            tile_location_under_y = min(tile_1_location[1], tile_2_location[1]) - 1
            if not isinstance(self.board[tile_location_under_y][tile_1_location[0]], Tile):
                print("Error: The card would hang over an empty cell, which is not allowed.")
                return False
            # Since we checked conditions 1, 2 and 3b, the card location is valid.
            return True

    def check_win_conditions(self, insert_tiles_pos, type_item):
        offsets = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for tilePos in insert_tiles_pos:
            for offset in offsets:
                if self.check_four_consecutive(tilePos, offset, type_item):
                    return True
        return False

    #@toggle_printing_off_decorator
    def check_four_consecutive(self, tile_pos, offset, type_item):
        """ Check whether or not there are 4 consecutive tiles with the same state of the type item
            from tilePos in the direction of the offset (offset can be seen as a normalized direction vector).
        """
        nbr_consecutives = 1 + self.get_nbr_matching_tiles_in_offset_direction(tile_pos, offset, type_item)
        # We never need to check the direction directly up from the inserted tile (offset (1, 1)) because it is
        # impossible to find a match in that direction.
        # If the number of consecutive tiles found is smaller than 4, then search in the opposite direction
        if offset != (-1, -1) and nbr_consecutives < 4:
            opposite_direction_offset = get_negative_tuple(offset)
            nbr_consecutives += self.get_nbr_matching_tiles_in_offset_direction(
                                                            tile_pos, opposite_direction_offset, type_item)
        return nbr_consecutives >= 4

    def get_nbr_matching_tiles_in_offset_direction(self, tile_pos, offset, type_item):
        nbr_consecutives = 0
        current_pos = tile_pos
        while nbr_consecutives < 4:
            next_pos = add_tuples(current_pos, offset)
            if all_values_positive(next_pos[0], next_pos[1], current_pos[0], current_pos[1]) and \
                    isinstance(self.board[tile_pos[1]][tile_pos[0]], Tile) \
                and isinstance(self.board[next_pos[1]][next_pos[0]], Tile) \
                and self.board[tile_pos[1]][tile_pos[0]].get_item_key(type_item) == \
                    self.board[next_pos[1]][next_pos[0]].get_item_key(type_item):
                    nbr_consecutives += 1
            else:
                break
            current_pos = next_pos
        return nbr_consecutives

    #@toggle_printing_off_decorator
    def generate_valid_next_moves(self):
        with TogglePrintingOffGuard():
            # The valid moves are generated differently depending on the current phase (standard moves or recycling moves)
            if self.isInRecyclingPhase():
                return self.generate_valid_recycling_moves()
            else:
                print ("is in not recycling")
                return self.generate_valid_regular_moves()

    def generate_valid_recycling_moves(self):
        cardOwnerPreviousTile = None
        cardsThatCanBeRecycledAndTheirLocations = dict()
        valid_tile_locations = list()
        # For all rows on the board, search upwards through the corresponding column
        # in order to find the highest nonempty tile of each column. This is because we can only recycle cards
        # that do not have anything on top of them.
        for i in range(0, self.DIMENSIONS_X_Y[0]):
            for j in range(0, self.DIMENSIONS_X_Y[1]):
                # If we found the highest tile on that column (i.e. the next highest tile is either an empty tile
                # or the very top of the board), then generate valid recycling moves that involve swapping it out.
                if isinstance(self.board[j][i], Tile) and \
                        (not isinstance(self.board[j + 1][i], Tile) or ((j+1) == self.DIMENSIONS_X_Y[1])):
                    cardToRecycle = self.board[j][i].cardOwner
                    # If we already checked the valid moves of that card, we can ignore it.
                    if cardToRecycle != cardOwnerPreviousTile:
                        cardsThatCanBeRecycledAndTheirLocations[cardToRecycle] = ((i, j), self.find_location_other_tile_of_card(cardToRecycle, (i, j)))
                    cardOwnerPreviousTile = cardToRecycle
                    # If the tile above the current one is not out of bounds, then
                    # we assume that it is a valid tile location, since it is, by definition, the
                    # first empty tile we encounter going upwards.
                    if (j + 1) == self.DIMENSIONS_X_Y[1]:
                        valid_tile_locations.append((i, j+1))
                    # We should NOT search the tiles upwards from there.
                    break

        valid_recycling_moves = list()
        # Then, for each card that can be recycled, generate its valid next moves
        for card, locations in cardsThatCanBeRecycledAndTheirLocations.items():
            potential_valid_recycling_moves = self.generate_valid_recycling_moves_for_card(card, locations, valid_tile_locations)
            if potential_valid_recycling_moves != None:
                valid_recycling_moves.extend(potential_valid_recycling_moves)
        return valid_recycling_moves # valid_recycling_moves

    def find_location_other_tile_of_card(self, card, first_tile_position):
        if (first_tile_position[0] + 1) < self.DIMENSIONS_X_Y[0] and self.board[first_tile_position[1]][first_tile_position[0] + 1] == card:
            return (first_tile_position[0]+1, first_tile_position[1])
        if (first_tile_position[0] - 1) >= 0 and self.board[first_tile_position[1]][first_tile_position[0] - 1] == card:
            return (first_tile_position[0] - 1, first_tile_position[1])
        if (first_tile_position[1] + 1) < self.DIMENSIONS_X_Y[1] and self.board[first_tile_position[1] + 1][first_tile_position[0]] == card:
            return (first_tile_position[0], first_tile_position[1]+1)
        if (first_tile_position[1] - 1) >= 0 and self.board[first_tile_position[1] - 1][first_tile_position[0]] == card:
            return (first_tile_position[0], first_tile_position[1]-1)

    def generate_valid_recycling_moves_for_card(self, card, cardLocations, valid_tile_locations):
        recycling_moves = list()
        for newCardLocation in valid_tile_locations:
            for rotationCode in self.get_rotation_codes():
                if self.isValidRecyclingMove(card.activeSide.tile1, card.activeSide.tile2, rotationCode,
                                        newCardLocation, cardLocations[0], cardLocations[1]):
                    recycling_moves.append([card, cardLocations, rotationCode, newCardLocation])
        return recycling_moves


    def generate_valid_regular_moves(self):
        valid_regular_moves = list()
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
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes((i, j),
                                                                        self.get_vertical_rotation_codes())
                    # Similar logic applies to the very top row, the "vertical" moves
                    # are guaranteed to be invalid.
                    elif j == self.DIMENSIONS_X_Y[1] - 1:
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes((i, j),
                                                                        self.get_horizontal_rotation_codes())
                    else:
                        potential_valid_moves = self.generate_valid_regular_moves_from_pos_and_rot_codes((i, j),
                                                                        self.get_rotation_codes())
                    if potential_valid_moves is not None:
                        valid_regular_moves.extend(potential_valid_moves)
                    # We should NOT search the tiles upwards from the first empty tile, since they are guaranteed to be invalid.
                    break
        return valid_regular_moves

    def generate_valid_regular_moves_from_pos_and_rot_codes(self, position, rotation_codes):
        regular_moves = []
        for rotation_code in rotation_codes:
            potential_regular_move = self.try_insert_card_in_new_board_AI(position, rotation_code)
            if potential_regular_move is not None:
                regular_moves.append(potential_regular_move)
        return regular_moves

    def try_insert_card_in_new_board_AI(self, position, rotation_code):
        new_card = Card(rotation_code)
        position_first_tile, position_second_tile = new_card.get_tile_positions(position)
        if self.card_location_is_valid_spot(position_first_tile, position_second_tile, new_card):
            return new_card, position
        else:
            return None

    def isInRecyclingPhase(self):
        # Returns whether or not the players have entered the recycling phase, meaning that only recycling moves
        # will be allowed from now on. This happens when all cards are placed on the board.
        return self.nbrCards >= self.maxNbrCards

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

def game_loop():
    b = Board(NBR_CARDS)
    p1 = DotPlayer()
    p2 = ColorPlayer()

    # trace_input = input("Would you like to produce a trace of the minimax? Enter Y for yes or N for no \n" )
    # while True:
    #     if len(trace_input) == 0:
    #         trace_input = input("Please enter Y or N \n")
    #     elif trace_input == 'Y' or trace_input == 'y':
    #         # call trace method
    #         break
    #     elif trace_input == 'N' or trace_input == 'n':
    #         break
    #     else:
    #         trace_input = input("Invalid entry. Please try again \n")


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

    nbr_moves = 0
    while nbr_moves < MAX_NBR_MOVES:
        if ai_player != None and current_player == ai_player:
            inserted_tiles_pos = b.ai_move(tracing)
        else:
            #inserted_tiles_pos = b.ai_move(tracing)
            inserted_tiles_pos = b.ask_for_input(current_player.name)
        print(b)
        if b.nbrCards >= 4:
            # Even if the other player wins at the same time as the current player, the current player has
            # the priority.
            # (i.e. The current players wins even if both players won simultaneously,
            # because the current player was the one to play the winning move)
            if b.check_win_conditions(inserted_tiles_pos, current_player.typeItem):
                print(current_player.name + " wins the game!!!")
                return
            if b.check_win_conditions(inserted_tiles_pos, other_player.typeItem):
                print(other_player.name + " wins the game!!!")
                return
        # We switch to the other player
        other_player = current_player
        current_player = p1 if current_player == p2 else p2
        nbr_moves += 1
    print (str(MAX_NBR_MOVES) + " have been played. Thus, the game ends in a DRAW!! Congratulations to both players!")

# main
game_loop()

