from Tkinter import Tk
from client_input import input_main, initiate_lobby, update_lobby, destroy_lobby_window
from client import *
import time
import threading

# Setup logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

lobby_update_thread = None
lobby_data = None


def updatelob(root, port, room_window):
    global lobby_data
    games = req_get_games(port)
    # (room_id, num players, max players)
    games = [(1, 3, 4), (2, 1, 5), (3, 3, 3)]
    update_lobby(root, games)

    lobby_data = room_window.action

    if lobby_data is not None:
        LOG.debug("Lobby updating returned: " + str(lobby_data))
        destroy_lobby_window(root)
    else:
        time.sleep(0.1)
        updatelob(root, port, room_window)


if __name__ == "__main__":
    root = Tk()
    port, nickname = input_main(root)
    LOG.debug("Port: %d, nickname: %s" % (port, nickname))

    user_id = reg_user(nickname, port)

    room_window = initiate_lobby(root)

    lobby_update_thread = threading.Thread(target=updatelob(root, port, room_window))
    lobby_update_thread.start()

    LOG.debug("Final lobby data is" + str(lobby_data))

    # TODO: Do the request based on the information, i.e. create game or join game
    LOG.debug("Doing create game or join game request")
