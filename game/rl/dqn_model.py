import torch
import torch.nn as nn
import torch.nn.functional as F

class QNet(nn.Module):
    def __init__(self, action_size=4):
        super(QNet, self).__init__()
        # Input: 1 kênh (bàn cờ 4x4)
        self.conv1 = nn.Conv2d(1, 64, kernel_size=2, stride=1, padding=0)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=2, stride=1, padding=0)
        
        # --- ĐÂY LÀ CHỖ QUAN TRỌNG NHẤT ---
        # Phải là 128 input -> 128 output (Code cũ bị lệch ở đây)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=2, stride=1, padding=0)
        
        # Flatten
        self.fc1 = nn.Linear(128, 256)
        self.fc2 = nn.Linear(256, action_size)

    def forward(self, x):
        x = x.view(-1, 1, 4, 4) 
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        x = x.view(x.size(0), -1) 
        x = F.relu(self.fc1(x))
        return self.fc2(x)