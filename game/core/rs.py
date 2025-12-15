import pygame
import os
from game.settings import * # Import settings để lấy màu sắc, font, text

class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame_x, frame_y, width, height, scale=None):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame_x, frame_y, width, height))
        if scale:
            image = pygame.transform.smoothscale(image, scale)
        return image

def load_number_sprites(img_dir, tile_size):
    sprites = {}
    values = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    for val in values:
        filename = f"tile_{val}.png"
        path = os.path.join(img_dir, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, tile_size)
                sprites[val] = img
            except: pass
    return sprites

def load_feature_sprites(img_path):
    feats = {}
    try:
        full_img = pygame.image.load(img_path).convert_alpha()
        btn_w = full_img.get_width() // 3
        btn_h = full_img.get_height()
        sheet = SpriteSheet(full_img)
        feats['reset'] = sheet.get_image(0, 0, btn_w, btn_h)
        feats['save'] = sheet.get_image(btn_w, 0, btn_w, btn_h)
        feats['menu'] = sheet.get_image(2 * btn_w, 0, btn_w, btn_h)
    except: pass
    return feats

# --- CÁC HÀM VẼ TỐI ƯU (DÙNG CHUNG) ---

def draw_popup_bg(screen, rect):
    """Vẽ nền Popup có bóng đổ và viền"""
    # 1. Bóng đổ
    shadow_rect = rect.copy()
    shadow_rect.move_ip(5, 5)
    pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
    # 2. Nền
    pygame.draw.rect(screen, POPUP_BG_COLOR, rect, border_radius=15)
    # 3. Viền
    pygame.draw.rect(screen, COLOR_TEXT_DARK, rect, 4, border_radius=15)

def draw_styled_btn(screen, rect, text, font, color=COLOR_ACCENT_BLUE):
    """Vẽ nút bấm có bóng đổ và viền"""
    # Bóng nút
    shadow = rect.copy()
    shadow.move_ip(3, 3)
    pygame.draw.rect(screen, (50, 50, 50), shadow, border_radius=8)
    # Thân nút
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, COLOR_TEXT_DARK, rect, 2, border_radius=8)
    # Chữ
    surf = font.render(text, True, (255, 255, 255))
    screen.blit(surf, surf.get_rect(center=rect.center))

# --- CLASS XỬ LÝ SETTINGS (DÙNG CHUNG CHO INTRO VÀ BOARD) ---
class SettingsPopup:
    def __init__(self, app):
        self.app = app
        self.width, self.height = 400, 300
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.rect = pygame.Rect(cx - self.width//2, cy - self.height//2, self.width, self.height)
        
        # Font riêng cho popup
        if os.path.exists(SHIN_FONT_PATH):
            self.title_font = pygame.font.Font(SHIN_FONT_PATH, 30)
            self.font = pygame.font.Font(SHIN_FONT_PATH, 22)
        else:
            self.title_font = pygame.font.SysFont('arial', 30, bold=True)
            self.font = pygame.font.SysFont('arial', 22)
            
        self.dragging_music = False
        self.dragging_sfx = False

    def handle_event(self, event):
        """Xử lý sự kiện, trả về hành động nếu có"""
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Định nghĩa các vùng bấm (Phải khớp với hàm draw)
        lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
        music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
        sfx_rect   = pygame.Rect(cx + 20, cy + 40, 200, 20)
        back_rect  = pygame.Rect(cx - 60, cy + 120, 120, 40)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if lang_rect.collidepoint(event.pos):
                self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'
                self.app.play_sfx('click')
                return 'LANG_CHANGED'
                
            elif music_rect.collidepoint(event.pos):
                self.dragging_music = True
                self._update_music(event.pos[0], music_rect)
                
            elif sfx_rect.collidepoint(event.pos):
                self.dragging_sfx = True
                self._update_sfx(event.pos[0], sfx_rect)
                
            elif back_rect.collidepoint(event.pos):
                self.app.play_sfx('click')
                return 'CLOSE'
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_music = False
            self.dragging_sfx = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music: self._update_music(event.pos[0], music_rect)
            elif self.dragging_sfx: self._update_sfx(event.pos[0], sfx_rect)
            
        return None

    def _update_music(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        val = max(0.0, min(1.0, ratio))
        pygame.mixer.music.set_volume(val)

    def _update_sfx(self, mouse_x, rect):
        ratio = (mouse_x - rect.x) / rect.width
        val = max(0.0, min(1.0, ratio))
        self.app.sfx_volume = val

    def draw(self, screen):
        # Vẽ nền dùng hàm tối ưu
        draw_popup_bg(screen, self.rect)

        txt = TEXTS[self.app.lang]
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Tiêu đề
        title = self.title_font.render(txt['setting'], True, COLOR_TEXT_DARK)
        screen.blit(title, title.get_rect(center=(cx, cy - 120)))

        # 1. Ngôn ngữ
        screen.blit(self.font.render(txt['lang_label'], True, COLOR_TEXT_DARK), (cx - 150, cy - 80))
        lang_rect = pygame.Rect(cx + 20, cy - 80, 120, 30)
        draw_styled_btn(screen, lang_rect, self.app.lang, self.font, (100, 200, 100))

        # 2. Music Slider
        vol_m = pygame.mixer.music.get_volume()
        screen.blit(self.font.render(txt['music_label'], True, COLOR_TEXT_DARK), (cx - 150, cy - 20))
        music_rect = pygame.Rect(cx + 20, cy - 20, 200, 20)
        self._draw_slider(screen, music_rect, vol_m)

        # 3. SFX Slider
        vol_s = getattr(self.app, 'sfx_volume', 0.5)
        screen.blit(self.font.render(txt['sfx_label'], True, COLOR_TEXT_DARK), (cx - 150, cy + 40))
        sfx_rect = pygame.Rect(cx + 20, cy + 40, 200, 20)
        self._draw_slider(screen, sfx_rect, vol_s)

        # 4. Nút Back
        back_rect = pygame.Rect(cx - 60, cy + 120, 120, 40)
        draw_styled_btn(screen, back_rect, txt['btn_back'], self.font, COLOR_ACCENT_RED)

    def _draw_slider(self, screen, rect, value):
        pygame.draw.rect(screen, (200,200,200), rect, border_radius=10) # Nền thanh
        pygame.draw.rect(screen, COLOR_ACCENT_BLUE, (rect.x, rect.y, rect.width * value, rect.height), border_radius=10) # Phần đã kéo
        # Núm tròn
        pygame.draw.circle(screen, COLOR_TEXT_DARK, (int(rect.x + rect.width * value), rect.centery), 12)