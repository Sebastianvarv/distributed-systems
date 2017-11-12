
import uuid

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
        self.game_started = False

    def make_move(self, user_id, x, y, value):
        if self.valid_move(x, y, value):
            self.scores[user_id] += 1
            return 1
        self.scores[user_id] -= 1
        return 0
            
    def valid_move(self, x, y, value):
        if self.solution[x][y] == value:
            return True
        return False
            
    def check_game_won(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True

    def add_player(self, player_id):
        self.scores[player_id] = 0
        if len(self.scores) == self.max_players:
            self.game_started = True

    def get_num_players(self):
        return len(self.scores)
