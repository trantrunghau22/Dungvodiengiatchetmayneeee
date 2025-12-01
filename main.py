import sys
import os

# Thêm đường dẫn hiện tại vào hệ thống để Python nhận diện gói 'game'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.app import App

def main():
    try:
        # Khởi tạo và chạy ứng dụng
        app = App()
        app.run()
    except Exception as e:
        print("CRITICAL ERROR:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
