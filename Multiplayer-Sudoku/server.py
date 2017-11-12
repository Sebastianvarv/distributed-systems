from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM

import sys

from players import Players

__PLAYERS = Players()

from common import __MSG_FIELD_SEP, __REQ_REG_USER, __REQ_GET_GAMES, \
    __REQ_CREATE_GAME, __REQ_ADD_PLAYER_TO_GAMEROOM, __REQ_MAKE_MOVE, \
    __REQ_INIT_GAME, __RSP_OK, __REQ_CONNECT_SERVER_PORT

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

            print "Server sai sonumi:" + msg

            msg_header, msg = msg.split(__MSG_FIELD_SEP, 1)

            if msg_header == __REQ_REG_USER:
                # Arguments: nick_name
                # Returns: Player uid

                print "server sai katte username: " + msg
                username = msg
                uid = str(__PLAYERS.reg_player(username))

                print "server genereeri uid: " + uid

                client_socket.send(__RSP_OK + __MSG_FIELD_SEP + uid)

            elif msg_header == __REQ_GET_GAMES:
                print("Get games", msg)
            elif msg_header == __REQ_CREATE_GAME:
                print("Create game", msg)

            elif msg_header == __REQ_ADD_PLAYER_TO_GAMEROOM:
                print("Add player to gameroom", msg)
            elif msg_header == __REQ_MAKE_MOVE:
                print("Making a mooooove", msg)
            elif msg_header == __REQ_INIT_GAME:
                print("Initialising game", msg)
            elif msg_header == __REQ_CONNECT_SERVER_PORT:
                client_socket.send(__RSP_OK)
        except KeyboardInterrupt:
            sys.exit()
