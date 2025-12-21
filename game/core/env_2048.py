import numpy as np
import random
import json
import os
import glob
from datetime import datetime

#KHỞI TẠO GAME CHỖ NÀY
class Game2048Env:
    def __init__(self, size=4):
        self.size = size #đặt kích thước mặc định của bàn cờ
        self.score = 0 #khởi tạo điểm số ban đầu
        self.board = np.zeros((size, size), dtype=int) 
        self.game_over = False #trạng thái game
        self.top_score = 0 #trạng thái best score
        
        #Biến theo dõi file lưu để lưu đè
        self.current_filename = None 
        
        self.load_bestscore() #load điểm cao nhất
        self.reset() #trạng thái có reset hay không

    def reset(self): #xóa sạch bàn cờ
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self.game_over = False
        self.current_filename = None 
        self.spawn_tile()
        self.spawn_tile()
        return self.board

    def spawn_tile(self):
        empty = list(zip(*np.where(self.board == 0))) #tìm lên danh sách các ô trống là ô có giá trị = 0
        if not empty: return False #không trống thì thôi
        r, c = random.choice(empty) #trống thì random tọa độ ô trống
        max_tile = np.max(self.board) #tìm giá trị lớn nhất của bàn cờ
        rand = random.random()
        if max_tile >= 128: #nếu xuất hiện giá trị lớn hơn hoặc bằng 128 rồi
            if rand < 0.01: val = 1 #1% ra ớt chuông
            elif rand < 0.11: val = 4 #11% ra số 4
            else: val = 2 #88% ra số 2
        else:
            if rand < 0.10: val = 4 #chưa đáp ứng đk trên thì sinh ô 4 với tỉ lệ 10 và 90 với 2
            else: val = 2
        
        self.board[r, c] = val #trả giá trị
        return True

#XỬ LÝ THAO TÁC DI CHUYỂN NÈ:
    def step(self, action):
        #0: UP
        #1: DOWN
        #2: LEFT
        #3: RIGHT
        prev_board = self.board.copy() #này để không bị mất bàn cờ ban đầu. 
        #ứng với hàng động nào thì gọi hàm đó
        if action == 2: self._move_left()
        elif action == 3: self._move_right()
        elif action == 0: self._move_up()
        elif action == 1: self._move_down()
        
        moved = not np.array_equal(prev_board, self.board)
        if moved:
            self.spawn_tile() #bàn cờ thay đổi thì xin ra ô
        
        if self._is_done():
            self.game_over = True #kiểm tra hết ô thì game over
            
        return self.board, self.score, self.game_over, moved

    #LOGIC GỘP KHI CÓ ƯỚT CHUÔNG
    def _merge_row(self, row):
        #Dồn các số khác 0 về phía trái.
        #So sánh 2 ô cạnh nhau:
        #Nếu bằng nhau: Gộp thành số mới gấp đôi, cộng điểm, bỏ qua ô kế tiếp.
        #Nếu khác nhau: Giữ nguyên.
        #Bổ sung các số 0 vào cuối hàng để đảm bảo độ dài không đổi.
        new_row = row[row != 0]
        merged_row = []
        i = 0
        while i < len(new_row):
            val = new_row[i]
            if i + 1 < len(new_row):
                next_val = new_row[i+1]
                #CASE 1:ra 256 dọn dẹp Ớt 
                if (val == 256 and next_val == 1) or (val == 1 and next_val == 256):
                    self.score += 256 
                    i += 2 
                    continue
                #CASE 2: Ớt không gộp với bất kỳ ai
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
        if (self.board == 0).any(): return False #còn ô trống thì falsse
