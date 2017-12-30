import logging
import Pyro4
from argparse import ArgumentParser

# ---------- Logging ----------
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()
# LOG.setLevel(logging.INFO)

# ---------- Constants ----------
__NAME = "CompetitiveSudoku"
__VER = "0.0.2"
__DESC = "Simple Competitive Sudoku Game"


def __info():
    return "%s v%s - %s" % (__NAME, __VER, __DESC)


@Pyro4.expose
class User(object):
    """
    User class, the main communication vector between the front-end and back-end
    """

    def __init__(self, name):
        self.name = name


@Pyro4.expose
class CompetitiveSudoku(object):
    """
    Main server class, complete functions and necessity to be determined
    """

    def __init__(self):
        self.users = {}

    def register(self, name):
        user = User(name)
        self.users[name] = user
        user_uri = daemon.register(user)

        return str(user_uri)


if __name__ == "__main__":
    parser = ArgumentParser(description=__info(), version=__VER)

    parser.add_argument("-mc", "--multicast", help="Multicast group URI", default="239.1.1.1")
    parser.add_argument("-mcp", "--multicastport", help="Multicast group port", default=7778)
    parser.add_argument("-h", "--host", help="Pyro host URI", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="Pyro host port", default=7777)

    args = parser.parse_args()

    # Make a Pyro daemon
    daemon = Pyro4.Daemon(host=args.host, port=args.port)

    # Register the Sudoku game with Pyro
    sudoku = CompetitiveSudoku()
    uri = daemon.register(sudoku)

    LOG.info("The game URI is: " + str(uri))

    # TODO: Do the multicast/broadcast for the server
