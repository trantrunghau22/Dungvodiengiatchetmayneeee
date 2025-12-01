import sys
import os

# Thêm đường dẫn hiện tại để Python tìm thấy thư mục 'game'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.app import App

def main():
    # Khởi tạo và chạy game trực tiếp
    app = App()
    app.run()

if __name__ == "__main__":
    main()
