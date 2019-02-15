from enum import Enum

# The specifications tell us that there are 24 cards available to be placed on the board (shared between both players).
NBR_CARDS = 24

addTuples = lambda tuple1, tuple2: tuple(x + y for x, y in zip(tuple1, tuple2))


def all_values_positive(array_values):
    for x in array_values:
        if x < 0:
            return False
    return True


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

    def __init__(self, color, dot_state, card_owner):
        self.color = color
        self.dotState = dot_state
        self.cardOwner = card_owner

    def get_item_key(self, type_item):
        if type_item == Tile.Color:
            return self.color
        else:
            return self.dotState

    """ # To remove if we find out we do not need a reference to the player owner
    def getPlayerOwner(self):
        # Return the player that owns this tile
        return self.cardOwner.owner
    """

    def __str__(self):
        # Note: We assume there is no more than 99 different ids
        return self.color.value + self.dotState.value + "%-2d" % self.cardOwner.id

    def __repr__(self):
        return self.__str__()


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
        """ #Will probably remove, unless we find out for whatever reason that
            #the card needs to know who is the player that placed it
        if len(playerOwner) > 1:
            print("Note: only the first letter of the player's name will be shown in output.")
        self.playerOwner = playerOwner
        """
        self.side1 = Side(Tile(Tile.Color.red, Tile.DotState.filled, self),
                          Tile(Tile.Color.white, Tile.DotState.empty, self))
        self.side2 = Side(Tile(Tile.Color.red, Tile.DotState.empty, self),
                          Tile(Tile.Color.white, Tile.DotState.filled, self))
        self.rotationCode = rotation_code
        if self.rotationCode <= self.NBR_ROTATION_CODES / 2:
            self.activeSide = self.side1
            self.orientation = self.Orientation(self.rotationCode)
        else:
            self.activeSide = self.side2
            self.orientation = self.Orientation(self.rotationCode - self.NBR_ROTATION_CODES / 2)
        self.id = Card.id_count
        Card.id_count += 1

    def get_tile_positions(self, position):
        if self.orientation == self.Orientation.right:
            return position, addTuples(position, (1, 0))
        elif self.orientation == self.Orientation.left:
            return addTuples(position, (1, 0)), position
        elif self.orientation == self.Orientation.up:
            return position, addTuples(position, (0, 1))
        else:  # if self.orientation == self.Orientation.down:
            return addTuples(position, (0, 1)), position

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
                                   'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17, 'T': 18,
                                   'U': 19, 'V': 20, 'W': 21, 'X': 22, 'Y': 23, 'Z': 24}

    def __init__(self, max_nbr_cards):
        # NOTE: Initially, the board is empty (no cards on it), so no tiles are on it either.
        # We illustrate a location on the board with no tile/card as a string (blank spaces).
        self.board = [[' ' * 4 for x in range(self.DIMENSIONS_X_Y[0])] for y in range (self.DIMENSIONS_X_Y[1])]
        self.nbrCards = 0
        # There is at most maxNbrCards cards on the board and we have to ensure no one can insert cards (through the
        # methods we provide) when we reach that quota.
        self.maxNbrCards = max_nbr_cards

    def convert_coordinate(self, letter_num_coordinate):
        """ Convert a coordinate in the form [A-Z] [0-9] (eg. A 2) (given as a tuple)
            to a coordinate in the current 2-dimensional array
            Note the letter is the column and the number is the row (so coordinate given as (column, row))
        """
        x_coord = self.convert_letter_to_num(letter_num_coordinate[0])
        if x_coord >= self.DIMENSIONS_X_Y[0]:
            raise Exception("ERROR: X coordinate " + str(letter_num_coordinate[0]) + " is out of bounds")
        y_coord = letter_num_coordinate[1] - 1
        if y_coord >= self.DIMENSIONS_X_Y[1] or y_coord < 0:
            raise Exception("ERROR: Y coordinate " + str(letter_num_coordinate[1]) + " is out of bounds")
        return x_coord, y_coord

    def convert_letter_to_num(self, letter):
        return self.CONVERSION_LETTER_TO_NUMBER[letter.upper()]

    def convert_num_to_letter(self, searched_number):
        """ NOTE: This is highly inefficient as we have to loop through 24 letters in the worst case.
            However, this is supposed to only be used for the output that is not required during the tournament
            (it's for debugging purposes)
        """
        for letter, number in self.CONVERSION_LETTER_TO_NUMBER.items():
            if number == searched_number:
                return letter
        raise Exception("No valid conversion from number " + str(searched_number) + " to a letter")

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
        if args[0] == "0":
            if len(args) != 4:
                print("Input error: Regular moves should have 4 arguments (not " + str(len(args)) + "):")
                print("0 orientationCode xCoord yCoord")
                print("Example: 0 5 A 2")
                return False
            return self.insert_card(args)
        else:
            if len(args) != 7:
                print("Input error: Swap moves should have 7 arguments (not " + str(len(args)) + "):")
                print("xCoordTile1 yCoordTile1 xCoordTile2 yCoordTile2 newOrientationCode newCoordX newCoordY")
                print("Example: F 2 F 3 3 A 2")
                return False
            return self.swap_card(args)

    def swap_card(self, args):
        # TODO: implement this method
        raise Exception("Method not implemented yet (lol)")

    def insert_card(self, input_args):
        """ Tries to insert card into the board from the inputArgs given by player.
            If it was successful in inserting it, it increments self.nbrCards by 1 and returns the newCard.
            Otherwise, it returns None.
        """
        # Ensure that an exception is thrown when we try to exceed the max number of cards to indicate failure
        if self.nbrCards >= self.maxNbrCards:
            print("Error: Cannot insert more than " + self.maxNbrCards + " cards on the board.\nPlease do a recycling "
                                                                         "move instead.")
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
        except Exception:
            print(input_args[2] + " " + input_args[3] + " does not represent a valid position.")
            return None
        position_first_tile, position_second_tile = new_card.get_tile_positions(position_new_card)
        if not self.card_location_is_valid_spot(position_first_tile, position_second_tile, new_card):
            print("The location where you want to place your card is not valid.")
            return None

        self.board[position_first_tile[1]][position_first_tile[0]] = new_card.activeSide.tile1
        self.board[position_second_tile[1]][position_second_tile[0]] = new_card.activeSide.tile2

        self.nbrCards += 1

        return position_new_card, position_second_tile

    def check_four_consecutive(self, tile_pos, offset, type_item):
        """ Check whether or not there are 4 consecutive tiles with the same state of the type item
            from tilePos in the direction of the offset (offset can be seen as a normalized direction vector).
        """
        nbr_consecutives = 1
        current_pos = tile_pos
        while nbr_consecutives < 4:
            next_pos = addTuples(current_pos, offset)
            if not all_values_positive([next_pos[0], next_pos[1], current_pos[0], current_pos[1]]):
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
        except Exception:
            print("Error: You cannot place a card on top of other cards.")
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

            occupied_locations = isinstance(self.board[tile1_location_y_under][tile_1_location[0]], Tile) and \
                                 isinstance(self.board[tile2_location_y_under][tile_2_location[0]], Tile)
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
        offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for tilePos in insert_tiles_pos:
            for offset in offsets:
                if self.check_four_consecutive(tilePos, offset, type_item):
                    return True

    def __str__(self):
        output_str = ''
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

    # Users decide which player they'd like to be
    user_input = input("Enter C if you'd like to play color, or D if you'd like to play dots \n")
    while user_input != '':
        if user_input == 'C' or user_input == 'c':
                current_player = p2
                other_player = p1
                break
        elif user_input == 'D' or user_input == 'd':
                current_player = p1
                other_player = p2
                break
        else:
            user_input = input("Invalid entry. Please try again \n")

    while True:
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


game_loop()
