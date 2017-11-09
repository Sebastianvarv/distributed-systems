
import uuid

class Game:


    def __init__(self, host_nickname):
        self.solution, self.board = read_solution()
        self.names = {}
        self.scores = {}
        self.add_player(host_nickname)

    def make_move(self, user_id, (x,y), value):
        if valid_move((x,y), value):
            self.scores[user_id] += 1
            return 1
        self.scores[user_id] -= 1
        return 0
            
    def valid_move(self, (x,y), value):
        if solution[x][y] == value:
            return True
        return False
            
    def check_game_won(self, user_id):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True

    def add_player(self, nickname):
        user_id = uuid.uuid4()
        self.names[user_id] = user_id
        self.scores[user_id] = 0

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
