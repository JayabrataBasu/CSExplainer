import numpy as np
from replay_buffer import ReplayBuffer

def train(agent, environment, episodes=1000, batch_size=32):
    """Train the agent using experience replay"""
    print(f"Training RL agent for {episodes} episodes...")
    
    # Initialize replay buffer
    replay_buffer = ReplayBuffer(capacity=10000)
    
    total_rewards = []
    
    for episode in range(episodes):
        state = environment.reset()
        episode_reward = 0
        done = False
        step_count = 0
        
        while not done and step_count < 100:
            # Select action using epsilon-greedy policy
            action = agent.select_action(state)
            
            # Take action and observe next state and reward
            next_state, reward, done, _ = environment.step(action)
            episode_reward += reward
            step_count += 1
            
            # Store experience in replay buffer
            replay_buffer.push(state, action, reward, next_state, done)
            
            # Move to next state
            state = next_state
            
            # Learn from experiences
            if len(replay_buffer) > batch_size:
                experiences = replay_buffer.sample(batch_size)
                for exp in experiences:
                    s, a, r, ns, d = exp
                    
                    # Q-learning update
                    target = r + (0 if d else agent.gamma * np.max(agent.q_table[ns]))
                    agent.q_table[s][a] += agent.alpha * (target - agent.q_table[s][a])
        
        total_rewards.append(episode_reward)
        if episode % 10 == 0:
            avg_reward = np.mean(total_rewards[-10:])
            print(f"Episode {episode}, Average Reward: {avg_reward}")
    
    return total_rewards
