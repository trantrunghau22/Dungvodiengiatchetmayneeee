import pygame
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
# Import IntroScreen
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        pygame.init()
        # Khởi tạo cửa sổ
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = self.screen # Alias cho tiện gọi
        
        pygame.display.set_caption("2048 Project")
        self.clock = pygame.time.Clock()
        self.running = True

        # Biến toàn cục (Global state)
        self.username = ""
        self.ai_mode = False

        # Bắt đầu với màn hình Intro
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
