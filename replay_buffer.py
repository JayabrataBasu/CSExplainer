import random
import numpy as np
from collections import deque

class ReplayBuffer:
    """Experience replay buffer for reinforcement learning"""
    
    def __init__(self, capacity=10000):
        """
        Initialize replay buffer with fixed capacity
        
        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """
        Add experience to the buffer
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether the episode is done
        """
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size):
        """
        Sample a batch of experiences randomly
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of sampled experiences
        """
        if batch_size > len(self.buffer):
            batch_size = len(self.buffer)
        
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        """Return the current size of the buffer"""
        return len(self.buffer)
