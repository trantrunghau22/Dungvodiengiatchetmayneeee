import pygame
import os
import json
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env
from game.settings import *

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        self._load_assets()
        
        # --- Layout Buttons (2 cột, 3 hàng) ---
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2 + 50
        w, h = 180, 50
        gap = 20
        
        # Cột 1
        self.btn_new = pygame.Rect(cx - w - gap, cy - h - gap, w, h)
        self.btn_load = pygame.Rect(cx - w - gap, cy, w, h)
        self.btn_setting = pygame.Rect(cx - w - gap, cy + h + gap, w, h)
        
        # Cột 2
        self.btn_credit = pygame.Rect(cx + gap, cy - h - gap, w, h)
        self.btn_tutorial = pygame.Rect(cx + gap, cy, w, h)
        self.btn_exit = pygame.Rect(cx + gap, cy + h + gap, w, h)

        # --- Trạng thái Modal ---
        self.modal = None # 'NEW_GAME', 'LOAD', 'SETTING', 'TUTORIAL', 'CREDIT', 'EXIT'
        self.saved_files = []
        self.file_rects = []
        self.del_file_rects = []
        
        self.modal_rect = pygame.Rect(150, 150, 500, 350)
        self.btn_close = pygame.Rect(self.modal_rect.right - 40, self.modal_rect.top + 10, 30, 30)

    def _load_assets(self):
        # Font load logic (giữ nguyên để tránh lỗi)
        self.font_title = pygame.font.SysFont("arial", 80, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)
        
        # Thử load font custom nếu có
        fpath = os.path.join(FONT_DIR, 'shin_font.ttf')
        if os.path.exists(fpath):
            self.font_title = pygame.font.Font(fpath, 80)
            self.font_btn = pygame.font.Font(fpath, 26)
            self.font_small = pygame.font.Font(fpath, 22)

    def handle_event(self, event):
        # Nếu đang mở Modal -> Xử lý riêng
        if self.modal:
            self._handle_modal_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_new.collidepoint(pos): self.modal = 'NEW_GAME'
            elif self.btn_load.collidepoint(pos): 
                self._scan_files()
                self.modal = 'LOAD'
            elif self.btn_tutorial.collidepoint(pos): self.modal = 'TUTORIAL'
            elif self.btn_credit.collidepoint(pos): self.modal = 'CREDIT'
            elif self.btn_setting.collidepoint(pos): self.modal = 'SETTING'
            elif self.btn_exit.collidepoint(pos): self.modal = 'EXIT'

    def _handle_modal_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Nút Close chung cho mọi modal (trừ Exit)
            if self.modal != 'EXIT' and self.btn_close.collidepoint(pos):
                self.modal = None
                return

            # --- Logic riêng từng modal ---
            if self.modal == 'NEW_GAME':
                # Vẽ 2 nút: Start Normal & AI Mode
                btn_normal = pygame.Rect(self.modal_rect.centerx - 100, self.modal_rect.centery - 40, 200, 50)
                btn_ai = pygame.Rect(self.modal_rect.centerx - 100, self.modal_rect.centery + 30, 200, 50)
                
                if btn_normal.collidepoint(pos):
                    self._start_game(ai=False)
                elif btn_ai.collidepoint(pos):
                    self._start_game(ai=True)

            elif self.modal == 'SETTING':
                # Nút Language
                btn_lang = pygame.Rect(self.modal_rect.centerx + 20, self.modal_rect.top + 80, 100, 40)
                # Nút Sound
                btn_sound = pygame.Rect(self.modal_rect.centerx + 20, self.modal_rect.top + 140, 100, 40)
                
                if btn_lang.collidepoint(pos):
                    self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'
                elif btn_sound.collidepoint(pos):
                    self.app.sound_on = not self.app.sound_on

            elif self.modal == 'EXIT':
                btn_yes = pygame.Rect(self.modal_rect.centerx - 110, self.modal_rect.bottom - 80, 100, 40)
                btn_no = pygame.Rect(self.modal_rect.centerx + 10, self.modal_rect.bottom - 80, 100, 40)
                if btn_yes.collidepoint(pos):
                    pygame.quit(); exit()
                elif btn_no.collidepoint(pos):
                    self.modal = None

            elif self.modal == 'LOAD':
                # Check nút xóa file
                for i, r in enumerate(self.del_file_rects):
                    if r.collidepoint(pos):
                        try:
                            os.remove(self.saved_files[i]['filename'])
                            self._scan_files()
                        except: pass
                        return
                # Check chọn file
                for i, r in enumerate(self.file_rects):
                    if r.collidepoint(pos):
                        f = self.saved_files[i]
                        is_ai = (f['mode'] == 'AI')
                        self._load_game(f['filename'], is_ai)

    def _start_game(self, ai):
        self.app.ai_mode = ai
        # Reset env
        env = Game2048Env(size=GRID_SIZE)
        env.reset()
        self.app.active_scene = BoardScene(env, self.app)

    def _load_game(self, fname, ai):
        if not os.path.exists(fname): return
        env = Game2048Env(size=GRID_SIZE)
        try:
            env.load_game(fname)
            self.app.ai_mode = ai
            self.app.active_scene = BoardScene(env, self.app)
        except: pass

    def _scan_files(self):
        self.saved_files = []
        try:
            for f in os.listdir('.'):
                if f.endswith('.json'):
                    mode = "Normal"
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            d = json.load(fp)
                            if d.get('ai_mode'): mode = "AI"
                    except: pass
                    self.saved_files.append({'filename': f, 'mtime': os.path.getmtime(f), 'mode': mode})
            self.saved_files.sort(key=lambda x: x['mtime'], reverse=True)
        except: pass

    def render(self):
        self.window.fill(BACKGROUND_COLOR)
        
        # Title
        title = self.font_title.render("2048 SHIN", True, (243, 178, 122))
        self.window.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 150)))

        txt = TEXTS[self.app.lang]

        # Draw 6 buttons
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_setting, txt['setting']), (self.btn_credit, txt['credit']),
            (self.btn_tutorial, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        for rect, label in buttons:
            self._draw_btn(rect, label)

        # Draw Modal
        if self.modal:
            self._render_modal()

    def _render_modal(self):
        # Dim background
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,150))
        self.window.blit(s, (0,0))
        
        # Modal Box
        pygame.draw.rect(self.window, (250, 248, 239), self.modal_rect, border_radius=15)
        pygame.draw.rect(self.window, TEXT_COLOR, self.modal_rect, width=3, border_radius=15)
        
        txt = TEXTS[self.app.lang]

        # Close button (trừ Exit)
        if self.modal != 'EXIT':
            pygame.draw.rect(self.window, (200, 50, 50), self.btn_close, border_radius=5)
            x_txt = self.font_btn.render("X", True, (255,255,255))
            self.window.blit(x_txt, x_txt.get_rect(center=self.btn_close.center))

        # Content
        if self.modal == 'NEW_GAME':
            b1 = pygame.Rect(self.modal_rect.centerx - 100, self.modal_rect.centery - 40, 200, 50)
            b2 = pygame.Rect(self.modal_rect.centerx - 100, self.modal_rect.centery + 30, 200, 50)
            self._draw_btn(b1, txt['start_normal'], (237, 204, 97))
            self._draw_btn(b2, txt['start_ai'], (237, 150, 97))

        elif self.modal == 'EXIT':
            msg = self.font_btn.render(txt['ask_exit'], True, TEXT_COLOR)
            self.window.blit(msg, msg.get_rect(center=(self.modal_rect.centerx, self.modal_rect.top + 80)))
            b1 = pygame.Rect(self.modal_rect.centerx - 110, self.modal_rect.bottom - 100, 100, 40)
            b2 = pygame.Rect(self.modal_rect.centerx + 10, self.modal_rect.bottom - 100, 100, 40)
            self._draw_btn(b1, txt['yes'], (200, 80, 80))
            self._draw_btn(b2, txt['no'], (100, 200, 100))

        elif self.modal == 'SETTING':
            # Label
            lbl_lang = self.font_btn.render(txt['lang'], True, TEXT_COLOR)
            lbl_snd = self.font_btn.render(txt['sound'], True, TEXT_COLOR)
            self.window.blit(lbl_lang, (self.modal_rect.x + 50, self.modal_rect.top + 90))
            self.window.blit(lbl_snd, (self.modal_rect.x + 50, self.modal_rect.top + 150))
            
            # Value Btns
            b_lang = pygame.Rect(self.modal_rect.centerx + 20, self.modal_rect.top + 80, 120, 40)
            b_snd = pygame.Rect(self.modal_rect.centerx + 20, self.modal_rect.top + 140, 120, 40)
            
            val_lang = "TIẾNG VIỆT" if self.app.lang == 'VI' else "ENGLISH"
            val_snd = txt['on'] if self.app.sound_on else txt['off']
            
            self._draw_btn(b_lang, val_lang, (200, 200, 200))
            self._draw_btn(b_snd, val_snd, (200, 200, 200))

        elif self.modal == 'TUTORIAL':
            y = self.modal_rect.top + 50
            for line in txt['tut_content']:
                t = self.font_small.render(line, True, TEXT_COLOR)
                self.window.blit(t, (self.modal_rect.x + 30, y))
                y += 35

        elif self.modal == 'CREDIT':
            y = self.modal_rect.centery - 40
            for line in txt['credit_content']:
                t = self.font_btn.render(line, True, TEXT_COLOR)
                self.window.blit(t, t.get_rect(center=(self.modal_rect.centerx, y)))
                y += 40

        elif self.modal == 'LOAD':
            self.file_rects = []
            self.del_file_rects = []
            y = self.modal_rect.top + 50
            
            if not self.saved_files:
                t = self.font_small.render("No files", True, (150,150,150))
                self.window.blit(t, (self.modal_rect.x+50, y))
            
            for i, f in enumerate(self.saved_files[:5]): # Show max 5
                rect = pygame.Rect(self.modal_rect.x+20, y + i*45, self.modal_rect.width-80, 40)
                self.file_rects.append(rect)
                
                # Nút Xóa
                d_rect = pygame.Rect(rect.right + 10, rect.y, 30, 40)
                self.del_file_rects.append(d_rect)
                
                pygame.draw.rect(self.window, (240, 240, 240), rect, border_radius=5)
                fname = f['filename'].replace('.json', '')
                t = self.font_small.render(f"{fname} ({f['mode']})", True, TEXT_COLOR)
                self.window.blit(t, (rect.x+10, rect.centery - t.get_height()//2))
                
                # Draw Del X
                pygame.draw.rect(self.window, (200, 80, 80), d_rect, border_radius=5)
                xt = self.font_small.render("X", True, (255,255,255))
                self.window.blit(xt, xt.get_rect(center=d_rect.center))

    def _draw_btn(self, rect, text, color=(246, 178, 107)):
        pygame.draw.rect(self.window, color, rect, border_radius=10)
        pygame.draw.rect(self.window, (100, 50, 0), rect, width=2, border_radius=10)
        t = self.font_btn.render(text, True, (0,0,0))
        self.window.blit(t, t.get_rect(center=rect.center))

    def update(self, dt): pass
