
import uuid
from common import __GAME_STATE_WAIT, __GAME_STATE_PLAY, __GAME_STATE_OVER

def read_solution():
    f = open("solutions.txt", "r")
    solution = [[None]*9 for x in range(0,9)]
    for i in range(9):
        row = f.readline().strip()
        split_row = row.split(" ")
        for j in range(9):
            solution[i][j] = int (split_row[j])
                     
    f.readline()
    
    board = [[None]*9 for x in range(0,9)]
    for i in range(9):
        row = f.readline().strip()
        split_row = row.split(" ")
        for j in range(9):
            board[i][j] = int (split_row[j])
    f.close()

    return solution, board


class Game:

    def __init__(self, max_players):
        self.solution, self.board = read_solution()
        self.scores = {}
        self.max_players = max_players
        self.game_state = 0

    def make_move(self, user_id, x, y, value):
        if self.valid_move(x, y, value):
            self.board[x][y] = value
            self.scores[user_id] += 1
            self.check_game_won()
            return True
        self.scores[user_id] -= 1
        return False
            
    def valid_move(self, x, y, value):
        if self.solution[x][y] == value:
            return True
        return False
            
    def check_game_won(self):
        game_won = True
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    game_won = False
        if game_won:
            self.game_state = 2

    # Add new player if possible - returns True if added, False if not
    def add_player(self, player_id):
        if len(self.scores) < self.max_players:
            self.scores[player_id] = 0
            if len(self.scores) == self.max_players:
                self.game_state = 1
            return True
        return False

    def get_num_players(self):
        return len(self.scores)

    def remove_player(self, player_id):
        self.scores.pop(player_id, None)

    def get_state(self, players):
        names_scores = []
        for uid, score in self.scores.items():
            name = players.get_player_name(uid)
            names_scores.append((name, score))
        return [self.board, names_scores, self.game_state]