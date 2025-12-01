import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.app import App

def main():
    try:
        app = App()
        app.run()
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
