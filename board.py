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

    def getPlayerOwner(self):
        """ Return the player that owns this tile"""
        return self.cardOwner.owner

    def __str__(self):
        return self.color.value + self.dotState.value + \
               (self.cardOwner.playerOwner[0] if len(self.cardOwner.playerOwner) > 0 else " ")

    def __repr__(self):
        return self.__str__()


class Side:

    def __init__(self, tile1, tile2):
        self.tile1 = tile1
        self.tile2 = tile2

    def __str__(self):
        return '||' + str(self.tile1) + ' | ' + str(self.tile2) + '||'


class Card:
    class Orientation(Enum):
        right = 1
        down = 2
        left = 3
        up = 4

    NBR_CARDS = 24
    NBR_ROTATION_CODES = 8

    def __init__(self, playerOwner, rotationCode=1):
        if len(playerOwner) > 1:
            print("Note: only the first letter of the player's name will be shown in output.")
        self.playerOwner = playerOwner
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

    def __str__(self):
        # NOTE: This specific "toString" method should only be used for debug purposes
        return  "Info on player " + str(self.playerOwner) + "'s card:\n" + \
                "Side 1: " + str(self.side1) + "\n" + \
                "Side 2: " + str(self.side2) + "\n" + \
                "Rotation Code: " + str(self.rotationCode) + "\n" + \
                "Active Side: " + ("Side 1" if self.activeSide == self.side1 else "Side 2") + "\n" + \
                "Orientation: " + str(self.orientation)


class Board:
    DIMENSIONS_X_Y = (8, 12)
    CONVERSION_LETTER_TO_NUMBER = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8,
                                'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17,
                                'T': 18, 'U': 19, 'V': 20, 'W': 21, 'X': 22, 'Y': 23, 'Z': 24}

    def __init__(self):
        self.board = [[Tile(Tile.Color.red, Tile.DotState.filled, Card('1')) for x in range(self.DIMENSIONS_X_Y[0])] for y in range (self.DIMENSIONS_X_Y[1])]

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

    def __str__(self):
        outputStr = ''
        rowIndex = 0
        for row in self.board:
            currentRowStr = '||' + "%2d" % (rowIndex+1) + '|| '
            for colVal in row:
                currentRowStr += '|' + str(colVal) + '|'
            currentRowStr += '\n'
            outputStr = currentRowStr + outputStr
            rowIndex += 1

        outputStr += ' ' * 7
        for row in range(self.DIMENSIONS_X_Y[0]):
            outputStr += ' ' * 2 + self.convertNumberToLetter(row) + ' ' * 2
        outputStr += '\n'
        return outputStr


c = Card("1")
#print(c, "\n")
c2 = Card("2", 7)
#print(c2)

b = Board()
print(b)
b.convertCoordinate(('c', 5))
