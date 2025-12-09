import pygame
import os

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
    #Load 12 ảnh riêng biệt từ thư mục img_dir
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
            except Exception as e:
                print(f"Lỗi load ảnh {filename}: {e}")
        else:
            print(f"Thiếu file ảnh: {filename}")
            
    return sprites

def load_feature_sprites(img_path):
    #Cắt features.png: Reset, Save, Menu
    feats = {}
    try:
        full_img = pygame.image.load(img_path).convert_alpha()
        
        # Vì ảnh features.png có 3 nút xếp ngang đều nhau
        btn_w = full_img.get_width() // 3
        btn_h = full_img.get_height()
        
        sheet = SpriteSheet(full_img)
        
        # Cắt 3 phần đều nhau
        feats['reset'] = sheet.get_image(0, 0, btn_w, btn_h)
        feats['save'] = sheet.get_image(btn_w, 0, btn_w, btn_h)
        feats['menu'] = sheet.get_image(2 * btn_w, 0, btn_w, btn_h)
        
    except Exception as e: 
        print(f"Lỗi cắt ảnh features: {e}")
        pass
    return feats