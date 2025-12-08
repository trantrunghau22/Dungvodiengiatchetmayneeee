import pygame
import os
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, SOUND_DIR
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        pygame.init()
        try: pygame.mixer.init()
        except: pass
        
        # [UPDATE] Mở Fullscreen
        # pygame.FULLSCREEN | pygame.SCALED giúp game tự co dãn để fit màn hình
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.window = self.screen
        
        pygame.display.set_caption("2048 - GROUP THỢ ĐIỆN VIẾT CODE")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Biến toàn cục
        self.username = "" 
        self.ai_mode = False
        
        # Cài đặt (Settings)
        self.music_on = True
        self.sound_on = True
        self.lang = 'VI' 

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
                # [FEATURE] Bấm ESC ở màn hình chính để thoát (fallback)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                     # Nếu đang ở intro mà bấm ESC thì thoát luôn cho tiện
                     if isinstance(self.active_scene, IntroScreen):
                         if self.active_scene.modal is None: # Chỉ thoát khi ko mở popup
                             self.running = False
                     # Các màn khác tự xử lý ESC
                else:
                    self.active_scene.handle_event(event)
            
            self.active_scene.update(dt)
            self.active_scene.render()
            pygame.display.flip()
        pygame.quit()
