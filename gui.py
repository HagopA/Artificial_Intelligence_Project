import sys, math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import board


def play_next_move():
    if boardWidget.winningPlayer is not None:
        return

    if game_info.ai_player != None and game_info.current_player == game_info.ai_player:
        inserted_tiles_pos = game_info.board.ai_move(game_info.tracing, game_info.current_player)
    else:
        inserted_tiles_pos = boardWidget.ask_for_input_qt(game_info.current_player.name)
    if len(inserted_tiles_pos) == 2:
        boardWidget.cardsPos.add(tuple(inserted_tiles_pos))
        boardWidget.lastCardPos = tuple(inserted_tiles_pos)
    else:
        boardWidget.cardsPos.remove((inserted_tiles_pos[0], inserted_tiles_pos[1]))
        boardWidget.cardsPos.add((inserted_tiles_pos[2], inserted_tiles_pos[3]))
        boardWidget.lastCardPos = (inserted_tiles_pos[2], inserted_tiles_pos[3])
    boardWidget.update()
    print(game_info.board)
    if game_info.board.nbr_cards >= 4:
        # Even if the other player wins at the same time as the current player, the current player has
        # the priority.
        # (i.e. The current players wins even if both players won simultaneously,
        # because the current player was the one to play the winning move)
        if game_info.board.check_win_conditions(inserted_tiles_pos, game_info.current_player.typeItem):
            print(game_info.current_player.name + " wins the game!!!")
            boardWidget.winningPlayer = game_info.current_player
            boardWidget.compute_next_move_btn.setVisible(False)
            return
        if game_info.board.check_win_conditions(inserted_tiles_pos, game_info.other_player.typeItem):
            print(game_info.other_player.name + " wins the game!!!")
            boardWidget.winningPlayer = game_info.other_player
            boardWidget.compute_next_move_btn.setVisible(False)
            return
    # We switch to the other player
    game_info.other_player = game_info.current_player
    game_info.current_player = game_info.p1 if game_info.current_player == game_info.p2 else game_info.p2
    game_info.nbr_moves += 1

    if game_info.nbr_moves >= board.MAX_NBR_MOVES:
        print (str(board.MAX_NBR_MOVES) + " moves have been played. Thus, the game ends in a DRAW!! Congratulations to both players!")
        boardWidget.compute_next_move_btn.setVisible(False)
        boardWidget.winningPlayer = -1
    boardWidget.compute_next_move_btn.setText(("dots" if game_info.current_player.typeItem == board.Tile.DotState else "colors") + " move")

