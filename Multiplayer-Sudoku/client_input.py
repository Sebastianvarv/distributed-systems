from Tkinter import Frame, Button, BOTH, Entry, Label
from ttk import Treeview
from ufopornoo import SudokuUI, SudokuGame
import time

# Input sizes
INPUT_WIDTH = 300
INPUT_HEIGHT = 80

# Lobby sizes
LOBBY_WIDTH = 650
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

        self.submit_name = Button(self, text="Submit and connect", command=self.__submit_connect)
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
                print "Player created: " + nickname
        else:
            # replace with warning window.
            print "Bad name input."

        try:
            port = int(self.entry_port.get())
        except (ValueError, TypeError):
            port = "-1"

        if isinstance(port, int):
            if 1000 < port < 65535:
                port_ok = True
                print "Ok port."
        else:
            # replace with warning window.
            print "Bad port"

        if name_ok and port_ok:
            self.nickname = nickname
            self.port = port


class LobbyUI(Frame):
    action = None

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku Lobby")
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Game lobby").grid(row=0)

        self.lobby_list = Treeview(self, columns=('Room ID', 'Players'))
        self.lobby_list.column("Room ID", width=100)
        self.lobby_list.column("Players", width=100)
        self.lobby_list.grid(row=1, column=1)

        self.connect_lobby = Button(self, text="Connect", command=self.__connect_lobby)
        self.connect_lobby.grid(row=1, column=2)

        Label(self, text="Enter max players.").grid(row=3, column=0)

        self.max_players = Entry(self)
        self.max_players.grid(row=3, column=1)

        self.create_game = Button(self, text="Create new game", command=self.__create_game)
        self.create_game.grid(row=3, column=2)

    def __connect_lobby(self):
        print "Lobby connect button has been pressed."
        current_item = self.lobby_list.focus()
        print current_item
        if current_item is not None:
            # selection = (room_id, )
            self.action = ('select', current_item[0])

            #list_selection = self.__get_current_selection()
            # do something related to destroying the window and returning selected lobby data.
            #self.selection = list_selection


    def __create_game(self):
        max_ok = False

        try:
            max_p = int(self.max_players.get())
        except (ValueError, TypeError):
            max_p = "-1"

        if isinstance(max_p, int):
            if max_p >= 2:
                max_ok = True
                print "Ok max player count."
        else:
            print "Bad max count."

        if max_ok:
            self.action = ('create', max_ok)


    def populate_list(self, games):
        """
        Method to re-populate the lobby list every poll.
        :param games:
        """
        previous_selection = self.lobby_list.selection()
        if len(previous_selection) > 0:
            print previous_selection[0]

        self.lobby_list.delete(*self.lobby_list.get_children())
        for game in games:
            self.lobby_list.insert('', 'end', values=("Game " + str(game[0]), str(game[1]) + "/" + str(game[2])))

        if len(previous_selection) > 0:
            self.lobby_list.selection_set(previous_selection[0])
            self.lobby_list.focus_set()
            self.lobby_list.focus(previous_selection[0])


def input_main(root):
    client_window = ConnectionUI(root)
    root.geometry("%dx%d" % (INPUT_WIDTH, INPUT_HEIGHT))
    while True:
        root.update()
        if client_window.port is not None and client_window.nickname is not None:
            print "Closing input window."
            client_window.destroy()
            return client_window.port, client_window.nickname


def initiate_lobby(root):
    room_window = LobbyUI(root)
    root.geometry("%dx%d" % (LOBBY_WIDTH, LOBBY_HEIGHT))
    print "Kick up the 4d3d3d3."
    return room_window


def update_lobby(root, games):
    """
    Update lobby list view.
    :param root:
    :param games:
    """

    lobby_instance = root.winfo_children()[0]
    lobby_instance.populate_list(games)
    root.update()


def destroy_lobby_window(root):
    lobby_instance = root.winfo_children()[0]

    print "Lobby is destroyed."
    lobby_instance.destroy()
