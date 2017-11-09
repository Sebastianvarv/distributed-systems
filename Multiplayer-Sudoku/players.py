
import uuid

class Players:

    def __init__(self):
        self.players = {}

    def reg_player(self, name):
        player_id = uuid.uuid4()
        self.players[player_id] = name
        return player_id

    def get_player_name(self, player_id):
        return self.players[player_id]
    
