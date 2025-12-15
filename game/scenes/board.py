import pygame
import os
import random
import numpy as np
from game.settings import *
from game.core.rs import load_number_sprites, load_feature_sprites, draw_popup_bg, draw_styled_btn, SettingsHelper

class BoardScene:
    def __init__(self, app, env):
        self.app = app
        self.screen = app.screen
        self.env = env
        
        #Assets
        self.sprites = load_number_sprites(IMG_DIR, (TILE_SIZE, TILE_SIZE))
        self.load_lang_assets()
        
        def load_popup_img(name, size):
            path = os.path.join(IMG_DIR, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            return None

        self.img_exit = load_popup_img('popup_exit.png', (100, 100))
        self.img_win  = load_popup_img('popup_win.png', (120, 100))
        self.img_lose = load_popup_img('popup_lose.png', (120, 100))

        #Fonts
        if os.path.exists(SHIN_FONT_PATH):
            self.font = pygame.font.Font(SHIN_FONT_PATH, 35)
            self.score_font = pygame.font.Font(SHIN_FONT_PATH, SCORESIZE)
            self.popup_font = pygame.font.Font(SHIN_FONT_PATH, 24)
            self.small_font = pygame.font.Font(SHIN_FONT_PATH, 20)
        else:
            self.font = pygame.font.SysFont('arial', 35, bold=True)
            self.score_font = pygame.font.SysFont('arial', SCORESIZE, bold=True)
            self.popup_font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 20)
        
        #Buttons
        btn_width = 100; btn_height = 165 
        btn_y = WHEIGHT - btn_height - 30 
        self.btn_reset = pygame.Rect(50, btn_y + 30, btn_width, btn_height)
        self.btn_menu = pygame.Rect(WWIDTH - 150, btn_y, btn_width, btn_height)
        self.btn_save = pygame.Rect(WWIDTH - 270, btn_y, btn_width, btn_height)
        self.btn_setting = pygame.Rect(WWIDTH - 160, btn_y - 100, btn_width, btn_height)
        self.btn_ai = pygame.Rect(WWIDTH - 260, 180, 200, 80)

        self.popup_mode = None 
        self.input_text = ""; self.overwrite_target = ""; self.best_shown = False 
        
        self.settings_helper = SettingsHelper(app)

    def load_lang_assets(self):
        if self.app.lang == 'EN':
            bg_file, feat_file, set_file = 'backgroundgame_en.png', 'features_en.png', 'settings_en.png'
        else:
            bg_file, feat_file, set_file = 'backgroundgame.png', 'features.png', 'settings.png'

        bg_path = os.path.join(IMG_DIR, bg_file)
        if not os.path.exists(bg_path): bg_path = os.path.join(IMG_DIR, 'backgroundgame.png')
        if os.path.exists(bg_path):
            self.bg = pygame.image.load(bg_path).convert()
            self.bg = pygame.transform.scale(self.bg, (WWIDTH, WHEIGHT))
        else:
            self.bg = pygame.Surface((WWIDTH, WHEIGHT)); self.bg.fill(COLOR_BG_CREAM)

        feat_path = os.path.join(IMG_DIR, feat_file)
        if not os.path.exists(feat_path): feat_path = os.path.join(IMG_DIR, 'features.png')
        self.feats = load_feature_sprites(feat_path)

        set_path = os.path.join(IMG_DIR, set_file)
        if not os.path.exists(set_path): set_path = os.path.join(IMG_DIR, 'settings.png')
        if os.path.exists(set_path):
            self.img_setting_icon = pygame.image.load(set_path).convert_alpha()
            self.img_setting_icon = pygame.transform.smoothscale(self.img_setting_icon, (110, 110))
        else: self.img_setting_icon = None

    def update(self, dt): 
        if self.env.score > self.env.top_score: self.env.top_score = self.env.score
        if self.env.game_over and self.popup_mode is None:
            if self.env.score >= self.env.top_score and self.env.score > 0 and not self.best_shown:
                self.popup_mode = 'NEW_BEST'; self.env.save_bestscore(); self.best_shown = True
            elif not self.best_shown: self.popup_mode = 'GAME_OVER'
        #AI
        if self.app.ai_mode and not self.env.game_over and not self.popup_mode:
            # GẮN CODE AI VÔ ĐÂY
            pass

    def handle_event(self, event):
        if self.popup_mode: self.handle_popup_event(event); return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_reset.collidepoint(event.pos):
                self.app.play_sfx('click'); self.env.reset(); self.app.play_sfx('start'); self.best_shown = False
            elif self.btn_save.collidepoint(event.pos):
                self.app.play_sfx('click'); self.popup_mode = 'SAVE'; self.input_text = ""
            elif self.btn_menu.collidepoint(event.pos):
                self.app.play_sfx('click'); self.popup_mode = 'EXIT' 
            elif self.btn_setting.collidepoint(event.pos):
                self.app.play_sfx('click'); self.popup_mode = 'SETTING'
            elif self.btn_ai.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.app.ai_mode = not self.app.ai_mode
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.popup_mode = 'EXIT'
            if not self.app.ai_mode:
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
        cx, cy = WWIDTH // 2, WHEIGHT // 2
        
        if self.popup_mode == 'SETTING':
            res = self.settings_helper.handle_event(event, cx, cy)
            if res == 'CLOSE': self.popup_mode = None
            elif res == 'LANG_CHANGED': self.load_lang_assets()
            return

        if self.popup_mode == 'SAVE':
            if event.type == pygame.TEXTINPUT:
                if len(self.input_text) < 15: self.input_text += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.input_text.strip(): return
                    filename = "save_" + self.input_text + ".json"
                    files = self.env.get_saved_files()
                    if filename in files: self.overwrite_target = self.input_text; self.popup_mode = 'OVERWRITE'
                    elif len(files) >= 5: self.popup_mode = 'MAX_FILES'
                    else: self.env.save_game(self.input_text, mode="AI" if self.app.ai_mode else "Normal"); self.popup_mode = None
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
                if pygame.Rect(cx - 130, cy + 60, 120, 40).collidepoint(event.pos): 
                    from game.scenes.intro import IntroScreen; self.app.active_scene = IntroScreen(self.app)
                elif pygame.Rect(cx + 10, cy + 60, 120, 40).collidepoint(event.pos): self.popup_mode = 'SAVE'

            elif self.popup_mode == 'MAX_FILES': self.popup_mode = 'SAVE' 

            elif self.popup_mode in ['NEW_BEST', 'GAME_OVER']:
                if pygame.Rect(cx - 60, cy + 80, 120, 40).collidepoint(event.pos):
                    if self.popup_mode == 'NEW_BEST' and not self.env.game_over: self.popup_mode = None 
                    else: from game.scenes.intro import IntroScreen; self.app.active_scene = IntroScreen(self.app)

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        score_surf = self.score_font.render(str(self.env.score), True, (0,0,0))
        self.screen.blit(score_surf, (340, 30)) 
        best_x = WWIDTH - 250 
        best_surf = self.score_font.render(str(self.env.top_score), True, (0,0,0))
        self.screen.blit(best_surf, (best_x, 38)) 
        ai_color = (100, 255, 100) if self.app.ai_mode else (200, 200, 200)
        draw_styled_btn(self.screen, self.btn_ai, TEXTS[self.app.lang]['ai_btn'], self.small_font, ai_color)

        for r in range(TVSIZE):
            for c in range(TVSIZE):
                val = self.env.board[r][c]
                x = TV_X + GAP + c * (TILE_SIZE + GAP)
                y = TV_Y + GAP + r * (TILE_SIZE + GAP)
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
        
        if self.img_setting_icon:
            dest = self.btn_setting.copy()
            if self.btn_setting.collidepoint(pygame.mouse.get_pos()): dest.x += random.randint(-1, 1); dest.y += random.randint(-1, 1)
            icon_rect = self.img_setting_icon.get_rect(center=dest.center)
            self.screen.blit(self.img_setting_icon, icon_rect)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), self.btn_setting, border_radius=10)
            t = self.small_font.render("Set", True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=self.btn_setting.center))

        if self.popup_mode: self.draw_popup()

    def draw_popup(self):
        overlay = pygame.Surface((WWIDTH, WHEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR); self.screen.blit(overlay, (0,0))

        cx, cy = WWIDTH // 2, WHEIGHT // 2
        txt = TEXTS[self.app.lang]
        
        if self.popup_mode == 'SETTING':
            self.settings_helper.draw(self.screen, cx, cy, self.popup_font, self.font)
            return

        box_rect = pygame.Rect(cx - 200, cy - 150, 400, 300)
        draw_popup_bg(self.screen, box_rect)

        if self.popup_mode == 'SAVE':
            self.draw_text_centered(txt['save_game_title'], -100, size=30, color=COLOR_TEXT_DARK)
            self.draw_text_centered(txt['enter_name'], -50, size=20, color=COLOR_TEXT_DARK)
            input_rect = pygame.Rect(cx - 100, cy - 10, 200, 40)
            pygame.draw.rect(self.screen, (255,255,255), input_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, input_rect, 2, border_radius=5)
            txt_surf = self.popup_font.render(self.input_text, True, COLOR_TEXT_DARK)
            self.screen.blit(txt_surf, (input_rect.x+10, input_rect.y+5))

        elif self.popup_mode == 'OVERWRITE':
            self.draw_text_centered(txt['file_exists'], -60, color=COLOR_ACCENT_RED)
            self.draw_text_centered(txt['overwrite_ask'], -10, color=COLOR_TEXT_DARK)
            draw_styled_btn(self.screen, pygame.Rect(cx - 80, cy + 50, 100, 40), txt['yes'], self.popup_font, COLOR_ACCENT_BLUE)
            draw_styled_btn(self.screen, pygame.Rect(cx + 20, cy + 50, 100, 40), txt['no'], self.popup_font, COLOR_ACCENT_RED)

        elif self.popup_mode == 'EXIT':
            img_rect = pygame.Rect(cx - 50, cy - 110, 100, 100) 
            if self.img_exit: self.screen.blit(self.img_exit, img_rect)
            self.draw_text_centered(txt['exit_msg'], 20, color=COLOR_TEXT_DARK)
            draw_styled_btn(self.screen, pygame.Rect(cx - 130, cy + 60, 120, 40), txt['btn_quit_now'], self.popup_font, COLOR_ACCENT_RED)
            draw_styled_btn(self.screen, pygame.Rect(cx + 10, cy + 60, 120, 40), txt['btn_save_quit'], self.popup_font, COLOR_ACCENT_BLUE)

        elif self.popup_mode == 'NEW_BEST':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_win: self.screen.blit(self.img_win, img_rect)
            self.draw_text_centered(txt['new_best_title'], -10, size=35, color=COLOR_ACCENT_RED)
            self.draw_text_centered(f"{self.env.score}", 30, size=40, color=COLOR_TEXT_DARK)
            draw_styled_btn(self.screen, pygame.Rect(cx - 60, cy + 80, 120, 40), txt['btn_continue'], self.popup_font, COLOR_ACCENT_BLUE)

        elif self.popup_mode == 'GAME_OVER':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_lose: self.screen.blit(self.img_lose, img_rect)
            self.draw_text_centered(txt['game_over_title'], 0, size=35, color=COLOR_ACCENT_RED)
            draw_styled_btn(self.screen, pygame.Rect(cx - 60, cy + 80, 120, 40), txt['btn_menu'], self.popup_font, COLOR_ACCENT_BLUE)

        elif self.popup_mode == 'MAX_FILES':
            self.draw_text_centered(txt['max_files'], 0, color=COLOR_ACCENT_RED)

    def draw_text_centered(self, text, y_off, size=24, color=(0,0,0)):
        if os.path.exists(SHIN_FONT_PATH): font = pygame.font.Font(SHIN_FONT_PATH, size)
        else: font = pygame.font.SysFont('arial', size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(WWIDTH//2, WHEIGHT//2 + y_off)))

    def _draw_feature_btn(self, rect, name):
        img = self.feats.get(name)
        if img:
            img = pygame.transform.smoothscale(img, (rect.width, rect.height))
            dest = rect.copy()
            if rect.collidepoint(pygame.mouse.get_pos()): dest.x += random.randint(-1, 1); dest.y += random.randint(-1, 1)
            self.screen.blit(img, dest)