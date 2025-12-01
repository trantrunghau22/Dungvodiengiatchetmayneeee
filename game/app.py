import pygame
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
# Import IntroScreen
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        pygame.init()
        # Khởi tạo màn hình
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = self.screen # Alias (tên khác) để các file khác gọi không bị lỗi
        
        pygame.display.set_caption("2048 Project")
        self.clock = pygame.time.Clock()
        self.running = True

        # --- BIẾN TOÀN CỤC (GLOBAL STATE) ---
        self.username = ""
        self.ai_mode = False

        # Khởi động vào màn hình Intro đầu tiên
        self.active_scene = IntroScreen(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            
            # Xử lý sự kiện (Event Handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.active_scene.handle_event(event)

            # Cập nhật & Vẽ (Update & Render)
            self.active_scene.update()
            self.active_scene.render()
            
            pygame.display.flip()

        pygame.quit()
