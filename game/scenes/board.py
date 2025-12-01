import pygame
import os
from game.settings import *
from game.core.env_2048 import Game2048Env, UP, DOWN, LEFT, RIGHT

# --- Cấu hình điều khiển ---
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

# --- Màn hình Intro (Menu chính) ---
class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        # Font setup - Ưu tiên font hệ thống nếu không có comicsans
        try:
            self.font_title = pygame.font.SysFont("comicsansms", 140, bold=True)
            self.font_small = pygame.font.SysFont("comicsansms", 32, bold=True)
            self.font_input = pygame.font.SysFont("comicsansms", 28)
        except:
            self.font_title = pygame.font.SysFont("arial", 100, bold=True)
            self.font_small = pygame.font.SysFont("arial", 32, bold=True)
            self.font_input = pygame.font.SysFont("arial", 28)

        # Buttons
        self.button_start = pygame.Rect(240, 420, 300, 60)
        self.button_ai = pygame.Rect(240, 500, 300, 60)
        self.button_load = pygame.Rect(240, 580, 300, 60)

        # Username input
        self.username = ""
        self.input_active = False
        self.input_box = pygame.Rect(200, 320, 400, 50)
        self.color_active = (243, 178, 122)
        self.color_inactive = (187, 173, 160)
        self.input_color = self.color_inactive

        # Load game input support
        self.load_mode = False            
        self.load_filename = ""          
        self.load_box = pygame.Rect(200, 660, 400, 50)
        self.load_color = self.color_inactive
        self.load_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Username box
            if self.input_box.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.color_active
            else:
                self.input_active = False
                self.input_color = self.color_inactive

            # Load game box
            if self.load_mode and self.load_box.collidepoint(event.pos):
                self.load_active = True
                self.load_color = self.color_active
            else:
                self.load_active = False
                self.load_color = self.color_inactive

            # Start game
            if self.button_start.collidepoint(event.pos):
                if self.username.strip() != "":
                    self.app.username = self.username
                    self.app.ai_mode = False
                    # Tạo Env mới và chuyển sang BoardScene
                    new_env = Game2048Env(size=GRID_SIZE)
                    new_env.reset()
                    self.app.active_scene = BoardScene(new_env, self.app)
                else:
                    print("Username required!")

            # AI mode
            if self.button_ai.collidepoint(event.pos):
                if self.username.strip() != "":
                    self.app.username = self.username
                    self.app.ai_mode = True
                    new_env = Game2048Env(size=GRID_SIZE)
                    new_env.reset()
                    self.app.active_scene = BoardScene(new_env, self.app)
                else:
                    print("Username required!")

            # Load game mode toggle
            if self.button_load.collidepoint(event.pos):
                self.load_mode = True
                self.load_active = True
                self.load_color = self.color_active
                print("Load mode enabled: please type filename")

        # Input by keyboard
        if event.type == pygame.KEYDOWN:
            # Username 
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                else:
                    if len(self.username) < 12:
                        self.username += event.unicode

            # Load filename
            if self.load_active and self.load_mode:
                if event.key == pygame.K_BACKSPACE:
                    self.load_filename = self.load_filename[:-1]
                elif event.key == pygame.K_RETURN:
                    self._try_load_game()
                else:
                    if len(self.load_filename) < 20:
                        self.load_filename += event.unicode

    def _try_load_game(self):
        filename = self.load_filename.strip()
        if filename == "":
            print("No filename entered.")
            return

        if not filename.lower().endswith(".json"):
            filename += ".json"

        if not os.path.exists(filename):
            print("Save file not found:", filename)
            return

        env = Game2048Env(size=GRID_SIZE)
        try:
            env.load_game(filename)
            print("Loaded game:", filename)
        except Exception as e:
            print("Error loading:", e)
            return

        self.app.username = self.username if self.username.strip() != "" else "Player"
        self.app.ai_mode = False # Giả sử load game là người chơi
        # Chuyển scene với env đã load
        self.app.active_scene = BoardScene(env, self.app)

    def render(self):
        self.window.fill((250, 248, 239))

        # Title
        title = self.font_title.render("2048", True, (243, 178, 122))
        self.window.blit(title, (190, 150))

        # Username input
        label = self.font_small.render("Enter username:", True, (119, 110, 101))
        self.window.blit(label, (200, 280))

        pygame.draw.rect(self.window, self.input_color, self.input_box, border_radius=10)
        text_surface = self.font_input.render(self.username, True, (0, 0, 0))
        self.window.blit(text_surface, (self.input_box.x+10, self.input_box.y+10))

        # Buttons
        self._draw_button(self.button_start, "START")
        self._draw_button(self.button_ai, "AI MODE")
        self._draw_button(self.button_load, "LOAD GAME")

        # Load filename textbox
        if self.load_mode:
            label2 = self.font_small.render("Enter save file:", True, (119, 110, 101))
            self.window.blit(label2, (200, 620))

            pygame.draw.rect(self.window, self.load_color, self.load_box, border_radius=10)
            ftext = self.font_input.render(self.load_filename, True, (0, 0, 0))
            self.window.blit(ftext, (self.load_box.x+10, self.load_box.y+10))

    def _draw_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        color = (243, 178, 122) if rect.collidepoint(mouse) else (246, 150, 101)
        pygame.draw.rect(self.window, color, rect, border_radius=12)
        text_surf = self.font_small.render(text, True, (250, 248, 239))
        text_rect = text_surf.get_rect(center=rect.center)
        self.window.blit(text_surf, text_rect)

    def update(self):
        pass


