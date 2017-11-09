
import uuid

class Players:

    def __init__(self):
        self.players = {}

    def reg_player(self, name):
        player_id = uuid.uuid4()
        self.players[player_id] = name

    
