import pygame
from game.settings import *
from game.core.env_2048 import Game2048Env
from game.scenes.board import BoardScene
import os

pygame.init()
class BoardScene:
    def __init__(self, env, app):
        self.env = env
        self.app = app
        self.username = app.username
class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.window = app.window
        self.font_title = pygame.font.SysFont("comicsansms", 140, bold=True)
        self.font_small = pygame.font.SysFont("comicsansms", 32, bold=True)
        self.font_input = pygame.font.SysFont("comicsansms", 28)
        #button
        self.button_start = pygame.Rect(240, 420, 300, 60)
        self.button_ai = pygame.Rect(240, 500, 300, 60)
        self.button_load = pygame.Rect(240, 580, 300, 60)

        #username input
        self.username = ""
        self.input_active = False
        self.input_box = pygame.Rect(200, 320, 400, 50)
        self.color_active = (243, 178, 122)
        self.color_inactive = (187, 173, 160)
        self.input_color = self.color_inactive

        #load game input support
        self.load_mode = False           # True → đang nhập tên file load
        self.load_filename = ""          # user nhập tên file
        self.load_box = pygame.Rect(200, 660, 400, 50)
        self.load_color = self.color_inactive
        self.load_active = False

 
    def handle_event(self, event):
        #click of mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            #username box
            if self.input_box.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.color_active
            else:
                self.input_active = False
                self.input_color = self.color_inactive

            #load game box
            if self.load_mode and self.load_box.collidepoint(event.pos):
                self.load_active = True
                self.load_color = self.color_active
            else:
                self.load_active = False
                self.load_color = self.color_inactive

            #start game
            if self.button_start.collidepoint(event.pos):
                if self.username.strip() != "":
                    self.app.username = self.username
                    self.app.ai_mode = False
                    self.app.env = Game2048Env()
                    self.app.active_scene = BoardScene(self.app.env, self.app)
                else:
                    print("Username required!")

            #AI mode
            if self.button_ai.collidepoint(event.pos):
                if self.username.strip() != "":
                    self.app.username = self.username
                    self.app.ai_mode = True
                    self.app.env = Game2048Env()
                    self.app.active_scene = BoardScene(self.app.env, self.app)
                else:
                    print("Username required!")

            #load game mode on
            if self.button_load.collidepoint(event.pos):
                self.load_mode = True
                self.load_active = True
                self.load_color = self.color_active
                print("Load mode enabled: please type filename")

        #input by keyboard
        if event.type == pygame.KEYDOWN:

            #username 
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                else:
                    if len(self.username) < 12:
                        self.username += event.unicode

            #load filename
            if self.load_active and self.load_mode:
                if event.key == pygame.K_BACKSPACE:
                    self.load_filename = self.load_filename[:-1]

                elif event.key == pygame.K_RETURN:
                    self._try_load_game()

                else:
                    if len(self.load_filename) < 20:
                        self.load_filename += event.unicode

    def _try_load_game(self):
        """Attempt to load a game with the given filename."""
        filename = self.load_filename.strip()
        if filename == "":
            print("No filename entered.")
            return

        if not filename.lower().endswith(".json"):
            filename += ".json"

        if not os.path.exists(filename):
            print("Save file not found:", filename)
            return

        #environment
        env = Game2048Env()
        try:
            env.load_game(filename)
            print("Loaded game:", filename)
        except Exception as e:
            print("Error loading:", e)
            return

        #type or saved
        if env.get_top_score() is not None:
            pass

        #set username
        self.app.username = self.username if self.username.strip() != "" else "player"

        #switch scene
        self.app.env = env
        self.app.ai_mode = False
        self.app.active_scene = BoardScene(env, self.app)

    def render(self):
        self.window.fill((250, 248, 239))

        #tittle
        title = self.font_title.render("2048", True, (243, 178, 122))
        self.window.blit(title, (190, 150))

        #username input
        label = self.font_small.render("Enter username:", True, (119, 110, 101))
        self.window.blit(label, (200, 280))

        pygame.draw.rect(self.window, self.input_color, self.input_box, border_radius=10)
        text_surface = self.font_input.render(self.username, True, (0, 0, 0))
        self.window.blit(text_surface, (self.input_box.x+10, self.input_box.y+10))

        #buttons
        self._draw_button(self.button_start, "START")
        self._draw_button(self.button_ai, "AI MODE")
        self._draw_button(self.button_load, "LOAD GAME")

        #load filename textbox
        if self.load_mode:
            label2 = self.font_small.render("Enter save file:", True, (119, 110, 101))
            self.window.blit(label2, (200, 620))

            pygame.draw.rect(self.window, self.load_color, self.load_box, border_radius=10)
            ftext = self.font_input.render(self.load_filename, True, (0, 0, 0))
            self.window.blit(ftext, (self.load_box.x+10, self.load_box.y+10))

        pygame.display.update()

    def _draw_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        color = (243, 178, 122) if rect.collidepoint(mouse) else (246, 150, 101)
        pygame.draw.rect(self.window, color, rect, border_radius=12)
        text_surf = self.font_small.render(text, True, (250, 248, 239))
        text_rect = text_surf.get_rect(center=rect.center)
        self.window.blit(text_surf, text_rect)
