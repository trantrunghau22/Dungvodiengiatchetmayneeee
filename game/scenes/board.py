import pygame
import os
import random
import numpy as np
from game.settings import *
from game.core.utils import load_number_sprites, load_feature_sprites

class BoardScene:
    def __init__(self, app, env):
        self.app = app
        self.screen = app.screen
        self.env = env
        
        # --- LOAD ASSETS (Không phụ thuộc ngôn ngữ) ---
        self.sprites = load_number_sprites(IMG_DIR, (TILE_SIZE, TILE_SIZE))
        
        # --- LOAD ASSETS (Phụ thuộc ngôn ngữ) ---
        # Gọi hàm này để load ảnh nền, nút bấm theo ngôn ngữ hiện tại
        self.load_lang_assets()
        
        # --- LOAD POPUP IMAGES ---
        def load_popup_img(name, size):
            path = os.path.join(IMG_DIR, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            return None

        self.img_exit = load_popup_img('popup_exit.png', (100, 100))
        self.img_win  = load_popup_img('popup_win.png', (120, 100))
        self.img_lose = load_popup_img('popup_lose.png', (120, 100))

        # --- FONTS ---
        self._init_fonts()
        
        # --- BUTTONS LAYOUT ---
        # Kích thước nút features
        btn_width = 100
        btn_height = 165 
        btn_y = WINDOW_HEIGHT - btn_height - 30 
        
        # Vị trí các nút
        self.btn_reset = pygame.Rect(50, btn_y, btn_width, btn_height)
        self.btn_menu = pygame.Rect(WINDOW_WIDTH - 150, btn_y, btn_width, btn_height)
        self.btn_save = pygame.Rect(WINDOW_WIDTH - 270, btn_y, btn_width, btn_height)
        # [MỚI] Nút Settings nằm bên trái nút Save
        self.btn_setting = pygame.Rect(WINDOW_WIDTH - 390, btn_y, btn_width, btn_height)

        # --- POPUP STATE ---
        self.popup_mode = None 
        self.input_text = ""
        self.overwrite_target = ""
        self.best_shown = False 
        
        # --- SETTINGS STATE (Cho Popup Settings) ---
        self.dragging_music = False
        self.dragging_sfx = False

    def _init_fonts(self):
        # Ưu tiên Shin Font, nếu không có thì dùng Arial
        if os.path.exists(SHIN_FONT_PATH):
            self.font = pygame.font.Font(SHIN_FONT_PATH, 35)
            self.score_font = pygame.font.Font(SHIN_FONT_PATH, SCORE_FONT_SIZE)
            self.popup_font = pygame.font.Font(SHIN_FONT_PATH, 24)
            self.small_font = pygame.font.Font(SHIN_FONT_PATH, 20)
        else:
            self.font = pygame.font.SysFont('arial', 35, bold=True)
            self.score_font = pygame.font.SysFont('arial', SCORE_FONT_SIZE, bold=True)
            self.popup_font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 20)

    def load_lang_assets(self):
        """Hàm load lại ảnh nền và nút bấm khi đổi ngôn ngữ"""
        # Xác định tên file dựa trên ngôn ngữ
        if self.app.lang == 'EN':
            bg_file = 'backgroundgame_en.png'
            feat_file = 'features_en.png'
            set_file = 'settings_en.png' # Icon settings bản EN
        else:
            bg_file = 'backgroundgame.png'
            feat_file = 'features.png'
            set_file = 'settings.png'    # Icon settings bản VI (hoặc icon chung)

        # 1. Background
        bg_path = os.path.join(IMG_DIR, bg_file)
        # Fallback về bản gốc nếu bản EN chưa có
        if not os.path.exists(bg_path): bg_path = os.path.join(IMG_DIR, 'backgroundgame.png')
        
        if os.path.exists(bg_path):
            self.bg = pygame.image.load(bg_path).convert()
        else:
            # Màu nền dự phòng nếu mất file ảnh
            self.bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.bg.fill(COLOR_BG_CREAM)
            
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

        # 2. Features (Reset, Save, Menu)
        feat_path = os.path.join(IMG_DIR, feat_file)
        if not os.path.exists(feat_path): feat_path = os.path.join(IMG_DIR, 'features.png')
        self.feats = load_feature_sprites(feat_path)

        # 3. Settings Icon (Mới)
        set_path = os.path.join(IMG_DIR, set_file)
        if not os.path.exists(set_path): set_path = os.path.join(IMG_DIR, 'settings.png')
        
        if os.path.exists(set_path):
            self.img_setting_icon = pygame.image.load(set_path).convert_alpha()
            # Scale ảnh icon cho vừa nút (ví dụ 100x165)
            self.img_setting_icon = pygame.transform.smoothscale(self.img_setting_icon, (100, 100))
        else:
            self.img_setting_icon = None

    def update(self, dt): 
        # Nếu điểm hiện tại > điểm cao nhất -> Cập nhật luôn
        if self.env.score > self.env.top_score:
            self.env.top_score = self.env.score
        
        # Kiểm tra Game Over để hiện Popup
        if self.env.game_over and self.popup_mode is None:
            # Nếu hết game và điểm >= top score cũ -> Thắng/Kỷ lục mới
            if self.env.score >= self.env.top_score and self.env.score > 0 and not self.best_shown:
                self.popup_mode = 'NEW_BEST'
                self.env.save_global_best_score() # Lưu lại kỷ lục
                self.best_shown = True
            elif not self.best_shown:
                self.popup_mode = 'GAME_OVER'

    def handle_event(self, event):
        # Ưu tiên xử lý Popup
        if self.popup_mode:
            self.handle_popup_event(event)
            return

        # Mouse Input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_reset.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.env.reset()
                self.app.play_sfx('start')
                self.best_shown = False
            
            elif self.btn_save.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.popup_mode = 'SAVE'
                self.input_text = ""
            
            elif self.btn_menu.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.popup_mode = 'EXIT' 
            
            # [MỚI] Xử lý nút Settings
            elif self.btn_setting.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.popup_mode = 'SETTING' # Mở popup settings
        
        # Keyboard Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.popup_mode = 'EXIT'

            action = None
            if event.key in [pygame.K_UP, pygame.K_w]: action = 0
            elif event.key in [pygame.K_DOWN, pygame.K_s]: action = 1
            elif event.key in [pygame.K_LEFT, pygame.K_a]: action = 2
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: action = 3
            
            if action is not None and not self.env.game_over:
                max_before = np.max(self.env.board) if self.env.board.size > 0 else 0
                board, current_score, done, moved = self.env.step(action)
                if moved:
                    self.app.play_sfx('slide') 
                    max_after = np.max(self.env.board) if self.env.board.size > 0 else 0
                    if max_after > max_before:
                        self.app.play_sfx('merge')
                if done:
                    self.app.play_sfx('lose')

    def handle_popup_event(self, event):
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # --- XỬ LÝ SETTINGS POPUP ---
        if self.popup_mode == 'SETTING':
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Nút Đổi Ngôn ngữ
                lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
                if lang_rect.collidepoint(event.pos):
                    self.toggle_language()
                    self.app.play_sfx('click')
                    return

                # Slider Nhạc
                music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
                if music_rect.collidepoint(event.pos):
                    self.dragging_music = True
                    self._update_music_vol(event.pos[0], music_rect)
                    return

                # Slider SFX
                sfx_rect = pygame.Rect(cx + 20, cy + 40, 200, 20)
                if sfx_rect.collidepoint(event.pos):
                    self.dragging_sfx = True
                    self._update_sfx_vol(event.pos[0], sfx_rect)
                    return

                # Nút Back
                back_rect = pygame.Rect(cx - 60, cy + 120, 120, 40)
                if back_rect.collidepoint(event.pos):
                    self.popup_mode = None
                    self.app.play_sfx('click')
                    return
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_music = False
                self.dragging_sfx = False

            elif event.type == pygame.MOUSEMOTION:
                music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
                sfx_rect   = pygame.Rect(cx + 20, cy + 40, 200, 20)
                if self.dragging_music:
                    self._update_music_vol(event.pos[0], music_rect)
                elif self.dragging_sfx:
                    self._update_sfx_vol(event.pos[0], sfx_rect)
            return

        # --- XỬ LÝ SAVE POPUP ---
        if self.popup_mode == 'SAVE':
            if event.type == pygame.TEXTINPUT:
                if len(self.input_text) < 15: self.input_text += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.input_text.strip(): return
                    filename = "save_" + self.input_text + ".json"
                    files = self.env.get_saved_files()
                    if filename in files:
                        self.overwrite_target = self.input_text
                        self.popup_mode = 'OVERWRITE'
                    elif len(files) >= 5:
                        self.popup_mode = 'MAX_FILES'
                    else:
                        self.env.save_game(self.input_text, mode="AI" if self.app.ai_mode else "Normal")
                        self.popup_mode = None
                elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE: self.popup_mode = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not pygame.Rect(cx - 200, cy - 150, 400, 300).collidepoint(event.pos):
                    self.popup_mode = None

        # --- XỬ LÝ CÁC POPUP KHÁC ---
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.popup_mode == 'OVERWRITE':
                if pygame.Rect(cx - 80, cy + 50, 100, 40).collidepoint(event.pos): 
                    self.env.save_game(self.overwrite_target, mode="AI" if self.app.ai_mode else "Normal")
                    self.popup_mode = None
                elif pygame.Rect(cx + 20, cy + 50, 100, 40).collidepoint(event.pos):
                    self.popup_mode = 'SAVE'

            elif self.popup_mode == 'EXIT':
                if pygame.Rect(cx - 130, cy + 60, 120, 40).collidepoint(event.pos): # Quit
                    from game.scenes.intro import IntroScreen
                    self.app.active_scene = IntroScreen(self.app)
                elif pygame.Rect(cx + 10, cy + 60, 120, 40).collidepoint(event.pos): # Save
                    self.popup_mode = 'SAVE'

            elif self.popup_mode == 'MAX_FILES':
                self.popup_mode = 'SAVE' 

            elif self.popup_mode in ['NEW_BEST', 'GAME_OVER']:
                if pygame.Rect(cx - 60, cy + 80, 120, 40).collidepoint(event.pos):
                    if self.popup_mode == 'NEW_BEST' and not self.env.game_over:
                        self.popup_mode = None 
                    else:
                        from game.scenes.intro import IntroScreen
                        self.app.active_scene = IntroScreen(self.app)

    # --- HÀM HỖ TRỢ SETTINGS ---
    def toggle_language(self):
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'
        # [QUAN TRỌNG] Load lại ảnh sau khi đổi ngôn ngữ
        self.load_lang_assets() 

    def _update_music_vol(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        val = max(0.0, min(1.0, ratio))
        pygame.mixer.music.set_volume(val)

    def _update_sfx_vol(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        val = max(0.0, min(1.0, ratio))
        self.app.sfx_volume = val

    def render(self):
        # --- VẼ ĐIỂM (Căn chỉnh lại tọa độ) ---
        # Điểm hiện tại: Cách cạnh trái 340px (theo ảnh background cũ của bạn)
        score_surf = self.score_font.render(str(self.env.score), True, (0,0,0))
        self.screen.blit(score_surf, (340, 30)) 
        
        # Điểm cao nhất: Căn chỉnh lại để không bị mất
        # Dùng TV_X + chiều rộng Grid + một khoảng nhỏ
        # Hoặc dùng tọa độ cố định an toàn hơn: WINDOW_WIDTH - 200
        best_surf = self.score_font.render(str(self.env.top_score), True, (0,0,0))
        
        # [FIXED] Tọa độ Best Score an toàn
        # Giả sử ô Best Score nằm ở góc phải trên
        best_x = WINDOW_WIDTH - 250 
        self.screen.blit(best_surf, (best_x, 38))
        
        # 1. Vẽ Background
        self.screen.blit(self.bg, (0, 0))
        
        # 2. Vẽ Điểm và Best Score
        # Lưu ý: Tọa độ này phải khớp với thiết kế background của bạn
        score_surf = self.score_font.render(str(self.env.score), True, (0,0,0))
        self.screen.blit(score_surf, (340, 30)) 
        
        best_surf = self.score_font.render(str(self.env.top_score), True, (0,0,0))
        self.screen.blit(best_surf, (1500, 38)) 
        
        # 3. Vẽ Bàn cờ
        for r in range(TV_GRID_SIZE):
            for c in range(TV_GRID_SIZE):
                val = self.env.board[r][c]
                x = TV_X + TILE_GAP + c * (TILE_SIZE + TILE_GAP)
                y = TV_Y + TILE_GAP + r * (TILE_SIZE + TILE_GAP)
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                # Vẽ ô trống
                pygame.draw.rect(self.screen, (200, 190, 180), rect, border_radius=8)
                
                if val != 0:
                    if val in self.sprites:
                        self.screen.blit(self.sprites[val], (x, y))
                    else:
                        pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=8)
                        t = self.font.render(str(val), True, (255,255,255))
                        self.screen.blit(t, t.get_rect(center=rect.center))
        
        # 4. Vẽ Nút chức năng
        self._draw_feature_btn(self.btn_reset, 'reset')
        self._draw_feature_btn(self.btn_save, 'save')
        self._draw_feature_btn(self.btn_menu, 'menu')
        
        # 5. Vẽ Nút Settings (Icon)
        if self.img_setting_icon:
            # Vẽ ảnh icon nếu có
            dest = self.btn_setting.copy()
            if self.btn_setting.collidepoint(pygame.mouse.get_pos()):
                dest.x += random.randint(-1, 1) # Hiệu ứng rung nhẹ khi hover
            self.screen.blit(self.img_setting_icon, dest)
        else:
            # Vẽ hình chữ nhật tạm nếu chưa có ảnh
            pygame.draw.rect(self.screen, (100, 100, 100), self.btn_setting, border_radius=10)
            t = self.small_font.render("Set", True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=self.btn_setting.center))

        # 6. Vẽ Popup nếu có
        if self.popup_mode:
            self.draw_popup()

    def draw_popup(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0,0))

        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        txt = TEXTS[self.app.lang]
        
        # Box nền
        box_rect = pygame.Rect(cx - 200, cy - 150, 400, 300)
        box_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        box_surf.fill(POPUP_BG_COLOR)
        self.screen.blit(box_surf, box_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), box_rect, 3, border_radius=15)

        # --- NỘI DUNG TỪNG POPUP ---
        
        if self.popup_mode == 'SETTING':
            title = self.popup_font.render(txt['setting'], True, (0,0,0))
            self.screen.blit(title, title.get_rect(center=(cx, cy - 120)))
            
            # 1. Ngôn ngữ
            self.screen.blit(self.small_font.render(txt['lang_label'], True, (0,0,0)), (cx - 150, cy - 80))
            lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
            pygame.draw.rect(self.screen, (100, 200, 100), lang_rect, border_radius=5)
            lang_t = self.small_font.render(self.app.lang, True, (255,255,255))
            self.screen.blit(lang_t, lang_t.get_rect(center=lang_rect.center))

            # 2. Music Slider
            vol_m = pygame.mixer.music.get_volume()
            self.screen.blit(self.small_font.render(txt['music_label'], True, (0,0,0)), (cx - 150, cy - 20))
            music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
            pygame.draw.rect(self.screen, (200,200,200), music_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100,100,255), (music_rect.x, music_rect.y, music_rect.width * vol_m, 20), border_radius=10)
            pygame.draw.circle(self.screen, (50,50,200), (int(music_rect.x + music_rect.width * vol_m), music_rect.centery), 12)

            # 3. SFX Slider
            vol_s = getattr(self.app, 'sfx_volume', 0.5)
            self.screen.blit(self.small_font.render(txt['sfx_label'], True, (0,0,0)), (cx - 150, cy + 40))
            sfx_rect = pygame.Rect(cx + 20, cy + 40, 200, 20)
            pygame.draw.rect(self.screen, (200,200,200), sfx_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100,255,100), (sfx_rect.x, sfx_rect.y, sfx_rect.width * vol_s, 20), border_radius=10)
            pygame.draw.circle(self.screen, (50,200,50), (int(sfx_rect.x + sfx_rect.width * vol_s), sfx_rect.centery), 12)

            # 4. Back
            back_rect = pygame.Rect(cx - 60, cy + 120, 120, 40)
            pygame.draw.rect(self.screen, (200, 200, 100), back_rect, border_radius=10)
            back_t = self.popup_font.render(txt['btn_back'], True, (0,0,0))
            self.screen.blit(back_t, back_t.get_rect(center=back_rect.center))

        elif self.popup_mode == 'SAVE':
            self.draw_text_centered(txt['save_game_title'], -100, size=30)
            self.draw_text_centered(txt['enter_name'], -50, size=20)
            input_rect = pygame.Rect(cx - 100, cy - 10, 200, 40)
            pygame.draw.rect(self.screen, (255,255,255), input_rect)
            pygame.draw.rect(self.screen, (0,0,0), input_rect, 2)
            self.draw_text(self.input_text, input_rect.x+10, input_rect.y+5)

        elif self.popup_mode == 'OVERWRITE':
            self.draw_text_centered(txt['file_exists'], -60, color=(200,0,0))
            self.draw_text_centered(txt['overwrite_ask'], -10)
            self.draw_btn_simple(txt['yes'], (cx - 80, cy + 50), (100, 200, 100))
            self.draw_btn_simple(txt['no'], (cx + 20, cy + 50), (200, 100, 100))

        elif self.popup_mode == 'EXIT':
            img_rect = pygame.Rect(cx - 50, cy - 110, 100, 100) 
            if self.img_exit: self.screen.blit(self.img_exit, img_rect)
            else:
                pygame.draw.rect(self.screen, (200,200,200), img_rect)
                self.draw_text_centered("[IMG]", -60, size=15)
            self.draw_text_centered(txt['exit_msg'], 20)
            self.draw_btn_simple(txt['btn_quit_now'], (cx - 130, cy + 60), (200, 100, 100), w=120)
            self.draw_btn_simple(txt['btn_save_quit'], (cx + 10, cy + 60), (100, 200, 100), w=120)

        elif self.popup_mode == 'NEW_BEST':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_win: self.screen.blit(self.img_win, img_rect)
            else: pygame.draw.rect(self.screen, (255,215,0), img_rect)
            self.draw_text_centered(txt['new_best_title'], -10, size=35, color=(200,0,0))
            self.draw_text_centered(f"{self.env.score}", 30, size=40)
            self.draw_btn_simple(txt['btn_continue'], (cx - 60, cy + 80), (100, 150, 255), w=120)

        elif self.popup_mode == 'GAME_OVER':
            img_rect = pygame.Rect(cx - 60, cy - 130, 120, 100)
            if self.img_lose: self.screen.blit(self.img_lose, img_rect)
            else: pygame.draw.rect(self.screen, (50,50,50), img_rect)
            self.draw_text_centered(txt['game_over_title'], 0, size=35, color=(255,0,0))
            self.draw_btn_simple(txt['btn_menu'], (cx - 60, cy + 80), (100, 150, 255), w=120)

        elif self.popup_mode == 'MAX_FILES':
            self.draw_text_centered(txt['max_files'], 0, color=(200,0,0))

    def draw_text_centered(self, text, y_off, size=24, color=(0,0,0)):
        if os.path.exists(SHIN_FONT_PATH): font = pygame.font.Font(SHIN_FONT_PATH, size)
        else: font = pygame.font.SysFont('arial', size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + y_off)))

    def draw_text(self, text, x, y, size=24):
        if os.path.exists(SHIN_FONT_PATH): font = pygame.font.Font(SHIN_FONT_PATH, size)
        else: font = pygame.font.SysFont('arial', size)
        surf = font.render(text, True, (0,0,0))
        self.screen.blit(surf, (x,y))

    def draw_btn_simple(self, text, pos, color, w=100, h=40):
        rect = pygame.Rect(pos[0], pos[1], w, h)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        surf = self.popup_font.render(text, True, (255,255,255))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_feature_btn(self, rect, name):
        # Hàm vẽ nút reset/save/menu từ features.png
        img = self.feats.get(name)
        if img:
            img = pygame.transform.smoothscale(img, (rect.width, rect.height))
            dest = rect.copy()
            if rect.collidepoint(pygame.mouse.get_pos()): dest.x += random.randint(-1, 1); dest.y += random.randint(-1, 1)
            self.screen.blit(img, dest)