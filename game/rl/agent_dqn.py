import torch
import torch.optim as optim
import torch.nn.functional as F
import random
import math
from game.rl.dqn_model import DQN
from game.rl.memory import ReplayMemory, Transition

class DQNAgent:
    def __init__(self, n_observations=16, n_actions=4, device='cpu'):
        self.device = device
        self.n_actions = n_actions
        
        # Policy Network (Mạng chính) và Target Network (Mạng mục tiêu)
        self.policy_net = DQN(n_observations, n_actions).to(device)
        self.target_net = DQN(n_observations, n_actions).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval() # Mạng target chỉ để tính toán, không train trực tiếp
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=1e-4)
        self.memory = ReplayMemory(10000)

        self.steps_done = 0
        self.EPS_START = 0.9
        self.EPS_END = 0.05
        self.EPS_DECAY = 2000 # Giảm dần tỷ lệ random sau 2000 bước

    def select_action(self, state):
        # Chiến thuật Epsilon-Greedy
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
            math.exp(-1. * self.steps_done / self.EPS_DECAY)
        self.steps_done += 1

        if sample > eps_threshold:
            with torch.no_grad():
                # Chọn hành động tốt nhất theo suy nghĩ của AI
                # max(1)[1] trả về chỉ số của hành động có Q-value cao nhất
                return self.policy_net(state).max(1)[1].view(1, 1)
        else:
            # Chọn hành động ngẫu nhiên (khám phá)
            return torch.tensor([[random.randrange(self.n_actions)]], device=self.device, dtype=torch.long)

    def optimize_model(self, batch_size=128, gamma=0.99):
        if len(self.memory) < batch_size:
            return

        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))

        # Lọc các trạng thái cuối cùng (None)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                              batch.next_state)), device=self.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
        
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # Tính Q(s, a) hiện tại
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Tính V(s_{t+1}) bằng mạng Target
        next_state_values = torch.zeros(batch_size, device=self.device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()

        # Tính Q mục tiêu (Target Q)
        expected_state_action_values = (next_state_values * gamma) + reward_batch

        # Tính Loss (Huber Loss) và cập nhật trọng số
        criterion = torch.nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        # Cắt gradient để tránh bùng nổ (Gradient Clipping)
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()
