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
    def __init__(self, screen):
        self.screen = screen
        self.env = Game2048Env(size=GRID_SIZE)
        self.state = self.env.reset()

        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)

        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)

    def draw_rounded(self, surf, rect, color, radius=TILE_RADIUS):
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    def render_header(self):
        title = self.font_title.render("2048", True, TEXT_COLOR)
        self.screen.blit(title, (BOARD_MARGIN, 40))

        score_rect = pygame.Rect(WINDOW_WIDTH - 200, 40, 160, 50)
        self.draw_rounded(self.screen, score_rect, SCORE_BG_COLOR)
        scr_text = self.font_small.render(f"Score: {self.env.score}", True, (255,255,255))
        self.screen.blit(scr_text, (score_rect.x + 16, score_rect.y + 14))

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.state = self.env.reset()
            elif event.key in KEY_TO_ACTION:
                action = KEY_TO_ACTION[event.key]
                s, r, d, info = self.env.step(action)
                self.state = s

    def update(self):
        pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_board()