import pygame
import os
import random
import numpy as np
#numpy xử lý ma trận
from game.settings import *
from game.core.utils import load_number_sprites, load_feature_sprites

class BoardScene:
    def __init__(self, app, env):
        self.app = app
        self.screen = app.screen
        self.env = env
        
        #Load file assets
        bg_filename = 'backgroundgame.png'
        if self.app.lang == 'EN': #chuyển thành en thì chạy sang background en
            bg_filename = 'backgroundgame_en.png'
            
        bg_path = os.path.join(IMG_DIR, bg_filename) 
        if os.path.exists(bg_path):
            self.bg = pygame.image.load(bg_path).convert()
        else:
            self.bg = pygame.image.load(os.path.join(IMG_DIR, 'backgroundgame.png')).convert()

        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT)) #tự co giãn hình theo kích thước cửa sổ
        
        #Load ba cái features đã tắt
        self.sprites = load_number_sprites(IMG_DIR, (TILE_SIZE, TILE_SIZE))
        self.feats = load_feature_sprites(os.path.join(IMG_DIR, 'features.png'))
        
        #Gọi fonts
        self.font = pygame.font.Font(SHIN_FONT_PATH, 35) if os.path.exists(SHIN_FONT_PATH) else pygame.font.SysFont('arial', 35)
        self.score_font = pygame.font.Font(SHIN_FONT_PATH, SCORE_FONT_SIZE) if os.path.exists(SHIN_FONT_PATH) else pygame.font.SysFont('arial', SCORE_FONT_SIZE)
        
        #Kích thước, vị trí các nút
        btn_width = 100
        btn_height = 165 
        btn_y = WINDOW_HEIGHT - btn_height - 30 
        self.btn_reset = pygame.Rect(50, btn_y, btn_width, btn_height)
        self.btn_menu = pygame.Rect(WINDOW_WIDTH - 150, btn_y, btn_width, btn_height)
        self.btn_save = pygame.Rect(WINDOW_WIDTH - 270, btn_y, btn_width, btn_height)

    def handle_event(self, event):
        #Kiểm vị trí chuột để bật sound
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_reset.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.env.reset()
                self.app.play_sfx('start')
            elif self.btn_save.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.env.save_game(f"save_{self.app.username}")
                print("Saved!")
            elif self.btn_menu.collidepoint(event.pos):
                self.app.play_sfx('click')
                from game.scenes.intro import IntroScreen
                self.app.active_scene = IntroScreen(self.app)

        #Kiểm tra keyboard để thực hiện action
        if event.type == pygame.KEYDOWN:
            action = None
            if event.key in [pygame.K_UP, pygame.K_w]: action = 0
            elif event.key in [pygame.K_DOWN, pygame.K_s]: action = 1
            elif event.key in [pygame.K_LEFT, pygame.K_a]: action = 2
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: action = 3
            
            if action is not None and not self.env.game_over: #nếu chưa bấm gì mà game chưa over
                #Lấy số lớn nhất TRƯỚC khi đi
                max_tile_before = 0
                if self.env.board.size > 0:
                    max_tile_before = np.max(self.env.board)
                #Thực hiện bước đi
                board, current_score, done, moved = self.env.step(action)
                if moved:
                    self.app.play_sfx('slide') 
                    #Lấy số lớn nhất SAU khi đi
                    max_tile_after = 0
                    if self.env.board.size > 0:
                        max_tile_after = np.max(self.env.board)
                    #Chỉ phát sound 'merge' nếu tạo ra được ô số LỚN HƠN kỷ lục cũ
                    if max_tile_after > max_tile_before:
                        self.app.play_sfx('merge')
                if done: #thua thì phát
                    self.app.play_sfx('lose')
    def update(self, dt): #để hàm update đỡ phải làm việc
        pass
    def render(self): #Hàm để vẽ
        self.screen.blit(self.bg, (0, 0))
        #Vẽ điểm và điểm cao nhất
        score_surf = self.score_font.render(str(self.env.score), True, (0,0,0))
        #Căn chỉnh lại tọa độ
        self.screen.blit(score_surf, (340, 30)) 
        #Vẽ bảng
        for r in range(TV_GRID_SIZE): #duyệt hàng
            for c in range(TV_GRID_SIZE): #duyệt cột
                val = self.env.board[r][c] #lấy giá trị
                x = TV_X + TILE_GAP + c * (TILE_SIZE + TILE_GAP)
                y = TV_Y + TILE_GAP + r * (TILE_SIZE + TILE_GAP)
                
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (200, 190, 180), rect, border_radius=8)
                
                if val != 0:
                    if val in self.sprites:
                        self.screen.blit(self.sprites[val], (x, y))
                    else: #vượt ngoài 2048 thì vẽ số bình thường
                        pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=8)
                        t = self.font.render(str(val), True, (255,255,255))
                        self.screen.blit(t, t.get_rect(center=rect.center))

        #Vẽ các phím features
        self._draw_feature_btn(self.btn_reset, 'reset')
        self._draw_feature_btn(self.btn_save, 'save')
        self._draw_feature_btn(self.btn_menu, 'menu')

        if self.env.game_over:
            #như có tấm nháp
            s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,150))
            #phủ màu trong lên
            self.screen.blit(s, (0,0))
            #hiện chữ ở giữa
            t = self.font.render("GAME OVER - Press RESET", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))

    def _draw_feature_btn(self, rect, name):
        img = self.feats.get(name)
        if not img: return
        #Co giãn ảnh cho vừa khít với kích thước nút đã định
        img = pygame.transform.smoothscale(img, (rect.width, rect.height))
        #Tạo bản sao vị trí để tính toán (không sửa vị trí gốc)
        dest = rect.copy()
        #Nếu chuột đúng vị tí thì lắc đít
        if rect.collidepoint(pygame.mouse.get_pos()):
            dest.x += random.randint(-2, 2)
            dest.y += random.randint(-2, 2)
            
        self.screen.blit(img, dest)