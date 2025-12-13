import os
import pygame

#PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')
FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')

#SCREEN
pygame.init()
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h
FPS = 60

#CONCEPT
COLOR_BG_CREAM = (250, 248, 239)
COLOR_TEXT_DARK = (60, 50, 50)
COLOR_ACCENT_RED = (200, 60, 60)
COLOR_ACCENT_BLUE = (60, 100, 200)

POPUP_BG_COLOR = (255, 255, 255, 240)
OVERLAY_COLOR = (0, 0, 0, 150)

#GRID
TV_GRID_SIZE = 4
TV_GRID_WIDTH = 490 
TV_GRID_HEIGHT = 500
TV_X = (WINDOW_WIDTH - TV_GRID_WIDTH) // 2
TV_Y = (WINDOW_HEIGHT - TV_GRID_HEIGHT) // 2 + 50 
TILE_GAP = 15
TILE_SIZE = (TV_GRID_WIDTH - (TILE_GAP * (TV_GRID_SIZE + 1))) // TV_GRID_SIZE
SCORE_FONT_SIZE = 60 

#SOUNDS
SOUND_FILES = {
    'bgm': 'bgm.mp3',
    'click': 'click.wav',
    'start': 'start.mp3',
    'lose': 'lose.mp3',
    'merge': 'merge.wav',
    'slide': 'slide.mp3'
}

#FONTS
FONT_NAME = "Comic Sans MS"
SHIN_FONT_PATH = os.path.join(FONT_DIR, 'shin_font.ttf')

