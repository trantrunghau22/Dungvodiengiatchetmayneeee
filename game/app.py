import pygame
import os
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, SOUND_DIR
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        pygame.init()
        try: pygame.mixer.init()
        except: pass
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = self.screen
        pygame.display.set_caption("2048 - Shin Style")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Biến toàn cục
        self.username = "Player" # Mặc định
        self.ai_mode = False
        
        # Cài đặt (Settings)
        self.music_on = True
        self.sound_on = True
        self.lang = 'VI' # Mặc định Tiếng Việt ('VI' hoặc 'EN')

        # Load nhạc nền
        bgm_path = os.path.join(SOUND_DIR, 'bgm.mp3')
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except: pass

        self.active_scene = IntroScreen(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.active_scene.handle_event(event)
            self.active_scene.update(dt)
            self.active_scene.render()
            pygame.display.flip()
        pygame.quit()
