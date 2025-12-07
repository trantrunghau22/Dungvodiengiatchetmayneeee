import pygame
import os
import time
import random
from game.settings import *
from game.core.env_2048 import UP, DOWN, LEFT, RIGHT
from game.core.env_2048 import Game2048Env 

KEY_TO_ACTION = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}

TOP_SCORE_FILE = "top_score.txt"

class BoardScene:
    def __init__(self, env, app):
        self.app = app
        self.screen = app.window 
        self.env = env           
        
        self.state = self.env.get_state() 
        self.game_over = False
        self.player_nickname = getattr(app, 'username', 'Player')
        
        self.start_time = time.time()
        self.env.total_time = getattr(self.env, 'total_time', 0) 
        self.top_score = self._load_top_score()
        
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.font_guide = pygame.font.SysFont(FONT_NAME, 18, bold=False) 
        
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)
        
        self.replay_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 100, 50)
        self.quit_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 + 50, 100, 50)

        self.last_move_time = 0
        self.move_delay = 150 

        # --- Popup States ---
        self.show_exit_confirm = False # Popup xác nhận thoát
        self.show_overwrite_confirm = False # Popup xác nhận ghi đè
        self.pending_quit = False # Cờ đánh dấu có thoát sau khi lưu không

        # Nút cho popup Thoát
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.btn_save_quit = pygame.Rect(cx - 100, cy - 60, 200, 40)
        self.btn_quit_nosave = pygame.Rect(cx - 100, cy, 200, 40)
        self.btn_cancel_exit = pygame.Rect(cx - 100, cy + 60, 200, 40)

        # Nút cho popup Ghi đè
        self.btn_overwrite = pygame.Rect(cx - 110, cy + 20, 100, 40)
        self.btn_cancel_save = pygame.Rect(cx + 10, cy + 20, 100, 40)

    def get_current_max_tile_score(self):
        return self.env.get_score() 
    
    def _load_top_score(self):
        try:
            with open(TOP_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_top_score(self):
        current_score = self.get_current_max_tile_score()
        if current_score > self.top_score:
            self.top_score = current_score
            with open(TOP_SCORE_FILE, 'w') as f:
                f.write(str(self.top_score))

    def _perform_save_game(self):
        """Hàm thực hiện lưu game thực sự"""
        filename = f"{self.player_nickname}"
        try:
            # Cập nhật thời gian chơi
            self.env.total_time += time.time() - self.start_time
            self.start_time = time.time() # Reset mốc thời gian
            
            current_ai_mode = self.app.ai_mode
            saved_path = self.env.save_game(filename, ai_mode=current_ai_mode)
            print(f"Game saved successfully to: {saved_path} (AI Mode: {current_ai_mode})")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def draw_rounded(self, surf, rect, color, radius=TILE_RADIUS):
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    def render_header(self):
        current_score = self.get_current_max_tile_score() 
        
        title = self.font_title.render("2048", True, TEXT_COLOR)
        self.screen.blit(title, (355, 40))

        score_rect = pygame.Rect(WINDOW_WIDTH - 150, 40, 145, 50)
        self.draw_rounded(self.screen, score_rect, SCORE_BG_COLOR)
        scr_text = self.font_small.render(f"Score: {current_score}", True, (255,255,255))
        self.screen.blit(scr_text, (score_rect.x + 16, score_rect.y + 14))

        nickname_rect = pygame.Rect(5, 40, 160, 50)
        self.draw_rounded(self.screen, nickname_rect, SCORE_BG_COLOR)
        nick_text = self.font_small.render(f"P: {self.player_nickname}", True, (255,255,255))
        self.screen.blit(nick_text, (nickname_rect.x + 10, nickname_rect.y + 14)) 
        
        top_score_rect = pygame.Rect(WINDOW_WIDTH - 300, 40, 145, 50)
        self.draw_rounded(self.screen, top_score_rect, SCORE_BG_COLOR)
        top_score_text = self.font_small.render(f"Top: {self.top_score}", True, (255,255,255))
        self.screen.blit(top_score_text, (top_score_rect.x + 16, top_score_rect.y + 14))

        if not self.game_over:
             elapsed_time = int(time.time() - self.start_time + self.env.total_time)
        else:
             elapsed_time = int(self.env.total_time)
             
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        
        time_text = self.font_small.render(time_str, True, TEXT_COLOR)
        self.screen.blit(time_text, (WINDOW_WIDTH//2 - 60, 90))

    def render_instructions(self):
        text = "Controls: [Arrows/WASD] Move   [S] Save Game   [R] Replay   [Q] Menu"
        guide_surf = self.font_guide.render(text, True, (119, 110, 101)) 
        guide_rect = guide_surf.get_rect(center=(WINDOW_WIDTH // 2, 115))
        self.screen.blit(guide_surf, guide_rect)

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)
        self.state = self.env.get_state()
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = self.board_rect.x + TILE_GAP + c * (self.tile_size + TILE_GAP)
                y = self.board_rect.y + TILE_GAP + r * (self.tile_size + TILE_GAP)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                
                val = int(self.state[r, c])
                color = TILE_COLORS.get(val, DEFAULT_LARGE_TILE_COLOR)
                self.draw_rounded(self.screen, rect, color, radius=TILE_RADIUS)
                
                if val != 0:
                    digits = len(str(val))
                    size = 48 if digits <= 3 else max(26, 100 - digits * 10)
                    font = pygame.font.SysFont(FONT_NAME, size, bold=True)
                    text_color = (0,0,0) if val <= 4 else (255,255,255)
                    text = font.render(str(val), True, text_color)
                    self.screen.blit(text, text.get_rect(center=rect.center))

    def render_game_over(self):
        if not self.game_over:
            return
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))
        
        go_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(go_text, go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
        
        self.draw_rounded(self.screen, self.replay_rect, (243, 178, 122))
        replay_label = self.font_button.render("REPLAY", True, (255,255,255))
        self.screen.blit(replay_label, replay_label.get_rect(center=self.replay_rect.center))
        
        self.draw_rounded(self.screen, self.quit_rect, (243, 178, 122))
        quit_label = self.font_button.render("MENU", True, (255,255,255))
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_rect.center))

    # --- Render Popup xác nhận thoát ---
    def render_exit_confirm(self):
        if not self.show_exit_confirm: return
        
        # Nền mờ
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # Khung thoại
        box_rect = pygame.Rect(WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT//2 - 120, 360, 260)
        pygame.draw.rect(self.screen, (250, 248, 239), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (119, 110, 101), box_rect, width=3, border_radius=10)

        # Tiêu đề
        msg = self.font_button.render("Unsaved progress will be lost!", True, (119, 110, 101))
        self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 90)))

        # Nút Save & Quit
        self.draw_rounded(self.screen, self.btn_save_quit, (237, 204, 97))
        txt = self.font_button.render("Save & Quit", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_save_quit.center))

        # Nút Quit without Saving
        self.draw_rounded(self.screen, self.btn_quit_nosave, (237, 97, 97))
        txt = self.font_button.render("Quit without Saving", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_quit_nosave.center))

        # Nút Cancel
        self.draw_rounded(self.screen, self.btn_cancel_exit, (119, 110, 101))
        txt = self.font_button.render("Cancel", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_cancel_exit.center))

    # --- Render Popup xác nhận ghi đè ---
    def render_overwrite_confirm(self):
        if not self.show_overwrite_confirm: return
        
        # Nền mờ
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # Khung thoại
        box_rect = pygame.Rect(WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT//2 - 100, 360, 200)
        pygame.draw.rect(self.screen, (250, 248, 239), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (119, 110, 101), box_rect, width=3, border_radius=10)

        # Tiêu đề
        msg1 = self.font_button.render(f"File '{self.player_nickname}' exists.", True, (119, 110, 101))
        msg2 = self.font_button.render("Overwrite it?", True, (119, 110, 101))
        self.screen.blit(msg1, msg1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60)))
        self.screen.blit(msg2, msg2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30)))

        # Nút Overwrite
        self.draw_rounded(self.screen, self.btn_overwrite, (237, 204, 97))
        txt = self.font_button.render("Yes", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_overwrite.center))

        # Nút Cancel
        self.draw_rounded(self.screen, self.btn_cancel_save, (119, 110, 101))
        txt = self.font_button.render("No", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_cancel_save.center))

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_instructions()
        self.render_board()
        self.render_game_over()
        
        # Vẽ popup
        if self.show_exit_confirm:
            self.render_exit_confirm()
        elif self.show_overwrite_confirm:
            self.render_overwrite_confirm()

    def handle_event(self, event):
        from game.scenes.intro import IntroScreen 

        # --- 1. Xử lý Popup Xác nhận Thoát ---
        if self.show_exit_confirm:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.btn_save_quit.collidepoint(pos):
                    # Lưu rồi thoát (kiểm tra ghi đè)
                    if self._check_save_and_overwrite_logic(quit_after=True):
                        # Nếu lưu thành công ngay (ko cần ghi đè) -> tự thoát trong hàm check
                        pass
                
                elif self.btn_quit_nosave.collidepoint(pos):
                    self._save_top_score() 
                    self.app.active_scene = IntroScreen(self.app)
                
                elif self.btn_cancel_exit.collidepoint(pos):
                    self.show_exit_confirm = False
            return

        # --- 2. Xử lý Popup Xác nhận Ghi đè ---
        if self.show_overwrite_confirm:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.btn_overwrite.collidepoint(pos):
                    self._perform_save_game()
                    self.show_overwrite_confirm = False
                    
                    if getattr(self, 'pending_quit', False):
                        self._save_top_score() 
                        self.app.active_scene = IntroScreen(self.app)

                elif self.btn_cancel_save.collidepoint(pos):
                    self.show_overwrite_confirm = False
                    self.pending_quit = False
            return

        # --- 3. Xử lý Game Over ---
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_q:
                    self.app.active_scene = IntroScreen(self.app)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.replay_rect.collidepoint(event.pos):
                    self.reset_game()
                elif self.quit_rect.collidepoint(event.pos):
                    self.app.active_scene = IntroScreen(self.app)
            return

        # --- 4. Xử lý Chơi Game ---
        if event.type == pygame.KEYDOWN:
            current_time = pygame.time.get_ticks()

            if event.key == pygame.K_r:
                self.reset_game()
            
            elif event.key == pygame.K_s:
                self.pending_quit = False
                self._check_save_and_overwrite_logic()

            elif event.key == pygame.K_q:
                self.show_exit_confirm = True

            elif event.key in KEY_TO_ACTION:
                if current_time - self.last_move_time < self.move_delay:
                    return 
                
                action = KEY_TO_ACTION[event.key]
                self._perform_move(action)
                self.last_move_time = current_time

    def _check_save_and_overwrite_logic(self, quit_after=False):
        """Kiểm tra xem file đã tồn tại chưa để hiện popup cảnh báo"""
        filename = f"{self.player_nickname}.json"
        
        if os.path.exists(filename):
            self.show_exit_confirm = False 
            self.show_overwrite_confirm = True
            self.pending_quit = quit_after 
            return False 
        else:
            self._perform_save_game()
            if quit_after:
                self._save_top_score() 
                # Trick để import cục bộ và chuyển cảnh
                self.app.active_scene = self.app.active_scene.__class__(self.env, self.app)
                from game.scenes.intro import IntroScreen 
                self.app.active_scene = IntroScreen(self.app)
            return True

    def _perform_move(self, action):
        s, r, d, info = self.env.step(action)
        if info.get('moved', True):
            self.state = s
            current_score = self.get_current_max_tile_score()
            if current_score > self.top_score:
                self.top_score = current_score
            
            if d: 
                self.game_over = True
                self.env.total_time += time.time() - self.start_time
                self._save_top_score()

    def reset_game(self):
        self.state = self.env.reset()
        self.game_over = False
        self._load_top_score()
        self.start_time = time.time()
        self.env.total_time = 0

    def update(self, dt):
        pass
