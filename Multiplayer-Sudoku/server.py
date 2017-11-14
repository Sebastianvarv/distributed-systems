import threading
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM
import pickle
import sys

from games import Games
from players import Players

__PLAYERS = Players()
__GAMES = Games()

from common import __MSG_FIELD_SEP, __REQ_REG_USER, __REQ_GET_GAMES, \
    __REQ_CREATE_GAME, __REQ_ADD_PLAYER_TO_GAMEROOM, __REQ_MAKE_MOVE, \
    __REQ_INIT_GAME, __RSP_OK, __REQ_CONNECT_SERVER_PORT, __RSP_GAME_FULL_ERROR, __REQ_GET_STATE, __REQ_REMOVE_PLAYER, \
    __REQ_REMOVE_PLAYER_LOBBY


def parse_msg(message, client_sock):
    """
    Method for parsing message and sending response to client
    :param message: message received by server
    :param client_sock: Client socket
    :return: None
    """
    msg_header, message = message.split(__MSG_FIELD_SEP, 1)
    if msg_header == __REQ_REG_USER:
        # Arguments: nick_name
        # Returns: Player uid
        username = message
        uid = str(__PLAYERS.reg_player(username))
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP + uid)

    elif msg_header == __REQ_GET_GAMES:
        # Returns all games
        print("Get games", message)
        resp = __GAMES.get_tuple()
        resp = pickle.dumps(resp)
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP + resp)

    elif msg_header == __REQ_CREATE_GAME:
        # Creates game and returns it's state
        print("Create game", message)
        player_uid, max_players = message.split(__MSG_FIELD_SEP, 1)
        game_uid = __GAMES.create_game(max_players)
        game = __GAMES.get_game(game_uid)
        game.add_player(player_uid)

        state = pickle.dumps(game.get_state(__PLAYERS))
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP + game_uid + __MSG_FIELD_SEP + state)

    elif msg_header == __REQ_ADD_PLAYER_TO_GAMEROOM:
        # Adds player to selected game room
        print("Add player to gameroom", message)
        player_id, game_id = message.split(__MSG_FIELD_SEP, 1)
        game = __GAMES.get_game(game_id)

        if len(game.scores) != game.max_players:
            game.add_player(player_id)
            state = pickle.dumps(game.get_state(__PLAYERS))
            client_sock.send(__RSP_OK + __MSG_FIELD_SEP + state)
        else:
            client_sock.send(__RSP_GAME_FULL_ERROR + __MSG_FIELD_SEP)

    elif msg_header == __REQ_MAKE_MOVE:
        # Makes move on selected board
        print("Making a move", message)
        player_id, game_id, x_coord, y_coord, val = message.split(__MSG_FIELD_SEP, 4)
        game = __GAMES.get_game(game_id)
        game.make_move(player_id, int(x_coord), int(y_coord), int(val))
        state = pickle.dumps(game.get_state(__PLAYERS))
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP + state)

    elif msg_header == __REQ_GET_STATE:
        # Returns current game state
        print("Get state", message)
        game_id = message
        game = __GAMES.get_game(game_id)
        state = pickle.dumps(game.get_state(__PLAYERS))
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP + state)

    elif msg_header == __REQ_REMOVE_PLAYER:
        # Removes player form the game room
        print("Remove player from game")
        game_id, player_id = message.split(__MSG_FIELD_SEP, 1)
        __GAMES.remove_player_from_game(game_id, player_id)
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP)

    elif msg_header == __REQ_REMOVE_PLAYER_LOBBY:
        # Remove player from the lobby
        print("Remove player from lobby")
        player_id = message
        __PLAYERS.remove_player(player_id)
        client_sock.send(__RSP_OK + __MSG_FIELD_SEP)

    elif msg_header == __REQ_CONNECT_SERVER_PORT:
        client_sock.send(__RSP_OK)


if __name__ == '__main__':
    parser = ArgumentParser(description="Sudoku server")

    parser.add_argument('-p', '--port',
                        help='Server port',
                        required=False,
                        default=7000)

    args = parser.parse_args()
    port = args.port

    # Creating a TCP/IP socket
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(10)

    print "Server started on port: " + str(port)
    while True:
        try:
            client_socket, source = server_socket.accept()
            msg = client_socket.recv(1024)

            print "Server received a message:" + msg
            msg_parse_thread = threading.Thread(parse_msg(msg, client_socket))
            msg_parse_thread.start()


        except KeyboardInterrupt:
            sys.exit()
