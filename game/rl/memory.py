import random
from collections import deque
import numpy as np
import torch

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        # Lưu trải nghiệm vào hàng đợi
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        # Lấy mẫu ngẫu nhiên để train
        batch = random.sample(self.memory, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        
        return (
            np.array(state),
            np.array(action),
            np.array(reward, dtype=np.float32),
            np.array(next_state),
            np.array(done, dtype=bool)
        )

    def __len__(self):
        return len(self.memory)