from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM

import sys

from common import __MSG_FIELD_SEP, __REQ_REG_USER, __REQ_GET_GAMES, \
    __REQ_CREATE_GAME, __REQ_ADD_PLAYER_TO_GAMEROOM, __REQ_MAKE_MOVE, \
    __REQ_INIT_GAME

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

    while True:
        try:
            client_socket, source = server_socket.accept()
            msg = client_socket.recv(1024)
            msg_header, msg = msg.split(__MSG_FIELD_SEP, 1)

            if msg_header == __REQ_REG_USER:
                print("Register user", msg)
                #     TODO: reg user
                username = msg



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
        except KeyboardInterrupt:
            sys.exit()
