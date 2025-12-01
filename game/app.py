import pygame
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.scenes.board import BoardScene
from game.scenes.intro import IntroScreen
self.username = None
self.ai_mode = False
self.active_scene = IntroScreen(self)
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2048 Project")
        self.clock = pygame.time.Clock()
        self.running = True

        self.active_scene = IntroScreen(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.active_scene.handle_event(event)

            self.active_scene.update()
            self.active_scene.render()
            pygame.display.flip()

        pygame.quit()
