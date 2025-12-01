import pygame
import os
from game.settings import *
from game.core.env_2048 import UP, DOWN, LEFT, RIGHT

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
        
        # SỬA LỖI: Dùng get_state() thay vì get_board()
        self.state = self.env.get_state() 
        
        self.game_over = False
        self.player_nickname = app.username
        self.top_score = self._load_top_score()
        
        # Font setup
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.font_guide = pygame.font.SysFont(FONT_NAME, 18, bold=False) # Font hướng dẫn
        
        # Buttons Rect
        self.replay_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 100, 50)
        self.quit_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 + 50, 100, 50)
        
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)

    def get_current_max_tile_score(self):
        return self.env.score 
    
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

    def render_instructions(self):
        # Nội dung hướng dẫn
        text = "Controls: [Arrows/WASD] Move   [S] Save Game   [R] Replay   [Q] Menu"
        # Tạo surface văn bản
        guide_surf = self.font_guide.render(text, True, (119, 110, 101)) 
        # Căn giữa theo chiều ngang, đặt ở vị trí y = 105
        guide_rect = guide_surf.get_rect(center=(WINDOW_WIDTH // 2, 105))
        # Vẽ lên màn hình
        self.screen.blit(guide_surf, guide_rect)

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)
        self.state = self.env.board 
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = self.board_rect.x + TILE_GAP + c * (self.tile_size + TILE_GAP)
                y = self.board_rect.y + TILE_GAP + r * (self.tile_size + TILE_GAP)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                
                val = int(self.state[r][c])
                color = TILE_COLORS.get(val, DEFAULT_LARGE_TILE_COLOR)
                self.draw_rounded(self.screen, rect, color, radius=TILE_RADIUS)
                
                if val != 0:
                    digits = len(str(val))
                    size = 48 if digits <= 3 else max(26, 100 - digits * 10)
                    font = pygame.font.SysFont(FONT_NAME, size, bold=True)
                    text_color = (0,0,0) if val <= 4 else (255,255,255)
                    text = font.render(str(val), True, text_color)
                    self.screen.blit(text, text.get_rect(center=rect.center))

    def handle_event(self, event):
        # Import cục bộ để tránh lỗi circular import
        from game.scenes.intro import IntroScreen 

        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_q:
                    self.app.active_scene = IntroScreen(self.app)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.replay_rect.collidepoint(mouse_pos):
                    self.reset_game()
                elif self.quit_rect.collidepoint(mouse_pos):
                    self.app.active_scene = IntroScreen(self.app)
            return

        # Xử lý chơi game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            
            # --- TÍNH NĂNG: Bấm S để lưu game ---
            elif event.key == pygame.K_s:
                filename = f"{self.player_nickname}_save"
                try:
                    saved_path = self.env.save_game(filename)
                    print(f"Game saved successfully to: {saved_path}")
                except Exception as e:
                    print(f"Error saving game: {e}")

            elif event.key == pygame.K_q:
                self.app.active_scene = IntroScreen(self.app)

            elif event.key in KEY_TO_ACTION:
                action = KEY_TO_ACTION[event.key]
                s, r, d, info = self.env.step(action)
                self.state = s
                if d: 
                    self.game_over = True
                    self._save_top_score()

    def reset_game(self):
        self.state = self.env.reset()
        self.game_over = False
        self._load_top_score()

    def update(self):
        if self.app.ai_mode and not self.game_over:
            pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        
        # Vẽ dòng hướng dẫn
        self.render_instructions()
        
        self.render_board()
        self.render_game_over()

    def render_game_over(self):
        if not self.game_over:
            return
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))
        
        go_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(go_text, go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
        
        # Replay Button
        self.draw_rounded(self.screen, self.replay_rect, (243, 178, 122))
        replay_label = self.font_button.render("REPLAY", True, (255,255,255))
        self.screen.blit(replay_label, replay_label.get_rect(center=self.replay_rect.center))
        
        # Menu Button
        self.draw_rounded(self.screen, self.quit_rect, (243, 178, 122))
        quit_label = self.font_button.render("MENU", True, (255,255,255))
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_rect.center))
