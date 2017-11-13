from Tkinter import Tk
from client_input import input_main, initiate_lobby, update_lobby, destroy_lobby_window
from client import *
import time
import threading

lobby_update_thread = None
lobby_data = None


def updatelob(root, port):
    global lobby_data
    games = req_get_games(port)
    lobby_data = update_lobby(root, games)
    print "lobby updating returned:", lobby_data

    if lobby_data is not None:
        pass
    else:
        time.sleep(0.1)
        updatelob(root, port)


if __name__ == "__main__":
    root = Tk()
    port, nickname = input_main(root)
    print(port, nickname)

    # Dummy shit
    user_id = reg_user(nickname, port)

    initiate_lobby(root)

    lobby_update_thread = threading.Thread(target=updatelob(root, port))
    lobby_update_thread.start()

    print lobby_data

    # TODO: Do the request based on the information, i.e. create game or join game
    print("Doing create game or join game request")

    # (room_id, num players, max players)
    # games = [(1, 3, 4), (2, 1, 5), (3, 3, 3)]
    # \Dummy shit
