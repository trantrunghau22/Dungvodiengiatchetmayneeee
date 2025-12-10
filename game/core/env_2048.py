import numpy as np
import random
import json
#Cơ chế lưu file
import os
from datetime import datetime

class Game2048Env:
    def __init__(self, size=4):
        self.size = size
        self.score = 0
        self.board = np.zeros((size, size), dtype=int)
        self.game_over = False
        self.top_score = 0
        self.reset()

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False
        self.spawn_tile()
        self.spawn_tile()
        return self.board

    def spawn_tile(self):
        empty = list(zip(*np.where(self.board == 0)))
        if not empty: return False
        r, c = random.choice(empty)
        # spawn Ớt (1) nếu trên bàn cờ đã có ô >= 128
        max_tile = np.max(self.board)
        rand = random.random()
        if max_tile >= 128:
            # Khi đã đạt mốc 128:
            # 1% ra Ớt (1)
            # 10% ra 4
            # 89% ra 2
            if rand < 0.01: val = 1
            elif rand < 0.11: val = 4 # 0.01 + 0.10
            else: val = 2
        else:
            # Khi chưa đạt mốc 128: Spawn như thường
            # 10% ra 4
            # 90% ra 2
            if rand < 0.10: val = 4
            else: val = 2
        
        self.board[r, c] = val
        return True

    def step(self, action):
        # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        prev_board = self.board.copy()
        
        if action == 2: self._move_left()
        elif action == 3: self._move_right()
        elif action == 0: self._move_up()
        elif action == 1: self._move_down()
        
        moved = not np.array_equal(prev_board, self.board)
        if moved:
            self.spawn_tile()
        
        if self._is_done():
            self.game_over = True
            
        return self.board, self.score, self.game_over, moved

    #LOGIC GỘP KHI CÓ ƯỚT CHUÔNG
    def _merge_row(self, row):
        # B1: Nén số về bên trái (loại bỏ số 0)
        new_row = row[row != 0]
        merged_row = []
        skip = False
        
        i = 0
        while i < len(new_row):
            val = new_row[i]
            if i + 1 < len(new_row):
                next_val = new_row[i+1]
                #CASE 1:ra 256 dọn dẹp Ớt (1)
                if (val == 256 and next_val == 1) or (val == 1 and next_val == 256):
                    self.score += 256 
                    i += 2 # Bỏ qua cả 2 ô
                    continue
                #CASE 2: Ớt (1) không gộp với bất kỳ ai
                elif val == 1 or next_val == 1:
                    merged_row.append(val)
                    i += 1
                    continue
                # CASE 3: Gộp bình thường (2+2, 4+4)
                elif val == next_val:
                    merged_val = val * 2
                    merged_row.append(merged_val)
                    self.score += merged_val
                    i += 2
                    continue
            merged_row.append(val)
            i += 1
            
        #Điền thêm số 0 cho đủ ô 
        res = np.array(merged_row, dtype=int)
        zeros = np.zeros(self.size - len(res), dtype=int)
        return np.concatenate([res, zeros])

    def _move_left(self):
        for r in range(self.size):
            self.board[r] = self._merge_row(self.board[r])

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

    def _is_done(self):
        if (self.board == 0).any(): return False
        #Kiểm tra còn nước đi không
        for r in range(self.size):
            for c in range(self.size - 1):
                v1, v2 = self.board[r, c], self.board[r, c+1]
                if v1 == v2 and v1 != 1: return False #Cùng số (ko phải ớt) -> gộp đc
                if (v1==1 and v2==512) or (v1==512 and v2==1): return False
        for r in range(self.size - 1):
            for c in range(self.size):
                v1, v2 = self.board[r, c], self.board[r+1, c]
                if v1 == v2 and v1 != 1: return False
                if (v1==1 and v2==512) or (v1==512 and v2==1): return False
        return True
    #Cơ chế save load game
    def save_game(self, filename, mode='Normal'):
        data = {
            "board": self.board.tolist(),
            "score": self.score,
            "mode": mode,
            "date": str(datetime.now())
        }
        if not filename.endswith('.json'): filename += ''
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_game(self, filename):
        if not os.path.exists(filename): return False
        with open(filename, 'r') as f:
            data = json.load(f)
            self.board = np.array(data['board'])
            self.score = data['score']
        return True