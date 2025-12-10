import torch
import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):
    def __init__(self, n_observations=16, n_actions=4):
        super(DQN, self).__init__()
        # 3 lớp kết nối đầy đủ (Fully Connected)
        self.layer1 = nn.Linear(n_observations, 256)
        self.layer2 = nn.Linear(256, 128)
        self.layer3 = nn.Linear(128, n_actions)

    def forward(self, x):
        # Hàm kích hoạt ReLU giúp AI học các mối quan hệ phi tuyến tính
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

