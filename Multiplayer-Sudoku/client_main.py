from Tkinter import Tk
import tkMessageBox
from client_input import initiate_input, initiate_lobby, update_lobby, destroy_lobby_window
from client import *
import time
import threading
import SudokuGameGUI

# Setup logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

sudoku_listen_thread = None
lobby_listen_thread = None
lobby_data = None
hard_exit = False


def update_lobby(root, port, room_window):
    """
    Updates the visual list of game rooms with the new data.
    :param root:
    :param port:
    :param room_window:
    :return loop ending boolean:
    """
    global lobby_data
    global hard_exit

    games = []
    try:
        games = req_get_games(port)
    except Exception as err:
        tkMessageBox.showwarning("Connection error", str(err))
        hard_exit = True
        return

    update_lobby(room_window, games)

    lobby_data = room_window.action

    if lobby_data is not None:
        destroy_lobby_window(room_window)
        return False
    else:
        time.sleep(0.1)
        return True


def update_lobby_helper(root, port, room_window, user_id):
    """
    This is the game lobby updater function.
    :param root:
    :param port:
    :param room_window:
    :return:
    """
    global hard_exit
    connected = True

    while connected:
        if hard_exit:
            room_window.destroy()

            # Remove player from the list of players in the server
            try:
                req_remove_player_lobby(user_id, port)
            except Exception as err:
                tkMessageBox.showwarning("Connection error", str(err))
                hard_exit = True

            break

        connected = update_lobby(root, port, room_window)


def update_game_state(sudoku_ui, game_state, user_id):
    """
    Calls the Sudoku UI game board visual state update.
    :param sudoku_ui:
    :param game_state:
    :return:
    """
    board, scores, game_progression = game_state
    keep_playing = True

    board_changed = sudoku_ui.update_board(root, board, scores, game_progression)

    if game_progression == 2:
        sudoku_ui.show_winner(scores[0], user_id)
        keep_playing = False

    return board_changed, keep_playing


def update_game(sudoku_ui, game_id, port, user_id, board_changed=None):
    """
    Gets updated game state from server to refresh the visual game state if needed.
    :param sudoku_ui:
    :param game_id:
    :param port:
    :param user_id:
    :param board_changed:
    :return loop ending boolean, board change for the next iteration:
    """
    global hard_exit

    try:
        if board_changed is not None:
            game_state = req_make_move(user_id, game_id, board_changed[0], board_changed[1], board_changed[2], port)
        else:
            game_state = req_get_state(game_id, port)

    except Exception as err:
        tkMessageBox.showwarning("Connection error", str(err))
        hard_exit = True
        return False, False

    board_changed, keep_playing = update_game_state(sudoku_ui, game_state, user_id)

    time.sleep(0.2)
    return board_changed, keep_playing


def update_game_helper(sudoku_ui, game_id, port, user_id):
    """
    This is the main game updater function.
    :param sudoku_ui:
    :param game_id:
    :param port:
    :param user_id:
    :return:
    """
    global hard_exit
    board_changed = None
    keep_playing = True

    while keep_playing:
        if hard_exit:
            sudoku_ui.destroy()
            hard_exit = False

            # Remove player from game
            try:
                req_remove_player(game_id, user_id, port)
            except Exception as err:
                tkMessageBox.showwarning("Connection error", str(err))
            break

        board_changed, keep_playing = update_game(sudoku_ui, game_id, port, user_id, board_changed)

    sudoku_ui.destroy()
    try:
        req_remove_player(game_id, user_id, port)
    except Exception as err:
        tkMessageBox.showwarning("Connection error", str(err))


def main_input(root):
    """
    Update input window if appropriate input is received and return it.
    :param root:
    :return port, nickname:
    """
    global hard_exit
    client_window = initiate_input(root)

    while True:
        if hard_exit:
            client_window.destroy()
            return None, None

        root.update()
        if client_window.port is not None and client_window.nickname is not None:
            LOG.debug("Port: %d, nickname: %s" % (client_window.port, client_window.nickname))
            user_id = None

            try:
                user_id = reg_user(client_window.nickname, client_window.port)
            except Exception as err:
                client_window.port, client_window.nickname = None, None
                tkMessageBox.showwarning("Connection error", str(err))

            if user_id is not None:
                client_window.destroy()
                return user_id, client_window.port


def main_lobby(root, port, user_id):
    """
    Runs the main game lobby thread.
    :param root:
    :param port:
    :return:
    """
    global lobby_data

    room_window = initiate_lobby(root)

    lobby_listen_thread = threading.Thread(target=update_lobby_helper(root, port, room_window, user_id))
    lobby_listen_thread.start()

    LOG.debug("Final lobby data is " + str(lobby_data))

    return lobby_data


def main_sudoku(root, lobby_data):
    """
    Runs the main sudoku game thread.
    :param root:
    :param lobby_data:
    :return:
    """
    action, value = lobby_data
    game_state = None

    if action == "create":
        LOG.debug("Creating new game by request of user")

        try:
            game_id, game_state = req_create_game(user_id, value, port)
        except Exception as err:
            tkMessageBox.showwarning("Connection error", str(err))
            return

    elif action == "select":
        game_id = value

        try:
            game_state = req_join_game(user_id, game_id, port)
        except Exception as err:
            tkMessageBox.showwarning("Connection error", str(err))
            return

    if not game_state:
        tkMessageBox.showwarning("Game error", "The selected room is full.")
        return

    LOG.debug("The game state is " + str(game_state))

    # First unpack game state into board, scores, game progression indicator
    board, scores, game_progression = game_state[0], game_state[1], game_state[2]

    LOG.debug("Scores are " + str(scores))
    LOG.debug("Game state is " + str(game_progression))

    game = SudokuGameGUI.SudokuBoard(board)
    sudoku_ui = SudokuGameGUI.SudokuUI(root, game)
    root.geometry("%dx%d" % (SudokuGameGUI.TOTAL_WIDTH, SudokuGameGUI.HEIGHT))

    sudoku_listen_thread = threading.Thread(target=update_game_helper(sudoku_ui, game_id, port, user_id))


def on_close():
    """
    Handling window close as a prompt.
    If user is okay with leaving, a global variable is set to exit and will be read in appropriate context
    to close the current window.
    :return:
    """
    global hard_exit
    if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
        hard_exit = True


if __name__ == "__main__":
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", on_close)

    user_id, port = main_input(root)
    LOG.debug('Closing input window.')

    # If received inputs are nones, it means client has left and there is nothing else we can do.
    if user_id is not None and port is not None:
        active_client = True
    else:
        active_client = False

    # If the client is active, we will proceed.
    while active_client:
        # Connect client to lobby and show the game rooms.
        lobby_data = main_lobby(root, port, user_id)

        # If we exited lobby permanently then break.
        if hard_exit:
            break

        # If lobby returned odd stuff, then start it anew.
        if lobby_data is None:
            continue

        # If we got here, then we're ready to play.
        main_sudoku(root, lobby_data)

    LOG.debug('kthxbye')
