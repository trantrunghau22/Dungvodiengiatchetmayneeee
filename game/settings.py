import os

# --- Cấu hình Màn hình ---
ROWS = 4
COLS = 4
GRID_SIZE = 4

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# --- Layout Bàn cờ ---
BOARD_MARGIN_LEFT = 260  
BOARD_MARGIN_TOP = 180
TILE_SIZE = 80
TILE_GAP = 10
BOARD_WIDTH = (TILE_SIZE * GRID_SIZE) + (TILE_GAP * (GRID_SIZE + 1))
BOARD_HEIGHT = BOARD_WIDTH 

# --- Màu sắc ---
BACKGROUND_COLOR = (255, 253, 208)
TEXT_COLOR = (60, 50, 50)
SCORE_TEXT_COLOR = (0, 0, 0)

# [FIXED] Thêm màu nền cho ô điểm số
SCORE_BG_COLOR = (200, 190, 180) 
BOARD_BG_COLOR = (150, 140, 130) # Màu nền khung bàn cờ

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
TILE_RADIUS = 10
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
        'credit_content': ["Game 2048", "Code by: Bạn & AI", "Graphics: Shin Style"]
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
        'credit_content': ["2048 Game", "Code by: You & AI", "Graphics: Shin Style"]
    }
}
