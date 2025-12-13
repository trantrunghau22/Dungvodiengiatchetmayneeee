import pygame
import os
import random
import numpy as np
from game.settings import *
from game.core.utils import load_number_sprites, load_feature_sprites

class BoardScene:
    def __init__(self, app, env):
        self.app = app
        self.screen = app.screen
        self.env = env
        
        # Background
        bg_filename = 'backgroundgame.png'
        if self.app.lang == 'EN': bg_filename = 'backgroundgame_en.png'
        bg_path = os.path.join(IMG_DIR, bg_filename) 
        if os.path.exists(bg_path): self.bg = pygame.image.load(bg_path).convert()
        else: self.bg = pygame.image.load(os.path.join(IMG_DIR, 'backgroundgame.png')).convert()
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.sprites = load_number_sprites(IMG_DIR, (TILE_SIZE, TILE_SIZE))
        self.feats = load_feature_sprites(os.path.join(IMG_DIR, 'features.png'))
        
        # [QUAN TRỌNG] Dùng Arial thay vì Shin Font để không lỗi tiếng Việt
        self.font = pygame.font.SysFont('arial', 35, bold=True)
        self.score_font = pygame.font.SysFont('arial', SCORE_FONT_SIZE, bold=True)
        self.popup_font = pygame.font.SysFont('arial', 24)
        
        # Popup Images
        def load_popup_img(name, size):
            path = os.path.join(IMG_DIR, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            return None
        self.img_exit = load_popup_img('popup_exit.png', (100, 100))
        self.img_win  = load_popup_img('popup_win.png', (120, 100))
        self.img_lose = load_popup_img('popup_lose.png', (120, 100))

        # Buttons
        btn_width = 100; btn_height = 165 
        btn_y = WINDOW_HEIGHT - btn_height - 30 
        self.btn_reset = pygame.Rect(50, btn_y, btn_width, btn_height)
        self.btn_menu = pygame.Rect(WINDOW_WIDTH - 150, btn_y, btn_width, btn_height)
        self.btn_save = pygame.Rect(WINDOW_WIDTH - 270, btn_y, btn_width, btn_height)

        # Popup State
        self.popup_mode = None 
        self.input_text = ""; self.overwrite_target = ""; self.best_shown = False 

    def update(self, dt): 
        if self.env.score > self.env.top_score: self.env.top_score = self.env.score
        if self.env.game_over and self.popup_mode is None:
            if self.env.score >= self.env.top_score and self.env.score > 0 and not self.best_shown:
                self.popup_mode = 'NEW_BEST'; self.env.save_global_best_score(); self.best_shown = True
            elif not self.best_shown: self.popup_mode = 'GAME_OVER'

    def handle_event(self, event):
        if self.popup_mode: self.handle_popup_event(event); return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_reset.collidepoint(event.pos):
                self.app.play_sfx('click'); self.env.reset(); self.app.play_sfx('start'); self.best_shown = False
            elif self.btn_save.collidepoint(event.pos):
                self.app.play_sfx('click'); self.popup_mode = 'SAVE'; self.input_text = ""
            elif self.btn_menu.collidepoint(event.pos):
                self.app.play_sfx('click'); self.popup_mode = 'EXIT' 
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.popup_mode = 'EXIT'
            action = None
            if event.key in [pygame.K_UP, pygame.K_w]: action = 0
            elif event.key in [pygame.K_DOWN, pygame.K_s]: action = 1
            elif event.key in [pygame.K_LEFT, pygame.K_a]: action = 2
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: action = 3
            
            if action is not None and not self.env.game_over:
                max_before = np.max(self.env.board) if self.env.board.size > 0 else 0
                board, current_score, done, moved = self.env.step(action)
                if moved:
                    self.app.play_sfx('slide') 
                    max_after = np.max(self.env.board) if self.env.board.size > 0 else 0
                    if max_after > max_before: self.app.play_sfx('merge')
                if done: self.app.play_sfx('lose')

    def handle_popup_event(self, event):
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # Xử lý nhập tên file Save (Hỗ trợ tiếng Việt)
        if self.popup_mode == 'SAVE':
            if event.type == pygame.TEXTINPUT:
                if len(self.input_text) < 15: self.input_text += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.input_text.strip(): return
                    filename = "save_" + self.input_text + ".json"
                    files = self.env.get_saved_files()
                    if filename in files:
                        self.overwrite_target = self.input_text; self.popup_mode = 'OVERWRITE'
                    elif len(files) >= 5: self.popup_mode = 'MAX_FILES'
                    else:
                        self.env.save_game(self.input_text, mode="AI" if self.app.ai_mode else "Normal")
                        self.popup_mode = None
                elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE: self.popup_mode = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not pygame.Rect(cx - 200, cy - 150, 400, 300).collidepoint(event.pos): self.popup_mode = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.popup_mode == 'OVERWRITE':
                if pygame.Rect(cx - 80, cy + 50, 100, 40).collidepoint(event.pos): 
                    self.env.save_game(self.overwrite_target, mode="AI" if self.app.ai_mode else "Normal"); self.popup_mode = None
                elif pygame.Rect(cx + 20, cy + 50, 100, 40).collidepoint(event.pos): self.popup_mode = 'SAVE'

            elif self.popup_mode == 'EXIT':
                if pygame.Rect(cx - 130, cy + 60, 120, 40).collidepoint(event.pos): # Quit
                    from game.scenes.intro import IntroScreen; self.app.active_scene = IntroScreen(self.app)
                elif pygame.Rect(cx + 10, cy + 60, 120, 40).collidepoint(event.pos): self.popup_mode = 'SAVE' # Save

            elif self.popup_mode == 'MAX_FILES': self.popup_mode = 'SAVE' 

            elif self.popup_mode in ['NEW_BEST', 'GAME_OVER']:
                if pygame.Rect(cx - 60, cy + 80, 120, 40).collidepoint(event.pos):
                    if self.popup_mode == 'NEW_BEST' and not self.env.game_over: self.popup_mode = None 
                    else:
                        from game.scenes.intro import IntroScreen; self.app.active_scene = IntroScreen(self.app)

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        score_surf = self.score_font.render(str(self.env.score), True, (0,0,0))
        self.screen.blit(score_surf, (340, 30)) 
        best_surf = self.score_font.render(str(self.env.top_score), True, (0,0,0))
        self.screen.blit(best_surf, (1500, 38)) 
        
        for r in range(TV_GRID_SIZE):
            for c in range(TV_GRID_SIZE):
                val = self.env.board[r][c]
                x = TV_X + TILE_GAP + c * (TILE_SIZE + TILE_GAP)
                y = TV_Y + TILE_GAP + r * (TILE_SIZE + TILE_GAP)
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (200, 190, 180), rect, border_radius=8)
                if val != 0:
                    if val in self.sprites: self.screen.blit(self.sprites[val], (x, y))
                    else:
                        pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=8)
                        t = self.font.render(str(val), True, (255,255,255))
                        self.screen.blit(t, t.get_rect(center=rect.center))
        
        self._draw_feature_btn(self.btn_reset, 'reset')
        self._draw_feature_btn(self.btn_save, 'save')
        self._draw_feature_btn(self.btn_menu, 'menu')

        if self.popup_mode: self.draw_popup()

    def draw_popup(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR); self.screen.blit(overlay, (0,0))

        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        txt = TEXTS[self.app.lang]
        
        box_rect = pygame.Rect(cx - 200, cy - 150, 400, 300)
        box_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        box_surf.fill(POPUP_BG_COLOR)
        self.screen.blit(box_surf, box_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), box_rect, 3, border_radius=15)

        if self.popup_mode == 'SAVE':
            self.draw_text_centered(txt['save_game_title'], -100, size=30)
            self.draw_text_centered(txt['enter_name'], -50, size=20)
            input_rect = pygame.Rect(cx - 100, cy - 10, 200, 40)
            pygame.draw.rect(self.screen, (255,255,255), input_rect)
            pygame.draw.rect(self.screen, (0,0,0), input_rect, 2)
            self.draw_text(self.input_text, input_rect.x+10, input_rect.y+5)

        elif self.popup_mode == 'OVERWRITE':
            self.draw_text_centered(txt['file_exists'], -60, color=(200,0,0))
            self.draw_text_centered(txt['overwrite_ask'], -10)
            self.draw_btn_simple(txt['yes'], (cx - 80, cy + 50), (100, 200, 100))
            self.draw_btn_simple(txt['no'], (cx + 20, cy + 50), (200, 100, 100))

        elif self.popup_mode == 'EXIT':
            img_rect = pygame.Rect(cx - 50, cy - 110, 100, 100) 
            if self.img_exit: self.screen.blit(self.img_exit, img_rect)
            else:
                pygame.draw.rect(self.screen, (200,200,200), img_rect)
                self.draw_text_centered("[IMG]", -60, size=15)
            self.draw_text_centered(txt['exit_msg'], 20)
            self.draw_btn_simple(txt['btn_quit_now'], (cx - 130, cy + 60), (200, 100, 100), w=120)
            self.draw_btn_simple(txt['btn_save_quit'], (cx + 10, cy + 60), (100, 200, 100), w=120)

        elif self.popup_mode == 'NEW_BEST':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_win: self.screen.blit(self.img_win, img_rect)
            else: pygame.draw.rect(self.screen, (255,215,0), img_rect)
            self.draw_text_centered(txt['new_best_title'], -10, size=35, color=(200,0,0))
            self.draw_text_centered(f"{self.env.score}", 30, size=40)
            self.draw_btn_simple(txt['btn_continue'], (cx - 60, cy + 80), (100, 150, 255), w=120)

        elif self.popup_mode == 'GAME_OVER':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_lose: self.screen.blit(self.img_lose, img_rect)
            else: pygame.draw.rect(self.screen, (50,50,50), img_rect)
            self.draw_text_centered(txt['game_over_title'], 0, size=35, color=(255,0,0))
            self.draw_btn_simple(txt['btn_menu'], (cx - 60, cy + 80), (100, 150, 255), w=120)

        elif self.popup_mode == 'MAX_FILES':
            self.draw_text_centered(txt['max_files'], 0, color=(200,0,0))

    def draw_text_centered(self, text, y_off, size=24, color=(0,0,0)):
        font = self.popup_font if size==24 else pygame.font.SysFont('arial', size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + y_off)))

    def draw_text(self, text, x, y, size=24):
        surf = self.popup_font.render(text, True, (0,0,0))
        self.screen.blit(surf, (x,y))

    def draw_btn_simple(self, text, pos, color, w=100, h=40):
        rect = pygame.Rect(pos[0], pos[1], w, h)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        surf = self.popup_font.render(text, True, (255,255,255))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_feature_btn(self, rect, name):
        img = self.feats.get(name)
        if img:
            img = pygame.transform.smoothscale(img, (rect.width, rect.height))
            dest = rect.copy()
            if rect.collidepoint(pygame.mouse.get_pos()): dest.x += random.randint(-2, 2); dest.y += random.randint(-2, 2)
            self.screen.blit(img, dest)