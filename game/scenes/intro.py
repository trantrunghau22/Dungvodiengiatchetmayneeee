import pygame
import math
import os
import random 
from game.settings import *
from game.scenes.board import BoardScene
from game.core.env_2048 import Game2048Env

class IntroScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.nickname = getattr(app, 'username', "")
        self.input_active = False
        
        #LOAD ASSETS
        self.bg = pygame.image.load(os.path.join(IMG_DIR, 'backgroundintro.png')).convert()
        self.bg = pygame.transform.scale(self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.title_img = pygame.image.load(os.path.join(IMG_DIR, 'title.png')).convert_alpha()
        self.title_base_size = self.title_img.get_size()
        
        self.font = pygame.font.SysFont('arial', 30, bold=True)
        if os.path.exists(SHIN_FONT_PATH):
            try:
                self.font = pygame.font.Font(SHIN_FONT_PATH, 30)
            except:
                self.font = pygame.font.SysFont("arial", 30, bold=True)
                
        self.small_font = pygame.font.SysFont('arial', 22)
        
        #input box
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 20, 300, 50)
        
        #layout
        btn_w, btn_h = 260, 80
        col_dist = 450
        row_dist = 110

        self.btn_new = pygame.Rect(cx - col_dist, cy - row_dist, btn_w, btn_h)
        self.btn_load = pygame.Rect(cx - col_dist, cy, btn_w, btn_h)
        self.btn_set = pygame.Rect(cx - col_dist, cy + row_dist, btn_w, btn_h)
        self.btn_cred = pygame.Rect(cx + 200, cy - row_dist, btn_w, btn_h)
        self.btn_tut = pygame.Rect(cx + 200, cy, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx + 200, cy + row_dist, btn_w, btn_h)
        
        # [SỬA] Thống nhất dùng tên biến show_load_popup
        self.show_load_popup = False
        self.saved_files = [] 
        self.err_msg = ""
        self.timer = 0

        # --- MODAL SYSTEM (QUẢN LÝ POPUP) ---
        self.modal = None # 'LOAD', 'SETTING', 'CREDIT', 'TUTORIAL'
        self.modal_rect = pygame.Rect(cx - 300, cy - 225, 600, 450)
        self.btn_close = pygame.Rect(self.modal_rect.right - 40, self.modal_rect.top + 10, 30, 30)
        
        # Load Game State
        self.saved_files = [] 
        self.rename_idx = -1
        self.rename_text = ""
        self.delete_confirm_idx = -1

    def handle_event(self, event):
        # 1. XỬ LÝ KHI ĐANG MỞ MODAL
        if self.modal:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Nút Close chung cho mọi modal
                if self.btn_close.collidepoint(event.pos):
                    self.modal = None
                    return
                
                # Logic riêng từng modal
                if self.modal == 'LOAD':
                    self._handle_load_events(event)
                elif self.modal == 'SETTING':
                    self._handle_setting_events(event)
            
            # Xử lý phím khi đang Rename trong Load Game
            if self.modal == 'LOAD' and event.type == pygame.KEYDOWN:
                self._handle_rename_input(event)
            
            return
        # [XỬ LÝ POPUP LOAD GAME]
        if self.show_load_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
                # Check click file
                for i, filename in enumerate(self.saved_files):
                    rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
                    if rect.collidepoint(event.pos):
                        env = Game2048Env(size=TV_GRID_SIZE)
                        if env.load_game(filename):
                            self.app.active_scene = BoardScene(self.app, env)
                        self.show_load_popup = False
                        return
                
                # Close (X)
                if pygame.Rect(cx + 120, cy - 140, 30, 30).collidepoint(event.pos):
                    self.show_load_popup = False
            return

        # [SỰ KIỆN CHÍNH]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.app.play_sfx('click')
            else:
                self.input_active = False    
            
            if self.btn_new.collidepoint(event.pos):
                self.app.play_sfx('click')
                if len(self.nickname) > 0:
                    self.start_game()
                else:
                    self.err_msg = TEXTS[self.app.lang]['start_err']

            elif self.btn_exit.collidepoint(event.pos):
                self.app.play_sfx('click')
                pygame.quit(); exit()

            elif self.btn_load.collidepoint(event.pos):
                self.app.play_sfx('click')
                temp = Game2048Env()
                self.saved_files = temp.get_saved_files()[:5]
                self.show_load_popup = True
            
            elif self.btn_set.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.toggle_language()

            elif self.btn_cred.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.open_modal('CREDIT')

            elif self.btn_tut.collidepoint(event.pos):
                self.app.play_sfx('click')
                self.open_modal('TUTORIAL')

        # Keyboard Input
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.nickname) > 0: self.start_game()
                else:
                    if len(self.nickname) < 15:
                        self.nickname += event.unicode
            self.app.username = self.nickname

    def open_modal(self, mode):
        self.modal = mode
        if mode == 'LOAD':
            temp = Game2048Env()
            self.saved_files = temp.get_saved_files()
            self.rename_idx = -1
            self.delete_confirm_idx = -1

    def handle_load_popup_event(self, event):
        cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        
        # Xử lý Rename (Nhập tên mới)
        if self.rename_idx != -1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Thực hiện đổi tên
                    if self.rename_text.strip():
                        temp = Game2048Env()
                        old = self.saved_files[self.rename_idx]
                        if temp.rename_game(old, self.rename_text):
                            self.open_load_popup() # Refresh list
                        else:
                            print("Rename failed or exists")
                    self.rename_idx = -1
                elif event.key == pygame.K_ESCAPE:
                    self.rename_idx = -1
                elif event.key == pygame.K_BACKSPACE:
                    self.rename_text = self.rename_text[:-1]
                else:
                    if len(self.rename_text) < 15: self.rename_text += event.unicode
            return

        # Xử lý Click chuột trong popup
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check Delete Confirm (Yes/No)
            if self.delete_confirm_idx != -1:
                # Vị trí nút Yes/No dựa trên hàm vẽ (điều chỉnh tọa độ cho khớp)
                # Giả sử nút Yes ở (cx-60, cy+20), No ở (cx+10, cy+20) relative to popup center?
                # Code vẽ delete confirm ở dưới, check tọa độ ở đó.
                
                # Để đơn giản, click đâu cũng hủy confirm trừ nút Yes
                # Nhưng logic đúng là check rect nút Yes.
                # Ở đây ta check đơn giản: Bấm file đó lần nữa để xác nhận xóa?
                # Hoặc bấm nút delete lần nữa?
                
                # Logic tốt hơn: Click nút Delete (Icon thùng rác) lần 2 để xác nhận.
                pass 

            for i, filename in enumerate(self.saved_files):
                # Tọa độ hàng file
                rect_file = pygame.Rect(cx - 150, cy - 100 + i*50, 240, 40) # File name area
                rect_ren  = pygame.Rect(cx + 95, cy - 100 + i*50, 30, 40)   # Rename icon area
                rect_del  = pygame.Rect(cx + 130, cy - 100 + i*50, 30, 40)  # Delete icon area

                # 1. Click Delete Icon
                if rect_del.collidepoint(event.pos):
                    if self.delete_confirm_idx == i:
                        # Đã confirm -> Xóa thật
                        temp = Game2048Env()
                        temp.delete_game(filename)
                        self.open_load_popup() # Refresh
                    else:
                        # Hỏi confirm
                        self.delete_confirm_idx = i
                        self.rename_idx = -1
                    return

                # 2. Click Rename Icon
                if rect_ren.collidepoint(event.pos):
                    self.rename_idx = i
                    self.rename_text = filename.replace("save_", "").replace(".json", "")
                    self.delete_confirm_idx = -1
                    return

                # 3. Click File Name -> Load Game
                if rect_file.collidepoint(event.pos):
                    env = Game2048Env(size=TV_GRID_SIZE)
                    if env.load_game(filename):
                        self.app.active_scene = BoardScene(self.app, env)
                    self.show_load_popup = False
                    return
            
            # Click ra ngoài để đóng popup hoặc hủy confirm
            popup_rect = pygame.Rect(cx - 200, cy - 150, 400, 350)
            close_rect = pygame.Rect(cx + 120, cy - 140, 30, 30)
            
            if close_rect.collidepoint(event.pos) or not popup_rect.collidepoint(event.pos):
                self.show_load_popup = False
            
            # Reset trạng thái nếu click chỗ khác
            self.delete_confirm_idx = -1
            self.rename_idx = -1
    
    def _handle_setting_events(self, event):
        # Nút đổi ngôn ngữ
        lang_rect = pygame.Rect(self.modal_rect.centerx - 80, self.modal_rect.centery - 20, 160, 40)
        if lang_rect.collidepoint(event.pos):
            self.toggle_language()

    def toggle_language(self):
        self.app.lang = 'EN' if self.app.lang == 'VI' else 'VI'

    def start_game(self):
        self.app.play_sfx('start')
        self.app.username = self.nickname
        env = Game2048Env(size=TV_GRID_SIZE)
        self.app.active_scene = BoardScene(self.app, env)

    def update(self, dt):
        self.timer += dt * 0.005 

    def render(self):
        self.screen.blit(self.bg, (0, 0))
        
        # Title Animation
        scale = 1.0 + 0.05 * math.sin(self.timer)
        w = int(self.title_base_size[0] * scale)
        h = int(self.title_base_size[1] * scale)
        scaled_title = pygame.transform.smoothscale(self.title_img, (w, h))
        title_rect = scaled_title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(scaled_title, title_rect)
        
        # Input Box
        color = COLOR_ACCENT_BLUE if self.input_active else (200, 200, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, self.input_rect, width=3, border_radius=10)
        
        txt_surf = self.font.render(self.nickname, True, COLOR_TEXT_DARK)
        self.screen.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        if not self.nickname and not self.input_active:
            hint = self.font.render(TEXTS[self.app.lang]['nickname_placeholder'], True, (150, 150, 150))
            self.screen.blit(hint, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        if self.err_msg:
            err = self.font.render(self.err_msg, True, COLOR_ACCENT_RED)
            self.screen.blit(err, (WINDOW_WIDTH//2 - err.get_width()//2, self.input_rect.bottom + 10))
        
        # Buttons
        txt = TEXTS[self.app.lang]
        buttons = [
            (self.btn_new, txt['new_game']), (self.btn_load, txt['load_game']),
            (self.btn_set, txt['setting']), (self.btn_cred, txt['credit']),
            (self.btn_tut, txt['tutorial']), (self.btn_exit, txt['exit'])
        ]
        
        for rect, text in buttons:
            self._draw_btn(rect, text)
            
        if self.show_load_popup:
            self.draw_load_popup(self.screen)
         
        if self.modal:
            self._draw_modal()

    def _draw_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        draw_rect = rect.copy()
        if rect.collidepoint(mouse_pos):
            draw_rect.x += random.randint(-2, 2)
            draw_rect.y += random.randint(-2, 2)
            color = COLOR_ACCENT_BLUE
        else:
            color = (255, 200, 150)
            
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, width=3, border_radius=15)
        
        t_surf = self.font.render(text, True, COLOR_TEXT_DARK)
        self.screen.blit(t_surf, t_surf.get_rect(center=draw_rect.center))
        
    def draw_load_popup(self, screen):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0,0))

        cx, cy = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        box = pygame.Rect(cx - 200, cy - 150, 400, 350)
        pygame.draw.rect(self.screen, POPUP_BG_COLOR, box, border_radius=10)
        
        # Close btn
        close = pygame.Rect(cx + 120, cy - 140, 30, 30)
        pygame.draw.rect(self.screen, (200,50,50), close)
        x_txt = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_txt, x_txt.get_rect(center=close.center))
        
        title = self.font.render(TEXTS[self.app.lang]['load_title'], True, (0,0,0))
        self.screen.blit(title, title.get_rect(center=(cx, cy - 120)))

        for i, f in enumerate(self.saved_files):
            rect = pygame.Rect(cx - 150, cy - 100 + i*50, 300, 40)
            pygame.draw.rect(self.screen, (200,200,255), rect, border_radius=5)
            name = f.replace("save_", "").replace(".json", "")
            t = self.font.render(name, True, (0,0,0))
            self.screen.blit(t, (rect.x + 10, rect.y + 5))
        # Khu vực tên file
            rect_file = pygame.Rect(cx - 150, y, 240, 40)
            
            # Khu vực nút Rename (icon bút chì giả lập bằng text 'R')
            rect_ren  = pygame.Rect(cx + 95, y, 30, 40)
            
            # Khu vực nút Delete (icon thùng rác giả lập bằng text 'D')
            rect_del  = pygame.Rect(cx + 130, y, 30, 40)

            # Vẽ nền file
            if i == self.delete_confirm_idx:
                pygame.draw.rect(self.window, (255, 200, 200), rect_file, border_radius=5) # Màu đỏ cảnh báo
                msg = self.small_font.render(TEXTS[self.app.lang]['delete_confirm'], True, (200,0,0))
                self.window.blit(msg, (rect_file.x + 5, rect_file.y + 10))
                
                # Highlight nút delete
                pygame.draw.rect(self.window, (255, 0, 0), rect_del, border_radius=5)
            
            elif i == self.rename_idx:
                pygame.draw.rect(self.window, (255, 255, 255), rect_file, border_radius=5)
                pygame.draw.rect(self.window, (0,0,255), rect_file, 2, border_radius=5)
                
                # Hiển thị text đang nhập
                t = self.font.render(self.rename_text, True, (0,0,0))
                self.window.blit(t, (rect_file.x + 10, rect_file.y + 5))
                
                # Ẩn các nút khác khi đang rename
                continue
                
            else:
                pygame.draw.rect(self.window, (200,200,255), rect_file, border_radius=5)
                name = f.replace("save_", "").replace(".json", "")
                t = self.font.render(name, True, (0,0,0))
                self.window.blit(t, (rect_file.x + 10, rect_file.y + 5))

            # Vẽ nút Rename (Màu vàng)
            if i != self.delete_confirm_idx:
                pygame.draw.rect(self.window, (255, 200, 100), rect_ren, border_radius=5)
                ren_txt = self.small_font.render("E", True, (0,0,0)) # E for Edit
                self.window.blit(ren_txt, ren_txt.get_rect(center=rect_ren.center))

            # Vẽ nút Delete (Màu đỏ)
            if i != self.delete_confirm_idx:
                pygame.draw.rect(self.window, (200, 100, 100), rect_del, border_radius=5)
            
            del_txt = self.small_font.render("X", True, (255,255,255))
            self.window.blit(del_txt, del_txt.get_rect(center=rect_del.center))
    def _draw_modal(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0,0))
        
        # Modal Box
        pygame.draw.rect(self.screen, POPUP_BG_COLOR, self.modal_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100,100,100), self.modal_rect, 3, border_radius=10)
        
        # Close Btn
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_close, border_radius=5)
        x_txt = self.font.render("X", True, (255,255,255))
        self.screen.blit(x_txt, x_txt.get_rect(center=self.btn_close.center))
        
        txt = TEXTS[self.app.lang]
        cx, cy = self.modal_rect.centerx, self.modal_rect.centery
        top_y = self.modal_rect.top

        # --- NỘI DUNG TỪNG MODAL ---
        if self.modal == 'LOAD':
            title = self.font.render(txt['load_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            
            if not self.saved_files:
                empty = self.small_font.render(txt['empty'], True, (150,150,150))
                self.screen.blit(empty, empty.get_rect(center=(cx, cy)))
            
            for i, f in enumerate(self.saved_files[:6]):
                y = top_y + 80 + i*50
                rect_file = pygame.Rect(cx - 150, y, 240, 40)
                rect_ren = pygame.Rect(cx + 95, y, 30, 40)
                rect_del = pygame.Rect(cx + 130, y, 30, 40)
                
                # Check trạng thái rename/delete
                if i == self.delete_confirm_idx:
                    pygame.draw.rect(self.screen, (255, 200, 200), rect_file, border_radius=5)
                    msg = self.small_font.render(txt['delete_confirm'], True, (200,0,0))
                    self.screen.blit(msg, (rect_file.x + 5, rect_file.y + 8))
                    pygame.draw.rect(self.screen, (255,0,0), rect_del, border_radius=5)
                elif i == self.rename_idx:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect_file, border_radius=5)
                    pygame.draw.rect(self.screen, (0,0,255), rect_file, 2, border_radius=5)
                    t = self.small_font.render(self.rename_text, True, (0,0,0))
                    self.screen.blit(t, (rect_file.x + 5, rect_file.y + 8))
                else:
                    pygame.draw.rect(self.screen, (220, 220, 255), rect_file, border_radius=5)
                    name = f.replace("save_", "").replace(".json", "")
                    t = self.small_font.render(name, True, (0,0,0))
                    self.screen.blit(t, (rect_file.x + 10, rect_file.y + 8))
                    
                    # Icons
                    pygame.draw.rect(self.screen, (255, 200, 100), rect_ren, border_radius=5)
                    self.screen.blit(self.small_font.render("E", True, (0,0,0)), (rect_ren.x+8, rect_ren.y+8))
                    
                    pygame.draw.rect(self.screen, (200, 100, 100), rect_del, border_radius=5)
                    self.screen.blit(self.small_font.render("X", True, (255,255,255)), (rect_del.x+8, rect_del.y+8))

        elif self.modal == 'SETTING':
            title = self.font.render(txt['setting'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            
            lang_rect = pygame.Rect(cx - 80, cy - 20, 160, 40)
            pygame.draw.rect(self.screen, (100, 200, 100), lang_rect, border_radius=5)
            lang_t = self.small_font.render(f"{txt['lang_label']} {self.app.lang}", True, (255,255,255))
            self.screen.blit(lang_t, lang_t.get_rect(center=lang_rect.center))

        elif self.modal == 'TUTORIAL':
            title = self.font.render(txt['tut_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            
            y = top_y + 100
            for line in txt['tut_content']:
                t = self.small_font.render(line, True, (0,0,0))
                self.screen.blit(t, (self.modal_rect.x + 50, y))
                y += 35

        elif self.modal == 'CREDIT':
            title = self.font.render(txt['credit_title'], True, COLOR_TEXT_DARK)
            self.screen.blit(title, title.get_rect(center=(cx, top_y + 40)))
            
            y = top_y + 100
            for line in txt['credit_content']:
                t = self.small_font.render(line, True, (0,0,0))
                self.screen.blit(t, t.get_rect(center=(cx, y)))
                y += 35