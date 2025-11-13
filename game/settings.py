import pygame
import random
import math
import numpy as np # Thêm thư viện numpy

pygame.init()

#Hằng số cửa sổ và màn hình
FPS = 120
WIDTH, HEIGHT = 800, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock() # Thêm CLOCK (cho app.py)
pygame.display.set_caption("2048")

#Hằng số cho bàn cờ
ROWS = 4
COLS = 4
RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

#Màu sắc và font
OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

# Font
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
SCORE_FONT = pygame.font.SysFont("comicsans", 40, bold=True) # Thêm font cho điểm

MOVE_VEL = 20

#Hàm vẽ
class Tile:
    COLORS = {
        2: (237, 229, 218),
        4: (238, 225, 201),
        8: (243, 178, 122),
        16: (246, 150, 101),
        32: (247, 124, 95),
        64: (247, 95, 59),
        128: (237, 208, 115),
        256: (237, 204, 99),
        512: (236, 202, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
    }

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        # Lấy màu từ dict, nếu không có thì trả về màu mặc định (viền)
        return self.COLORS.get(self.value, OUTLINE_COLOR)

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        # Chỉ vẽ chữ nếu giá trị > 0
        if self.value > 0:
            text = FONT.render(str(self.value), 1, FONT_COLOR)
            window.blit(
                text,
                (
                    self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                    self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
                ),
            )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        # (Giữ nguyên hàm này của bạn)
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    
    window.fill(BACKGROUND_COLOR)

    # Vẽ các ô trống (ô giá trị 0)
 
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) not in tiles:
                # Lấy màu của ô số 0 (ô trống)
                color = (205, 192, 180) 
                pygame.draw.rect(window, color, (c * RECT_WIDTH, r * RECT_HEIGHT, RECT_WIDTH, RECT_HEIGHT))

    # Vẽ các ô có số
    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)
