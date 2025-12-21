import pygame
import math
import os
import random 
from game.settings import *
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env
from game.core.rs import draw_popup_bg, draw_blinkbtn, SettingsHelper

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.nickname = getattr(app, 'username', "")
        self.input_active = False
        self.err_msg = ""
        
        #LOAD ASSETS
        bg_path = os.path.join(IMG_DIR, 'backgroundintro.png')
        if os.path.exists(bg_path): self.bg = pygame.image.load(bg_path).convert()
        else:
            self.bg = pygame.Surface((WWIDTH, WHEIGHT))
            self.bg.fill((250, 248, 239))
        self.bg = pygame.transform.scale(self.bg, (WWIDTH, WHEIGHT))
        
        title_path = os.path.join(IMG_DIR, 'title.png')
        if os.path.exists(title_path): self.title_img = pygame.image.load(title_path).convert_alpha()
        else:
            self.title_img = pygame.Surface((400, 150))
            self.title_img.fill((200,100,100))
        self.title_base_size = self.title_img.get_size()
        
        if os.path.exists(SHIN_FONT_PATH):
            self.font = pygame.font.Font(SHIN_FONT_PATH, 30)
            self.small_font = pygame.font.Font(SHIN_FONT_PATH, 22)
        else:

            try:
                self.font = pygame.font.SysFont('tahoma', 30, bold=True) 
                self.small_font = pygame.font.SysFont('tahoma', 22)
            except:
                self.font = pygame.font.SysFont('arial', 30, bold=True)
                self.small_font = pygame.font.SysFont('arial', 22)
        
        #INPUT, CÁC NÚT
        cx, cy = WWIDTH // 2, WHEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        
        btn_w, btn_h = 260, 80
        col_dist = 450; row_dist = 110

        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        self.timer = 0
        
        #MODAL
        #CHỌN CHẾ ĐỘ
        self.modal = None # 'LOAD', 'SETTING', 'CREDIT', 'TUTORIAL', 'CHOOSE_MODE'
        self.modal_rect = pygame.Rect(cx - 300, cy - 225, 700, 450)

        self.btn_close = pygame.Rect(self.modal_rect.left + 10, self.modal_rect.top + 10, 30, 30)
        
        self.saved_files = [] 
        self.rename_idx = -1; self.rename_text = ""; self.delete_confirm_idx = -1
        
        self.settings_helper = SettingsHelper(app)

    def handle_event(self, event):
        #CÁC SỰ KIỆN
        if self.modal:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.modal != 'SETTING':
                    if self.btn_close.collidepoint(event.pos):
                        self.app.play_sfx('click')
                        self.modal = None; return
            if self.modal == 'LOAD':
                self._handle_load_events(event)
            elif self.modal == 'SETTING': 
                cx, cy = self.modal_rect.centerx, self.modal_rect.centery
                res = self.settings_helper.handle_event(event, cx, cy)
                if res == 'CLOSE': self.modal = None
            elif self.modal == 'CHOOSE_MODE':
                self._handle_choose_mode(event)
            
            if event.type == pygame.KEYDOWN and self.modal == 'LOAD':
                self._handle_rename_input(event)
            
            if event.type == pygame.TEXTINPUT and self.modal == 'LOAD' and self.rename_idx != -1:
                 if len(self.rename_text) < 15: self.rename_text += event.text
            return

        #SỰ KIỆN MÀN HÌNH CHÍNH
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.app.play_sfx('click')
            else: self.input_active = False    
            
            if self.btn_new.collidepoint(event.pos):
                self.app.play_sfx('click')
                if len(self.nickname) > 0:
                    #KHOAN HẢ VÀO GAME, CHO CHỌN CHẾ ĐỘ TRƯỚC 
                    self.modal = 'CHOOSE_MODE'
                else: self.err_msg = TEXTS[self.app.lang]['start_err']

            elif self.btn_exit.collidepoint(event.pos):
                self.app.play_sfx('click'); pygame.quit(); exit()

            elif self.btn_load.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('LOAD')
            elif self.btn_set.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('SETTING')
            elif self.btn_cred.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('CREDIT')
            elif self.btn_tut.collidepoint(event.pos):
                self.app.play_sfx('click'); self.open_modal('TUTORIAL')

        if self.input_active:
            if event.type == pygame.TEXTINPUT:
                if len(self.nickname) < 15: self.nickname += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.modal = 'CHOOSE_MODE'
            self.app.username = self.nickname

    def open_modal(self, mode):
        self.modal = mode
        if mode == 'LOAD':
            temp = Game2048Env()
            self.saved_files = temp.get_saved_files()
            self.rename_idx = -1; self.delete_confirm_idx = -1

    def _handle_choose_mode(self, event):
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        #Tọa độ 2 nút chọn
        btn_human = pygame.Rect(cx - 150, cy - 20, 300, 60)
        btn_ai    = pygame.Rect(cx - 150, cy + 60, 300, 60)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_human.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.start_game(ai_mode=False) # Người chơi tự chơi
            elif btn_ai.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.start_game(ai_mode=True)  # Chế độ AI

    def _handle_load_events(self, event):
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        top_y = self.modal_rect.top
        
        if event.type != pygame.MOUSEBUTTONDOWN: return

        for i, f in enumerate(self.saved_files):
            y = top_y + 80 + i*50 
            rect_del = pygame.Rect(cx + 130, y, 30, 40)
            rect_ren = pygame.Rect(cx + 95, y, 30, 40)
            rect_file = pygame.Rect(cx - 150, y, 240, 40)

            #Xử lý nút x
            if rect_del.collidepoint(event.pos):
                if self.delete_confirm_idx == i:
                    Game2048Env().delete_game(f)
                    self.open_modal('LOAD') #Reload danh sách
                else:
                    self.delete_confirm_idx = i; self.rename_idx = -1
                return

            #Xử lý nút e
            if rect_ren.collidepoint(event.pos):
                self.rename_idx = i
                self.rename_text = f.replace("save_", "").replace(".json", "")
                self.delete_confirm_idx = -1
                return

            #Chọn file
            if rect_file.collidepoint(event.pos):
                if self.rename_idx == -1 and self.delete_confirm_idx == -1:
                    env = Game2048Env(size=TVSIZE)
                    if env.load_game(f):
                        #CHuyển file, khỏi chọn mode cho load game là người chơi
                        self.app.play_sfx('start')
                        self.app.username = self.nickname
                        self.app.active_scene = BoardScene(self.app, env, ai_mode=False)

        self.delete_confirm_idx = -1; self.rename_idx = -1

    def _handle_rename_input(self, event):
        if self.rename_idx != -1:
            if event.key == pygame.K_RETURN:
                if self.rename_text.strip():
                    old = self.saved_files[self.rename_idx]
                    if Game2048Env().rename_game(old, self.rename_text):
                        self.open_modal('LOAD')
                        self.rename_idx = -1
                    else:
                        printf("Tên file không được bỏ trống!")
            elif event.key == pygame.K_ESCAPE: self.rename_idx = -1
            elif event.key == pygame.K_BACKSPACE: self.rename_text = self.rename_text[:-1]

    def start_game(self, ai_mode=False):
        self.app.play_sfx('start')
        self.app.username = self.nickname
        env = Game2048Env(size=TVSIZE)
        #TRUYỀN AI VÀO BOARD NÈ
        self.app.active_scene = BoardScene(self.app, env, ai_mode=ai_mode)

    def update(self, dt): self.timer += dt * 0.005

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale); h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        self.screen.blit(scaled_title, scaled_title.get_rect(center=(WWIDTH//2, 150)))
        
        if self.app.username:
            txt_hello = TEXTS[self.app.lang]['hello']
            full_text = f"{txt_hello} {self.app.username.upper()}!"
    
            if os.path.exists(SHIN_FONT_PATH):
                big_font = pygame.font.Font(SHIN_FONT_PATH, 55) 
            else:
                big_font = pygame.font.SysFont('arial', 55, bold=True)
            
            text_x = (WWIDTH // 2)
            text_y = self.input_rect.y - 150 
            
            offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
            for ox, oy in offsets:
                surf = big_font.render(full_text, True, (0,0,0)) 
                self.screen.blit(surf, surf.get_rect(center=(text_x+ox, text_y+oy)))

            surf = big_font.render(full_text, True, (255,215,0))
            self.screen.blit(surf, surf.get_rect(center=(text_x, text_y)))
        #Input Box
        color = COLOR_ACCENT_BLUE if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        self.screen.blit(self.font.render(self.nickname, True, TXTdarkcolor), (self.input_rect.x+10, self.input_rect.y+5))
        
        if not self.nickname and not self.input_active:
            self.screen.blit(self.small_font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150,150,150)), (self.input_rect.x+10, self.input_rect.y+10))
        if self.err_msg:
            self.screen.blit(self.small_font.render(self.err_msg, True, COLOR_ACCENT_RED), (WWIDTH//2-100, self.input_rect.bottom+10))
        
        txt = TEXTS[self.app.lang]
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_set, txt['setting']), (self.btn_cred, txt['credit']),
            (self.btn_tut, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        for rect, label in buttons: self._draw_btn(rect, label)

        if self.modal: self._draw_modal()

    def _draw_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        draw_rect = rect.copy()
        if rect.collidepoint(mouse_pos):
            draw_rect.x += random.randint(-2, 2); draw_rect.y += random.randint(-2, 2)
            color = COLOR_ACCENT_BLUE
        else: color = (255, 200, 150)
        
        shadow = draw_rect.copy(); shadow.move_ip(3, 3)
        pygame.draw.rect(self.screen, (50,50,50), shadow, border_radius=15)
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, width=3, border_radius=15)
        t = self.font.render(text, True, TXTdarkcolor)
        self.screen.blit(t, t.get_rect(center=draw_rect.center))

    def _draw_modal(self):
        overlay = pygame.Surface((WWIDTH, WHEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR); self.screen.blit(overlay, (0,0))
        
        #Xử lý riêng Setting
        if self.modal == 'SETTING':
            self.settings_helper.draw(self.screen, self.modal_rect.centerx, self.modal_rect.centery, self.small_font, self.font)
            return

        draw_popup_bg(self.screen, self.modal_rect)
        
        #Vẽ nút X (Close) ở góc TRÁI TRÊN
        #Tọa độ đã define ở __init__
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_close, border_radius=5)
        pygame.draw.rect(self.screen, TXTdarkcolor, self.btn_close, 2, border_radius=5)
        self.screen.blit(self.font.render("X", True, (255,255,255)), self.btn_close.move(5, -2))
        
        txt = TEXTS[self.app.lang]
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        top_y = self.modal_rect.top

        if self.modal == 'LOAD':
            title = self.font.render(txt['load_title'], True, TXTdarkcolor)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            if not self.saved_files:
                self.screen.blit(self.small_font.render(txt['empty'], True, (150,150,150)), (cx-30, cy))
            for i, f in enumerate(self.saved_files[:6]):
                y = top_y + 80 + i*50 
                rect_file = pygame.Rect(cx - 150, y, 240, 40)
                
                if i == self.delete_confirm_idx:
                    pygame.draw.rect(self.screen, (255, 200, 200), rect_file, border_radius=5)
                    self.screen.blit(self.small_font.render(txt['delete_confirm'], True, (200,0,0)), (rect_file.x+5, rect_file.y+8))
                elif i == self.rename_idx:
                    pygame.draw.rect(self.screen, (255,255,255), rect_file, border_radius=5)
                    pygame.draw.rect(self.screen, (0,0,255), rect_file, 2, border_radius=5)
                    self.screen.blit(self.small_font.render(self.rename_text, True, (0,0,0)), (rect_file.x+5, rect_file.y+8))
                else:
                    pygame.draw.rect(self.screen, (220,220,255), rect_file, border_radius=5)
                    name = f.replace("save_", "").replace(".json", "")
                    self.screen.blit(self.small_font.render(name, True, (0,0,0)), (rect_file.x+10, rect_file.y+8))
                
                pygame.draw.rect(self.screen, (255, 200, 100), (cx + 95, y, 30, 40), border_radius=5)
                self.screen.blit(self.small_font.render("E", True, (0,0,0)), (cx + 102, y+8))
                pygame.draw.rect(self.screen, (200, 100, 100), (cx + 130, y, 30, 40), border_radius=5)
                self.screen.blit(self.small_font.render("X", True, (255,255,255)), (cx + 137, y+8))

        elif self.modal == 'CHOOSE_MODE':
            # Popup chọn chế độ 
            txt = TEXTS[self.app.lang] 
            
            title = self.font.render(txt['choose_mode'], True, TXTdarkcolor)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            
            btn_human = pygame.Rect(cx - 150, cy - 20, 300, 60)
            btn_ai    = pygame.Rect(cx - 150, cy + 60, 300, 60)
            
            draw_blinkbtn(self.screen, btn_human, txt['mode_player'], self.font, (100, 200, 100))
            draw_blinkbtn(self.screen, btn_ai, txt['mode_ai'], self.font, (100, 150, 255))

        elif self.modal == 'CREDIT':
            title = self.font.render(txt['credit_title'], True, TXTdarkcolor)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            y = top_y + 100
            for line in txt['credit_content']:
                t = self.small_font.render(line, True, TXTdarkcolor)
                self.screen.blit(t, t.get_rect(center=(cx, y)))
                y += 35

        elif self.modal == 'TUTORIAL':
            title = self.font.render(txt['tut_title'], True, TXTdarkcolor)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            y = top_y + 100
            for line in txt['tut_content']:
                t = self.small_font.render(line, True, TXTdarkcolor)
                self.screen.blit(t, (self.modal_rect.x + 50, y))
                y += 35