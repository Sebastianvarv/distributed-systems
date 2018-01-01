import pickle
from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
from common import __MSG_FIELD_SEP, __REQ_REG_USER, __REQ_GET_GAMES, \
    __REQ_CREATE_GAME, __REQ_ADD_PLAYER_TO_GAMEROOM, __REQ_MAKE_MOVE, \
    __REQ_INIT_GAME, __MSG_END, __RSP_OK, __REQ_CONNECT_SERVER_PORT, __RSP_GAME_FULL_ERROR, __REQ_GET_STATE, \
    __REQ_REMOVE_PLAYER, __REQ_REMOVE_PLAYER_LOBBY
import logging

# Setup logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

__USER_ID = None
__CURRENT_GAME_ID = None


def connect_server(server_port):
    """
    Connects server port and returns socket
    :param server_port: port to connect
    :return: socket
    """
    server = ('127.0.0.1', server_port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(server)
    sock.send("")
    return sock


def reg_user(username, server_port):
    """
    Request for registering user
    :param username: Nickname
    :param server_port: port to connect
    :return: user_id
    """
    global __USER_ID
    sock = connect_server(server_port)

    sock.send(__REQ_REG_USER + __MSG_FIELD_SEP + username.encode("utf-8"))
    resp = sock.recv(1024)

    LOG.debug("Response is " + str(resp))
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        LOG.error("Something went wrong with registering the user")
    __USER_ID = resp
    sock.shutdown(SHUT_WR)
    sock.close()
    return __USER_ID


def req_get_games(server_port):
    """
    Request for getting gamerooms information (lobby)
    :param server_port: port to connect
    :return: list of tuples containing information of game rooms[(room_id, num players, max players)]
    """
    sock = connect_server(server_port)
    sock.send(__REQ_GET_GAMES + __MSG_FIELD_SEP)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        LOG.error("Something went wrong while trying to fetch existing games")
    sock.shutdown(SHUT_WR)
    sock.close()
    resp = pickle.loads(resp)
    return resp


def req_create_game(player_id, max_players, server_port):
    """
    Request for creating game
    :param player_id: client's player_id
    :param max_players: number of maximum players in the game room
    :param server_port: port to connect
    :return: created game id
    """
    global __CURRENT_GAME_ID
    sock = connect_server(server_port)
    sock.send(__REQ_CREATE_GAME + __MSG_FIELD_SEP + player_id + __MSG_FIELD_SEP + str(max_players))
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        LOG.error("Something went wrong while trying to create game")

    sock.shutdown(SHUT_WR)
    sock.close()
    __CURRENT_GAME_ID, state = resp.split(__MSG_FIELD_SEP, 1)
    state = pickle.loads(state)
    return __CURRENT_GAME_ID, state


def req_make_move(player_id, game_id, x_coord, y_coord, val, server_port):
    """
    Request for making move on sudoku table
    :param player_id: client's player_id
    :param game_id: current game id
    :param x_coord: x coordinate on sudoku board
    :param y_coord: y coordinate on sudoku board
    :param val: value to insert to the cell
    :param server_port: port to connect
    :return: state object which is [board, [(name, score)]]
    """
    sock = connect_server(server_port)
    sock.send(__REQ_MAKE_MOVE + __MSG_FIELD_SEP + str(player_id) + __MSG_FIELD_SEP + str(game_id) + __MSG_FIELD_SEP +
              str(x_coord) + __MSG_FIELD_SEP + str(y_coord) + __MSG_FIELD_SEP + str(val))

    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        LOG.error("Something went wrong while trying to bust a move")
    state = pickle.loads(resp)
    sock.shutdown(SHUT_WR)
    sock.close()
    return state


def req_join_game(player_id, game_id, server_port):
    """
    Request for joining game
    :param player_id: player uid
    :param game_id: game uid which we want to join
    :param server_port: server port to handle the conenction
    :return: state object which is [board, [(name, score)]]
    """
    sock = connect_server(server_port)
    sock.send(__REQ_ADD_PLAYER_TO_GAMEROOM + __MSG_FIELD_SEP + player_id + __MSG_FIELD_SEP + game_id)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)

    if header == __RSP_OK:
        state = pickle.loads(resp)
        sock.shutdown(SHUT_WR)
        sock.close()
        return state
    elif header == __RSP_GAME_FULL_ERROR:
        LOG.info("The chosen game room is full!")
        sock.shutdown(SHUT_WR)
        sock.close()
        return False
    else:
        LOG.error("Something went wrong while trying to join the game room")

    sock.shutdown(SHUT_WR)
    sock.close()
    return False


def req_get_state(game_id, server_port):
    """
    Request to get game state
    :param game_id: game uid
    :param server_port: port to connect
    :return: state object which is [board, [(name, score)]]
    """
    sock = connect_server(server_port)
    sock.send(__REQ_GET_STATE + __MSG_FIELD_SEP + game_id)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header == __RSP_OK:
        state = pickle.loads(resp)
        sock.shutdown(SHUT_WR)
        sock.close()
        return state


def req_remove_player(game_id, player_id, server_port):
    """
    Request to remove player from game room
    :param game_id: game id
    :param player_id: player id
    :param server_port: server port
    :return: None
    """
    sock = connect_server(server_port)
    sock.send(__REQ_REMOVE_PLAYER + __MSG_FIELD_SEP + game_id + __MSG_FIELD_SEP + player_id)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header == __RSP_OK:
        return


def req_remove_player_lobby(player_id, server_port):
    """
    Removes player from the lobby and overall players list.
    :param player_id: player id
    :param server_port: port to connect
    :return: None
    """
    sock = connect_server(server_port)
    sock.send(__REQ_REMOVE_PLAYER_LOBBY + __MSG_FIELD_SEP + player_id)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header == __RSP_OK:
        return
