import numpy as np
import random
import json

class RLAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        """
        Initialize a Reinforcement Learning Agent
        
        Args:
            state_size: Size of the state space
            action_size: Size of the action space
            alpha: Learning rate
            gamma: Discount factor for future rewards
            epsilon: Exploration rate
            epsilon_decay: Rate at which to decay epsilon
            epsilon_min: Minimum value of epsilon
        """
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Initialize Q-table
        self.q_table = np.zeros((state_size, action_size))
        
        # Load prerequisite relationships
        self.prerequisites = self._load_knowledge_relationships()

    def _load_knowledge_relationships(self):
        """Load prerequisite relationships from a JSON file"""
        try:
            with open('knowledge_graph.json', 'r') as file:
                data = json.load(file)
                
                # Create a prerequisite matrix
                prereq_matrix = np.zeros((self.state_size, self.state_size))
                
                # Fill the prerequisite matrix
                for concept, prereqs in data.items():
                    concept_id = int(concept)
                    for prereq in prereqs:
                        prereq_id = int(prereq)
                        prereq_matrix[concept_id][prereq_id] = 1
                        
                return prereq_matrix
        except FileNotFoundError:
            print("Knowledge graph file not found. Initializing empty prerequisite matrix.")
            return np.zeros((self.state_size, self.state_size))

    def select_action(self, state):
        """
        Select an action using epsilon-greedy policy
        
        Args:
            state: Current state
            
        Returns:
            Selected action
        """
        # Explore: choose a random action
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        # Exploit: choose the best action
        return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state, done):
        """
        Update Q-value for a state-action pair
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether the episode is done
        """
        # Q-learning update rule
        target = reward
        if not done:
            target += self.gamma * np.max(self.q_table[next_state])
        
        self.q_table[state][action] += self.alpha * (target - self.q_table[state][action])
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
