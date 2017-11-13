import pickle
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
from common import __MSG_FIELD_SEP, __REQ_REG_USER, __REQ_GET_GAMES, \
    __REQ_CREATE_GAME, __REQ_ADD_PLAYER_TO_GAMEROOM, __REQ_MAKE_MOVE, \
    __REQ_INIT_GAME, __MSG_END, __RSP_OK, __REQ_CONNECT_SERVER_PORT

__USER_ID = None
__CURRENT_GAME_ID = None


def connect_server(server_port):
    server = ('127.0.0.1', server_port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(server)
    sock.send("")
    return sock


def reg_user(username, server_port):
    sock = connect_server(server_port)
    sock.send(__REQ_REG_USER + __MSG_FIELD_SEP + username)
    resp = sock.recv(1024)

    print(resp)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        print("miskit laks reg useris katki")

    __USER_ID = resp
    sock.shutdown(SHUT_WR)
    sock.close()
    return __USER_ID


# TODO: handle error reg user


def req_get_games(server_port):
    print "joudsin get gamesi"
    sock = connect_server(server_port)
    sock.send(__REQ_GET_GAMES + __MSG_FIELD_SEP)
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        print("miskit laks get games katki")
        #         TODO: handle error get games
    sock.shutdown(SHUT_WR)
    sock.close()
    resp = pickle.loads(resp)
    return resp


def req_create_game(player_uid, max_players, server_port):
    sock = connect_server(server_port)
    sock.send(__REQ_CREATE_GAME + __MSG_FIELD_SEP + player_uid + __MSG_FIELD_SEP + str(max_players))
    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        print("miskit laks get games katki")
        #         TODO: handle error create game

    sock.shutdown(SHUT_WR)
    sock.close()
    __CURRENT_GAME_ID = resp
    return __CURRENT_GAME_ID


def req_make_move(player_id, game_id, x_coord, y_coord, val, server_port):
    sock = connect_server(server_port)
    sock.send(__REQ_MAKE_MOVE + __MSG_FIELD_SEP + player_id + __MSG_FIELD_SEP + game_id + __MSG_FIELD_SEP + x_coord +
              __MSG_FIELD_SEP + y_coord + __MSG_FIELD_SEP + val)

    resp = sock.recv(1024)
    header, resp = resp.split(__MSG_FIELD_SEP, 1)
    if header != __RSP_OK:
        print("miskit laks make move katki")
        #         TODO: handle error create game

    scores, board = resp.split(__MSG_FIELD_SEP, 1)
    sock.shutdown(SHUT_WR)
    sock.close()
    return scores, board
