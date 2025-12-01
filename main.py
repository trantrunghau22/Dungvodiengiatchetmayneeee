import sys
import os

# Thêm đường dẫn hiện tại vào sys.path để Python nhận diện module 'game'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.app import App

def main():
    try:
        # Khởi tạo ứng dụng
        app = App()
        # Chạy vòng lặp game
        app.run()
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