# --- Màn hình chơi Game (BoardScene) ---
class BoardScene:
    # Đã sửa __init__ để nhận env và app từ IntroScreen
    def __init__(self, env, app):
        self.app = app
        self.screen = app.window # Map app.window vào self.screen để logic cũ hoạt động
        self.env = env           # Sử dụng env được truyền vào thay vì tạo mới
        self.state = self.env.get_board() # Lấy state hiện tại từ env
        
        self.game_over = False
        self.player_nickname = app.username
        self.top_score = self._load_top_score()
        
        # Setup Fonts & Rects (Logic cũ)
        self.font_title = pygame.font.SysFont(FONT_NAME, 38, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_button = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        
        self.replay_rect = pygame.Rect(REPLAY_BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.quit_rect = pygame.Rect(QUIT_BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        total_gap = (GRID_SIZE + 1) * TILE_GAP
        self.tile_size = (BOARD_SIZE - total_gap) // GRID_SIZE
        self.board_rect = pygame.Rect(BOARD_MARGIN, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)

    def get_current_max_tile_score(self):
        # Lấy điểm hoặc giá trị ô lớn nhất từ env
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
        nick_text = self.font_small.render(f"Player: {self.player_nickname}", True, (255,255,255))
        self.screen.blit(nick_text, (nickname_rect.x + 10, nickname_rect.y + 14)) 
        
        top_score_rect = pygame.Rect(WINDOW_WIDTH - 300, 40, 145, 50)
        self.draw_rounded(self.screen, top_score_rect, SCORE_BG_COLOR)
        top_score_text = self.font_small.render(f"Top: {self.top_score}", True, (255,255,255))
        self.screen.blit(top_score_text, (top_score_rect.x + 16, top_score_rect.y + 14))

    def render_board(self):
        self.draw_rounded(self.screen, self.board_rect, BOARD_BG_COLOR, radius=12)
        # Cập nhật state mới nhất từ env trước khi vẽ
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
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_q:
                    # Quay về màn hình Intro thay vì thoát hẳn
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
            elif event.key in KEY_TO_ACTION:
                action = KEY_TO_ACTION[event.key]
                s, r, d, info = self.env.step(action)
                self.state = s
                if d: # Nếu game kết thúc (d=Done)
                    if info.get('terminal_reason') == 'no_legal_moves':
                        self.game_over = True
                        self._save_top_score()

    def reset_game(self):
        self.state = self.env.reset()
        self.game_over = False
        self._load_top_score()

    def update(self):
        # Nếu có AI mode, gọi logic AI ở đây
        if self.app.ai_mode and not self.game_over:
            # Ví dụ: action = simple_ai(self.env)
            # self.env.step(action)
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
        quit_label = self.font_button.render("MENU (Q)", True, BUTTON_TEXT_COLOR)
        self.screen.blit(quit_label, quit_label.get_rect(center=self.quit_rect.center))
