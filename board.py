from enum import Enum


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

    MAX_NBR_CARDS = 24
    NBR_ROTATION_CODES = 8
    # NOTE: The id system is probably not necessary, but it allows us
    # to identify the different cards placed on the board. For debugging purposes it will be quite useful. Also,
    # please do not call self.id_count but Card.id_count instead whenever you want to modify the value of the variable.
    id_count = 0

    def __init__(self, rotationCode=1):
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
        self.rotationCode = rotationCode
        if self.rotationCode <= self.NBR_ROTATION_CODES / 2:
            self.activeSide = self.side1
            self.orientation = self.Orientation(self.rotationCode)
        else:
            self.activeSide = self.side2
            self.orientation = self.Orientation(self.rotationCode - self.NBR_ROTATION_CODES / 2)
        self.id = Card.id_count
        Card.id_count += 1
        if Card.id_count > Card.MAX_NBR_CARDS:
            raise Exception("Error: exceeded the maximum number of cards allowed.\nThere can only be at most " + str(Card.MAX_NBR_CARDS) + " created.")

    def __str__(self):
        # NOTE: This specific "toString" method should only be used for debug purposes
        #return #"Info on player " + str(self.playerOwner) + "'s card:\n" + \
        return  "Side 1: " + str(self.side1) + "\n" + \
                "Side 2: " + str(self.side2) + "\n" + \
                "Rotation Code: " + str(self.rotationCode) + "\n" + \
                "Active Side: " + ("Side 1" if self.activeSide == self.side1 else "Side 2") + "\n" + \
                "Orientation: " + str(self.orientation) + "\n"


class Board:
    DIMENSIONS_X_Y = (8, 12)
    CONVERSION_LETTER_TO_NUMBER = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8,
                                'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17,
                                'T': 18, 'U': 19, 'V': 20, 'W': 21, 'X': 22, 'Y': 23, 'Z': 24}

    def __init__(self):
        # NOTE: Initially, the board is empty (no cards on it), so no tiles are on it either.
        # We illustrate a location in the board that has no card on it as blank spaces.
        self.board = [[' ' * 4 for x in range(self.DIMENSIONS_X_Y[0])] for y in range (self.DIMENSIONS_X_Y[1])]

        # DEBUGGING TO BE REMOVED
        c = Card()
        self.board[1][2] = Tile(Tile.Color.red, Tile.DotState.empty, c)
        self.board[1][3] = Tile(Tile.Color.white, Tile.DotState.filled, c)
        # END OF REMOVAL

    def convertCoordinate(self, letterNumberCoord):
        """ Convert a coordinate in the form [A-Z] [0-9] (eg. A 2) (given as a tuple)
            to a coordinate in the current 2-dimensional array
            Note the letter is the column and the number is the row (so coordinate given as (column, row))
        """
        xCoord = letterNumberCoord[1] - 1
        if xCoord > self.DIMENSIONS_X_Y[1] or xCoord < 0:
            raise Exception("ERROR: Y coordinate " + str(letterNumberCoord[1]) + " is out of bounds")
        yCoord = self.convertLetterToNumber(letterNumberCoord[0])
        if yCoord > self.DIMENSIONS_X_Y[0] or yCoord < 0:
            raise Exception("ERROR: X coordinate " + str(letterNumberCoord[0]) + " is out of bounds")
        return (xCoord, yCoord)

    def convertLetterToNumber(self, letter):
        return self.CONVERSION_LETTER_TO_NUMBER[letter.upper()]

    def convertNumberToLetter(self, searchedNumber):
        """ NOTE: This is highly inefficient as we have to loop through 24 letters in the worst case.
            However, this is supposed to only be used for the output that is not required during the tournament
            (it's for debugging purposes)
        """
        for letter, number in self.CONVERSION_LETTER_TO_NUMBER.items():
            if number == searchedNumber:
                return letter
        raise Exception("No valid conversion from number " + str(searchedNumber) + " to a letter")

    def readInput(self, inputStd):
        args = inputStd.split()
        if args[0] == 0:
            self.insertCard(args)
        else:
            self.swapCard(args)

    def swapCard(self, args):
        #TODO: implement this method
        raise Exception("Method not implemented yet (lol)")

    def insertCard(self, inputArgs):
        newCard = Card(inputArgs[1])
        positionNewCard = self.convertCoordinate((inputArgs[2], inputArgs[3]))
        #TODO: finish implementing this method
        raise Exception("Method not fully implemented yet (lol)")

    def __str__(self):
        outputStr = ''
        rowIndex = 0
        for row in self.board:
            currentRowStr = "%2d" % (rowIndex + 1) + ' '
            for colVal in row:
                currentRowStr += '|' + str(colVal)
            currentRowStr += '|\n'
            outputStr = currentRowStr + outputStr
            rowIndex += 1

        outputStr += ' ' * 5
        for row in range(self.DIMENSIONS_X_Y[0]):
            #outputStr += ' ' * 4 + self.convertNumberToLetter(row)
            outputStr += self.convertNumberToLetter(row) + ' ' * 4
        outputStr += '\n\n'
        return outputStr

c = Card()
print(c, "\n")
c2 = Card(7)
print(c2)

b = Board()
print(b)
b.convertCoordinate(('c', 5))
