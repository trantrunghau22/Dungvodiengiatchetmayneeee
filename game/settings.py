import os
#os là thư viện làm việc với các tệp tin 
import pygame

#PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#Để truy cập tới thư mục to nhất chứa file mình cần
##__file__ là file code hiện tại
#os.path.abspath(...): Lấy đường dẫn tuyệt đối (đầy đủ) của file
#os.path.dirname(...) (Lần 1): Lấy thư mục chứa file này. (Kết quả: C:\Projects\MyGame\src)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
#Nối các đường dẫn
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')
FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')

#SCREEN
pygame.init() #Khởi động Module, chạy và xử lý các tệp tin
info = pygame.display.Info() ##lấy thông số kỹ thuật màn hình
WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h
FPS = 60

#CONCEPT
# Màu sắc
COLOR_BG_CREAM = (250, 248, 239)
COLOR_TEXT_DARK = (60, 50, 50)
COLOR_ACCENT_RED = (200, 60, 60)
COLOR_ACCENT_BLUE = (60, 100, 200)

#Tọa độ các lưới của màn hình TV 
TV_GRID_SIZE = 4 #kích thước 4x4
TV_GRID_WIDTH = 490 
TV_GRID_HEIGHT = 500
#Căn vị trí center của bàn cờ
TV_X = (WINDOW_WIDTH - TV_GRID_WIDTH) // 2
TV_Y = (WINDOW_HEIGHT - TV_GRID_HEIGHT) // 2 + 50 
#khoảng cách giữa các ô và kích thước ô
TILE_GAP = 15
TILE_SIZE = (TV_GRID_WIDTH - (TILE_GAP * (TV_GRID_SIZE + 1))) // TV_GRID_SIZE
#kích thước của ô score
SCORE_FONT_SIZE = 60 

#SOUNDS
SOUND_FILES = {
    'bgm': 'bgm.mp3',       # Nhạc nền
    'click': 'click.wav',   # Click chuột
    'start': 'start.mp3',   # Vào game / Reset
    'lose': 'lose.mp3',     # Thua game
    'merge': 'merge.wav',   # Gộp được điểm mới
    'slide': 'slide.mp3'    # Lướt phím
}

#FONTS
FONT_NAME = "comic-sans" # lốp dự phòng
SHIN_FONT_PATH = os.path.join(FONT_DIR, 'shin_font.ttf') #truy cập file font

#TEXT 
TEXTS = {
    'VI': {
        'nickname_placeholder': 'Cho xin tên đi (max 15 ký tự)',
        'start_err': 'Hãy nhập tên để chơi!',
        'score': 'Điểm',
        'best': 'Đỉnh nhất',
        'ask_save': 'Muốn lưu game thiệt hông?',
        'ask_quit': 'Bộ muốn thoát thiệt à?',
        'yes': 'Chứ gì', 'no': 'Không có nha'
    },
    'EN': {
        'nickname_placeholder': 'Enter Name (max 15 chars)',
        'start_err': 'Enter name first!',
        'score': 'Score',
        'best': 'Best',
        'ask_save': 'Save Game?',
        'ask_quit': 'Quit?',
        'yes': 'Yes', 'no': 'No'
    }
}