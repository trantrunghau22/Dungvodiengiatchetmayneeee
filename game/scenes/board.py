import pygame
import os
import time
from game.settings import *
from game.core.env_2048 import UP, DOWN, LEFT, RIGHT
from game.core.env_2048 import Game2048Env # Cần thiết cho việc tạo Env mới nếu cần

# --- Điều khiển ---
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
        
        # --- Trạng thái Game và Điểm ---
        self.state = self.env.get_state() 
        self.game_over = False
        self.player_nickname = getattr(app, 'username', 'Player')
        
        # Thêm biến thời gian để theo dõi thời gian chơi
        self.start_time = time.time()
        self.env.total_time = getattr(self.env, 'total_time', 0) # Lấy thời gian từ env nếu load game
        
        # Tải Top Score từ file (Logic của đoạn 2)
        self.top_score = self._load_top_score()
        
        # --- Cài đặt Font ---
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 24, bold=True) # Dùng font lớn hơn từ đoạn 1
        self.font_guide = pygame.font.SysFont(FONT_NAME, 18, bold=False) 
        
        # --- Kích thước và Vị trí ---
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)
        
        # Vị trí nút Game Over (sử dụng vị trí của đoạn 2 và kích thước của đoạn 1)
        self.replay_rect = pygame.Rect(WINDOW_WIDTH//2 - 145, WINDOW_HEIGHT//2 + 50, 140, 50)
        self.quit_rect = pygame.Rect(WINDOW_WIDTH//2 + 5, WINDOW_HEIGHT//2 + 50, 140, 50)

    # --- Chức năng Quản lý Top Score (Đoạn 2) ---
    def get_current_max_tile_score(self):
        # Trả về điểm (là ô lớn nhất) từ môi trường env_2048
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

    # --- Vẽ UI ---
    def draw_rounded(self, surf, rect, color, radius=TILE_RADIUS):
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    def render_header(self):
        current_score = self.get_current_max_tile_score() 
        
        # Vùng hiển thị điểm (dùng layout của đoạn 2, tinh chỉnh để hiển thị 3 mục)
        
        # 1. Nickname
        nickname_rect = pygame.Rect(5, 40, 160, 50)
        self.draw_rounded(self.screen, nickname_rect, SCORE_BG_COLOR)
        nick_text = self.font_small.render(f"P: {self.player_nickname}", True, (255,255,255))
        self.screen.blit(nick_text, (nickname_rect.x + 10, nickname_rect.y + 14)) 
        
        # 2. Top Score
        top_score_rect = pygame.Rect(WINDOW_WIDTH - 320, 40, 145, 50)
        self.draw_rounded(self.screen, top_score_rect, SCORE_BG_COLOR)
        top_score_text = self.font_small.render(f"Top: {self.top_score}", True, (255,255,255))
        self.screen.blit(top_score_text, (top_score_rect.x + 16, top_score_rect.y + 14))

        # 3. Current Score
        score_rect = pygame.Rect(WINDOW_WIDTH - 165, 40, 160, 50)
        self.draw_rounded(self.screen, score_rect, SCORE_BG_COLOR)
        scr_text = self.font_small.render(f"Score: {current_score}", True, (255,255,255))
        self.screen.blit(scr_text, (score_rect.x + 16, score_rect.y + 14))
        
        # Title
        title = self.font_title.render("2048", True, TEXT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 40))

        # Thời gian chơi (Đoạn 1)
        if not self.game_over:
             elapsed_time = int(time.time() - self.start_time)
        else:
             elapsed_time = int(self.env.total_time) # Dùng thời gian đã lưu khi game over
             
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        
        time_text = self.font_small.render(time_str, True, TEXT_COLOR)
        time_x = BOARD_MARGIN + (BOARD_SIZE - time_text.get_width()) // 2
        self.screen.blit(time_text, (time_x, BOARD_TOP - 40))

    def render_instructions(self):
        text = "Controls:   [Arrows/WASD] Move      [S] Save Game      [R] Replay      [Q] Menu"
        guide_surf = self.font_guide.render(text, True, (119, 110, 101)) 
        guide_rect = guide_surf.get_rect(center=(WINDOW_WIDTH // 2, 105))
        self.screen.blit(guide_surf, guide_rect)

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)
        
        # Cập nhật trạng thái trước khi vẽ
        self.state = self.env.get_state()
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Tính toán vị trí
                x = self.board_rect.x + TILE_GAP + c * (self.tile_size + TILE_GAP)
                y = self.board_rect.y + TILE_GAP + r * (self.tile_size + TILE_GAP)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                
                val = int(self.state[r, c]) # env_2048.py dùng numpy array nên có thể dùng [r, c]
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
            
        # Lớp phủ mờ (Đoạn 2)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Text GAME OVER (Đoạn 2)
        go_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(go_text, go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
        
        # Nut choi lai (R)
        self.draw_rounded(self.screen, self.replay_rect, (243, 178, 122))
        replay_label = self.font_button.render("REPLAY (R)", True, (255,255,255))
        self.screen.blit(replay_label, replay_label.get_rect(center=self.replay_rect.center))
        
        # Quay lai menu (Q)
        self.draw_rounded(self.screen, self.quit_rect, (243, 178, 122))
        quit_label = self.font_button.render("MENU (Q)", True, (255,255,255))
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_rect.center))

    # --- Xử lý sự kiện ---
    def handle_event(self, event):
        from game.scenes.intro import IntroScreen # Import trong hàm để tránh circular dependency

        # Xử lý sau khi Game Over
        if self.game_over:
            # Xử lý R (Replay) và Q (Quit)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_q:
                    self.app.active_scene = IntroScreen(self.app)
            
            # Xử lý click chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.replay_rect.collidepoint(mouse_pos):
                    self.reset_game()
                elif self.quit_rect.collidepoint(mouse_pos):
                    self.app.active_scene = IntroScreen(self.app)
            return

        # Xử lý khi đang chơi
        if event.type == pygame.KEYDOWN:
            # R: Replay
            if event.key == pygame.K_r:
                self.reset_game()
            
            # S: Save Game
            elif event.key == pygame.K_s:
                # Lưu game, sử dụng nickname để đặt tên file
                filename = f"{self.player_nickname}"
                try:
                    # Gán thời gian đã chơi vào env trước khi lưu
                    self.env.total_time = time.time() - self.start_time
                    saved_path = self.env.save_game(filename)
                    print(f"Game saved successfully to: {saved_path}")
                except Exception as e:
                    print(f"Error saving game: {e}")

            # Q: Quit to Menu
            elif event.key == pygame.K_q:
                # Đảm bảo điểm cao nhất được lưu trước khi quay về menu
                self._save_top_score() 
                self.app.active_scene = IntroScreen(self.app)

            # Nut di chuyen (Arrows/WASD)
            elif event.key in KEY_TO_ACTION:
                action = KEY_TO_ACTION[event.key]
                s, r, d, info = self.env.step(action)
                self.state = s
                
                # Cập nhật Top Score tức thì (Đoạn 1)
                self.top_score = max(self.top_score, self.env.score)
                
                if d: # Nếu game over
                    self.game_over = True
                    # Lưu lại thời gian chơi
                    self.env.total_time = time.time() - self.start_time
                    self._save_top_score() # Lưu điểm cao nhất vào file

    def reset_game(self):
        self.state = self.env.reset()
        self.game_over = False
        self._load_top_score()
        self.start_time = time.time() # Reset thời gian bắt đầu
        self.env.total_time = 0

    def update(self):
        # Chức năng cho AI (sẽ được code sau)
        if self.app.ai_mode and not self.game_over:
            # Thêm logic AI ở đây
            pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_instructions()
        self.render_board()
        self.render_game_over()
