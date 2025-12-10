import random
from collections import namedtuple, deque

# Định nghĩa cấu trúc dữ liệu cho một bước đi
Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity) # Hàng đợi, tự xóa cũ khi đầy

    def push(self, *args):
        """Lưu một transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        """Lấy ngẫu nhiên các mẫu để train"""
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
