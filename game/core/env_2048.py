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
        
        # Biến trạng thái game và thời gian (từ Đoạn 1 & board.py)
        self.game_over = False
        self.total_time = 0
        
        # Biến quản lý điểm cao nhất (từ Đoạn 2)
        self._top_score = None 
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    def reset(self):
        # Đặt lại trạng thái game
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False
        self.total_time = 0
        
        # Sinh 2 ô khởi đầu
        self._spawn_tile()
        self._spawn_tile()
        
        # Trong Đoạn 2 có _recompute_score(), nhưng vì score là tổng điểm gộp, 
        # nên việc đặt score = 0 ở đây là chính xác.
        # Tuy nhiên, nếu bạn muốn score là ô lớn nhất (như Đoạn 2 định nghĩa), 
        # thì cần gọi _recompute_score() sau khi spawn. 
        # Tôi sẽ dùng định nghĩa score là TỔNG ĐIỂM GỘP (như Đoạn 1) và score max tile (như Đoạn 2 cho _recompute_score),
        # và cho rằng `board.py` dùng `self.env.get_score()` là điểm hiển thị (max tile).

        # Đảm bảo top score được reset/set giá trị mặc định cho game mới
        self._top_score = None 
        
        return self.get_state()

    def get_state(self):
        return self.board.copy()

    # --- Các hàm Get Score ---
    def get_score(self):
        # Trả về ô lớn nhất (theo logic _recompute_score của Đoạn 2)
        # Hoặc tổng điểm gộp (nếu dùng score tích lũy trong _merge)
        # Để thống nhất với Đoạn 2 và tránh xung đột với Reward, ta sẽ dùng self.board.max()
        if (self.board != 0).any():
            return int(self.board.max())
        return 0

    def get_top_score(self):
        # Return topscore from saved or lastest files
        return int(self._top_score) if self._top_score is not None else None

    # --- Spawn & Done functions ---
    def _spawn_tile(self):
        # Spawn ô 2/4 randomly theo tỷ lệ 90% 10%
        empty = list(zip(*np.where(self.board == 0)))
        if not empty:
            return False
        r, c = random.choice(empty)
        self.board[r, c] = 4 if random.random() < 0.1 else 2
        return True

    def is_done(self):
        # Kiểm tra xem game đã kết thúc (thua) hay chưa
        if (self.board == 0).any():
            return False
        # Check hàng ngang
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.board[r, c] == self.board[r, c + 1]:
                    return False
        # Check hàng dọc
        for r in range(self.size - 1):
            for c in range(self.size):
                if self.board[r, c] == self.board[r + 1, c]:
                    return False
        return True

    # --- Bước di chuyển (Step for RL) ---
    def step(self, action):
        assert action in (UP, DOWN, LEFT, RIGHT), "Invalid action"

        prev_board = self.get_state()
        
        # Đoạn 1: Lưu self.score trước (tổng điểm gộp)
        # Đoạn 2: Lưu self.score trước (ô lớn nhất)
        # Dùng logic của Đoạn 1 để tính Reward (điểm tăng thêm)
        prev_score = self.score # self.score là tổng điểm gộp (chỉ được cập nhật trong _merge)

        # Buốc di
        if action == LEFT:
            self._move_left()
        elif action == RIGHT:
            self._move_right()
        elif action == UP:
            self._move_up()
        elif action == DOWN:
            self._move_down()

        moved = not np.array_equal(prev_board, self.board)
        
        # Reward là điểm GỘP được cộng thêm vào self.score trong _merge
        reward = self.score - prev_score 

        # Chỉ spawn 1 ô nếu bàn thay đổi
        if moved:
            self._spawn_tile()
        
        # Cập nhật trạng thái game over
        done = self.is_done()
        if done:
             self.game_over = True # Dùng biến trạng thái của Đoạn 1

        info = {"moved": moved}
        return self.get_state(), reward, done, info

    # --- Core logic của game (Giữ lại logic _move, _compress, _merge của Đoạn 1) ---
    def _compress(self, row):
        new = row[row != 0]
        if new.size == 0:
            return np.zeros_like(row)
        zeros = np.zeros(self.size - len(new), dtype=int)
        return np.concatenate([new, zeros])

    def _merge(self, row):
        # Tính toán điểm gộp được trong bước này
        gained = 0
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                gained += row[i]
                row[i + 1] = 0
        
        # Cập nhật TỔNG điểm gộp của game
        self.score += gained
        return row

    def _move_left(self):
        for r in range(self.size):
            # Lưu ý: Đoạn 1 dùng row = self.board[r] (tham chiếu trực tiếp)
            # Đoạn 2 dùng row = self.board[r].copy() (tạo bản sao)
            # Để đảm bảo an toàn khi xử lý mảng (dù _compress tạo bản sao mới) 
            # và thống nhất với Đoạn 2, ta nên dùng .copy() khi trích xuất.
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

    # --- Hàm Score tính toán lại (từ Đoạn 2, Dùng để hỗ trợ Load/Export) ---
    def _recompute_score(self):
        # Hàm này dùng để đồng bộ self.score (tổng điểm gộp) hoặc max tile
        # Tuy nhiên, trong Đoạn 2, nó được dùng để gán self.score = max_tile.
        # Để tránh xung đột với self.score (tổng điểm gộp) dùng cho Reward, 
        # ta giữ nguyên logic _recompute_score của Đoạn 2 nhưng không gọi nó trong step, 
        # chỉ dùng cho Load/Export nếu cần self.score là max_tile.
        # Vì board.py dùng self.env.get_score(), ta sẽ dùng self.board.max() trong get_score()
        # và giữ self.score (tổng điểm gộp) để tính Reward.
        if self.board.size == 0:
            # Không cần gán self.score = 0 vì nó đã được cập nhật trong _merge
            pass
        else:
            # Nếu cần, bạn có thể gán self.score = int(self.board.max()) nếu muốn score là ô lớn nhất.
            pass


    # --- Hàm save/load game (từ Đoạn 2, Bổ sung total_time) ---
    def save_game(self, filename):
        if not filename.lower().endswith('.json'):
            filename = filename + '.json'
        data = {
            "board": self.board.tolist(),
            # Lưu self.score là TỔNG điểm gộp (cho mục đích RL/Load chính xác)
            "score": int(self.score), 
            "top_score": int(self._top_score) if self._top_score is not None else None,
            "total_time": self.total_time, # Bổ sung thời gian
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

        # Tải board
        board_list = data['board']
        arr = np.array(board_list, dtype=int)
        if arr.shape != (self.size, self.size):
            raise ValueError(f"Saved board has wrong shape {arr.shape}, expected {(self.size, self.size)}")

        self.board = arr
        
        # Tải score (tổng điểm gộp)
        self.score = int(data.get('score', 0))
        
        # Tải total_time và game_over
        self.total_time = data.get('total_time', 0)
        self.game_over = self.is_done() # Xác định game over bằng cách kiểm tra trạng thái

        # Quản lý top score
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
        
        # Cập nhật trạng thái game over sau khi load
        self.game_over = self.is_done()
        
        return self.get_state()
