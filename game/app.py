import pygame
import os
from game.settings import * 
#import hết luôn
from game.scenes.intro import IntroScreen

class App:
    def __init__(self):
        #Khởi tạo game và âm thanh 
        pygame.init()
        try:
            #Tăng buffer để giảm độ trễ âm thanh khi lướt nhanh
            pygame.mixer.init(buffer=510) 
        except Exception as e:
            print("Warning: Sound device not found.", e) #Lỗi thì in ra

        #Fullscreen
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        #pygame.display để tạo surface để vẽ lên, toán tử OR để FULLSCREEN hoặc là chỉnh kích thước to nhỏ tùy ý tự chỉnh lại
        self.window = self.screen
        
        pygame.display.set_caption("2048 - SHIN AND THO DIEN")
        self.clock = pygame.time.Clock() #Để kiểm soát tốc độ chạy game, lát gắn cho nó fps 60
        self.running = True #Kiểm soát vòng lặp game
        
        #Các biến toàn cục
        self.username = "" 
        self.ai_mode = False
        
        #Settings
        self.show_settings_popup = False
        self.lang = 'VI' 
        

        self.sound_on = True 
        self.music_on = True

        #SOUNDS
        #nạp các file âm thanh vào bộ nhớ
        self.sounds = {}
        self._load_sounds()
        #chơi nhạc nền
        self.play_music()
        #Khởi tạo intro
        self.active_scene = IntroScreen(self)

    def _load_sounds(self):
        #Nạp tên và tên file từ soundfiles bên settings
        for name, filename in SOUND_FILES.items():
            if name == 'bgm': continue #Nhạc nền thì kệ, xử lý riêng
            path = os.path.join(SOUND_DIR, filename)
            if os.path.exists(path): #nạp file rồi xem file có tồn tại không
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(0.4) 
                    self.sounds[name] = sound 
                except Exception as e:
                    print(f"Error loading sound {filename}: {e}")
            else:
                print(f"Missing sound file: {filename}")

    def play_music(self):
        #Nhạc nền
        bgm_path = os.path.join(SOUND_DIR, SOUND_FILES['bgm'])
        if os.path.exists(bgm_path) and self.music_on: #kiểm tra có tồn tại và có bật
            try:
                pygame.mixer.music.load(bgm_path) #vừa tải vừa load tiết kiệm RAM
                pygame.mixer.music.set_volume(0.3) 
                pygame.mixer.music.play(-1) #cho lặp vô tận
            except: pass #Lỗi thì kệ, để tránh màn hình sập

    def toggle_music(self):
        #Chuyển trạng thái nhạc nền
        self.music_on = not self.music_on
        self.update_music_state()

    def update_music_state(self):
        #Cập nhật trạng thái nhạc nền
        if self.music_on:
            if not pygame.mixer.music.get_busy():
                self.play_music()
        else:
            pygame.mixer.music.stop()


    def play_sfx(self, name):
        #phát các âm thanh effect
        if self.sound_on and name in self.sounds:
            try:
                self.sounds[name].play()
            except: pass

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #ấn nút X thì running thành false, nghỉ chạy
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                     # Nếu đang ở intro mà bấm ESC thì thoát
                     if isinstance(self.active_scene, IntroScreen):
                         self.running = False
                else:
                    self.active_scene.handle_event(event) #Chia ra đang ở cửa sổ nào thì hàm cửa sổ đó xử lý
            
            self.active_scene.update(dt) #Tính toán lại các thông số, truyền vào dt để kiểm soát chạy khớp thời gian thực
            self.active_scene.render() #Vẽ
            pygame.display.flip()
        pygame.quit()
