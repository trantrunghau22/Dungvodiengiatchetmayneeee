import os
import pygame

# Khởi tạo pygame để lấy info màn hình (chỉ chạy 1 lần khi import)
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# --- Cấu hình Màn hình Cơ sở (Base Resolution) ---
# Dùng hệ quy chiếu 800x600 để thiết kế, sau đó scale lên
BASE_WIDTH = 800
BASE_HEIGHT = 600

# Tính tỉ lệ scale (chọn tỉ lệ nhỏ hơn để fit màn hình)
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y) * 0.9 # Nhân 0.9 để chừa chút lề

# Kích thước cửa sổ thực tế (Fullscreen)
WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT

# Offset để căn giữa nội dung game
OFFSET_X = (WINDOW_WIDTH - (BASE_WIDTH * SCALE)) // 2
OFFSET_Y = (WINDOW_HEIGHT - (BASE_HEIGHT * SCALE)) // 2

# --- Hàm helper để scale kích thước và tọa độ ---
def s(value):
    return int(value * SCALE)

def s_rect(x, y, w, h):
    # x, y, w, h là kích thước trong hệ quy chiếu 800x600
    return pygame.Rect(OFFSET_X + s(x), OFFSET_Y + s(y), s(w), s(h))

# --- Cấu hình Game ---
ROWS = 4
COLS = 4
GRID_SIZE = 4

# Layout Bàn cờ (Hệ quy chiếu Base 800x600)
# Các biến này cần được định nghĩa để board.py sử dụng
BASE_BOARD_MARGIN_LEFT = 260
BASE_BOARD_MARGIN_TOP = 180
BASE_TILE_SIZE = 80
BASE_TILE_GAP = 10

# Tính toán kích thước Base
BASE_BOARD_WIDTH = (BASE_TILE_SIZE * GRID_SIZE) + (BASE_TILE_GAP * (GRID_SIZE + 1))
BASE_BOARD_HEIGHT = BASE_BOARD_WIDTH 

# Các biến Scale (để board.py dùng)
BOARD_MARGIN_LEFT = OFFSET_X + s(BASE_BOARD_MARGIN_LEFT)
BOARD_MARGIN_TOP = OFFSET_Y + s(BASE_BOARD_MARGIN_TOP)
BOARD_WIDTH = s(BASE_BOARD_WIDTH)
BOARD_HEIGHT = s(BASE_BOARD_HEIGHT)
TILE_SIZE = s(BASE_TILE_SIZE)
TILE_GAP = s(BASE_TILE_GAP)

# --- Màu sắc ---
BACKGROUND_COLOR = (255, 253, 208)
TEXT_COLOR = (60, 50, 50)
SCORE_TEXT_COLOR = (0, 0, 0)
SCORE_BG_COLOR = (187, 173, 160)
BOARD_BG_COLOR = (187, 173, 160)

TILE_COLORS = {
    0: (205, 193, 180), 2: (238, 228, 218), 4: (237, 224, 200),
    8: (242, 177, 121), 16: (245, 149, 99), 32: (246, 124, 95),
    64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
    4096: (255, 60, 60), 8192: (75, 200, 75),
}
DEFAULT_LARGE_TILE_COLOR = (60, 58, 50)

# --- Assets Config ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')
FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')

FONT_NAME = "comicsansms"
FPS = 60
TILE_RADIUS = int(10 * SCALE)
TOP_SCORE_FILE = "top_score.txt"

# --- TỪ ĐIỂN NGÔN NGỮ ---
TEXTS = {
    'VI': {
        'new_game': 'GAME MỚI', 'load_game': 'TẢI GAME', 'setting': 'CÀI ĐẶT',
        'tutorial': 'HƯỚNG DẪN', 'credit': 'TÁC GIẢ', 'exit': 'THOÁT',
        'start_normal': 'BẮT ĐẦU', 'start_ai': 'CHẾ ĐỘ AI',
        'music': 'Nhạc nền', 'sound': 'Âm thanh', 'lang': 'Ngôn ngữ',
        'close': 'Đóng', 'on': 'BẬT', 'off': 'TẮT',
        'ask_exit': 'Bạn muốn thoát game?', 'yes': 'Có', 'no': 'Không',
        'save_title': 'Lưu Game', 'enter_name': 'Nhập tên file:',
        'overwrite_msg': 'File đã tồn tại!', 'overwrite_ask': 'Ghi đè hay đổi tên?',
        'btn_overwrite': 'Ghi đè', 'btn_rename': 'Đổi tên',
        'score': 'Điểm', 'best': 'Đỉnh', 'game_over': 'HẾT GIỜ',
        'tut_content': [
            "Cách chơi 2048:",
            "- Dùng phím Mũi tên hoặc WASD để di chuyển.",
            "- Hai ô cùng số sẽ gộp lại thành số lớn hơn.",
            "- Mục tiêu: Tạo ra ô số 2048!",
            "- Bấm 'S' để lưu game, 'Q' để ra menu."
        ],
        'credit_content': [
            "HCMUS - 25CTT3",
            "GROUP THỢ ĐIỆN VIẾT CODE",
            "GAME 2048",
            "Trần Trung Hậu - 25120188",
            "Vũ Gia Bảo - 25120168",
            "Đào Khánh Băng - 25120162",
            "Phạm Hoàng Tường An - 25120159",
            "Ngô Bảo - 25120165",
            "Trần Phạm Đăng Duy - 25120138",
            "GRAPHICS: SHIN STYLE"
        ]
    },
    'EN': {
        'new_game': 'NEW GAME', 'load_game': 'LOAD GAME', 'setting': 'SETTINGS',
        'tutorial': 'TUTORIAL', 'credit': 'CREDITS', 'exit': 'EXIT',
        'start_normal': 'START', 'start_ai': 'AI MODE',
        'music': 'Music', 'sound': 'Sound', 'lang': 'Language',
        'close': 'Close', 'on': 'ON', 'off': 'OFF',
        'ask_exit': 'Do you want to exit?', 'yes': 'Yes', 'no': 'No',
        'save_title': 'Save Game', 'enter_name': 'Enter filename:',
        'overwrite_msg': 'File exists!', 'overwrite_ask': 'Overwrite or Rename?',
        'btn_overwrite': 'Overwrite', 'btn_rename': 'Rename',
        'score': 'Score', 'best': 'Best', 'game_over': 'GAME OVER',
        'tut_content': [
            "How to play 2048:",
            "- Use Arrow keys or WASD to move tiles.",
            "- Merge tiles with the same number.",
            "- Goal: Create the 2048 tile!",
            "- Press 'S' to Save, 'Q' for Menu."
        ],
        'credit_content': [
            "HCMUS - 25CTT3",
            "GROUP THỢ ĐIỆN VIẾT CODE",
            "GAME 2048",
            "Trần Trung Hậu - 25120188",
            "Vũ Gia Bảo - 25120168",
            "Đào Khánh Băng - 25120162",
            "Phạm Hoàng Tường An - 25120159",
            "Ngô Bảo - 25120165",
            "Trần Phạm Đăng Duy - 25120138",
            "GRAPHICS: SHIN STYLE"
        ]
    }
}
