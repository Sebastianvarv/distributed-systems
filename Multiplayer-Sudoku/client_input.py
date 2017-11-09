from Tkinter import Frame, Button, BOTH, Entry, Label
from ttk import Treeview
from ufopornoo import SudokuUI, SudokuGame
import time

# Input sizes
INPUT_WIDTH = 300
INPUT_HEIGHT = 80

# Lobby sizes
LOBBY_WIDTH = 500
LOBBY_HEIGHT = 400

# Sudoku sizes
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
        self.parent.title("Server connection")
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
        Input name has no space and less or equal to 8 characters.
        Input port consists of an integer between 1001 and 65535.
        """
        name_ok = False
        port_ok = False

        nickname = self.entry_nickname.get()
        if 8 >= len(nickname) > 0:
            if ' ' not in nickname:
                name_ok = True
                print "Spank me " + nickname
        else:
            print "Bad name."

        try:
            port = int(self.entry_port.get())
        except (ValueError, TypeError):
            port = "-1"

        print type(port)

        if isinstance(port, int):
            if 1000 < port < 65535:
                port_ok = True
                print "Ok port."
        else:
            print "Bad doggos."

        if name_ok and port_ok:
            self.nickname = nickname
            self.port = port


class LobbyUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku Lobby")
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Game room").grid(row=0)

        self.lobby_list = Treeview(self)
        self.lobby_list["columns"] = ("Game room", "Players")
        self.lobby_list.column("Game room", width=100)
        self.lobby_list.column("Players", width=100)
        self.lobby_list.grid(row=1, column=0)

        self.connect_lobby = Button(self,
                                    text="Submit and connect",
                                    command=self.__connect_lobby)
        self.connect_lobby.grid(row=2, column=1)

    def __connect_lobby(self):
        selection = self.get_current_selection()
        print "daddy wants to play"
        print selection
        # do something related to destroying the window and returning selected lobby data.

    def get_current_selection(self):
        current_item = self.lobby_list.focus()
        return current_item

    def populate_list(self, games):
        for game in games:
            print game
            #self.lobby_list.insert("", 0, text="Line 1", values=("1A", "1b"))


def input_main(root):
    client_window = ConnectionUI(root)
    root.geometry("%dx%d" % (INPUT_WIDTH, INPUT_HEIGHT + 40))
    while True:
        root.update()
        if client_window.port is not None and client_window.nickname is not None:
            print "input is fucking dead get the fuck out of here shit!"
            client_window.destroy()
            return client_window.port, client_window.nickname


def initiate_lobby(root):
    room_window = LobbyUI(root)
    root.geometry("%dx%d" % (LOBBY_WIDTH, LOBBY_HEIGHT))
    print "Kick up the 4d3d3d3."


def update_lobby(root, games):
    lobby_instance = root.winfo_children()[0]

    lobby_instance.populate_list(games)
    root.update()
    # don't print this when polling is active pls
    print "Lobby updated."


def destroy_lobby_window(root):
    lobby_instance = root.winfo_children()[0]

    print "lobby is fucking dead get the fuck out of here shit!"
    lobby_instance.destroy()
