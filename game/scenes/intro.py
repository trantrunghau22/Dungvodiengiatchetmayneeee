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
        self.err_msg = ""
        
        # --- LOAD ASSETS ---
        bg_path = os.path.join(IMG_DIR, 'backgroundintro.png')
        if os.path.exists(bg_path): self.bg = pygame.image.load(bg_path).convert()
        else:
            self.bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.bg.fill((250, 248, 239))
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        title_path = os.path.join(IMG_DIR, 'title.png')
        if os.path.exists(title_path): self.title_img = pygame.image.load(title_path).convert_alpha()
        else:
            self.title_img = pygame.Surface((400, 150))
            self.title_img.fill((200,100,100))
        self.title_base_size = self.title_img.get_size()
        
        # --- [QUAN TRỌNG] SỬA FONT ĐỂ HIỆN TIẾNG VIỆT ---
        # Dùng SysFont('arial') thay vì shin_font.ttf
        self.font = pygame.font.SysFont('arial', 30, bold=True)
        self.small_font = pygame.font.SysFont('arial', 22)
        
        # INPUT & LAYOUT
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        
        btn_w, btn_h = 260, 80
        col_dist = 450; row_dist = 110

        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        self.timer = 0
        
        # --- MODAL SYSTEM ---
        self.modal = None # 'LOAD', 'SETTING', 'CREDIT', 'TUTORIAL'
        self.modal_rect = pygame.Rect(cx - 300, cy - 225, 600, 450)
        self.btn_close = pygame.Rect(self.modal_rect.right - 40, self.modal_rect.top + 10, 30, 30)
        
        # Load Game State
        self.saved_files = [] 
        self.rename_idx = -1; self.rename_text = ""; self.delete_confirm_idx = -1

        # Settings State (Volume)
        self.vol_music = 0.5
        self.vol_sfx = 0.5
        self.dragging_music = False
        self.dragging_sfx = False
        pygame.mixer.music.set_volume(self.vol_music)

    def handle_event(self, event):
        # 1. MODAL EVENTS
        if self.modal:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_close.collidepoint(event.pos):
                    self.modal = None; return
                
                if self.modal == 'LOAD': self._handle_load_events(event)
                elif self.modal == 'SETTING': self._handle_setting_click(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.modal == 'SETTING':
                    self.dragging_music = False
                    self.dragging_sfx = False

            elif event.type == pygame.MOUSEMOTION:
                if self.modal == 'SETTING': self._handle_setting_drag(event)

            elif event.type == pygame.KEYDOWN and self.modal == 'LOAD':
                self._handle_rename_input(event)
            
            # Text input cho rename (Hỗ trợ tiếng Việt)
            if event.type == pygame.TEXTINPUT and self.modal == 'LOAD' and self.rename_idx != -1:
                 if len(self.rename_text) < 15: self.rename_text += event.text

            return

        # 2. MAIN SCREEN EVENTS
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.app.play_sfx('click')
            else: self.input_active = False    
            
            if self.btn_new.collidepoint(event.pos):
                self.app.play_sfx('click')
                if len(self.nickname) > 0: self.start_game()
                else: self.err_msg = TEXTS[self.app.lang]['start_err']

            elif self.btn_exit.collidepoint(event.pos):
                self.app.play_sfx('click'); pygame.quit(); exit()

            # Open Modals
            elif self.btn_load.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('LOAD')
            elif self.btn_set.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('SETTING')
            elif self.btn_cred.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('CREDIT')
            elif self.btn_tut.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('TUTORIAL')

        # Nhập tên User (Dùng Text Input để hỗ trợ tiếng Việt)
        if self.input_active:
            if event.type == pygame.TEXTINPUT:
                if len(self.nickname) < 15: self.nickname += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.start_game()
            self.app.username = self.nickname

    def open_modal(self, mode):
        self.modal = mode
        if mode == 'LOAD':
            temp = Game2048Env()
            self.saved_files = temp.get_saved_files()
            self.rename_idx = -1; self.delete_confirm_idx = -1

    # --- SETTINGS LOGIC ---
    def _handle_setting_click(self, event):
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
        music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
        sfx_rect   = pygame.Rect(cx + 20, cy + 40, 200, 20)
        back_rect  = pygame.Rect(cx - 60, cy + 120, 120, 40)

        if lang_rect.collidepoint(event.pos):
            self.toggle_language(); self.app.play_sfx('click')
        elif music_rect.collidepoint(event.pos):
            self.dragging_music = True; self._update_music_vol(event.pos[0], music_rect)
        elif sfx_rect.collidepoint(event.pos):
            self.dragging_sfx = True; self._update_sfx_vol(event.pos[0], sfx_rect)
        elif back_rect.collidepoint(event.pos):
            self.modal = None; self.app.play_sfx('click')

    def _handle_setting_drag(self, event):
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
        sfx_rect   = pygame.Rect(cx + 20, cy + 40, 200, 20)
        if self.dragging_music: self._update_music_vol(event.pos[0], music_rect)
        elif self.dragging_sfx: self._update_sfx_vol(event.pos[0], sfx_rect)

    def _update_music_vol(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        self.vol_music = max(0.0, min(1.0, ratio))
        pygame.mixer.music.set_volume(self.vol_music)

    def _update_sfx_vol(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        self.vol_sfx = max(0.0, min(1.0, ratio))
        self.app.sfx_volume = self.vol_sfx 

    # --- LOAD GAME LOGIC ---
    def _handle_load_events(self, event):
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        top_y = self.modal_rect.top
        
        for i, f in enumerate(self.saved_files):
            y = top_y + 80 + i*50 
            rect_del = pygame.Rect(cx + 130, y, 30, 40)
            rect_ren = pygame.Rect(cx + 95, y, 30, 40)
            rect_file = pygame.Rect(cx - 150, y, 240, 40)

            if rect_del.collidepoint(event.pos):
                if self.delete_confirm_idx == i:
                    Game2048Env().delete_game(f); self.open_modal('LOAD')
                else: self.delete_confirm_idx = i; self.rename_idx = -1
                return
            if rect_ren.collidepoint(event.pos):
                self.rename_idx = i
                self.rename_text = f.replace("save_", "").replace(".json", "")
                self.delete_confirm_idx = -1
                return
            if rect_file.collidepoint(event.pos):
                if self.rename_idx == -1 and self.delete_confirm_idx == -1:
                    env = Game2048Env(size=TV_GRID_SIZE)
                    if env.load_game(f): self.app.active_scene = BoardScene(self.app, env)

        self.delete_confirm_idx = -1; self.rename_idx = -1

    def _handle_rename_input(self, event):
        if self.rename_idx != -1:
            if event.key == pygame.K_RETURN:
                if self.rename_text.strip():
                    old = self.saved_files[self.rename_idx]
                    Game2048Env().rename_game(old, self.rename_text)
                    self.open_modal('LOAD')
                self.rename_idx = -1
            elif event.key == pygame.K_ESCAPE: self.rename_idx = -1
            elif event.key == pygame.K_BACKSPACE: self.rename_text = self.rename_text[:-1]

    def toggle_language(self):
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'

    def start_game(self):
        self.app.play_sfx('start')
        self.app.username = self.nickname
        env = Game2048Env(size=TV_GRID_SIZE)
        self.app.active_scene = BoardScene(self.app, env)

    def update(self, dt): self.timer += dt * 0.005

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale); h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        self.screen.blit(scaled_title, scaled_title.get_rect(center=(WINDOW_WIDTH//2, 150)))
        
        color = COLOR_ACCENT_BLUE if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        self.screen.blit(self.font.render(self.nickname, True, COLOR_TEXT_DARK), (self.input_rect.x+10, self.input_rect.y+5))
        
        if not self.nickname and not self.input_active:
            self.screen.blit(self.small_font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150,150,150)), (self.input_rect.x+10, self.input_rect.y+10))
        if self.err_msg:
            self.screen.blit(self.small_font.render(self.err_msg, True, COLOR_ACCENT_RED), (WINDOW_WIDTH//2-100, self.input_rect.bottom+10))
        
        txt = TEXTS[self.app.lang]
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_set, txt['setting']), (self.btn_cred, txt['credit']),
            (self.btn_tut, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        for rect, label in buttons: self._draw_btn(rect, label)

        if self.modal: self._draw_modal()

    def _draw_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        draw_rect = rect.copy()
        if rect.collidepoint(mouse_pos):
            draw_rect.x += random.randint(-2, 2); draw_rect.y += random.randint(-2, 2)
            color = COLOR_ACCENT_BLUE
        else: color = (255, 200, 150)
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, width=3, border_radius=15)
        t = self.font.render(text, True, COLOR_TEXT_DARK)
        self.screen.blit(t, t.get_rect(center=draw_rect.center))

    def _draw_modal(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR); self.screen.blit(overlay, (0,0))
        
        pygame.draw.rect(self.screen, POPUP_BG_COLOR, self.modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100,100,100), self.modal_rect, 3, border_radius=10)
        
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_close, border_radius=5)
        self.screen.blit(self.font.render("X", True, (255,255,255)), self.btn_close.move(5, -2))
        
        txt = TEXTS[self.app.lang]
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        top_y = self.modal_rect.top

        if self.modal == 'LOAD':
            title = self.font.render(txt['load_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            if not self.saved_files:
                self.screen.blit(self.small_font.render(txt['empty'], True, (150,150,150)), (cx-30, cy))
            for i, f in enumerate(self.saved_files[:6]):
                y = top_y + 80 + i*50 
                rect_file = pygame.Rect(cx - 150, y, 240, 40)
                
                if i == self.delete_confirm_idx:
                    pygame.draw.rect(self.screen, (255, 200, 200), rect_file, border_radius=5)
                    self.screen.blit(self.small_font.render(txt['delete_confirm'], True, (200,0,0)), (rect_file.x+5, rect_file.y+8))
                elif i == self.rename_idx:
                    pygame.draw.rect(self.screen, (255,255,255), rect_file, border_radius=5)
                    pygame.draw.rect(self.screen, (0,0,255), rect_file, 2, border_radius=5)
                    self.screen.blit(self.small_font.render(self.rename_text, True, (0,0,0)), (rect_file.x+5, rect_file.y+8))
                else:
                    pygame.draw.rect(self.screen, (220,220,255), rect_file, border_radius=5)
                    name = f.replace("save_", "").replace(".json", "")
                    self.screen.blit(self.small_font.render(name, True, (0,0,0)), (rect_file.x+10, rect_file.y+8))
                
                pygame.draw.rect(self.screen, (255, 200, 100), (cx + 95, y, 30, 40), border_radius=5)
                self.screen.blit(self.small_font.render("E", True, (0,0,0)), (cx + 102, y+8))
                pygame.draw.rect(self.screen, (200, 100, 100), (cx + 130, y, 30, 40), border_radius=5)
                self.screen.blit(self.small_font.render("X", True, (255,255,255)), (cx + 137, y+8))

        elif self.modal == 'SETTING':
            title = self.font.render(txt['setting'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 30)))
            
            # Ngôn ngữ
            self.screen.blit(self.small_font.render(txt['lang_label'], True, (0,0,0)), (cx - 150, cy - 80))
            lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
            pygame.draw.rect(self.screen, (100, 200, 100), lang_rect, border_radius=5)
            self.screen.blit(self.small_font.render(self.app.lang, True, (255,255,255)), (lang_rect.x+40, lang_rect.y+2))

            # Music Slider
            self.screen.blit(self.small_font.render(txt['music_label'], True, (0,0,0)), (cx - 150, cy - 20))
            music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
            pygame.draw.rect(self.screen, (200,200,200), music_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100,100,255), (music_rect.x, music_rect.y, music_rect.width * self.vol_music, 20), border_radius=10)
            pygame.draw.circle(self.screen, (50,50,200), (int(music_rect.x + music_rect.width * self.vol_music), music_rect.centery), 12)

            # SFX Slider
            self.screen.blit(self.small_font.render(txt['sfx_label'], True, (0,0,0)), (cx - 150, cy + 40))
            sfx_rect = pygame.Rect(cx + 20, cy + 40, 200, 20)
            pygame.draw.rect(self.screen, (200,200,200), sfx_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100,255,100), (sfx_rect.x, sfx_rect.y, sfx_rect.width * self.vol_sfx, 20), border_radius=10)
            pygame.draw.circle(self.screen, (50,200,50), (int(sfx_rect.x + sfx_rect.width * self.vol_sfx), sfx_rect.centery), 12)

            # Back Button
            back_rect = pygame.Rect(cx - 60, cy + 120, 120, 40)
            pygame.draw.rect(self.screen, (200, 200, 100), back_rect, border_radius=10)
            self.screen.blit(self.font.render(txt['btn_back'], True, (0,0,0)), (back_rect.x+10, back_rect.y+2))

        elif self.modal == 'CREDIT':
            title = self.font.render(txt['credit_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            y = top_y + 100
            for line in txt['credit_content']:
                t = self.small_font.render(line, True, (0,0,0))
                self.screen.blit(t, t.get_rect(center=(cx, y)))
                y += 35

        elif self.modal == 'TUTORIAL':
            title = self.font.render(txt['tut_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            y = top_y + 100
            for line in txt['tut_content']:
                t = self.small_font.render(line, True, (0,0,0))
                self.screen.blit(t, (self.modal_rect.x + 50, y))
                y += 35