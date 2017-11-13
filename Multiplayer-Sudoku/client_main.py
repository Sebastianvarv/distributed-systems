from Tkinter import Tk
from client_input import input_main, initiate_lobby, update_lobby, destroy_lobby_window
from client import *
import time

if __name__ == "__main__":
    root = Tk()
    port, nickname = input_main(root)
    print(port, nickname)

    # Dummy shit
    player_id = reg_user(nickname, port)

    initiate_lobby(root)
    # (room_id, num players, max players)
    game_id = req_create_game(player_id, 4, port)
    games = req_get_games(port)
    # (room_id, num players, max players)
    # games = [(1, 3, 4), (2, 1, 5), (3, 3, 3)]
    # \Dummy shit

    print "games: " + str(games)

    # This update needs to be polled!
    update_lobby(root, games)
    t1 = time.time()
    while True:
        if time.time() - t1 > 5:
            destroy_lobby_window(root)
            break

