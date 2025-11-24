import pygame
from game.settings import *
from game.scenes.board import BoardScene
pygame.init()

class IntroScreen():
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font_title = pygame.font.SysFont("comicsansms", 160, bold=True)
        self.font_small = pygame.font.SysFont("comicsansms", 35, bold=True)
        self.button = pygame.Rect(298,500,200,60)   
        pygame.display.set_caption("2048")
  


    def handle_event (self, event):
        #screen = pygame.display.set_mode((800,600))
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button.collidepoint(event.pos):
                self.app.active_scene = BoardScene(self.app)

    def update(self):
        pass

    def render_header(self):
        title = self.font_title.render("2048", True, (243, 178, 122))
        self.screen.blit(title, (210, 290))

    def render_button_start(self):
        self.button_start = pygame.Rect(300,515,220,45)
        surf = self.font_small.render("start",True,(250, 248, 239))
        a,b= pygame.mouse.get_pos()
        if self.button_start.collidepoint(a, b):
            pygame.draw.rect(self.screen, (243, 178, 122), self.button_start)
        else:
            pygame.draw.rect(self.screen, (246, 150, 101), self.button_start)
        
        #self.draw_rounded(self.screen, self.button_start, (246, 150, 101), radius=10)
        text_rect = surf.get_rect(center=self.button_start.center)
        self.screen.blit(surf, text_rect)

    def render_button_ai(self):
        self.button_ai = pygame.Rect(300,585,220,45)
        surf = self.font_small.render("ai mode",True,(250, 248, 239))
        a,b= pygame.mouse.get_pos()
        if self.button_ai.collidepoint(a, b):
            pygame.draw.rect(self.screen, (243, 178, 122), self.button_ai)
        else:
            pygame.draw.rect(self.screen, (246, 150, 101), self.button_ai)
        
        #self.draw_rounded(self.screen, self.button_ai, (246, 150, 101), radius=10)
        text_rect = surf.get_rect(center=self.button_ai.center)
        self.screen.blit(surf, text_rect)

    def draw_rounded(self, surf, rect, color, radius=10):
        pygame.draw.rect(surf, color, rect, border_radius=radius)


    def render(self):
        self.screen.fill((250, 248, 239))
        self.render_header()
        self.render_button_start()
        self.render_button_ai()

    

class Button:
    def __init__(self, x, y, width, height, text, font, idle_color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.idle_color

        pygame.draw.rect(surface, color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
