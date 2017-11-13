
import uuid
from game import Game

class Games:

    def __init__(self):
        self.games = {}

    def create_game(self, max_players):
        game_id = str(uuid.uuid4())
        new_game = Game(max_players)
        self.games[game_id] = new_game
        return game_id

    def get_game(self, game_id):
        return self.games[game_id]

    def get_tuple(self):
        '''
        Returns tuple representation of games,
        :return: (room_id, num_players, max_players)
        '''
        output = []
        # (room_id, num players, max players)
        for uid, game in self.games.items():
            elem = tuple((uid, len(game.scores), game.max_players))
            print elem
            output.append(elem)
        return output
