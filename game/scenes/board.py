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
        
        # Load assets
        fpath = os.path.join(FONT_DIR, 'shin_font.ttf')
        if os.path.exists(fpath):
            self.font_score = pygame.font.Font(fpath, 30)
            self.font_tile = pygame.font.Font(fpath, 40)
            self.font_popup = pygame.font.Font(fpath, 24)
            self.font_btn = pygame.font.Font(fpath, 20)
        else:
            self.font_score = pygame.font.SysFont(FONT_NAME, 30, bold=True)
            self.font_tile = pygame.font.SysFont(FONT_NAME, 40, bold=True)
            self.font_popup = pygame.font.SysFont("arial", 24)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)
        
        # Time & Score
        self.start_time = time.time()
        self.env.total_time = getattr(self.env, 'total_time', 0) 
        
        # [TOP SCORE] Load lại điểm cao nhất mỗi khi vào màn chơi
        self._load_top_score()
        self.top_score = self.env.get_top_score() or 0

        # Anti-spam
        self.last_move_time = 0
        self.move_delay = 150 
        self.unsaved_changes = False 

        # --- UI STATES ---
        self.mode = 'PLAY' 
        self.save_name = ""
        self.pending_quit = False
        
        # --- LAYOUT ---
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # Nút chức năng
        btn_y = BOARD_MARGIN_TOP + BOARD_HEIGHT + 20
        self.btn_reset = pygame.Rect(BOARD_MARGIN_LEFT, btn_y, 80, 40)
        self.btn_save  = pygame.Rect(BOARD_MARGIN_LEFT + 90, btn_y, 80, 40)
        self.btn_set   = pygame.Rect(BOARD_MARGIN_LEFT + 180, btn_y, 80, 40)
        self.btn_menu  = pygame.Rect(BOARD_MARGIN_LEFT + 270, btn_y, 80, 40)

        # Popup Save/Exit
        self.popup_rect = pygame.Rect(cx - 200, cy - 100, 400, 200)
        self.input_rect = pygame.Rect(cx - 150, cy, 300, 40)
        self.btn_confirm_1 = pygame.Rect(cx - 110, cy + 60, 100, 40)
        self.btn_confirm_2 = pygame.Rect(cx + 10, cy + 60, 100, 40)
        
        # Popup Setting (Trong game)
        self.setting_rect = pygame.Rect(cx - 150, cy - 100, 300, 200)
        self.btn_set_lang = pygame.Rect(cx - 60, cy - 30, 120, 40)
        # [UPDATE] Nút âm thanh rộng hơn
        self.btn_set_sound = pygame.Rect(cx - 80, cy + 30, 160, 40)
        
        # Game Over Buttons
        self.replay_rect = pygame.Rect(cx - 120, cy + 50, 100, 50)
        self.quit_rect = pygame.Rect(cx + 20, cy + 50, 100, 50)

        # Board Layout
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_WIDTH - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN_LEFT, BOARD_MARGIN_TOP, BOARD_WIDTH, BOARD_HEIGHT)

    def _load_top_score(self):
        try:
            if os.path.exists(TOP_SCORE_FILE):
                with open(TOP_SCORE_FILE, 'r') as f:
                    val = int(f.read().strip())
                    self.env.update_top_score(val)
        except: pass

    def _save_top_score(self):
        try:
            with open(TOP_SCORE_FILE, 'w') as f:
                f.write(str(self.top_score))
        except: pass

    def handle_event(self, event):
        # --- XỬ LÝ NÚT CLOSE (X) CHO POPUP ---
        if self.mode != 'PLAY':
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Xác định rect của popup hiện tại
                current_rect = self.setting_rect if self.mode == 'SETTING' else self.popup_rect
                # Vị trí nút X (Góc trên phải)
                close_btn_rect = pygame.Rect(current_rect.right - 35, current_rect.top + 5, 30, 30)
                
                if close_btn_rect.collidepoint(event.pos):
                    self.mode = 'PLAY' # Đóng popup quay lại chơi
                    return

        # 1. Nhập tên file
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

        # 2. Popup Setting
        if self.mode == 'SETTING':
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.btn_set_lang.collidepoint(pos):
                    self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'
                elif self.btn_set_sound.collidepoint(pos):
                    self.app.sound_on = not self.app.sound_on
            return

        # 3. Popup Confirm
        if self.mode in ['CONFIRM_OVERWRITE', 'EXIT_CONFIRM']:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.btn_confirm_1.collidepoint(pos):
                    if self.mode == 'CONFIRM_OVERWRITE':
                        self._do_save(overwrite=True)
                    elif self.mode == 'EXIT_CONFIRM':
                        self.mode = 'INPUT_NAME'
                        self.save_name = ""
                        self.pending_quit = True
                elif self.btn_confirm_2.collidepoint(pos):
                    if self.mode == 'CONFIRM_OVERWRITE':
                        self.mode = 'INPUT_NAME'
                    elif self.mode == 'EXIT_CONFIRM':
                        from game.scenes.intro import IntroScreen
                        self.app.active_scene = IntroScreen(self.app)
            return
        
        # 4. Game Over
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.replay_rect.collidepoint(event.pos):
                    # [FIXED] Reset hoàn toàn
                    self.state = self.env.reset()
                    self.start_time = time.time()
                    self.game_over = False
                    self.unsaved_changes = False
                elif self.quit_rect.collidepoint(event.pos):
                    self._save_top_score()
                    from game.scenes.intro import IntroScreen
                    self.app.active_scene = IntroScreen(self.app)
            return

        # 5. Chơi game
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # [FIXED] Nút RESET hoạt động đúng
            if self.btn_reset.collidepoint(pos):
                self.state = self.env.reset() # Cập nhật lại state bàn cờ
                self.game_over = False        # Đảm bảo tắt game over
                self.start_time = time.time()
                self.unsaved_changes = False
            
            elif self.btn_save.collidepoint(pos):
                self.mode = 'INPUT_NAME'
                self.save_name = ""
                self.pending_quit = False
            
            elif self.btn_set.collidepoint(pos):
                self.mode = 'SETTING'

            elif self.btn_menu.collidepoint(pos):
                self._request_exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.mode = 'INPUT_NAME'
                self.save_name = ""
                self.pending_quit = False
            
            elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self._request_exit()
            
            elif event.key == pygame.K_r:
                # [FIXED] Reset bằng phím tắt
                self.state = self.env.reset()
                self.game_over = False
                self.start_time = time.time()
                self.unsaved_changes = False

            elif not self.game_over and event.key in KEY_TO_ACTION:
                curr = pygame.time.get_ticks()
                if curr - self.last_move_time > self.move_delay:
                    self._move(KEY_TO_ACTION[event.key])
                    self.last_move_time = curr

    def _request_exit(self):
        if self.unsaved_changes:
            self.mode = 'EXIT_CONFIRM'
        else:
            self._save_top_score()
            from game.scenes.intro import IntroScreen
            self.app.active_scene = IntroScreen(self.app)

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
            self.unsaved_changes = False
            
            # Lưu luôn top score khi save game cho chắc ăn
            self._save_top_score()

            if self.pending_quit:
                from game.scenes.intro import IntroScreen
                self.app.active_scene = IntroScreen(self.app)
        except Exception as e:
            print("Save error:", e)

    def _move(self, action):
        s, r, d, info = self.env.step(action)
        if info.get('moved'):
            self.state = s
            self.unsaved_changes = True
            
            curr_max = self.env.get_score()
            if curr_max > self.top_score:
                self.top_score = curr_max
                # Lưu top score ngay khi phá kỷ lục
                self._save_top_score() 
                
            if d: self.game_over = True

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_board()
        self.render_buttons()
        
        if self.mode != 'PLAY':
            self._render_popup()
        elif self.game_over:
            self._render_gameover()

    def render_buttons(self):
        self._draw_btn_small(self.btn_reset, "RESET", (200, 100, 100))
        self._draw_btn_small(self.btn_save, "SAVE", (100, 200, 100))
        self._draw_btn_small(self.btn_set, "SETTING", (100, 100, 200))
        self._draw_btn_small(self.btn_menu, "MENU", (200, 200, 100))

    def _draw_btn_small(self, rect, text, color):
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 50, 50), rect, width=2, border_radius=8)
        t = self.font_btn.render(text, True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=rect.center))

    def _render_popup(self):
        # Dim background
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,150))
        self.screen.blit(s, (0,0))
        
        txt = TEXTS[self.app.lang]
        
        # Chọn khung popup để vẽ
        target_rect = self.setting_rect if self.mode == 'SETTING' else self.popup_rect
        self._draw_popup_box(target_rect)
        
        # --- VẼ NÚT X (CLOSE) ---
        close_rect = pygame.Rect(target_rect.right - 35, target_rect.top + 5, 30, 30)
        pygame.draw.rect(self.screen, (200, 60, 60), close_rect, border_radius=5)
        x_txt = self.font_btn.render("X", True, (255,255,255))
        self.screen.blit(x_txt, x_txt.get_rect(center=close_rect.center))
        # ------------------------

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
            
            self._draw_btn_small(self.btn_confirm_1, txt['btn_overwrite'], (240, 100, 100))
            self._draw_btn_small(self.btn_confirm_2, txt['btn_rename'], (100, 200, 100))

        elif self.mode == 'EXIT_CONFIRM':
            msg = self.font_popup.render("Chưa lưu game!", True, TEXT_COLOR)
            sub = self.font_popup.render("Bạn muốn lưu trước khi thoát?", True, TEXT_COLOR)
            self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))
            self.screen.blit(sub, sub.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20)))
            self._draw_btn_small(self.btn_confirm_1, txt['yes'], (100, 200, 100))
            self._draw_btn_small(self.btn_confirm_2, txt['no'], (200, 80, 80))

        elif self.mode == 'SETTING':
            title = self.font_popup.render(txt['setting'], True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.setting_rect.centerx, self.setting_rect.top + 20)))
            
            lang_txt = "TIẾNG VIỆT" if self.app.lang == 'VI' else "ENGLISH"
            # [UPDATE] Màu chữ ĐEN (0,0,0) cho nút Setting thay vì Trắng
            self._draw_btn_custom_text(self.btn_set_lang, lang_txt, (220, 220, 220), (0,0,0))
            
            sound_txt = f"{txt['sound']}: {txt['on'] if self.app.sound_on else txt['off']}"
            self._draw_btn_custom_text(self.btn_set_sound, sound_txt, (220, 220, 220), (0,0,0))

    def _draw_popup_box(self, rect):
        pygame.draw.rect(self.screen, (250, 248, 239), rect, border_radius=10)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, width=3, border_radius=10)

    # Hàm vẽ nút riêng cho Setting để đổi màu chữ
    def _draw_btn_custom_text(self, rect, text, bg_color, txt_color):
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 50, 50), rect, width=2, border_radius=8)
        t = self.font_btn.render(text, True, txt_color)
        self.screen.blit(t, t.get_rect(center=rect.center))

    def render_header(self):
        txt = TEXTS[self.app.lang]
        score = self.env.get_score()
        pygame.draw.rect(self.screen, SCORE_BG_COLOR, (WINDOW_WIDTH-180, 40, 160, 60), border_radius=5)
        lbl = self.font_popup.render(f"{txt['score']}: {score}", True, (255,255,255))
        self.screen.blit(lbl, (WINDOW_WIDTH-170, 55))
        
        # Hiển thị Top Score bên cạnh
        pygame.draw.rect(self.screen, SCORE_BG_COLOR, (WINDOW_WIDTH-350, 40, 160, 60), border_radius=5)
        top_lbl = self.font_popup.render(f"Top: {self.top_score}", True, (255,255,255))
        self.screen.blit(top_lbl, (WINDOW_WIDTH-340, 55))

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
        self._draw_btn_small(self.replay_rect, "REPLAY", (237, 204, 97))
        self._draw_btn_small(self.quit_rect, "MENU", (237, 204, 97))

    def update(self, dt): pass
