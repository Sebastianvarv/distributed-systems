from Tkinter import Frame, Button, BOTH, Entry, Label, CENTER
from ttk import Treeview
import tkMessageBox
import logging

# Setup logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

# Input sizes
INPUT_WIDTH = 300
INPUT_HEIGHT = 80

# Lobby sizes
LOBBY_WIDTH = 400
LOBBY_HEIGHT = 400

class ConnectionUI(Frame):
    nickname = None
    port = None

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__initUI()

    def __initUI(self):
        self.parent.title('Server connection')
        self.pack(fill=BOTH, expand=1)

        Label(self, text='Insert port').grid(row=0, padx=(35, 0))
        Label(self, text='Insert name').grid(row=1, padx=(35, 0))

        self.entry_port = Entry(self)
        self.entry_port.grid(row=0, column=1)

        self.entry_nickname = Entry(self)
        self.entry_nickname.grid(row=1, column=1)

        self.submit_name = Button(self, text='Submit and connect', command=self.__submit_connect)
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
                LOG.debug('Player created: ' + nickname)
            else:
                tkMessageBox.showwarning(
                    "Name error",
                    "Player name cannot contain space."
                )
        elif len(nickname) <= 0:
            tkMessageBox.showwarning(
                "Name error",
                "Player name cannot be empty."
            )
        elif len(nickname) > 8:
            tkMessageBox.showwarning(
                "Name error",
                "Player name has to be less than 9 characters long."
            )

        try:
            port = int(self.entry_port.get())
        except (ValueError, TypeError):
            port = '-1'

        if isinstance(port, int):
            if 1000 < port < 65535:
                port_ok = True
                LOG.debug('Ok port.')
            else:
                tkMessageBox.showwarning(
                    "Port error",
                    "Port number has to be between 1000 and 65535."
                )
        else:
            tkMessageBox.showwarning(
                "Port error",
                "Port number has to be an integer."
            )

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
        self.parent.title('Sudoku Lobby')
        self.pack(fill=BOTH, expand=1)

        self.lobby_list = Treeview(self, columns=('room', 'players'))
        self.lobby_list['show'] = 'headings'
        self.lobby_list.heading('room', text='Room ID')
        self.lobby_list.column('room', width=250, anchor=CENTER)
        self.lobby_list.heading('players', text='Players')
        self.lobby_list.column('players', width=100, anchor=CENTER)
        self.lobby_list.grid(row=1, column=0, columnspan=2, rowspan=2, padx=20, pady=(10, 0))

        self.connect_lobby = Button(self, text='Join existing game', command=self.__connect_lobby)
        self.connect_lobby.grid(row=3, column=1, pady=(0, 10))

        Label(self, text='Create and join a new\n game with n players:').grid(row=4, column=0)

        self.max_players = Entry(self)
        self.max_players.grid(row=4, column=1)

        self.create_game = Button(self, text='Join new game', command=self.__create_game)
        self.create_game.grid(row=5, column=1)

    def __connect_lobby(self):
        """
        Handle lobby connection button."""
        LOG.debug('Lobby connect button has been pressed.')
        current_item = self.lobby_list.focus()
        selected_id = None

        if current_item is not None and current_item.strip() != '':
            # Select game column value from item values dictionary.
            selected_id = self.lobby_list.item(current_item)['values'][0]
            LOG.debug('Player wishes to join game ' + str(selected_id))

            if selected_id is not None:
                self.action = ('select', selected_id)
        else:
            tkMessageBox.showwarning(
                "Connection error",
                "Please select a game from the lobby to join."
            )


    def __create_game(self):
        """
        Create game with some number of max players."""
        max_ok = False

        try:
            max_count = int(self.max_players.get())
        except (ValueError, TypeError):
            max_count = -1
            tkMessageBox.showwarning(
                "Input error",
                "Max player count has to be an integer."
            )

        if isinstance(max_count, int):
            if max_count >= 2:
                max_ok = True
                LOG.debug('Ok max player count.')
            else:
                tkMessageBox.showwarning(
                    "Input error",
                    "Max player count has to be larger than 2."
                )
                LOG.error('Bad max count.')

        if max_ok:
            self.action = ('create', max_count)


    def populate_list(self, games):
        """
        Method to re-populate the lobby list every poll.
        Additionally retains the focused line during polling.
        :param games:
        """
        previous_selection = self.lobby_list.selection()
        prev_item = None
        if len(previous_selection) > 0:
            prev_item = self.lobby_list.item(previous_selection[0])

        self.lobby_list.delete(*self.lobby_list.get_children())
        for game in games:
            self.lobby_list.insert('', 'end', values=(str(game[0]), str(game[1]) + '/' + str(game[2])))

        if prev_item is not None:
            for item in self.lobby_list.get_children():
                if self.lobby_list.item(item) == prev_item:
                    self.lobby_list.selection_set(item)
                    self.lobby_list.focus(item)


def input_main(root):
    """
    Create input UI and attach it to root.
    Keep polling until appropriate input is receiver and return it.
    :param root:
    :return port, nickname:
    """
    client_window = ConnectionUI(root)
    root.geometry('%dx%d' % (INPUT_WIDTH, INPUT_HEIGHT))
    while True:
        root.update()
        if client_window.port is not None and client_window.nickname is not None:
            LOG.debug('Closing input window.')
            client_window.destroy()
            return client_window.port, client_window.nickname


def initiate_lobby(root):
    """
    Create lobby UI and attach it to root.
    :param root:
    """
    room_window = LobbyUI(root)
    root.geometry('%dx%d' % (LOBBY_WIDTH, LOBBY_HEIGHT))
    LOG.debug('Kick up the 4d3d3d3.')
    return room_window


def update_lobby(root, games):
    """
    Update lobby list view from games list data.
    :param root:
    :param games:
    """

    lobby_instance = root.winfo_children()[0]
    lobby_instance.populate_list(games)
    root.update()


def destroy_lobby_window(root):
    """
    Close lobby UI portion of root.
    :param root:
    """
    lobby_instance = root.winfo_children()[0]
    LOG.debug('Lobby is destroyed.')
    lobby_instance.destroy()
