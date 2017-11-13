import argparse
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board


class SudokuUI(Frame):
    def __init__(self, parent, board):
        self.game = board
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares """
        for i in xrange(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in xrange(9):
            for j in xrange(9):
                answer = self.game.board[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers"
                    )

    def __cell_clicked(self, event):
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.board[row][col] == 0:
                self.row, self.col = row, col

        self.__draw_cursor()

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __key_pressed(self, event):
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.board[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()

    def update_board(self, root, board):
        return_val = None

        # Check if user has added any values
        if self.game.board != board:
            change_row = -1
            change_column = -1

            # Find where the user added elements
            for i, row in enumerate(self.game.board):
                if row != board[i]:
                    change_row = i

                    for j, elem in enumerate(row):
                        if elem != board[i][j]:
                            # Found the changed element
                            change_column = j
                            break

            change_value = self.game.board[change_row][change_column]

            if change_row == -1 and change_column == -1 and change_value == 0:
                raise SudokuError("Something has gone to shit, can't find the edited value")

            return_val = (change_row, change_column, change_value)

        self.game.update_board(board)
        root.update()

        return return_val


class SudokuBoard(object):
    """
    Sudoku Board representation
    """

    def __init__(self, board):
        self.board = self.__create_board(board)

    def __create_board(self, input_board):
        if len(input_board) != 9:
            raise SudokuError("There must be 9 rows to the board")

        for row in input_board:
            if len(row) != 9:
                raise SudokuError("There must be 9 columns to a row")

            for digit in row:
                if type(digit) != int and 0 <= digit < 10:
                    raise SudokuError("Only numbers between 0-9 are permitted on the sudoku field")

        return input_board

    def update_board(self, input_board):
        if len(input_board) != 9:
            raise SudokuError("There must be 9 rows to the board")

        for row in input_board:
            if len(row) != 9:
                raise SudokuError("There must be 9 columns to a row")

            for digit in row:
                if type(digit) != int and 0 <= digit < 10:
                    raise SudokuError("Only numbers between 0-9 are permitted on the sudoku field")

        self.board = input_board


class SudokuError(Exception):
    """
    An application specific error.
    """
    pass