#logic của cái đống dưới đây: 
#Kiểm tra ô trống: Nếu bàn cờ còn số 0 thì return False
#Kiểm tra gộp ngang/dọc: Duyệt qua từng ô và so sánh với ô bên cạnh nhau
#Nếu hai ô cạnh nhau có giá trị bằng nhau còn gộp được thì chưa thua
#Quy tắc đặc biệt: Kiểm tra cặp (1, 256) hoặc (256, 1). Nếu tồn tại cặp này cạnh nhau Còn nước đi thì chưa thua
#Nếu không thỏa mãn các điều kiện trên return true.
        for r in range(self.size):
            for c in range(self.size - 1):
                v1, v2 = self.board[r, c], self.board[r, c+1]
                if v1 == v2 and v1 != 1: return False 
                if (v1==1 and v2==256) or (v1==256 and v2==1): return False
        for r in range(self.size - 1):
            for c in range(self.size):
                v1, v2 = self.board[r, c], self.board[r+1, c]
                if v1 == v2 and v1 != 1: return False
                if (v1==1 and v2==256) or (v1==256 and v2==1): return False
        return True

    #Cơ chế save load game
    def get_saved_files(self):
        return sorted(glob.glob("save_*.json"))

    def load_bestscore(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    self.top_score = int(f.read())
            else:
                self.top_score = 0
        except:
            self.top_score = 0
        return self.top_score

    def save_bestscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(int(self.top_score)))

    def save_game(self, filename, mode='Normal'):
        if not filename.startswith("save_"): #này phần định dạng tên file tiền tố và hậu tố
            filename = "save_" + filename
        if not filename.endswith(".json"):
            filename += ".json"
        
        if self.score > self.top_score:
            self.top_score = self.score
            self.save_bestscore() #logic cập nhật best score

        data = { #những thông tin sẽ lấy để lưu
            "board": self.board.tolist(), #chuyển ma trận thành danh sách do numpy ko hỗ trợ lưu ma trận
            "score": int(self.score), #điểm
            "mode": mode, #chế độ
            "game_over": self.game_over, #tình trạng game 
            "date": str(datetime.now()) #thời gian
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f) #ghi ra file 
        
        #Cập nhật file hiện tại sau khi lưu
        self.current_filename = filename

    def load_game(self, filename): #lóad lại
        if not os.path.exists(filename): return False #truy cập file theo tên file, không thấy thì trả về false
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.board = np.array(data['board'])
                self.score = int(data['score'])
                self.game_over = data.get('game_over', False)
                self.load_bestscore()
            #load các tài nguyên đã ghi
            #Xem đang chơi file nào
            self.current_filename = filename
            return True
        except Exception as e: 
            print(f"Lỗi load game: {e}")
            return False
            
    def delete_game(self, filename): #xóa file
        try:
            if os.path.exists(filename): #Kiểm tra file có tồn tại không
                os.remove(filename) #có thì xóa
                #Xóa file rồi thì reset biến currentfilename
                if self.current_filename == filename:
                    self.current_filename = None # Reset về None để tránh lỗi save đè vào file không còn tồn tạ
                return True
        except: pass # Reset về None để tránh lỗi save đè vào file không còn tồn tạ
        return False

    def rename_game(self, old_name, new_name):
        if not new_name.strip(): return False #Kiểm tra đầu vào: Tên mới không được để trống (chỉ toàn dấu cách)
        
        if not old_name.startswith("save_"): old_name = "save_" + old_name #Chuẩn hóa tên file CŨ (để tìm đúng file cần đổi)
        if not old_name.endswith(".json"): old_name += ".json"
        
        if not new_name.startswith("save_"): new_name = "save_" + new_name #Chuẩn hóa tên file MỚI (để tạo file đích đúng chuẩn)
        if not new_name.endswith(".json"): new_name += ".json"
        
        #if os.path.exists(new_name): return False #Kiểm tra trùng lặp: Nếu tên mới đã có file tồn tại rồi thì KHÔNG cho đổi (tránh ghi đè nhầm)
        try:
            os.replace(old_name, new_name) #Thực hiện đổi tên file
            #Cập nhật tên file nếu được đổi
            if self.current_filename == old_name: #Nếu file vừa bị đổi tên chính là file đang chơi hiện tại
                self.current_filename = new_name #Cập nhật biến theo dõi thành tên mới
            return True
        except: return False
