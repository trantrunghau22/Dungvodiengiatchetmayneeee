import numpy as np
import random
# Import hằng số kích thước từ file settings
# Dấu ".." nghĩa là đi ra ngoài 1 cấp (từ core/ ra game/) rồi vào settings
from ..settings import ROWS, COLS

# Định nghĩa các hành động (action)
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class GameLogic:
   #Chỉ dùng Numpy. 
   # Không biết gì về Pygame, Tile, hay màu sắc.
   # Đây là file mà thư mục rl/ (AI) sẽ import và sử dụng.
    
    def __init__(self):
        self.size = ROWS
        #Cấu trúc dữ liệu board (numpy array)
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False

    #Reset()
    def reset(self):
        """Reset 'Não' về trạng thái ban đầu: bàn trống, 2 ô ngẫu nhiên."""
        self.board.fill(0) # Tạo bàn trống
        self.score = 0
        self.game_over = False
        self.spawn_tile() # Sinh 2 ô ngẫu nhiên
        self.spawn_tile()
        return self.board

    #Nhiệm vụ như tên hàm
    def spawn_tile(self):
        """Thêm số 2 hoặc 4 vào một ô trống trong numpy array."""
        empty_cells = np.argwhere(self.board == 0)
        if len(empty_cells) == 0:
# Hết chỗ
            return False 

        row, col = empty_cells[random.randint(0, len(empty_cells) - 1)]
        self.board[row, col] = 4 if random.random() < 0.1 else 2
        return True

    # Xử lý step(action)
    def step(self, action):
        """
        Thực hiện hành động (UP, DOWN, LEFT, RIGHT).
        Trả về (state, reward, done) - chuẩn cho AI
        state (bàn cờ mới), reward (điểm kiếm được), done (game over?)
        """
        if self.game_over:
            return self.board, 0, self.game_over

        board_before = self.board.copy()
        score_gained = 0
        
        # Xử lý logic di chuyển
        if action == LEFT:
            self.board, score_gained = self._process_all_rows(self.board)
        elif action == RIGHT:
            # Lật -> Trượt Trái -> Lật lại
            flipped = np.fliplr(self.board)
            processed, score_gained = self._process_all_rows(flipped)
            self.board = np.fliplr(processed)
        elif action == UP:
            # Xoay -> Trượt Trái -> Xoay ngược lại
            rotated = np.rot90(self.board)
            processed, score_gained = self._process_all_rows(rotated)
            self.board = np.rot90(processed, -1)
        elif action == DOWN:
            # Xoay -> Trượt Trái -> Xoay ngược lại
            rotated = np.rot90(self.board, -1)
            processed, score_gained = self._process_all_rows(rotated)
            self.board = np.rot90(processed)

        # Cập nhật tổng điểm
        self.score += score_gained
        # Kiểm tra xem bàn cờ có thay đổi không
        changed = not np.array_equal(board_before, self.board)
        
        if changed:
            self.spawn_tile()
           self.game_over = self.is_game_over()
        
        # Trả về state (bàn cờ), reward (điểm vừa kiếm), done (kết thúc?)
        return self.board, score_gained, self.game_over

    #Gộp và tính điểm
    def _process_all_rows(self, board):
        #Hàm nội bộ (bên trái)
        new_board = np.zeros_like(board)
        total_score = 0
        for i in range(self.size):
            row, score = self._merge_line(board[i, :])
            new_board[i, :] = row
            total_score += score
        return new_board, total_score

    def _merge_line(self, line):
       #Hàm nội bộ
        score = 0
        
        # Trượt (Slide): [0, 2, 0, 2] -> [2, 2, 0, 0]
        non_zero = line[line != 0] # Lấy các số khác 0
        slide = np.zeros(self.size, dtype=int)
        slide[:len(non_zero)] = non_zero
        
        # Gộp (Merge): [2, 2, 0, 0] -> [4, 0, 0, 0]
        for i in range(self.size - 1):
            if slide[i] == slide[i+1] and slide[i] != 0:
                slide[i] *= 2
                slide[i+1] = 0
                score += slide[i] # Tính điểm
        
        # Trượt lại (Slide): [4, 0, 4, 0] -> [4, 4, 0, 0]
        non_zero = slide[slide != 0]
        new_line = np.zeros(self.size, dtype=int)
        new_line[:len(non_zero)] = non_zero
        return new_line, score

    def is_game_over(self):
        """Kiểm tra xem game đã kết thúc chưa."""
        # Còn ô trống không?
        if np.any(self.board == 0):
            return False
            
        #  Còn nước đi ngang không? (kiểm tra gộp [i,j] và [i,j+1])
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i, j] == self.board[i, j+1]:
                    return False
                    
        # Còn nước đi dọc không? (kiểm tra gộp [i,j] và [i+1,j])
        for j in range(self.size):
            for i in range(self.size - 1):
                if self.board[i, j] == self.board[i+1, j]:
                    return False
                    
        # Không còn ô trống và không thể gộp
        return True

