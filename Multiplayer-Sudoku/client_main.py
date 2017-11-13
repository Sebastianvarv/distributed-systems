from Tkinter import Tk
from client_input import input_main, initiate_lobby, update_lobby, destroy_lobby_window
from client import *
import time
import threading
import sys
import SudokuGameGUI

# Setup logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

sudoku_refresh_thread = None
lobby_refresh_thread = None
lobby_data = None


def refresh_lobby(root, port, room_window):
    global lobby_data
    games = req_get_games(port)
    update_lobby(root, games)

    lobby_data = room_window.action

    if lobby_data is not None:
        LOG.debug("Lobby updating returned: " + str(lobby_data))
        destroy_lobby_window(root)
    else:
        time.sleep(0.1)
        refresh_lobby(root, port, room_window)


def refresh_game_state(game_state):
    board, scores, game_progression = game_state
    board_changed = sudoku_ui.update_board(root, board)
    LOG.debug("sudoku game updating gave back " + str(board_changed))

    return board_changed


def refresh_game(sudoku_ui, game_id, port, root, user_id, board_changed=None):
    if board_changed is not None:
        game_state = req_make_move(user_id, game_id, board_changed[0], board_changed[1], board_changed[2], port)
    else:
        game_state = req_get_state(game_id, port)

    board_changed = refresh_game_state(game_state)

    time.sleep(1)
    refresh_game(sudoku_ui, game_id, port, root, user_id, board_changed)


if __name__ == "__main__":
    root = Tk()
    port, nickname = input_main(root)
    LOG.debug("Port: %d, nickname: %s" % (port, nickname))

    user_id = reg_user(nickname, port)

    room_window = initiate_lobby(root)

    lobby_refresh_thread = threading.Thread(target=refresh_lobby(root, port, room_window))
    lobby_refresh_thread.start()

    LOG.debug("Final lobby data is " + str(lobby_data))

    if lobby_data is None:
        LOG.error("Could not fetch data about game creation/selection")
        sys.exit(1)

    action, value = lobby_data
    game_state = None

    if action == "create":
        LOG.debug("Creating new game by request of user")
        game_id, game_state = req_create_game(user_id, value, port)
    elif action == "select":
        game_id = value
        game_state = req_join_game(user_id, game_id, port)

    LOG.debug("The game state is " + str(game_state))

    # TODO: Create game board
    # First unpack game state into board, scores, game progression indicator
    board, scores, game_progression = game_state[0], game_state[1], game_state[2]

    LOG.debug("Board is " + str(board))
    LOG.debug("Scores are " + str(scores))
    LOG.debug("Game state is " + str(game_progression))

    game = SudokuGameGUI.SudokuBoard(board)

    LOG.debug(game.board)

    sudoku_ui = SudokuGameGUI.SudokuUI(root, game)
    root.geometry("%dx%d" % (SudokuGameGUI.WIDTH, SudokuGameGUI.HEIGHT))

    sudoku_refresh_thread = threading.Thread(target=refresh_game(sudoku_ui, game_id, port, root, user_id))
