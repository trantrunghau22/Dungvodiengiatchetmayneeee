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
        self.nickname = getattr(app, 'username', "") #Giữ lại tên user
        self.err_msg = "" #thông báo lỗi nếu chưa nhập
        self.show_settings_popup = False
        self.popup_close_btn = None
        self.popup_lang_btn = None
        self.cred_popup = False
        self.tut_popup = False

        
        #LOAD ASSETS
        self.bg = pygame.image.load(os.path.join(IMG_DIR, 'backgroundintro.png')).convert()
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.title_img = pygame.image.load(os.path.join(IMG_DIR, 'title.png')).convert_alpha()
        self.title_base_size = self.title_img.get_size()
        
        #fonts
        self.font = pygame.font.Font(SHIN_FONT_PATH, 30) if os.path.exists(SHIN_FONT_PATH) else pygame.font.SysFont('arial', 30)
        
        #input box
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        self.active_input = False
        
        #layout cho 7 boxes
        btn_w, btn_h = 260, 80
        col_dist = 450 #Khoảng cách cột
        row_dist = 110 #Khoảng cách hàng

        #Bên trái
        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        #Bên phải
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        self.buttons = [
            (self.btn_new, "NEW GAME"), (self.btn_load, "LOAD GAME"), (self.btn_set, "SETTINGS"),
            (self.btn_cred, "CREDITS"), (self.btn_tut, "TUTORIAL"), (self.btn_exit, "EXIT")
        ]
        
        self.timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Vô vùng đó thì cho hàm kia thành true và có sound
            if self.input_rect.collidepoint(event.pos):
                self.active_input = True
                self.app.play_sfx('click')
            else:
                self.active_input = False    
            #Check các box
            if self.btn_new.collidepoint(event.pos):
                self.app.play_sfx('click')
                #Chỉ check tên khi ấn New Game
                if len(self.nickname) > 0:
                    self.start_game()
                else:
                    self.err_msg = TEXTS[self.app.lang]['start_err']

            elif self.btn_exit.collidepoint(event.pos):
                self.app.play_sfx('click')
                pygame.quit(); exit()

            elif self.btn_load.collidepoint(event.pos):
                 self.app.play_sfx('click')

            
            #Có thể mở settings/load mà không cần check tên
            elif self.btn_set.collidepoint(event.pos):
            #LOGIC CHECK SETTINGS, BỔ SUNG THÊM MỤC NÀY 
                self.show_settings_popup = True
                self.app.play_sfx('click')
                     

            elif self.btn_cred.collidepoint(event.pos):
                self.cred_popup = True
                self.app.play_sfx('click')
                

            elif self.btn_tut.collidepoint(event.pos):
                self.tut_popup = True
                self.app.play_sfx('click')
                

        #Hàm handle popup screen credits
        if self.cred_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
               if self.popup_cred_close_btn.collidepoint(event.pos):
                    self.cred_popup = False
                    self.app.play_sfx('click')
                    return
            return


        #Hàm handle popup screen tutorial
        if self.tut_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
               if self.popup_tut_close_btn.collidepoint(event.pos):
                    self.tut_popup = False
                    self.app.play_sfx('click')
                    return
            return

        #Hàm handle popup screen settings
        if self.show_settings_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.popup_setting_close_btn.collidepoint(event.pos):
                    self.show_settings_popup = False
                    self.app.play_sfx('click')
                    return
                    
                if self.popup_lang_btn.collidepoint(event.pos):
                    self.toggle_language()
                    self.app.play_sfx('click')
                    return
                    
            return  # Tránh xử lý các sự kiện khác khi popup đang hiển thị


       #phím nhập tên đồ thôi         
        if event.type == pygame.KEYDOWN:
            if self.active_input:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.start_game()
                else:
                    if len(self.nickname) < 15:
                        self.nickname += event.unicode
            
            #Cập nhạt user
            self.app.username = self.nickname

    def toggle_language(self):
        #NÈ KHÚC NÀY CẦN BỔ SUNG NÈ
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'
        # Xóa thông báo lỗi (nếu có)
        self.err_msg = ""

        # Nếu chưa nhập nickname thì reset placeholder
        if not self.nickname:
            self.err_msg = ""


    def start_game(self):
        self.app.play_sfx('start')
        self.app.username = self.nickname #Lưu tên chính thức
        env = Game2048Env(size=TV_GRID_SIZE)
        self.app.active_scene = BoardScene(self.app, env)

    def update(self, dt):
        self.timer += dt * 0.005 #cần để nảy title

    def render(self): #hàm vẽ chính nè
        self.screen.blit(self.bg, (0, 0))
        #cho title lắc đít
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale)
        h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        title_rect = scaled_title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(scaled_title, title_rect)
        #Vẽ để nhập
        color = COLOR_ACCENT_BLUE if self.active_input else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        
        txt_surf = self.font.render(self.nickname, True, COLOR_TEXT_DARK)
        self.screen.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + 10))
        #Hiện để bắt user nhập
        if not self.nickname and not self.active_input:
            hint = self.font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150, 150, 150))
            self.screen.blit(hint, (self.input_rect.x + 10, self.input_rect.y + 10))
        #Không nhập tên mà đòi chơi thì lỗi
        if self.err_msg:
            err = self.font.render(self.err_msg, True, COLOR_ACCENT_RED)
            self.screen.blit(err, (WINDOW_WIDTH//2 - err.get_width()//2, self.input_rect.bottom + 10))
        #Vẽ các nút
        for rect, text in self.buttons:
        # Nếu text là key trong TEXTS thì dùng TEXTS, không thì giữ nguyên
            key = text.lower().replace(" ", "_")
            if key in TEXTS[self.app.lang]:
                display_text = TEXTS[self.app.lang][key]
            else:
                display_text = text  # fallback

            self._draw_btn(rect, display_text)
            

        #Popup 3 cái screen khi nhấn nút
        if self.show_settings_popup:
            self.draw_settings_popup()
        
        if self.cred_popup:
            self.draw_cred_popup()
            
        if self.tut_popup:
            self.draw_tut_popup()

        
    #Hàm này để vẽ button và cho nó lắc đít ngựa chỉnh đổi màu đồ
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
        

    #Hàm vẽ popup settings
    def draw_settings_popup(self):
        #Nền mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #Vẽ popup settings
        popup_w, popup_h = 500, 350
        popup_rect = pygame.Rect(
            (WINDOW_WIDTH - popup_w) // 2,
            (WINDOW_HEIGHT - popup_h) // 2,
            popup_w,
            popup_h
        )

        pygame.draw.rect(self.screen, (255, 255, 255), popup_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, popup_rect, width=4, border_radius=20)

        #Nút đóng
        self.popup_setting_close_btn = pygame.Rect(popup_rect.right - 30, popup_rect.top + 10, 20,20)
        pygame.draw.rect(self.screen, (200, 50, 50), self.popup_setting_close_btn, border_radius=5)
        x_text = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_text, x_text.get_rect(center=self.popup_setting_close_btn.center))

        #Nội dung popup
        popup_settings_title = self.font.render("SETTINGS", True, COLOR_TEXT_DARK)
        self.screen.blit(popup_settings_title, popup_settings_title.get_rect(center=(popup_rect.centerx, popup_rect.top + 40)))
        lang_text = self.font.render(f"Language: {'VI' if self.app.lang == 'VI' else 'EN'} (Click to toggle)", True, COLOR_TEXT_DARK)
        self.screen.blit(lang_text, lang_text.get_rect(center=(popup_rect.centerx, popup_rect.top + 90)))
        
        ####
        lang_btn = pygame.Rect(popup_rect.centerx - 120, popup_rect.centery - 20, 240, 60)
        self.popup_lang_btn = lang_btn

        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, lang_btn, border_radius=12)
        pygame.draw.rect(self.screen, (255,255,255), lang_btn, width=3, border_radius=12)

        lang_txt = self.font.render("Toggle Language", True, COLOR_TEXT_DARK)
        self.screen.blit(lang_txt, lang_txt.get_rect(center=lang_btn.center))


    #Hàm vẽ popup credits
    def draw_cred_popup(self):
        #Nền mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #Vẽ popup settings
        popup_w, popup_h = 500, 350
        popup_rect = pygame.Rect(
            (WINDOW_WIDTH - popup_w) // 2,
            (WINDOW_HEIGHT - popup_h) // 2,
            popup_w,
            popup_h
        )

        pygame.draw.rect(self.screen, (255, 255, 255), popup_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, popup_rect, width=4, border_radius=20)

        #Nút đóng
        self.popup_cred_close_btn = pygame.Rect(popup_rect.right - 30, popup_rect.top + 10, 20,20)
        pygame.draw.rect(self.screen, (200, 50, 50), self.popup_cred_close_btn, border_radius=5)
        x_text = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_text, x_text.get_rect(center=self.popup_cred_close_btn.center))

         #Nội dung popup
        popup_cred_title = self.font.render("CREDITS", True, COLOR_TEXT_DARK)
        self.screen.blit(popup_cred_title, popup_cred_title.get_rect(center=(popup_rect.centerx, popup_rect.top + 40)))
        cred_lines = [
            "2048 - SHIN VA THO DIEN",
            "Developed by: ",
            "25120188 - Tran Trung Hau",
            "25120168 - Vo Gia Bao",
            "25120162 - Dao Khanh Bang",
            "25120159 - Pham Hoang Tuong An",
            "25120165 - Ngo Bao",
            "25120138: Tran Pham Dang Duy",
            "Special Thanks to: Mr. Le Duc Khoan",
            "12/2025"
        ]
        for i, line in enumerate(cred_lines):
            cred_text = self.font.render(line, True, COLOR_TEXT_DARK)
            self.screen.blit(cred_text, cred_text.get_rect(center=(popup_rect.centerx, popup_rect.top + 90 + i * 40)))

    #Hàm vẽ popup tutorial
    def draw_tut_popup(self):
        #Nền mờ
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        #Vẽ popup settings
        popup_w, popup_h = 500, 350
        popup_rect = pygame.Rect(
            (WINDOW_WIDTH - popup_w) // 2,
            (WINDOW_HEIGHT - popup_h) // 2,
            popup_w,
            popup_h
        )

        pygame.draw.rect(self.screen, (255, 255, 255), popup_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, popup_rect, width=4, border_radius=20)

        #Nút đóng
        self.popup_tut_close_btn = pygame.Rect(popup_rect.right - 30, popup_rect.top + 10, 20,20)
        pygame.draw.rect(self.screen, (200, 50, 50), self.popup_tut_close_btn, border_radius=5)
        x_text = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_text, x_text.get_rect(center=self.popup_tut_close_btn.center))

        popup_tut_title = self.font.render("TUTORIAL", True, COLOR_TEXT_DARK)
        self.screen.blit(popup_tut_title, popup_tut_title.get_rect(center=(popup_rect.centerx, popup_rect.top + 40)))
        tut_lines = [
            "Use arrow keys to move tiles.",
            "Combine tiles with the same number to create larger numbers.",
            " ",
            "Reach 2048 to win the game!",
            "Good luck and have fun!"
        ]
        for i, line in enumerate(tut_lines):
            tut_text = self.font.render(line, True, COLOR_TEXT_DARK)
            self.screen.blit(tut_text, tut_text.get_rect(center=(popup_rect.centerx, popup_rect.top + 90 + i * 40)))

