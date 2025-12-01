import pygame
from game.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
# Import màn hình Intro để khởi động
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        pygame.init()
        # Khởi tạo cửa sổ game
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = self.screen # Tạo alias (tên gọi khác) để khớp với các file khác
        
        pygame.display.set_caption("2048 Project")
        self.clock = pygame.time.Clock()
        self.running = True

        # --- BIẾN TOÀN CỤC (GLOBAL STATE) ---
        # Lưu trữ thông tin dùng chung cho toàn bộ game
        self.username = ""
        self.ai_mode = False

        # Bắt đầu game bằng màn hình Intro
        self.active_scene = IntroScreen(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            
            # Xử lý sự kiện (Event Handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    # Chuyển sự kiện cho màn hình đang hiển thị xử lý
                    self.active_scene.handle_event(event)

            # Cập nhật & Vẽ màn hình (Update & Render)
            self.active_scene.update()
            self.active_scene.render()
            
            pygame.display.flip()

        pygame.quit()
