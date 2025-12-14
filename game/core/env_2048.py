import numpy as np
import random
import json
import os
import glob
from datetime import datetime

class Game2048Env:
    def __init__(self, size=4):
        self.size = size
        self.score = 0
        self.board = np.zeros((size, size), dtype=int)
        self.game_over = False
        self.top_score = 0
        
        # [QUAN TRỌNG] Load top score ngay khi khởi tạo
        self.load_global_best_score()
        
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
        max_tile = np.max(self.board)
        rand = random.random()
        if max_tile >= 128:
            if rand < 0.01: val = 1
            elif rand < 0.11: val = 4 
            else: val = 2
        else:
            if rand < 0.10: val = 4
            else: val = 2
        self.board[r, c] = val
        return True

    def step(self, action):
        prev_board = self.board.copy()
        if action == 2: self._move_left()
        elif action == 3: self._move_right()
        elif action == 0: self._move_up()
        elif action == 1: self._move_down()
        
        moved = not np.array_equal(prev_board, self.board)
        if moved: self.spawn_tile()
        if self._is_done(): self.game_over = True
        return self.board, self.score, self.game_over, moved

    def _merge_row(self, row):
        new_row = row[row != 0]
        merged_row = []
        i = 0
        while i < len(new_row):
            val = new_row[i]
            if i + 1 < len(new_row):
                next_val = new_row[i+1]
                if (val == 256 and next_val == 1) or (val == 1 and next_val == 256):
                    self.score += 256; i += 2; continue
                elif val == 1 or next_val == 1:
                    merged_row.append(val); i += 1; continue
                elif val == next_val:
                    merged_val = val * 2
                    merged_row.append(merged_val); self.score += merged_val; i += 2; continue
            merged_row.append(val); i += 1
        res = np.array(merged_row, dtype=int)
        zeros = np.zeros(self.size - len(res), dtype=int)
        return np.concatenate([res, zeros])

    def _move_left(self):
        for r in range(self.size): self.board[r] = self._merge_row(self.board[r])
    def _move_right(self):
        self.board = np.fliplr(self.board); self._move_left(); self.board = np.fliplr(self.board)
    def _move_up(self):
        self.board = self.board.T; self._move_left(); self.board = self.board.T
    def _move_down(self):
        self.board = self.board.T; self._move_right(); self.board = self.board.T

    def _is_done(self):
        if (self.board == 0).any(): return False
        for r in range(self.size):
            for c in range(self.size - 1):
                v1, v2 = self.board[r, c], self.board[r, c+1]
                if v1 == v2 and v1 != 1: return False
                if (v1==1 and v2==512) or (v1==512 and v2==1): return False
        for r in range(self.size - 1):
            for c in range(self.size):
                v1, v2 = self.board[r, c], self.board[r+1, c]
                if v1 == v2 and v1 != 1: return False
                if (v1==1 and v2==512) or (v1==512 and v2==1): return False
        return True

    def get_saved_files(self): return sorted(glob.glob("save_*.json"))

    def load_global_best_score(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f: self.top_score = int(f.read())
            else: self.top_score = 0
        except: self.top_score = 0
        return self.top_score

    def save_global_best_score(self):
        with open("highscore.txt", "w") as f: f.write(str(int(self.top_score)))

    def save_game(self, filename, mode='Normal'):
        if not filename.startswith("save_"): filename = "save_" + filename
        if not filename.endswith(".json"): filename += ".json"
        
        if self.score > self.top_score:
            self.top_score = self.score
            self.save_global_best_score()

        data = {
            "board": self.board.tolist(),
            "score": int(self.score),
            "mode": mode,
            "game_over": self.game_over,
            "date": str(datetime.now())
        }
        with open(filename, 'w') as f: json.dump(data, f)

    def load_game(self, filename):
        if not os.path.exists(filename): return False
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.board = np.array(data['board'])
                self.score = int(data['score'])
                self.game_over = data.get('game_over', False)
                self.load_global_best_score()
            return True
        except: return False

    def delete_game(self, filename):
        try:
            if os.path.exists(filename): os.remove(filename); return True
        except: pass
        return False

    def rename_game(self, old_name, new_name):
        if not new_name.strip(): return False
        if not old_name.startswith("save_"): old_name = "save_" + old_name
        if not old_name.endswith(".json"): old_name += ".json"
        if not new_name.startswith("save_"): new_name = "save_" + new_name
        if not new_name.endswith(".json"): new_name += ".json"
        if os.path.exists(new_name): return False
        try: os.rename(old_name, new_name); return True
        except: return False