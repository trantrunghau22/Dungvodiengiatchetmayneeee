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
        self.nickname = getattr(app, 'username', "")
        self.input_active = False
        
        #LOAD ASSETS
        self.bg = pygame.image.load(os.path.join(IMG_DIR, 'backgroundintro.png')).convert()
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.title_img = pygame.image.load(os.path.join(IMG_DIR, 'title.png')).convert_alpha()
        self.title_base_size = self.title_img.get_size()
        
        self.font = pygame.font.Font(SHIN_FONT_PATH, 30) if os.path.exists(SHIN_FONT_PATH) else pygame.font.SysFont('arial', 30)
        
        #input box
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        
        #layout
        btn_w, btn_h = 260, 80
        col_dist = 450
        row_dist = 110

        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        # [SỬA] Thống nhất dùng tên biến show_load_popup
        self.show_load_popup = False
        self.saved_files = [] 
        self.err_msg = ""
        self.timer = 0

    def handle_event(self, event):
        # [XỬ LÝ POPUP LOAD GAME]
        if self.show_load_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
                # Check click file
                for i, filename in enumerate(self.saved_files):
                    rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
                    if rect.collidepoint(event.pos):
                        env = Game2048Env(size=TV_GRID_SIZE)
                        if env.load_game(filename):
                            self.app.active_scene = BoardScene(self.app, env)
                        self.show_load_popup = False
                        return
                
                # Close (X)
                if pygame.Rect(cx + 120, cy - 140, 30, 30).collidepoint(event.pos):
                    self.show_load_popup = False
            return

        # [SỰ KIỆN CHÍNH]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.app.play_sfx('click')
            else:
                self.input_active = False    
            
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
                self.saved_files = temp.get_saved_files()[:5]
                self.show_load_popup = True
            
            elif self.btn_set.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.toggle_language()

        # Keyboard Input
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.start_game()
                else:
                    if len(self.nickname) < 15:
                        self.nickname += event.unicode
            self.app.username = self.nickname

    def toggle_language(self):
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'

    def start_game(self):
        self.app.play_sfx('start')
        self.app.username = self.nickname
        env = Game2048Env(size=TV_GRID_SIZE)
        self.app.active_scene = BoardScene(self.app, env)

    def update(self, dt):
        self.timer += dt * 0.005 

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        
        # Title Animation
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale)
        h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        title_rect = scaled_title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(scaled_title, title_rect)
        
        # Input Box
        color = COLOR_ACCENT_BLUE if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        
        txt_surf = self.font.render(self.nickname, True, COLOR_TEXT_DARK)
        self.screen.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        if not self.nickname and not self.input_active:
            hint = self.font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150, 150, 150))
            self.screen.blit(hint, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        if self.err_msg:
            err = self.font.render(self.err_msg, True, COLOR_ACCENT_RED)
            self.screen.blit(err, (WINDOW_WIDTH//2 - err.get_width()//2, self.input_rect.bottom + 10))
        
        # Buttons
        txt = TEXTS[self.app.lang]
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_set, txt['setting']), (self.btn_cred, txt['credit']),
            (self.btn_tut, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        
        for rect, text in buttons:
            self._draw_btn(rect, text)
            
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
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0,0))

        cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        box = pygame.Rect(cx - 200, cy - 150, 400, 350)
        pygame.draw.rect(self.screen, POPUP_BG_COLOR, box, border_radius=10)
        
        # Close btn
        close = pygame.Rect(cx + 120, cy - 140, 30, 30)
        pygame.draw.rect(self.screen, (200,50,50), close)
        x_txt = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_txt, x_txt.get_rect(center=close.center))
        
        title = self.font.render(TEXTS[self.app.lang]['load_title'], True, (0,0,0))
        self.screen.blit(title, title.get_rect(center=(cx, cy - 120)))

        for i, f in enumerate(self.saved_files):
            rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
            pygame.draw.rect(self.screen, (200,200,255), rect, border_radius=5)
            name = f.replace("save_", "").replace(".json", "")
            t = self.font.render(name, True, (0,0,0))
            self.screen.blit(t, (rect.x + 10, rect.y + 5))