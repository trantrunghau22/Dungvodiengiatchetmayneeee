import os
import torch
import numpy as np
from tqdm import tqdm
from game.core.env_2048 import Game2048Env
from game.rl.agent_dqn import DQNAgent
from game.rl.memory import ReplayMemory

# Thiết lập
EPISODES = 2000          # Số ván chơi để học
BATCH_SIZE = 64          # Kích thước mẫu học mỗi lần
TARGET_UPDATE = 10       # Sau bao nhiêu ván thì cập nhật mạng Target
CHECKPOINT_DIR = "checkpoints"

if not os.path.exists(CHECKPOINT_DIR):
    os.makedirs(CHECKPOINT_DIR)

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    env = Game2048Env()
    agent = DQNAgent(device=device)
    memory = ReplayMemory(10000)
    
    best_score = 0
    
    # Progress bar để theo dõi
    progress_bar = tqdm(range(EPISODES))
    
    for e in progress_bar:
        state = env.reset()
        # Biến score này của env tích lũy, nên ta cần biến tracking riêng cho reward
        prev_score = 0 
        total_reward = 0
        done = False
        
        while not done:
            # 1. Chọn hành động
            action = agent.act(state)
            
            # 2. Thực hiện hành động
            next_state, current_score, done, moved = env.step(action)
            
            # 3. Thiết kế Reward (Đã tối ưu)
            step_reward = 0
            diff = current_score - prev_score
            
            # --- A. Phạt nặng nếu đi vào tường (Ưu tiên cao nhất) ---
            if not moved:
                step_reward = -10
            else:
                # --- B. Điểm từ việc gộp số (Dùng Log2 để chuẩn hóa) ---
                if diff > 0:
                    step_reward += np.log2(diff)
                    # Thưởng thêm nếu đạt mốc quan trọng (Kích thích AI lên số to)
                    if diff >= 512: step_reward += 5
                    if diff >= 1024: step_reward += 10
                    if diff >= 2048: step_reward += 20
                
                # --- C. Thưởng ô trống (Sống sót là quan trọng) ---
                empty_tiles = len(list(zip(*np.where(next_state == 0))))
                step_reward += empty_tiles * 0.1

                # --- D. Chiến thuật: Số to nhất nằm ở góc ---
                # Giúp AI định hướng bàn cờ gọn gàng
                max_tile = np.max(next_state)
                corners = [(0,0), (0,3), (3,0), (3,3)]
                in_corner = False
                for r, c in corners:
                    if next_state[r, c] == max_tile:
                        in_corner = True
                        break
                if in_corner:
                    step_reward += 2 # Thưởng nóng vì biết giữ "Vua" ở góc

                # --- E. Cơ chế đặc biệt: Số 1 nằm cạnh 256 ---
                ones = list(zip(*np.where(next_state == 1)))
                two_fiftysixes = list(zip(*np.where(next_state == 256)))
                
                for r1, c1 in ones:
                    # Nếu có nhiều số 1, ta chỉ cần xét 1 cặp gần nhất là được thưởng
                    found_pair = False
                    for r2, c2 in two_fiftysixes:
                        dist = abs(r1 - r2) + abs(c1 - c2)
                        if dist == 1:
                            step_reward += 5 # Thưởng đậm để khuyến khích ghép cặp này
                            found_pair = True
                            break
                    if found_pair: break 
            
            # --- F. Phạt nếu thua ---
            if done:
                step_reward -= 10

            prev_score = current_score
            
            # 4. Lưu vào bộ nhớ
            memory.push(state, action, step_reward, next_state, done)
            
            # 5. Cập nhật trạng thái
            state = next_state
            total_reward += step_reward
            
            # 6. Train model
            agent.replay(memory, BATCH_SIZE)
        
        # Hết 1 ván: Cập nhật epsilon và Target Network
        agent.decay_epsilon()
        if e % TARGET_UPDATE == 0:
            agent.update_target_network()
            
        # Lưu model nếu đạt kỷ lục mới
        if current_score > best_score:
            best_score = current_score
            agent.save(os.path.join(CHECKPOINT_DIR, "best_model.pth"))
            
        progress_bar.set_description(f"Ep: {e} | Score: {current_score} | Best: {best_score} | Eps: {agent.epsilon:.2f}")

    # Lưu model cuối cùng
    agent.save(os.path.join(CHECKPOINT_DIR, "final_model.pth"))
    print("Training Complete!")

if __name__ == "__main__":
    train()