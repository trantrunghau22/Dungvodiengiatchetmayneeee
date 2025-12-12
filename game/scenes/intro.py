import pygame
import math
import os
import random 
from game.settings import *
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.nickname = getattr(app, 'username', "") # Giữ lại tên user
        self.input_active = False
        
        # --- LOAD ASSETS ---
        bg_path = os.path.join(IMG_DIR, 'backgroundintro.png')
        if os.path.exists(bg_path):
            self.bg = pygame.image.load(bg_path).convert()
        else:
            self.bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.bg.fill((250, 248, 239))
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        title_path = os.path.join(IMG_DIR, 'title.png')
        if os.path.exists(title_path):
            self.title_img = pygame.image.load(title_path).convert_alpha()
        else:
            self.title_img = pygame.Surface((400, 150), pygame.SRCALPHA)
            self.title_img.fill((200, 100, 100))
        self.title_base_size = self.title_img.get_size()
        
        # Fonts
        self.font = pygame.font.Font(SHIN_FONT_PATH, 30) if os.path.exists(SHIN_FONT_PATH) else pygame.font.SysFont('arial', 30)
        
        # Input box
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        
        # Layout cho 7 boxes
        btn_w, btn_h = 260, 80
        col_dist = 450 # Khoảng cách cột
        row_dist = 110 # Khoảng cách hàng

        # Bên trái
        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        # Bên phải
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        self.buttons = [
            (self.btn_new, "NEW GAME"), (self.btn_load, "LOAD GAME"), (self.btn_set, "SETTINGS"),
            (self.btn_cred, "CREDITS"), (self.btn_tut, "TUTORIAL"), (self.btn_exit, "EXIT")
        ]
        
        self.err_msg = ""
        
        # [SỬA LỖI] Khởi tạo timer và các biến Load Game đúng chỗ
        self.timer = 0
        self.show_load_popup = False
        self.saved_files = [] 

    def handle_event(self, event):
        # [XỬ LÝ POPUP LOAD GAME]
        if self.show_load_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
                # Check click vào từng file
                for i, filename in enumerate(self.saved_files):
                    rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
                    if rect.collidepoint(event.pos):
                        # Load game
                        env = Game2048Env(size=TV_GRID_SIZE)
                        if env.load_game(filename):
                            self.app.active_scene = BoardScene(self.app, env)
                        self.show_load_popup = False
                        return
                
                # Click nút Close (X) hoặc ra ngoài
                close_rect = pygame.Rect(cx + 120, cy - 140, 30, 30)
                popup_rect = pygame.Rect(cx - 200, cy - 150, 400, 350)
                
                if close_rect.collidepoint(event.pos) or not popup_rect.collidepoint(event.pos):
                    self.show_load_popup = False
            return

        # [XỬ LÝ SỰ KIỆN CHÍNH]
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check Input Focus
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.app.play_sfx('click')
            else:
                self.input_active = False    
            
            # Check Buttons
            if self.btn_new.collidepoint(event.pos):
                self.app.play_sfx('click')
                if len(self.nickname) > 0:
                    self.start_game()
                else:
                    self.err_msg = TEXTS[self.app.lang]['start_err']

            elif self.btn_exit.collidepoint(event.pos):
                self.app.play_sfx('click')
                pygame.quit(); exit()

            elif self.btn_load.collidepoint(event.pos):
                self.app.play_sfx('click')
                temp = Game2048Env()
                self.saved_files = temp.get_saved_files()[:5] # Lấy tối đa 5 file
                self.show_load_popup = True
            
            # Bổ sung logic cho Settings (Toggle Language)
            elif self.btn_set.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.toggle_language()

        # Nhập tên (Chỉ xử lý khi active)     
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.start_game()
                else:
                    if len(self.nickname) < 15:
                        self.nickname += event.unicode
            
            # Cập nhật username vào app để dùng chung
            self.app.username = self.nickname

    def toggle_language(self):
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'

    def start_game(self):
        self.app.play_sfx('start')
        self.app.username = self.nickname # Lưu tên chính thức
        env = Game2048Env(size=TV_GRID_SIZE)
        self.app.active_scene = BoardScene(self.app, env)

    def update(self, dt):
        self.timer += dt * 0.005 # Cần self.timer đã khởi tạo ở __init__

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        
        # Hiệu ứng Title (Lắc lư)
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale)
        h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        title_rect = scaled_title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(scaled_title, title_rect)
        
        # Vẽ Input Box
        color = COLOR_ACCENT_BLUE if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        
        txt_surf = self.font.render(self.nickname, True, COLOR_TEXT_DARK)
        self.screen.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        # Placeholder text
        if not self.nickname and not self.input_active:
            hint = self.font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150, 150, 150))
            self.screen.blit(hint, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        # Error Message
        if self.err_msg:
            err = self.font.render(self.err_msg, True, COLOR_ACCENT_RED)
            self.screen.blit(err, (WINDOW_WIDTH//2 - err.get_width()//2, self.input_rect.bottom + 10))
        
        # Vẽ các nút Menu
        txt = TEXTS[self.app.lang]
        # Cập nhật lại text nút dựa trên ngôn ngữ hiện tại
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_set, txt['setting']), (self.btn_cred, txt['credit']),
            (self.btn_tut, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        
        for rect, text in buttons:
            self._draw_btn(rect, text)
            
        # Vẽ Popup Load Game nếu đang bật
        if self.show_load_popup:
            self.draw_load_popup(self.screen)

    def _draw_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        draw_rect = rect.copy()
        if rect.collidepoint(mouse_pos):
            draw_rect.x += random.randint(-2, 2)
            draw_rect.y += random.randint(-2, 2)
            color = COLOR_ACCENT_BLUE
        else:
            color = (255, 200, 150)
            
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, width=3, border_radius=15)
        
        t_surf = self.font.render(text, True, COLOR_TEXT_DARK)
        self.screen.blit(t_surf, t_surf.get_rect(center=draw_rect.center))
        
    def draw_load_popup(self, screen):
        # Lớp phủ mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.window.blit(overlay, (0,0))

        cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        box = pygame.Rect(cx - 200, cy - 150, 400, 350)
        pygame.draw.rect(self.window, POPUP_BG_COLOR, box, border_radius=10)
        
        # Close btn (X)
        close = pygame.Rect(cx + 120, cy - 140, 30, 30)
        pygame.draw.rect(self.window, (200,50,50), close)
        x_txt = self.font.render("X", True, (255,255,255))
        self.window.blit(x_txt, x_txt.get_rect(center=close.center))
        
        # Tiêu đề Popup
        title = self.font.render(TEXTS[self.app.lang]['load_title'], True, (0,0,0))
        self.window.blit(title, title.get_rect(center=(cx, cy - 120)))

        # Danh sách file
        if not self.saved_files:
            empty_txt = self.font.render(TEXTS[self.app.lang]['empty'], True, (100,100,100))
            self.window.blit(empty_txt, empty_txt.get_rect(center=(cx, cy)))
        
        for i, f in enumerate(self.saved_files):
            rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
            pygame.draw.rect(self.window, (200,200,255), rect, border_radius=5)
            # Làm đẹp tên file hiển thị
            name = f.replace("save_", "").replace(".json", "")
            t = self.font.render(name, True, (0,0,0))
            self.window.blit(t, (rect.x + 10, rect.y + 5))