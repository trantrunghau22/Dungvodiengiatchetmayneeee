import torch
import numpy as np
import os
from tqdm import tqdm
import matplotlib.pyplot as plt

# Import môi trường game của bạn
from game.core.env_2048 import Game2048Env
from game.rl.agent_dqn import DQNAgent

# Cấu hình huấn luyện
BATCH_SIZE = 128
NUM_EPISODES = 2000  # Số ván chơi
TARGET_UPDATE = 10   # Cập nhật mạng target sau mỗi 10 ván
CHECKPOINT_DIR = 'checkpoints'

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def preprocess_state(board):
    """
    XỬ LÝ ĐẶC BIỆT CHO GAME CÓ SỐ 1 (SHIN-CHAN)
    Quy đổi:
    - Ô 0 (Trống) -> 0.0
    - Ô 1 (Shin)  -> 1.0 (Không dùng log2)
    - Ô >= 2      -> log2(x) + 1.0 (VD: 2->2.0, 4->3.0, 256->9.0)
    """
    flat_board = board.flatten()
    processed = np.zeros_like(flat_board, dtype=np.float32)
    
    mask_0 = (flat_board == 0)
    mask_1 = (flat_board == 1)
    mask_others = (flat_board > 1)
    
    processed[mask_0] = 0.0
    processed[mask_1] = 1.0
    processed[mask_others] = np.log2(flat_board[mask_others]) + 1.0
    
    return torch.tensor(processed, dtype=torch.float32, device=device).unsqueeze(0)

def train():
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)

    env = Game2048Env(size=4)
    agent = DQNAgent(n_observations=16, n_actions=4, device=device)
    
    scores = []
    print(f"Training on: {device}")
    
    for i_episode in tqdm(range(NUM_EPISODES)):
        board = env.reset()
        state = preprocess_state(board)
        total_score = 0
        prev_score = 0
        
        for t in range(1000): # Giới hạn 1000 bước mỗi game
            # 1. Chọn hành động
            action = agent.select_action(state)
            
            # 2. Thực hiện hành động
            # env.step trả về: board, score, done, moved
            next_board, current_total_score, done, moved = env.step(action.item())
            
            # 3. Tính Reward
            step_reward = current_total_score - prev_score
            prev_score = current_total_score
            
            # Phạt nếu đi vào tường (không di chuyển được)
            if not moved:
                step_reward -= 10
            
            # Phạt nếu thua game
            if done:
                step_reward -= 50
                next_state = None
            else:
                next_state = preprocess_state(next_board)
                # Thưởng nhẹ cho việc ô lớn nhất tăng lên (khuyến khích)
                step_reward += np.max(next_board) / 2048.0

            reward = torch.tensor([step_reward], device=device)

            # 4. Lưu vào bộ nhớ và tối ưu hóa
            agent.memory.push(state, action, next_state, reward)
            state = next_state
            agent.optimize_model(BATCH_SIZE)

            if done:
                break
        
        scores.append(env.score)
        
        # Cập nhật mạng Target
        if i_episode % TARGET_UPDATE == 0:
            agent.target_net.load_state_dict(agent.policy_net.state_dict())
            
        # Lưu model định kỳ
        if (i_episode + 1) % 500 == 0:
            torch.save(agent.policy_net.state_dict(), f'{CHECKPOINT_DIR}/model_ep_{i_episode+1}.pth')

    print("Training Complete!")
    
    # Vẽ biểu đồ điểm số
    plt.plot(scores)
    plt.xlabel('Episode')
    plt.ylabel('Score')
    plt.title('Training Result')
    plt.savefig('training_result.png')
    plt.show()

if __name__ == "__main__":
    train()
