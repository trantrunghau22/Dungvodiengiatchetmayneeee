import pygame
from game.settings import *
from game.core.env_2048 import Game2048Env, UP, DOWN, LEFT, RIGHT

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

class BoardScene:
    def __init__(self, screen, player_nickname="Player"):
        self.screen = screen
        self.env = Game2048Env(size=GRID_SIZE)
        self.state = self.env.reset()
        self.game_over = False
        self.player_nickname = player_nickname
        self.top_score = self._load_top_score()
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.replay_rect = pygame.Rect(REPLAY_BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.quit_rect = pygame.Rect(QUIT_BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)

    def get_current_max_tile_score(self):
        max_val = 0
        if self.state is not None:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    val = int(self.state[r, c])
                    if val > max_val:
                        max_val = val
        return max_val
   
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
        nick_text = self.font_small.render(f"Player: {self.player_nickname}", True, (255,255,255))
        self.screen.blit(nick_text, (nickname_rect.x + 10, nickname_rect.y + 14)) 
        
        top_score_rect = pygame.Rect(WINDOW_WIDTH - 300, 40, 145, 50)
        self.draw_rounded(self.screen, top_score_rect, SCORE_BG_COLOR)
        top_score_text = self.font_small.render(f"Top: {self.top_score}", True, (255,255,255))
        self.screen.blit(top_score_text, (top_score_rect.x + 16, top_score_rect.y + 14))
    # ----------------------------------------------------

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)
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

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.replay_rect.collidepoint(mouse_pos):
                    self.reset_game()
                elif self.quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            elif event.key in KEY_TO_ACTION:
                action = KEY_TO_ACTION[event.key]
                s, r, d, info = self.env.step(action)
                self.state = s
                if d and info['terminal_reason'] == 'no_legal_moves':
                    self.game_over = True
                    self._save_top_score()

    def reset_game(self):
        self.state = self.env.reset()
        self.game_over = False
        self._load_top_score()

    def update(self):
        pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
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
        self.draw_rounded(self.screen, self.replay_rect, BUTTON_BG_COLOR)
        replay_label = self.font_button.render("REPLAY (R)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(replay_label, replay_label.get_rect(center=self.replay_rect.center))
        self.draw_rounded(self.screen, self.quit_rect, BUTTON_BG_COLOR)
        quit_label = self.font_button.render("QUIT (Q)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_rect.center))