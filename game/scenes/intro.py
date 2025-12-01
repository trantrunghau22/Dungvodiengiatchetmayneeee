import pygame
import os
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env
from game.settings import GRID_SIZE

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        
        # Font setup
        try:
            self.font_title = pygame.font.SysFont("comicsansms", 140, bold=True)
            self.font_small = pygame.font.SysFont("comicsansms", 32, bold=True)
            self.font_input = pygame.font.SysFont("comicsansms", 28)
        except:
            self.font_title = pygame.font.SysFont("arial", 100, bold=True)
            self.font_small = pygame.font.SysFont("arial", 32, bold=True)
            self.font_input = pygame.font.SysFont("arial", 28)

        # Buttons Rect
        self.button_start = pygame.Rect(240, 420, 300, 60)
        self.button_ai = pygame.Rect(240, 500, 300, 60)
        self.button_load = pygame.Rect(240, 580, 300, 60)

        # Username input
        self.username = getattr(self.app, 'username', "")
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

            # --- NÚT START ---
            if self.button_start.collidepoint(event.pos):
                self._start_game(ai_mode=False)

            # --- NÚT AI MODE ---
            if self.button_ai.collidepoint(event.pos):
                self._start_game(ai_mode=True)

            # --- NÚT LOAD GAME ---
            if self.button_load.collidepoint(event.pos):
                self.load_mode = True
                self.load_active = True
                self.load_color = self.color_active
                print("Load mode enabled: please type filename")

        # Input bàn phím
        if event.type == pygame.KEYDOWN:
            # Nhập Username
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    # Bấm Enter ở ô Username cũng Start Game luôn
                    self._start_game(ai_mode=False)
                elif event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                else:
                    if len(self.username) < 12:
                        self.username += event.unicode

            # Nhập tên file Load Game
            if self.load_active and self.load_mode:
                if event.key == pygame.K_BACKSPACE:
                    self.load_filename = self.load_filename[:-1]
                elif event.key == pygame.K_RETURN:
                    self._try_load_game()
                else:
                    if len(self.load_filename) < 20:
                        self.load_filename += event.unicode

    def _start_game(self, ai_mode=False):
        if self.username.strip() == "":
            print("Username required!")
            return
            
        self.app.username = self.username
        self.app.ai_mode = ai_mode
        
        # Tạo môi trường mới và chuyển cảnh
        # Đây là phần quan trọng để khớp với BoardScene mới
        new_env = Game2048Env(size=GRID_SIZE)
        new_env.reset()
        self.app.active_scene = BoardScene(new_env, self.app)

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
        self.app.ai_mode = False 
        # Truyền env đã load vào BoardScene
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
        # Fix lỗi hiển thị ô vuông: Font chỉ render text
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
