# 🎮 Game 2048 - Shin-chan - AI Powered with Deep Q-Learning

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0-red)

> Đồ án môn học **Nhập môn Công nghệ Thông tin** > **Khoa Công nghệ Thông tin - Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM**

Dự án này tái hiện trò chơi 2048 nổi tiếng với giao diện đồ họa Shinchan và tích hợp **AI Agent** sử dụng mô hình **CNNs (Convolutional Neural Networks)** kết hợp **Deep Q-Learning** để tự động chinh phục trò chơi.

<img width="1867" height="1347" alt="image" src="https://github.com/user-attachments/assets/1ef6c25d-9894-42ec-98a2-603150b46a77" />

---

## 🎮 Giao diện
<img width="1734" height="1079" alt="image" src="https://github.com/user-attachments/assets/980dc1fd-76d3-40bc-b6e1-3fca81f96248" />
<img width="1750" height="1079" alt="image" src="https://github.com/user-attachments/assets/ac66a4ed-a746-4224-93f3-3c235e880bb2" />
<img width="1794" height="1079" alt="image" src="https://github.com/user-attachments/assets/46665ec5-941f-48f2-b990-e4d4047c1cd5" />

---

## ✨ Tính năng nổi bật

* **Chế độ chơi đa dạng:**
    * 👤 **Human Mode:** Người chơi tự thao tác bằng các phím mũi tên hoặc WASD.
    * 🤖 **AI Mode:** AI tự động chơi dựa trên mô hình đã huấn luyện.
* **Cơ chế chơi game đặc biệt:**
   * Hỗ trợ **vật cản đặc biệt (Ô số 1 - Ớt chuông)**:
    * **Điều kiện xuất hiện:** Khi bàn cờ đạt được ô số **128** trở lên, hệ thống sẽ có **1%** tỉ lệ sinh ra ô giá trị 1 (biểu tượng Ớt chuông) thay vì số 2 hoặc 4 thông thường.
    * **Cơ chế phá hủy:** Các ô Ớt chuông không thể gộp với nhau. Để loại bỏ, người chơi (hoặc AI) bắt buộc phải tạo ra ô số **256** và gộp trực tiếp vào ô Ớt chuông để ô Ớt chuông biến mất.
    * **AI Adaptation:** Agent được lập trình để nhận diện "Ớt chuông" như một trạng thái đặc biệt (trọng số 0.5) và học chiến thuật tích lũy tài nguyên để phá giải vật cản này.
* **Hệ thống & Cài đặt (System & Settings):**
    * 💾 **Save & Load Game:** Cho phép lưu trạng thái bàn cờ hiện tại và tiếp tục chơi bất cứ lúc nào, đảm bảo không mất tiến trình.
    * 🌍 **Đa ngôn ngữ (Multi-language):** Hỗ trợ chuyển đổi linh hoạt giữa **Tiếng Việt** và **Tiếng Anh** ngay trong giao diện.
    * 🔊 **Tùy chỉnh Âm thanh:** Hệ thống Setting cho phép điều chỉnh âm lượng hoặc tắt/bật nhạc nền và hiệu ứng âm thanh.
    * 🛡️ **Error Handling:** Cơ chế bắt lỗi tự động giúp game vận hành mượt mà, không bị crash đột ngột.
    * 🖼️ **Hình ảnh**:** Hình ảnh đa dạng, sinh động, chủ đề Shin-chan.

---

## 🛠️ Cài đặt & Môi trường

Đồ án khuyến khích sử dụng **Micromamba** (hoặc Conda) để quản lý môi trường nhằm tránh xung đột thư viện.

### 1. Clone dự án
```bash
git clone https://github.com/trantrunghau22/Dungvodiengiatchetmayneeee.git
cd Dungvodiengiatchetmayneeee
```

