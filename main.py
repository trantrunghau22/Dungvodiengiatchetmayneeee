from game.app import App

if __name__ == "__main__":
    try:
        app = App() #gắn class App
        app.run() #chạy app
 #Dòng này để khi lỡ chương trình chạy ra lỗi, thay vì crash sập thì nó sẽ hiện ra lỗi là e, khi được gắn biến. 
 #Dòng input là để dừng chương trình để đọc lỗi
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")