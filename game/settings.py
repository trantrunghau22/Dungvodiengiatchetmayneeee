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
WWIDTH = info.current_w
WHEIGHT = info.current_h
FPS = 60

#CONCEPT
COLOR_BG_CREAM = (250, 248, 239)
COLOR_TEXT_DARK = (60, 50, 50)
COLOR_ACCENT_RED = (200, 60, 60)
COLOR_ACCENT_BLUE = (60, 100, 200)

POPUP_BG_COLOR = (255, 255, 255, 240)
OVERLAY_COLOR = (0, 0, 0, 150)

#GRID
TVSIZE = 4
TVWIDTH = 490 
TVHEIGHT = 500
TV_X = (WWIDTH - TVWIDTH) // 2
TV_Y = (WHEIGHT - TVHEIGHT) // 2 + 50 
GAP = 15
TILE_SIZE = (TVWIDTH - (GAP * (TVSIZE + 1))) // TVSIZE
SCORESIZE = 60 

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

#TEXTS
TEXTS = {
    'VI': {
        'new_game': 'GAME MỚI', 'load_game': 'TẢI GAME', 'setting': 'CÀI ĐẶT',
        'credit': 'TÁC GIẢ', 'tutorial': 'HƯỚNG DẪN', 'exit': 'THOÁT',
        
        'nickname_placeholder': 'Cho xin tên đi (max 15 ký tự)',
        'start_err': 'Nhập đi rồi chơi má ơi!',
        'score': 'Điểm', 'best': 'Đỉnh nhất',
        'ask_save': 'Muốn lưu game thiệt hông?', 'ask_quit': 'Bộ muốn thoát thiệt à?',
        'yes': 'Ok nhuôn', 'no': 'Thôi khỏi đi',
        
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
        'delete': 'Xóa', 'rename': 'Đổi tên',

        'hello' : 'XIN CHÀO',

        'ai_btn': 'CHƠI AI',

        'lang_label': 'Ngôn ngữ:',
        'music_label': 'Nhạc nền:',
        'sfx_label': 'Hiệu ứng:',
        'btn_back': 'QUAY LẠI',
        'on': 'BẬT', 'off': 'TẮT',

        'tut_title': 'HƯỚNG DẪN',
        'tut_content': [
            "Cách chơi 2048 của thợ điện:",
            "- Dùng phím Mũi tên hoặc WASD để di chuyển.",
            "- Hai ô cùng số sẽ gộp lại thành số lớn hơn.",
            "- Ớt chuông có cơ chế gộp đặc biệt. Sau khi bạn chơi được đến ô 128, có",
            "khả năng sẽ xuất hiện ô ớt chuông, các ô ớt chuông không thể gộp với nhau",
            "nhưng có thể gộp với ô 256 rồi cả hai biến mất. Bạn sẽ có điểm thưởng.",
            "- Mục tiêu: Đạt điểm càng cao càng tốt! Càng nhiều ô trống càng ngon!"
        ],
        'credit_title': 'ĐỘI NGŨ THỰC HIỆN',
        'credit_content': [
            "Đồ án Nhập môn CNTT",
            "Nhóm: Thợ Điện Viết Code",
            "---",
            "Đào Khánh Băng",
            "Vũ Gia Bảo",
            "Trần Trung Hậu",
            "Ngô Bảo",
            "Phạm Trần Đăng Duy",
            "Phạm Tường An"
        ]
    },
    'EN': {
        'new_game': 'NEW GAME', 'load_game': 'LOAD GAME', 'setting': 'SETTINGS',
        'credit': 'CREDITS', 'tutorial': 'TUTORIAL', 'exit': 'EXIT',

        'nickname_placeholder': 'Enter Name (max 15 chars)',
        'start_err': 'Enter name first!',
        'score': 'Score', 'best': 'Best',
        'ask_save': 'Save Game?', 'ask_quit': 'Quit?',
        'yes': 'Yes', 'no': 'No', 
        
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
        'delete': 'Delete', 'rename': 'Rename',

        'hello' : 'HELLO',

        'ai_btn': 'CHƠI AI',


        'lang_label': 'Language:',
        'music_label': 'Music:',
        'sfx_label': 'SFX:',
        'btn_back': 'BACK',
        'on': 'ON', 'off': 'OFF',

        'tut_title': 'TUTORIAL',
        'tut_content': [
            "How to play 2048:",
            "- Use the arrow keys or WASD to move.",
            "- Two tiles with the same number will merge into a larger one.",
            "- Bell peppers have a special merging mechanic. After you reach the 128 tile, ", 
            "there is a chance that a bell pepper tile will appear. Bell pepper tiles cannot",
            "merge with each other, but they can merge with a 256 tile, after which both",
            "tiles disappear and you receive a bonus score."
            "- Goal: Get the highest score possible! The more empty tiles, the better!"
        ],
        'credit_title': 'CREDITS',
        'credit_content': [
            "Intro to IT Project",
            "Team: Electrician Coders",
            "---",
            "Dao Khanh Bang",
            "Vu Gia Bao",
            "Tran Trung Hau",
            "Ngo Bao",
            "Pham Tran Dang Duy",
            "Pham Tuong An"
        ]
    }
}