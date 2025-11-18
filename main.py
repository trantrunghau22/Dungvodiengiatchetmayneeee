import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from game.app import App

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
