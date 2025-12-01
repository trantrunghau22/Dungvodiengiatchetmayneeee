import pygame
import os
import time
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env
from game.settings import GRID_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        
        # --- Font setup ---
        try:
            self.font_title = pygame.font.SysFont("comicsansms", 140, bold=True)
            self.font_small = pygame.font.SysFont("comicsansms", 32, bold=True)
            self.font_input = pygame.font.SysFont("comicsansms", 28)
            self.font_list  = pygame.font.SysFont("arial", 24) # Font cho danh sách file
        except:
            self.font_title = pygame.font.SysFont("arial", 100, bold=True)
            self.font_small = pygame.font.SysFont("arial", 32, bold=True)
            self.font_input = pygame.font.SysFont("arial", 28)
            self.font_list  = pygame.font.SysFont("arial", 24)

        # --- Main Buttons ---
        self.button_start = pygame.Rect(240, 420, 300, 60)
        self.button_ai = pygame.Rect(240, 500, 300, 60)
        self.button_load = pygame.Rect(240, 580, 300, 60)

        # --- Username input ---
        self.username = getattr(self.app, 'username', "")
        self.input_active = False
        self.input_box = pygame.Rect(200, 320, 400, 50)
        self.color_active = (243, 178, 122)
        self.color_inactive = (187, 173, 160)
        self.input_color = self.color_inactive

        # --- Load Game Modal (Cửa sổ chọn file) ---
        self.show_load_list = False  # Trạng thái hiển thị danh sách
        self.saved_files = []        # Danh sách file tìm được
        self.file_rects = []         # Vùng bấm của từng file
        
        # Khung cửa sổ danh sách
        self.list_bg_rect = pygame.Rect(100, 150, 600, 500)
        self.btn_close_list = pygame.Rect(550, 160, 140, 40) # Nút đóng danh sách

    def _scan_saved_files(self):
        """Quét thư mục để tìm file .json và sắp xếp theo thời gian mới nhất"""
        files = []
        try:
            # Lấy tất cả file trong thư mục hiện tại
            all_files = os.listdir('.')
            for f in all_files:
                if f.endswith('.json'):
                    files.append(f)
            
            # Sắp xếp theo thời gian sửa đổi (mới nhất lên đầu)
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        except Exception as e:
            print("Error scanning files:", e)
        
        self.saved_files = files

    def handle_event(self, event):
        # --- 1. Xử lý khi đang mở danh sách Load Game ---
        if self.show_load_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Check nút Đóng (Close)
                if self.btn_close_list.collidepoint(mouse_pos):
                    self.show_load_list = False
                    return

                # Check click vào từng file
                for i, rect in enumerate(self.file_rects):
                    if rect.collidepoint(mouse_pos):
                        selected_file = self.saved_files[i]
                        self._load_selected_file(selected_file)
                        return
            return # Nếu đang mở list thì chặn các sự kiện bên dưới

        # --- 2. Xử lý màn hình Intro bình thường ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Nhập Username
            if self.input_box.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.color_active
            else:
                self.input_active = False
                self.input_color = self.color_inactive

            # START GAME
            if self.button_start.collidepoint(event.pos):
                self._start_game(ai_mode=False)

            # AI MODE
            if self.button_ai.collidepoint(event.pos):
                self._start_game(ai_mode=True)

            # LOAD GAME BUTTON -> Mở danh sách
            if self.button_load.collidepoint(event.pos):
                self._scan_saved_files() # Quét file mới nhất
                self.show_load_list = True

        # Input bàn phím (Chỉ cho Username)
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self._start_game(ai_mode=False)
                elif event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                else:
                    if len(self.username) < 12:
                        self.username += event.unicode

    def _start_game(self, ai_mode=False):
        if self.username.strip() == "":
            print("Username required!")
            # Có thể thêm hiệu ứng rung lắc hoặc đổi màu ô nhập để báo lỗi
            return
            
        self.app.username = self.username
        self.app.ai_mode = ai_mode
        
        # Tạo game mới
        new_env = Game2048Env(size=GRID_SIZE)
        new_env.reset()
        self.app.active_scene = BoardScene(new_env, self.app)

    def _load_selected_file(self, filename):
        # Load file đã chọn
        print(f"Loading file: {filename}")
        
        if not os.path.exists(filename):
            print("File not found!")
            return

        env = Game2048Env(size=GRID_SIZE)
        try:
            env.load_game(filename)
            print("Loaded successfully!")
        except Exception as e:
            print("Error loading game:", e)
            return

        # Nếu username trống thì lấy tên từ tên file (vd: Hau_save.json -> Hau)
        if self.username.strip() == "":
            base_name = filename.replace("_save.json", "").replace(".json", "")
            self.app.username = base_name
        else:
            self.app.username = self.username

        self.app.ai_mode = False 
        self.app.active_scene = BoardScene(env, self.app)

    def render(self):
        self.window.fill((250, 248, 239))

        # Title
        title = self.font_title.render("2048", True, (243, 178, 122))
        self.window.blit(title, (190, 150))

        # Username input
        label = self.font_small.render("Enter username:", True, (119, 110, 101))
        self.window.blit(label, (200, 280))

        pygame.draw.rect(self.window, self.input_color, self.input_box, border_radius=10)
        text_surface = self.font_input.render(self.username, True, (0, 0, 0))
        self.window.blit(text_surface, (self.input_box.x+10, self.input_box.y+10))

        # Buttons chính
        self._draw_button(self.button_start, "START")
        self._draw_button(self.button_ai, "AI MODE")
        self._draw_button(self.button_load, "LOAD GAME")

        # --- VẼ DANH SÁCH FILE NẾU ĐANG BẬT ---
        if self.show_load_list:
            self._render_load_list()

    def _render_load_list(self):
        # 1. Vẽ lớp phủ mờ (overlay)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.window.blit(overlay, (0, 0))

        # 2. Vẽ khung danh sách
        pygame.draw.rect(self.window, (250, 248, 239), self.list_bg_rect, border_radius=15)
        pygame.draw.rect(self.window, (187, 173, 160), self.list_bg_rect, width=4, border_radius=15)

        # 3. Tiêu đề danh sách
        title_surf = self.font_small.render("Select Saved Game", True, (119, 110, 101))
        self.window.blit(title_surf, (self.list_bg_rect.x + 20, self.list_bg_rect.y + 20))

        # 4. Nút Đóng (Close)
        mouse_pos = pygame.mouse.get_pos()
        close_color = (243, 178, 122) if self.btn_close_list.collidepoint(mouse_pos) else (187, 173, 160)
        pygame.draw.rect(self.window, close_color, self.btn_close_list, border_radius=8)
        close_txt = self.font_input.render("Close", True, (255, 255, 255))
        self.window.blit(close_txt, close_txt.get_rect(center=self.btn_close_list.center))

        # 5. Vẽ danh sách các file
        self.file_rects = [] # Reset danh sách vùng bấm
        start_y = self.list_bg_rect.y + 80
        
        if not self.saved_files:
            empty_txt = self.font_list.render("No saved files found (.json)", True, (150, 150, 150))
            self.window.blit(empty_txt, (self.list_bg_rect.x + 40, start_y))
        else:
            # Chỉ hiện tối đa 8 file mới nhất để không bị tràn màn hình
            for i, filename in enumerate(self.saved_files[:8]):
                # Tạo vùng bấm cho từng dòng
                item_rect = pygame.Rect(self.list_bg_rect.x + 20, start_y + i*50, 560, 40)
                self.file_rects.append(item_rect)

                # Hiệu ứng hover chuột
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.window, (238, 228, 218), item_rect, border_radius=5)
                    text_color = (243, 178, 122)
                else:
                    text_color = (119, 110, 101)

                # Vẽ tên file
                # Cắt bớt tên nếu quá dài
                display_name = filename if len(filename) < 40 else filename[:37] + "..."
                txt_surf = self.font_list.render(f"{i+1}. {display_name}", True, text_color)
                
                # Canh giữa theo chiều dọc của dòng
                txt_rect = txt_surf.get_rect(midleft=(item_rect.x + 10, item_rect.centery))
                self.window.blit(txt_surf, txt_rect)

    def _draw_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        # Đổi màu khi hover
        color = (243, 178, 122) if rect.collidepoint(mouse) else (246, 150, 101)
        pygame.draw.rect(self.window, color, rect, border_radius=12)
        text_surf = self.font_small.render(text, True, (250, 248, 239))
        text_rect = text_surf.get_rect(center=rect.center)
        self.window.blit(text_surf, text_rect)

    def update(self):
        pass
