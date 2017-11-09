from clientpornoo import main
from client import *

if __name__ == "__main__":
    port, nickname = main()
    print(port, nickname)

    sock = connect_server(port)
    reg_user(sock, nickname)

    games = req_get_games(sock)

    # (room_id, num players, max players)
    games = [(1, 3, 4), (2, 1, 5), (3, 3, 3)]
    print(games)
