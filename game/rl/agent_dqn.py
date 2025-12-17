import torch
import torch.nn as nn
import numpy as np
from game.rl.dqn_model import QNet

class DQNAgent:
    def __init__(self, state_size=16, action_size=4, device='cpu'):
        self.device = device
        self.policy_net = QNet().to(device)
        self.policy_net.eval() # Chế độ đánh giá

    def preprocess_state(self, board):
        board_flat = board.flatten()
        processed = np.zeros_like(board_flat, dtype=np.float32)
        
        # 1. Ô trống
        mask_0 = (board_flat == 0)
        processed[mask_0] = 0.0
        
        # 2. Xử lý Số 1 (Vật cản)
        # --- SỬA QUAN TRỌNG: Đưa về 0.5 để AI phân biệt rõ với Số 2 (là 1.0) ---
        mask_1 = (board_flat == 1)
        processed[mask_1] = 0.5 
        
        # 3. Các số khác (2, 4, 8...)
        # Số 2 -> log2(2) = 1.0
        # Số 4 -> log2(4) = 2.0
        mask_other = (board_flat > 1)
        processed[mask_other] = np.log2(board_flat[mask_other])
        
        # 4. Chuẩn hóa
        processed = processed / 16.0 
        return torch.FloatTensor(processed).unsqueeze(0).to(self.device)

    def act(self, state):
        with torch.no_grad():
            state_tensor = self.preprocess_state(state)
            q_values = self.policy_net(state_tensor)
            # Trả về mảng điểm số của cả 4 hướng
            return q_values.cpu().data.numpy()[0] 

    def load(self, filename):
        self.policy_net.load_state_dict(torch.load(filename, map_location=self.device))
        self.policy_net.eval()