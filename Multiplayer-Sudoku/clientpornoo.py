import argparse
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, RIGHT, LEFT, Entry, Label
from ufopornoo import SudokuUI, SudokuGame
import time

#Input sizes
INPUT_WIDTH = 200
INPUT_HEIGHT = 80

MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
SUDOKU_WIDTH = SUDOKU_HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board

class ConnectionUI(Frame):
    nickname = None
    port = None

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__initUI()

    def __initUI(self):
        self.parent.title("Connect nigguh")
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Insert port").grid(row=0)
        Label(self, text="Insert name").grid(row=1)

        self.entry_port = Entry(self)
        self.entry_port.grid(row=0, column=1)

        self.entry_nickname = Entry(self)
        self.entry_nickname.grid(row=1, column=1)

        self.submit_name = Button(self,
                                  text="Submit and connect",
                                  command=self.__submit_connect)
        self.submit_name.grid(row=2, column=1)

    def __submit_connect(self):
        """
        no space and less or equal to 8 characters"""
        name_ok = False
        port_ok = False

        nickname = self.entry_nickname.get()
        if len(nickname) <= 8:
            if ' ' not in nickname:
                name_ok = True
                print "spank me " + nickname
        else:
            print "fack ure name"

        try:
            port = int(self.entry_port.get())
        except (ValueError, TypeError):
            port = "-1"

        print type(port)

        if isinstance(port, int):
            if 1000 < port < 65535:
                port_ok = True
                print "spank me daddy"
        else:
            print "fack ure port"

        if name_ok and port_ok:
            self.nickname = nickname
            self.port = port


if __name__ == '__main__':
    root = Tk()
    client_window = ConnectionUI(root)
    root.geometry("%dx%d" % (INPUT_WIDTH, INPUT_HEIGHT + 40))
    while True:
        root.update()
        if client_window.port is not None and client_window.nickname is not None:
            print "we're fucking dead get the fuck out of here shit!"
            client_window.destroy()
            break

    board_name = "debug"
    with open('.\%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        sudoku_ui = SudokuUI(root, game)
        root.geometry("%dx%d" % (SUDOKU_WIDTH, SUDOKU_HEIGHT + 40))
        while True:
            root.update()
            sudoku_ui.destroy()
            time.sleep(5)
            break