class BoardWidget(QtWidgets.QWidget):
    def __init__(self, board):
        super().__init__()
        self.board = board
        # We only need to keep a reference to the cards on the board to display them properly in the UI.
        self.cardsPos = set()
        self.lastCardPos = None
        self.winningPlayer = None
        self.setGeometry(300, 100, 900, 900)
        self.setWindowTitle("Double Card")

        quit_btn = QtWidgets.QPushButton("Quit", self)
        quit_btn.move(700, 100)
        quit_btn.setShortcut(QtCore.Qt.Key_Escape)
        quit_btn.clicked.connect(QtCore.QCoreApplication.instance().quit)

        self.compute_next_move_btn = QtWidgets.QPushButton("Compute move", self)
        self.compute_next_move_btn.move(700, 615)
        self.compute_next_move_btn.setShortcut(QtCore.Qt.Key_Space)
        self.compute_next_move_btn.clicked.connect(play_next_move)

        self.show()

    def ask_for_input_qt(self, player):
        inserted_tiles_pos = None
        while inserted_tiles_pos is None:
            input_str = QtWidgets.QInputDialog.getText(self, player + " move",
                        player + ", please enter " +
                            ("a recycling move" if self.board.isInRecyclingPhase() else "a regular move") + ":")[0]
            inserted_tiles_pos = self.board.read_input(input_str)
        return inserted_tiles_pos

    def paintWinningPlayerText(self, painter):
        if isinstance(self.winningPlayer, board.ColorPlayer):
            painter.setBrush(QtGui.QColor(255, 0, 0))
        elif isinstance(self.winningPlayer, board.DotPlayer):
            painter.setBrush(QtGui.QBrush(QtGui.QColor(125, 125, 125), Qt.Dense6Pattern))
        else:
            painter.setBrush(QtGui.QColor(255, 255, 26))
        painter.drawRect(675, 250, 175, 100)

        painter.setFont(QtGui.QFont('Decorative', 10))
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))

        if self.winningPlayer == -1:
            painter.drawText(700, 300, "The game is a DRAW")
        else:
            painter.drawText(700, 300, self.winningPlayer.name)
            painter.drawText(700, 320, "wins the game!")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        if self.winningPlayer is not None:
            self.paintWinningPlayerText(painter)
        self.drawBoard(painter)
        self.drawLegendRotCodes(painter)
        painter.end()

    def drawBoard(self, painter):
        x_init_pos = 50
        y_init_pos = 50
        board_x_dim = 600
        board_y_dim = 700
        painter.setBrush(QtGui.QColor(116, 77, 37))
        painter.drawRect(x_init_pos, y_init_pos, board_x_dim, board_y_dim)
        painter.setFont(QtGui.QFont('Decorative', 10))
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))

        x_increment = board_x_dim / (self.board.DIMENSIONS_X_Y[0] + 1)
        y_increment = board_y_dim / (self.board.DIMENSIONS_X_Y[1] + 1)
        y_curr_offset = 0
        for j in range(0, self.board.DIMENSIONS_X_Y[1]):
            y_curr_offset += y_increment
            painter.drawLine(x_init_pos, y_init_pos + y_curr_offset, x_init_pos + board_x_dim, y_init_pos + y_curr_offset)
            painter.drawText(x_init_pos + x_increment / 2.5, y_init_pos + y_curr_offset - y_increment / 2.5, str(self.board.DIMENSIONS_X_Y[1] - j))
        x_curr_offset = 0
        for i in range(0, self.board.DIMENSIONS_X_Y[0]):
            x_curr_offset += x_increment
            painter.drawLine(x_init_pos + x_curr_offset, y_init_pos, x_init_pos + x_curr_offset, y_init_pos + board_y_dim)
            painter.drawText(x_init_pos + x_curr_offset + x_increment / 2.5, board_y_dim + y_increment / 1.75, self.board.convert_num_to_letter(i))

        for i in range(0, self.board.DIMENSIONS_X_Y[0]):
            for j in range(0, self.board.DIMENSIONS_X_Y[1]):
                tile_to_be_drawn = self.board.board[j][i]
                if isinstance(tile_to_be_drawn, board.Tile):
                    x_pos = x_init_pos + x_increment * (i + 1)
                    y_pos = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - j - 1)
                    self.draw_tile(painter, tile_to_be_drawn, x_pos, y_pos, x_increment, y_increment)

        self.drawCardsBorders(painter, x_init_pos, y_init_pos, x_increment, y_increment)

    def draw_tile(self, painter, tile_to_be_drawn, x_pos, y_pos, x_increment, y_increment):
        radius = 10
        if tile_to_be_drawn.color == board.Tile.Color.red:
            painter.setBrush(QtGui.QColor(255, 0, 0))
        else:
            painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(x_pos, y_pos, x_increment, y_increment)
        if tile_to_be_drawn.dotState == board.Tile.DotState.filled:
            painter.setBrush(QtGui.QColor(0, 0, 0))
        else:
            painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(x_pos - radius + x_increment / 2, y_pos - radius + y_increment / 2, radius * 2, radius * 2)

    def drawCardsBorders(self, painter, x_init_pos, y_init_pos, x_increment, y_increment):
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 153), 4, Qt.SolidLine))
        for card in self.cardsPos:
            self.drawCardBorders(painter, card, x_init_pos, y_init_pos, x_increment, y_increment)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0), 4, Qt.SolidLine))
        if self.lastCardPos is not None:
            self.drawCardBorders(painter, self.lastCardPos, x_init_pos, y_init_pos, x_increment, y_increment)

    def drawCardBorders(self, painter, card_to_be_drawn, x_init_pos, y_init_pos, x_increment, y_increment):
        if card_to_be_drawn[0] < card_to_be_drawn[1]:
            if card_to_be_drawn[0][0] == card_to_be_drawn[1][0]:
                bottom_left_pos_x = x_init_pos + x_increment * (card_to_be_drawn[0][0] + 1)
                bottom_left_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[0][1])
                top_right_pos_x = x_init_pos + x_increment * (card_to_be_drawn[1][0] + 2)
                top_right_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[1][1] - 1)
            else:
                bottom_left_pos_x = x_init_pos + x_increment * (card_to_be_drawn[0][0] + 1)
                bottom_left_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[0][1])
                top_right_pos_x = x_init_pos + x_increment * (card_to_be_drawn[1][0] + 2)
                top_right_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[1][1] - 1)
        else:
            if card_to_be_drawn[0][0] == card_to_be_drawn[1][0]:
                bottom_left_pos_x = x_init_pos + x_increment * (card_to_be_drawn[1][0] + 1)
                bottom_left_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[1][1])
                top_right_pos_x = x_init_pos + x_increment * (card_to_be_drawn[0][0] + 2)
                top_right_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[0][1] - 1)
            else:
                top_right_pos_x = x_init_pos + x_increment * (card_to_be_drawn[1][0] + 1)
                top_right_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[1][1])
                bottom_left_pos_x = x_init_pos + x_increment * (card_to_be_drawn[0][0] + 2)
                bottom_left_pos_y = y_init_pos + y_increment * (self.board.DIMENSIONS_X_Y[1] - card_to_be_drawn[0][1] - 1)
        painter.drawLine(bottom_left_pos_x, bottom_left_pos_y, top_right_pos_x, bottom_left_pos_y)
        painter.drawLine(bottom_left_pos_x, top_right_pos_y, top_right_pos_x, top_right_pos_y)
        painter.drawLine(bottom_left_pos_x, bottom_left_pos_y, bottom_left_pos_x, top_right_pos_y)
        painter.drawLine(top_right_pos_x, bottom_left_pos_y, top_right_pos_x, top_right_pos_y)

    def drawLegendRotCodes(self, painter):
        painter.setFont(QtGui.QFont('Decorative', 10))
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawText(660, 470, "1")
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(680, 450, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(693.75, 459, 5, 5)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(710, 450, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(723.75, 459, 5, 5)

        painter.drawText(660, 507.5, "2")
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(680, 480, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(693.75, 489, 5, 5)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(680, 500, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(693.75, 509, 5, 5)

        painter.drawText(660, 550, "3")
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(680, 530, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(693.75, 539, 5, 5)
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(710, 530, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(723.75, 539, 5, 5)

        painter.drawText(660, 587.5, "4")
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(680, 560, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(693.75, 569, 5, 5)
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(680, 580, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(693.75, 589, 5, 5)

        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawText(780, 470, "5")
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(800, 450, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(813.75, 459, 5, 5)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(830, 450, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(843.75, 459, 5, 5)

        painter.drawText(780, 507.5, "6")
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(800, 480, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(813.75, 489, 5, 5)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(800, 500, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(813.75, 509, 5, 5)

        painter.drawText(780, 550, "7")
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(800, 530, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(813.75, 539, 5, 5)
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(830, 530, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(843.75, 539, 5, 5)

        painter.drawText(780, 587.5, "8")
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(800, 560, 30, 20)
        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawEllipse(813.75, 569, 5, 5)
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.drawRect(800, 580, 30, 20)
        painter.setPen(QtGui.QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawEllipse(813.75, 589, 5, 5)

# MAIN
board.set_up_game()

game_info = board.game_info

app = QtWidgets.QApplication(sys.argv)
boardWidget = BoardWidget(game_info.board)
boardWidget.show()
app.exec_()