#TEXT 
TEXTS = {
    'VI': {
        # --- Intro Menu [BỔ SUNG CÁC KEY THIẾU] ---
        'new_game': 'CHƠI GAME',
        'load_game': 'TẢI GAME',
        'setting': 'CÀI ĐẶT',
        'credit': 'TÁC GIẢ',
        'tutorial': 'HƯỚNG DẪN',
        'exit': 'THOÁT',
        
        # --- Main Game ---
        'nickname_placeholder': 'Cho xin tên đi (max 15 ký tự)',
        'start_err': 'Nhập đi rồi chơi má ơi!',
        'score': 'Điểm',
        'best': 'Đỉnh nhất',
        'ask_save': 'Muốn lưu game thiệt hông?',
        'ask_quit': 'Bộ muốn thoát thiệt à?',
        'yes': 'Ok nhuôn', 'no': 'Thôi khỏi đi',
        
        # --- Popups ---
        'save_game_title': 'LƯU GAME',
        'enter_name': 'Nhập tên file (Max 5 file):',
        'file_exists': 'Tên file này có òi!',
        'overwrite_ask': 'Bạn có muốn ghi đè không?',
        'max_files': '5 file rồi má ơi!',
        'exit_title': 'THOÁT GAME',
        'exit_msg': 'Bạn có muốn lưu trước khi thoát?',
        'btn_save_quit': 'Lưu & Thoát',
        'btn_quit_now': 'Thoát luôn',
        'new_best_title': 'BẠN THÌ GIỎI RỒI!',
        'new_best_msg': 'Kỷ lục mới:',
        'game_over_title': 'BẠI CHUYẾN NÀY',
        'game_over_msg': 'Hết đi được rồi nha!',
        'btn_continue': 'Tiếp tục',
        'load_title': 'CHỌN FILE ĐỂ CHƠI',
        'btn_menu': 'Về Menu',
        'empty': '(Trống)',

        'saved_success': 'Đã lưu nha!',
        'delete_confirm': 'Xóa file này nha?',
        'rename_title': 'Đổi tên:',
        'file_not_found': 'Không thấy file đâu á!',
        'delete': 'Xóa',
        'rename': 'Đổi tên',

        # Settings
        'lang_label': 'Ngôn ngữ:',
        'music_label': 'Nhạc nền:',
        'sfx_label': 'Hiệu ứng:',
        'btn_back': 'QUAY LẠI',

        # Settings / Tutorial / Credit Content
        'lang_label': 'Ngôn ngữ:',
        'sound_label': 'Âm thanh:',
        'on': 'BẬT', 'off': 'TẮT',

        'tut_title': 'HƯỚNG DẪN',
        'tut_content': [
            "Cách chơi 2048:",
            "- Dùng phím Mũi tên hoặc WASD để di chuyển.",
            "- Hai ô cùng số sẽ gộp lại thành số lớn hơn.",
            "- Ớt chuông (1) có cơ chế gộp đặc biệt.",
            "- Mục tiêu: Đạt điểm càng cao càng tốt!",
            "- Bấm 'S' để Lưu, 'Esc' để Thoát."
        ],
        
        'credit_title': 'ĐỘI NGŨ THỰC HIỆN',
        'credit_content': [
            "Đồ án Nhập môn CNTT",
            "Nhóm: Thợ Điện Viết Code",
            "---",
            "Coder 1: Trần Trung Hậu",
            "Coder 2: Vũ Gia Bảo",
            "Designer: Đào Khánh Băng",
            "Support: Tường An, Ngô Bảo, Đăng Duy"
        ]
    },
    'EN': {
        # --- Intro Menu [ADDED MISSING KEYS] ---
        'new_game': 'NEW GAME',
        'load_game': 'LOAD GAME',
        'setting': 'SETTINGS',
        'credit': 'CREDITS',
        'tutorial': 'TUTORIAL',
        'exit': 'EXIT',

        # --- Main Game ---
        'nickname_placeholder': 'Enter Name (max 15 chars)',
        'start_err': 'Enter name first!',
        'score': 'Score',
        'best': 'Best',
        'ask_save': 'Save Game?',
        'ask_quit': 'Quit?',
        'yes': 'Yes', 'no': 'No', 
        
        # --- Popups ---
        'save_game_title': 'SAVE GAME',
        'enter_name': 'Enter filename (Max 5 files):',
        'file_exists': 'File already exists!',
        'overwrite_ask': 'Do you want to overwrite?',
        'max_files': 'Limit of 5 files reached!',
        'exit_title': 'EXIT GAME',
        'exit_msg': 'Save before quitting?',
        'btn_save_quit': 'Save & Quit',
        'btn_quit_now': 'Quit Now',
        'new_best_title': 'CONGRATULATIONS!',
        'new_best_msg': 'New High Score:',
        'game_over_title': 'GAME OVER',
        'game_over_msg': 'No moves left!',
        'btn_continue': 'Continue',
        'load_title': 'SELECT FILE TO LOAD',
        'btn_menu': 'Menu',
        'empty': '(Empty)',

        'saved_success': 'Saved!',
        'delete_confirm': 'Delete this file?',
        'rename_title': 'Rename:',
        'file_not_found': 'File not found!',
        'delete': 'Delete',
        'rename': 'Rename',

        # Settings / Tutorial / Credit Content
        'lang_label': 'Language:',
        'sound_label': 'Sound:',
        'on': 'ON', 'off': 'OFF',
        
        # Settings
        'lang_label': 'Language:',
        'music_label': 'Music:',
        'sfx_label': 'SFX:',
        'btn_back': 'BACK',

        'tut_title': 'TUTORIAL',
        'tut_content': [
            "How to play 2048:",
            "- Use Arrow keys or WASD to move tiles.",
            "- Merge tiles with same numbers.",
            "- Chili (1) has special merge rules.",
            "- Goal: Get the highest score!",
            "- Press 'S' to Save, 'Esc' to Quit."
        ],
        
        'credit_title': 'CREDITS',
        'credit_content': [
            "Intro to IT Project",
            "Team: Electrician Coders",
            "---",
            "Coder 1: Tran Trung Hau",
            "Coder 2: Vu Gia Bao",
            "Designer: Dao Khanh Bang",
            "Support: Tuong An, Ngo Bao, Dang Duy"
        ]
    }
}