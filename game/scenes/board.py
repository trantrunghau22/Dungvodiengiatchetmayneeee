import pygame
import time
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
        self.env = Game2048Env(size=GRID_SIZE)
        self.state = self.env.reset()
         
        self.player_nickname = player_nickname
        self.top_score = 0
        self.start_time = time.time()
        
        
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 24, bold=True)  
        
        
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)
        
        self.replay_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 150, BOARD_TOP + BOARD_SIZE // 2, 140, 50
        )
        self.quit_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 + 10, BOARD_TOP + BOARD_SIZE // 2, 140, 50
        )

  

    def draw_rounded(self, surf, rect, color, radius=TILE_RADIUS):
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    def reset_game(self):
        self.state = self.env.reset()
        
        self.env.total_time = 0 
        self.start_time = time.time()
        
   

    def render_header(self): 

        
        title = self.font_title.render("2048", True, TEXT_COLOR)
        self.screen.blit(title, (BOARD_MARGIN, 40))
        
        nick_text = self.font_small.render(
            f"Player: {self.player_nickname}", True, TEXT_COLOR
        )
        self.screen.blit(nick_text, (BOARD_MARGIN, 90))

       
        
     
        SCORE_FRAME_RECT = pygame.Rect(WINDOW_WIDTH - 200, 20, 160, 100)
        self.draw_rounded(self.screen, SCORE_FRAME_RECT, SCORE_BG_COLOR)
        
        
        SCORE_Y = SCORE_FRAME_RECT.y + 10
        SCORE_X = SCORE_FRAME_RECT.x + 10  
        
        scr_text = self.font_small.render(
            f"Score: {self.env.score}", True, (255, 255, 255)
        )
        self.screen.blit(scr_text, (SCORE_X, SCORE_Y))
        
        
        TOP_SCORE_Y = SCORE_Y + 40 
        
         
        TOP_SCORE_TEXT_COLOR = (200, 200, 200) 
        
        top_scr_text = self.font_small.render(
            f"Top: {self.top_score}", True, TOP_SCORE_TEXT_COLOR
        )
        self.screen.blit(top_scr_text, (SCORE_X, TOP_SCORE_Y))
        
         
        if not self.env.game_over:
            elapsed_time = int(time.time() - self.start_time)
        else:
            elapsed_time = int(self.env.total_time)
            
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        
        time_text = self.font_small.render(time_str, True, TEXT_COLOR)
        time_x = BOARD_MARGIN + (BOARD_SIZE - time_text.get_width()) // 2
        self.screen.blit(time_text, (time_x, BOARD_TOP - 40))

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Tính toán vị trí
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
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        
        game_over_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, BOARD_TOP + BOARD_SIZE // 3))
        self.screen.blit(game_over_text, text_rect)

        # Nút Replay (R)
        self.draw_rounded(self.screen, self.replay_button_rect, (50, 200, 50))
        replay_text = self.font_button.render("Replay (R)", True, (255, 255, 255))
        self.screen.blit(
            replay_text, replay_text.get_rect(center=self.replay_button_rect.center)
        )

        # Nút Quit
        self.draw_rounded(self.screen, self.quit_button_rect, (200, 50, 50))
        quit_text = self.font_button.render("Quit", True, (255, 255, 255))
        self.screen.blit(
            quit_text, quit_text.get_rect(center=self.quit_button_rect.center)
        )

     
    def handle_event(self, event):
         
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset_game()
            return

         
        if self.env.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.replay_button_rect.collidepoint(mouse_pos):
                    self.reset_game()
                 
                elif self.quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()
            return  
         
        if event.type == pygame.KEYDOWN and event.key in KEY_TO_ACTION:
            action = KEY_TO_ACTION[event.key]
            s, r, d, info = self.env.step(action)
            self.state = s
            
           
            self.top_score = max(self.top_score, self.env.score)
            
           
            if d:
                self.env.game_over = d
                self.env.total_time = time.time() - self.start_time

    def update(self):
        pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.render_header()
        self.render_board()
        
         
        if self.env.game_over:
            self.render_game_over()
