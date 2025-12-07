import numpy as np
import random
import json
import os
from datetime import datetime

# Hằng số di chuyển
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class Game2048Env:
    def __init__(self, size=4, seed=None):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.score = 0 
        
        self.game_over = False
        self.total_time = 0
        self._top_score = None 
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False
        self.total_time = 0
        
        self._spawn_tile()
        self._spawn_tile()
        
        self._top_score = None 
        
        return self.get_state()

    def get_state(self):
        return self.board.copy()

    def get_score(self):
        # Trả về số lớn nhất trên bàn cờ
        if self.board.size > 0:
            return int(np.max(self.board))
        return 0

    def get_top_score(self):
        return int(self._top_score) if self._top_score is not None else None

    # --- Spawn & Done functions ---
    def _spawn_tile(self):
        empty = list(zip(*np.where(self.board == 0)))
        if not empty:
            return False
        r, c = random.choice(empty)
        self.board[r, c] = 4 if random.random() < 0.1 else 2
        return True

    def is_done(self):
        if (self.board == 0).any():
            return False
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.board[r, c] == self.board[r, c + 1]:
                    return False
        for r in range(self.size - 1):
            for c in range(self.size):
                if self.board[r, c] == self.board[r + 1, c]:
                    return False
        return True

    # --- Bước di chuyển ---
    def step(self, action):
        assert action in (UP, DOWN, LEFT, RIGHT), "Invalid action"

        prev_board = self.get_state()
        prev_internal_score = self.score 

        if action == LEFT:
            self._move_left()
        elif action == RIGHT:
            self._move_right()
        elif action == UP:
            self._move_up()
        elif action == DOWN:
            self._move_down()

        moved = not np.array_equal(prev_board, self.board)
        reward = self.score - prev_internal_score 

        if moved:
            self._spawn_tile()
        
        done = self.is_done()
        if done:
             self.game_over = True

        info = {"moved": moved}
        return self.get_state(), reward, done, info

    # --- Core logic ---
    def _compress(self, row):
        new = row[row != 0]
        if new.size == 0:
            return np.zeros_like(row)
        zeros = np.zeros(self.size - len(new), dtype=int)
        return np.concatenate([new, zeros])

    def _merge(self, row):
        gained = 0
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                gained += row[i]
                row[i + 1] = 0
        self.score += gained
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

    def _recompute_score(self):
        pass

    # --- SỬA HÀM SAVE/LOAD ---
    def save_game(self, filename, ai_mode=False): # Thêm tham số ai_mode
        if not filename.lower().endswith('.json'):
            filename = filename + '.json'
        
        display_score = int(np.max(self.board)) if self.board.size > 0 else 0
        
        data = {
            "board": self.board.tolist(),
            "score": int(self.score),
            "display_score": display_score,
            "top_score": int(self._top_score) if self._top_score is not None else None,
            "total_time": self.total_time,
            "ai_mode": ai_mode, # Lưu chế độ chơi
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

        board_list = data['board']
        arr = np.array(board_list, dtype=int)
        if arr.shape != (self.size, self.size):
            raise ValueError(f"Saved board has wrong shape {arr.shape}, expected {(self.size, self.size)}")

        self.board = arr
        self.score = int(data.get('score', 0))
        self.total_time = data.get('total_time', 0)
        self.game_over = self.is_done()

        if 'top_score' in data and data['top_score'] is not None:
            try:
                self._top_score = int(data['top_score'])
            except:
                self._top_score = None
        else:
            self._top_score = None
        
        # Hàm load_game của env chỉ load dữ liệu bàn cờ
        # Việc đọc ai_mode sẽ do IntroScreen xử lý khi load file
        
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
            "total_time": self.total_time,
            "top_score": int(self._top_score) if self._top_score is not None else None
        }

    def load_from_dict(self, data):
        if 'board' not in data:
            raise ValueError("Missing 'board' key")
        arr = np.array(data['board'], dtype=int)
        if arr.shape != (self.size, self.size):
            raise ValueError("Wrong board shape")
            
        self.board = arr
        self.score = int(data.get('score', 0))
        self.total_time = data.get('total_time', 0)
        self._top_score = int(data['top_score']) if data.get('top_score') is not None else None
        self.game_over = self.is_done()
        return self.get_state()
