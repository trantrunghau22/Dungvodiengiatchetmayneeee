import numpy as np
import random
import json
import os
from datetime import datetime
#Hang so di chuyen
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class Game2048Env:
    def __init__(self, size=4, seed=None):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.score = 0
        self._top_score = None
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
#Thuat toan chay tinh
    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self._spawn_tile()
        self._spawn_tile()
        self._recompute_score()
        self._top_score = None
        return self.get_state()

    def get_state(self):
        return self.board.copy()

    def get_score(self):
        #Score la o cao nhat
        return int(self.score)

    def get_top_score(self):
        #Return topscore from saved or lastest files
        return int(self._top_score) if self._top_score is not None else None

    #Spawn & Done fuctions
    def _spawn_tile(self):
        #Spawn o 2/4 randomly theo ty le 90% 10%
        empty = list(zip(*np.where(self.board == 0)))
        if not empty:
            return False
        r, c = random.choice(empty)
        self.board[r, c] = 4 if random.random() < 0.1 else 2
        return True

    def is_done(self):
        #Tra ve gia tri True neu khong con o nao bang 0
        if (self.board == 0).any():
            return False
        #Check hang ngang
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.board[r, c] == self.board[r, c + 1]:
                    return False
        #Check hang doc
        for r in range(self.size - 1):
            for c in range(self.size):
                if self.board[r, c] == self.board[r + 1, c]:
                    return False
        return True

    #Buoc di chuyen
    def step(self, action):
        assert action in (UP, DOWN, LEFT, RIGHT), "Invalid action"

        prev_board = self.get_state()
        prev_max = int(self.score)

        #Buoc di
        if action == LEFT:
            self._move_left()
        elif action == RIGHT:
            self._move_right()
        elif action == UP:
            self._move_up()
        elif action == DOWN:
            self._move_down()

        moved = not np.array_equal(prev_board, self.board)

        #chi spawn 1 o neu bang thay doi
        if moved:
            self._spawn_tile()

        #Cap nhat so diem
        self._recompute_score()
        reward = int(self.score) - prev_max

        done = self.is_done()
        info = {"moved": moved}
        return self.get_state(), reward, done, info

    #Thuat toan quan trong cua game
    def _compress(self, row):
        new = row[row != 0]
        if new.size == 0:
            return np.zeros_like(row)
        zeros = np.zeros(len(row) - len(new), dtype=int)
        return np.concatenate([new, zeros])

    def _merge(self, row):
        gained = 0
        for i in range(len(row) - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                gained += row[i]
                row[i + 1] = 0
        return row

    def _move_left(self):
        for r in range(self.size):
            row = self.board[r].copy()
            row = self._compress(row)
            row = self._merge(row)
            row = self._compress(row)
            self.board[r] = row

    def _move_right(self):
        self.board = np.fliplr(self.board)
        self._move_left()
        self.board = np.fliplr(self.board)

    def _move_up(self):
        self.board = self.board.T
        self._move_left()
        self.board = self.board.T

    def _move_down(self):
        self.board = self.board.T
        self._move_right()
        self.board = self.board.T

    #Diem so
    def _recompute_score(self):
#empty thi tra 0 diem, khong thi cap nhat diem gan nhat
        if self.board.size == 0:
            self.score = 0
        else:
            self.score = int(self.board.max()) if (self.board != 0).any() else 0

    #Ham save/load game 
    def save_game(self, filename):
        if not filename.lower().endswith('.json'):
            filename = filename + '.json'
        data = {
            "board": self.board.tolist(),
            "score": int(self.score),
            "top_score": int(self._top_score) if self._top_score is not None else None,
            "saved_at": datetime.utcnow().isoformat() + "Z"
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return os.path.abspath(filename)

    def load_game(self, filename):
        if not os.path.exists(filename):
            if os.path.exists(filename + '.json'):
                filename = filename + '.json'
            else:
                raise FileNotFoundError(f"No such file: {filename}")

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'board' not in data:
            raise ValueError("Invalid save file: missing 'board' key")

        #Tai board
        board_list = data['board']
        arr = np.array(board_list, dtype=int)
        if arr.shape != (self.size, self.size):
            raise ValueError(f"Saved board has wrong shape {arr.shape}, expected {(self.size, self.size)}")

        self.board = arr
        self._recompute_score()

        #Co top score thi load 
        if 'top_score' in data and data['top_score'] is not None:
            try:
                self._top_score = int(data['top_score'])
            except:
                self._top_score = None
        else:
            self._top_score = None

        return self.get_state()

    def update_top_score(self, top_score):
        try:
            self._top_score = int(top_score)
        except:
            self._top_score = None
    def export_to_dict(self):
        return {
            "board": self.board.tolist(),
            "score": int(self.score),
            "top_score": int(self._top_score) if self._top_score is not None else None
        }

    def load_from_dict(self, data):
        if 'board' not in data:
            raise ValueError("Missing 'board' key")
        arr = np.array(data['board'], dtype=int)
        if arr.shape != (self.size, self.size):
            raise ValueError("Wrong board shape")
        self.board = arr
        self._recompute_score()
        self._top_score = int(data['top_score']) if data.get('top_score') is not None else None
        return self.get_state()
