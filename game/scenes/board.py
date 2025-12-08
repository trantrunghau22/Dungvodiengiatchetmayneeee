import pygame
import os
import time
from game.settings import *
from game.core.env_2048 import UP, DOWN, LEFT, RIGHT

KEY_TO_ACTION = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}

class BoardScene:
    def __init__(self, env, app):
        self.app = app
        self.screen = app.window 
        self.env = env           
        self.state = self.env.get_state() 
        self.game_over = False
        
        # Load assets (Font)
        # Ưu tiên font custom nếu có
        fpath = os.path.join(FONT_DIR, 'shin_font.ttf')
        if os.path.exists(fpath):
            self.font_score = pygame.font.Font(fpath, 30)
            self.font_tile = pygame.font.Font(fpath, 40)
            self.font_popup = pygame.font.Font(fpath, 24)
        else:
            self.font_score = pygame.font.SysFont(FONT_NAME, 30, bold=True)
            self.font_tile = pygame.font.SysFont(FONT_NAME, 40, bold=True)
            self.font_popup = pygame.font.SysFont("arial", 24)
        
        # Time & Score
        self.start_time = time.time()
        self.env.total_time = getattr(self.env, 'total_time', 0) 
        self._load_top_score()
        self.top_score = self.env.get_top_score() or 0

        # Anti-spam
        self.last_move_time = 0
        self.move_delay = 150 

        # --- SAVE GAME UI STATES ---
        self.mode = 'PLAY' # 'PLAY', 'INPUT_NAME', 'CONFIRM_OVERWRITE', 'EXIT_CONFIRM'
        self.save_name = ""
        self.pending_quit = False # Cờ đánh dấu có thoát sau khi lưu không
        
        # Popup Rects
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.popup_rect = pygame.Rect(cx - 200, cy - 100, 400, 200)
        self.input_rect = pygame.Rect(cx - 150, cy, 300, 40)
        self.btn_confirm_1 = pygame.Rect(cx - 110, cy + 60, 100, 40) # Save / Overwrite / Yes
        self.btn_confirm_2 = pygame.Rect(cx + 10, cy + 60, 100, 40)  # Rename / No
        
        # Game Over Buttons
        self.replay_rect = pygame.Rect(cx - 120, cy + 50, 100, 50)
        self.quit_rect = pygame.Rect(cx + 20, cy + 50, 100, 50)

        # Board Layout
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_WIDTH - total_gap) // GRID_SIZE
        # Căn giữa bàn cờ hoặc dùng vị trí cố định
        self.board_rect = pygame.Rect(BOARD_MARGIN_LEFT, BOARD_MARGIN_TOP, BOARD_WIDTH, BOARD_HEIGHT)

    def _load_top_score(self):
        try:
            with open(TOP_SCORE_FILE, 'r') as f:
                self.env.update_top_score(int(f.read().strip()))
        except: pass

    def handle_event(self, event):
        # 1. Xử lý nhập tên file
        if self.mode == 'INPUT_NAME':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._check_filename()
                elif event.key == pygame.K_BACKSPACE:
                    self.save_name = self.save_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.mode = 'PLAY'
                else:
                    if len(self.save_name) < 15: self.save_name += event.unicode
            return

        # 2. Xử lý Popup Confirm (Overwrite / Exit)
        if self.mode in ['CONFIRM_OVERWRITE', 'EXIT_CONFIRM']:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Nút Trái (Ghi đè / Có thoát)
                if self.btn_confirm_1.collidepoint(pos):
                    if self.mode == 'CONFIRM_OVERWRITE':
                        self._do_save(overwrite=True)
                    elif self.mode == 'EXIT_CONFIRM':
                        from game.scenes.intro import IntroScreen
                        self.app.active_scene = IntroScreen(self.app)
                
                # Nút Phải (Đổi tên / Không thoát)
                elif self.btn_confirm_2.collidepoint(pos):
                    if self.mode == 'CONFIRM_OVERWRITE':
                        self.mode = 'INPUT_NAME' # Quay lại nhập tên
                    elif self.mode == 'EXIT_CONFIRM':
                        self.mode = 'PLAY'
            return
        
        # 3. Xử lý Game Over
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.replay_rect.collidepoint(event.pos):
                    self.env.reset()
                    self.start_time = time.time()
                    self.game_over = False
                elif self.quit_rect.collidepoint(event.pos):
                    from game.scenes.intro import IntroScreen
                    self.app.active_scene = IntroScreen(self.app)
            return

        # 4. Xử lý chơi game bình thường
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # Bật popup lưu
                self.mode = 'INPUT_NAME'
                self.save_name = ""
                self.pending_quit = False
            
            elif event.key == pygame.K_q: # Hỏi thoát
                self.mode = 'EXIT_CONFIRM'
            
            elif event.key == pygame.K_r: # Replay
                self.env.reset()
                self.start_time = time.time()
                self.game_over = False

            elif not self.game_over and event.key in KEY_TO_ACTION:
                # Anti-spam logic
                curr = pygame.time.get_ticks()
                if curr - self.last_move_time > self.move_delay:
                    self._move(KEY_TO_ACTION[event.key])
                    self.last_move_time = curr

    def _check_filename(self):
        if not self.save_name.strip(): return
        fname = self.save_name + ".json"
        if os.path.exists(fname):
            self.mode = 'CONFIRM_OVERWRITE'
        else:
            self._do_save()

    def _do_save(self, overwrite=False):
        self.env.total_time += time.time() - self.start_time
        self.start_time = time.time()
        try:
            self.env.save_game(self.save_name, ai_mode=self.app.ai_mode)
            print(f"Saved {self.save_name}!")
            self.mode = 'PLAY'
            # Nếu lệnh lưu đến từ việc muốn thoát game (Save & Quit - tính năng mở rộng)
            # Hiện tại ta chưa có nút Save & Quit riêng, nhưng logic này giúp mở rộng sau này
            if self.pending_quit:
                from game.scenes.intro import IntroScreen
                self.app.active_scene = IntroScreen(self.app)
        except Exception as e:
            print("Save error:", e)

    def _move(self, action):
        s, r, d, info = self.env.step(action)
        if info.get('moved'):
            self.state = s
            curr_max = self.env.get_score()
            if curr_max > self.top_score:
                self.top_score = curr_max
                with open(TOP_SCORE_FILE, 'w') as f: f.write(str(self.top_score))
            if d: self.game_over = True

    def update(self, dt):
        pass

    # --- RENDER ---
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_board()
        
        # Vẽ Popup đè lên nếu có
        if self.mode != 'PLAY':
            self._render_popup()
        elif self.game_over:
            self._render_gameover()

    def _render_popup(self):
        # Dim background
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,150))
        self.screen.blit(s, (0,0))
        
        # Box
        pygame.draw.rect(self.screen, (250, 248, 239), self.popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.popup_rect, width=3, border_radius=10)
        
        txt = TEXTS[self.app.lang]
        
        if self.mode == 'INPUT_NAME':
            title = self.font_popup.render(txt['save_title'], True, TEXT_COLOR)
            self.screen.blit(title, (self.popup_rect.centerx - title.get_width()//2, self.popup_rect.top + 20))
            
            sub = self.font_popup.render(txt['enter_name'], True, TEXT_COLOR)
            self.screen.blit(sub, (self.popup_rect.centerx - sub.get_width()//2, self.popup_rect.top + 60))
            
            pygame.draw.rect(self.screen, (255,255,255), self.input_rect, border_radius=5)
            pygame.draw.rect(self.screen, TEXT_COLOR, self.input_rect, width=2, border_radius=5)
            
            name_surf = self.font_popup.render(self.save_name, True, (0,0,0))
            self.screen.blit(name_surf, (self.input_rect.x + 10, self.input_rect.centery - name_surf.get_height()//2))
            
            hint = self.font_popup.render("(Enter to Save)", True, (150,150,150))
            self.screen.blit(hint, (self.popup_rect.centerx - hint.get_width()//2, self.popup_rect.bottom - 30))

        elif self.mode == 'CONFIRM_OVERWRITE':
            msg1 = self.font_popup.render(txt['overwrite_msg'], True, TEXT_COLOR)
            msg2 = self.font_popup.render(txt['overwrite_ask'], True, TEXT_COLOR)
            self.screen.blit(msg1, msg1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40)))
            self.screen.blit(msg2, msg2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10)))
            
            self._draw_btn(self.btn_confirm_1, txt['btn_overwrite'], (240, 100, 100))
            self._draw_btn(self.btn_confirm_2, txt['btn_rename'], (100, 200, 100))

        elif self.mode == 'EXIT_CONFIRM':
            msg = self.font_popup.render(txt['ask_exit'], True, TEXT_COLOR)
            self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30)))
            self._draw_btn(self.btn_confirm_1, txt['yes'], (200, 80, 80))
            self._draw_btn(self.btn_confirm_2, txt['no'], (100, 200, 100))

    def _draw_btn(self, rect, text, color):
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        t = self.font_popup.render(text, True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=rect.center))

    def render_header(self):
        txt = TEXTS[self.app.lang]
        score = self.env.get_score()
        
        # Vẽ điểm số góc phải
        pygame.draw.rect(self.screen, SCORE_BG_COLOR, (WINDOW_WIDTH-180, 40, 160, 60), border_radius=5)
        lbl = self.font_popup.render(f"{txt['score']}: {score}", True, (255,255,255))
        self.screen.blit(lbl, (WINDOW_WIDTH-170, 55))
        
        # Vẽ Top Score (nếu muốn)
        # ...

    def render_board(self):
        pygame.draw.rect(self.screen, BOARD_BG_COLOR, self.board_rect, border_radius=10)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = self.board_rect.x + TILE_GAP + c*(self.tile_size+TILE_GAP)
                y = self.board_rect.y + TILE_GAP + r*(self.tile_size+TILE_GAP)
                val = self.state[r][c]
                color = TILE_COLORS.get(val, DEFAULT_LARGE_TILE_COLOR)
                pygame.draw.rect(self.screen, color, (x,y,self.tile_size,self.tile_size), border_radius=TILE_RADIUS)
                if val:
                    t = self.font_tile.render(str(val), True, (0,0,0) if val<=4 else (255,255,255))
                    self.screen.blit(t, t.get_rect(center=(x+self.tile_size//2, y+self.tile_size//2)))

    def _render_gameover(self):
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,128))
        self.screen.blit(s, (0,0))
        
        txt = TEXTS[self.app.lang]
        t = self.font_tile.render(txt['game_over'], True, (255,0,0))
        self.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60)))
        
        # Nút Replay / Menu
        self._draw_btn(self.replay_rect, "REPLAY", (237, 204, 97))
        self._draw_btn(self.quit_rect, "MENU", (237, 204, 97))