### 2. Thiết lập môi trường
```bash
micromamba create -n game_2048 python=3.9
micromamba activate game_2048
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng dẫn sử dụng
Khởi chạy Game
Để bắt đầu trò chơi:
```bash
python main.py
```
Huấn luyện AI (Training)
Nếu bạn muốn huấn luyện lại mô hình từ đầu: 
```bash
python game/rl/train_dqn.py
```

---

## 🧠 Kiến trúc AI & Thuật toán

Mô hình AI sử dụng mạng nơ-ron tích chập (CNN) để trích xuất đặc trưng từ bàn cờ 4x4.

### 1. Tiền xử lý dữ liệu (Preprocessing)
Trước khi đưa vào mạng, trạng thái bàn cờ được chuẩn hóa (`agent_dqn.py`):
* **Logarithmic Scaling:** Các số $2, 4, 8...$ được chuyển về dạng $\log_2(x)$ (Ví dụ: $2 \to 1.0, 4 \to 2.0$).
* **Obstacle Handling:** Ô có giá trị **1** (vật cản) được gán giá trị đặc biệt là **0.5** để AI phân biệt với ô trống ($0.0$) và ô số 2 ($1.0$).
* **Normalization:** Toàn bộ ma trận được chia cho **16.0** để đưa về khoảng giá trị nhỏ, giúp mạng hội tụ nhanh hơn.

### 2. Mô hình Deep Q-Network (QNet)
Mạng được định nghĩa trong `dqn_model.py` với kiến trúc 3 lớp tích chập:

| Layer | Type | Configuration | Output Shape |
| :--- | :--- | :--- | :--- |
| **Input** | Tensor | Bàn cờ được reshape | `(1, 4, 4)` |
| **Conv1** | Conv2d | Kernel: 2, Stride: 1, Filters: 64 | `(64, 3, 3)` |
| **Conv2** | Conv2d | Kernel: 2, Stride: 1, Filters: 128 | `(128, 2, 2)` |
| **Conv3** | Conv2d | Kernel: 2, Stride: 1, Filters: 128 | `(128, 1, 1)` |
| **Flatten** | View | Duỗi phẳng tensor | `(128)` |
| **FC1** | Linear | 128 $\to$ 256 | `(256)` |
| **Output** | Linear | 256 $\to$ 4 | `(4)` (Lên, Xuống, Trái, Phải) |

*Hàm kích hoạt (Activation Function):* **ReLU** được sử dụng sau mỗi lớp Conv và FC1.

---

## 📂 Cấu trúc thư mục

```text
game_2048/
├── assets/                  # Tài nguyên đa phương tiện
│   ├── fonts/               # Font chữ sử dụng trong game
│   ├── images/              # Hình ảnh đồ họa (background, icon)
│   └── sounds/              # Hiệu ứng âm thanh & nhạc nền
├── checkpoints/             # Thư mục lưu trữ model AI
│   └── AI_model.pth         # File trọng số (weights) của model tốt nhất
├── game/
│   ├── core/
│   │   ├── env_2048.py      # Logic game & OpenAI Gym wrapper
│   │   └── rs.py            # File cấu hình tài nguyên/hỗ trợ
│   ├── rl/                  # Module Reinforcement Learning
│   │   ├── agent_dqn.py     # Class DQNAgent, xử lý state, chọn action
│   │   ├── dqn_model.py     # Kiến trúc mạng QNet (CNN)
│   │   ├── memory.py        # Replay Buffer (Bộ nhớ kinh nghiệm)
│   │   └── train_dqn.py     # Vòng lặp huấn luyện AI
│   ├── scenes/              # Giao diện Pygame
│   │   ├── intro.py         # Màn hình Intro (Menu chính)
│   │   └── board.py         # Màn hình chơi game chính
│   ├── settings.py          # Cấu hình màu sắc, kích thước
│   └── app.py               # Quản lý luồng ứng dụng (Game Loop)
├── bestscore.txt            # File lưu điểm số cao nhất (High Score)
├── main.py                  # Điểm khởi chạy chương trình (Entry point)
├── requirements.txt         # Danh sách thư viện cần thiết
└── README.md                # Tài liệu hướng dẫn
```

---

## 👥 Tác giả:

### HCMUS - GROUP THỢ ĐIỆN VIẾT CODE - 25CTT3

| Thành viên | MSSV |
| :--- | :--- |
| Trần Trung Hậu | 25120188 |
| Đào Khánh Băng | 25120162 |
| Phạm Hoàng Tường An | 25120159 |
| Ngô Bảo | 25120165 |
| Vũ Gia Bảo | 25120168 |
| Trần Phạm Đăng Duy | 25120138 |

Giảng viên hướng dẫn thực hành: Thầy Lê Đức Khoan.

---

<img width="1867" height="1347" alt="image" src="https://github.com/user-attachments/assets/aaa5e3ae-26d7-4ace-9886-9efaac3c5d4f" />

---
