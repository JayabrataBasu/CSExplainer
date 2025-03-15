import numpy as np
import json
import os
import pickle

class LearningEnvironment:
    """
    Environment for the reinforcement learning agent.
    Represents the state space of concepts and their relationships.
    """
    def __init__(self, concepts=None, difficulty_levels=None):
        # If concepts are provided, use them, otherwise load default
        if concepts:
            self.concepts = concepts
        else:
            self.concepts = self._load_default_concepts()
            
        # Number of concepts
        self.num_concepts = len(self.concepts)
        
        # Concept difficulty (0-1 scale)
        if difficulty_levels:
            self.difficulty = difficulty_levels
        else:
            self.difficulty = np.random.rand(self.num_concepts) * 0.5 + 0.3  # 0.3-0.8 range
        
        # Concept relationships (prerequisite graph)
        # If concept A is a prerequisite for B, then prerequisites[B][A] = 1
        self.prerequisites = np.zeros((self.num_concepts, self.num_concepts))
        self._generate_prerequisite_relationships()
        
        # Current state (concept index and mastery level)
        self.current_concept = 0
        self.mastery_levels = np.zeros(self.num_concepts)
        
    def _load_default_concepts(self):
        """Load default concepts from knowledge base"""
        try:
            with open('data/cs_knowledge.json', 'r') as f:
                knowledge = json.load(f)
                return list(knowledge.keys())
        except Exception:
            # Return some default concepts if loading fails
            return ["algorithms", "data structures", "recursion", "oop", "complexity analysis"]
    
    def _generate_prerequisite_relationships(self):
        """Generate a directed graph of concept prerequisites"""
        # Simple approach: Concepts with lower indices tend to be prerequisites for higher ones
        for i in range(1, self.num_concepts):
            # Each concept has 1-3 prerequisites from earlier concepts
            num_prereqs = min(i, np.random.randint(1, 4))
            prereq_indices = np.random.choice(i, num_prereqs, replace=False)
            for idx in prereq_indices:
                self.prerequisites[i][idx] = 1
    
    def reset(self, start_concept=None):
        """Reset the environment to initial state"""
        if start_concept is not None and 0 <= start_concept < self.num_concepts:
            self.current_concept = start_concept
        else:
            # Start from a concept with no prerequisites
            possible_starts = [i for i in range(self.num_concepts) 
                              if np.sum(self.prerequisites[i]) == 0]
            self.current_concept = np.random.choice(possible_starts)
            
        self.mastery_levels = np.zeros(self.num_concepts)
        return self.current_concept
    
    def step(self, action):
        """
        Take an action in the environment
        
        Args:
            action: Index of the next concept to study
            
        Returns:
            tuple of (next_state, reward, done)
        """
        # Check if action is valid
        if not (0 <= action < self.num_concepts):
            # Invalid action, penalize and don't change state
            return self.current_concept, -5, False
        
        # Check if prerequisites are met
        prereqs = self.prerequisites[action]
        prereqs_satisfied = True
        
        # If there are prerequisites with mastery level below 0.7, penalize
        for i in range(self.num_concepts):
            if prereqs[i] > 0 and self.mastery_levels[i] < 0.7:
                prereqs_satisfied = False
                break
        
        # Calculate reward and update state
        if not prereqs_satisfied:
            # Penalize for skipping prerequisites
            reward = -3.0
        else:
            # Base reward depends on concept difficulty
            difficulty = self.difficulty[action]
            
            # Higher reward for learning more advanced concepts when ready
            if self.mastery_levels[action] < 0.3:  # Not yet learned
                # Reward is inversely proportional to difficulty
                reward = 2.0 * (1.2 - difficulty)
            elif self.mastery_levels[action] < 0.7:  # Partially learned
                reward = 1.0
            else:  # Already well-learned
                reward = 0.2
                
            # Update mastery level for the concept
            self.mastery_levels[action] += (0.3 * (1 - self.mastery_levels[action]))
        
        # Update current concept
        self.current_concept = action
        
        # Check if done (all concepts mastered)
        done = np.all(self.mastery_levels >= 0.7)
            
        return action, reward, done
    
    def get_valid_actions(self):
        """Get list of valid next actions based on prerequisites"""
        valid_actions = []
        for action in range(self.num_concepts):
            # Check prerequisites
            prereqs_met = True
            for i in range(self.num_concepts):
                if self.prerequisites[action][i] > 0 and self.mastery_levels[i] < 0.5:
                    prereqs_met = False
                    break
            
            if prereqs_met:
                valid_actions.append(action)
                
        return valid_actions
    
    def get_state_representation(self):
        """Get a representation of the current state"""
        return {
            'current_concept': self.current_concept,
            'concept_name': self.concepts[self.current_concept],
            'mastery_levels': self.mastery_levels.tolist()
        }

class LearningPathRL:
    """Reinforcement learning agent for optimizing learning paths"""
    def __init__(self, env=None, alpha=0.1, gamma=0.9, epsilon=0.1):
        # Learning environment
        self.env = env if env else LearningEnvironment()
        
        # RL parameters
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate
        
        # Number of states and actions
        self.num_states = self.env.num_concepts
        self.num_actions = self.env.num_concepts
        
        # Q-table: Expected future rewards for state-action pairs
        self.q_table = np.zeros((self.num_states, self.num_actions))
        
        # Load pre-trained model if available
        self._load_model()
        
    def train(self, episodes=1000):
        """Train the agent through multiple episodes"""
        print(f"Training RL agent for {episodes} episodes...")
        
        # Track progress
        total_rewards = []
        
        for episode in range(episodes):
            state = self.env.reset()
            done = False
            episode_reward = 0
            step_count = 0
            
            while not done and step_count < 100:  # Limit steps to avoid infinite loops
                # Choose action using epsilon-greedy strategy
                if np.random.random() < self.epsilon:
                    # Explore: choose random valid action
                    valid_actions = self.env.get_valid_actions()
                    if not valid_actions:
                        # No valid actions, break out of episode
                        break
                    action = np.random.choice(valid_actions)
                else:
                    # Exploit: choose best action
                    action = np.argmax(self.q_table[state])
                
                # Take action and observe next state and reward
                next_state, reward, done = self.env.step(action)
                
                # Update Q-table using Q-learning formula
                self.q_table[state][action] += self.alpha * (
                    reward + 
                    self.gamma * np.max(self.q_table[next_state]) - 
                    self.q_table[state][action]
                )
                
                # Update state
                state = next_state
                episode_reward += reward
                step_count += 1
            
            total_rewards.append(episode_reward)
            
            # Reduce exploration rate over time
            self.epsilon = max(0.01, self.epsilon * 0.995)
            
            # Print progress
            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(total_rewards[-100:])
                print(f"Episode {episode + 1}/{episodes}, Avg Reward: {avg_reward:.2f}, Epsilon: {self.epsilon:.4f}")
        
        # Save the trained model
        self._save_model()
        
        return total_rewards
    
    def suggest_next_concept(self, current_concept_idx=None, mastery_levels=None):
        """
        Suggest the next concept to learn based on current state
        
        Args:
            current_concept_idx: Index of current concept (if None, use environment's)
            mastery_levels: Array of mastery levels for all concepts
            
        Returns:
            Index of the suggested next concept
        """
        # Update environment state if provided
        if current_concept_idx is not None:
            self.env.current_concept = current_concept_idx
            
        if mastery_levels is not None:
            self.env.mastery_levels = np.array(mastery_levels)
            
        # Get current state
        state = self.env.current_concept
        
        # Get valid actions
        valid_actions = self.env.get_valid_actions()
        
        if not valid_actions:
            # No valid actions, suggest the concept with highest mastery progress
            return np.argmax(self.env.mastery_levels)
        
        # Filter q_table for valid actions only
        valid_q_values = [self.q_table[state][action] for action in valid_actions]
        
        # Find best action
        best_action_idx = np.argmax(valid_q_values)
        best_action = valid_actions[best_action_idx]
        
        return best_action
    
    def get_optimal_path(self, start_concept=0):
        """
        Determine an optimal learning path from a starting concept
        
        Args:
            start_concept: Index of the starting concept
            
        Returns:
            List of concept indices representing the suggested path
        """
        # Reset environment
        self.env.reset(start_concept)
        
        # Follow optimal policy until done
        path = [start_concept]
        done = False
        step_count = 0
        
        while not done and step_count < self.num_states * 2:  # Avoid infinite loops
            # Get next concept using greedy policy
            next_concept = self.suggest_next_concept()
            
            # Skip if already in path (avoid cycles)
            if next_concept in path:
                # Choose an alternative that's not in the path
                valid_actions = [a for a in self.env.get_valid_actions() if a not in path]
                if not valid_actions:
                    break  # No more options
                next_concept = valid_actions[0]  # Take first valid action
            
            # Take action in environment
            _, _, done = self.env.step(next_concept)
            
            # Add to path
            path.append(next_concept)
            step_count += 1
            
            # Stop if all concepts have been covered
            if len(path) >= self.num_states:
                break
                
        return path
    
    def _save_model(self, filepath='data/rl_model.pkl'):
        """Save the trained model to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model data
            model_data = {
                'q_table': self.q_table,
                'env_concepts': self.env.concepts,
                'env_difficulty': self.env.difficulty,
                'env_prerequisites': self.env.prerequisites,
                'params': {
                    'alpha': self.alpha,
                    'gamma': self.gamma,
                    'epsilon': self.epsilon
                }
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
                
            print(f"Model saved to {filepath}")
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def _load_model(self, filepath='data/rl_model.pkl'):
        """Load a trained model from disk"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    model_data = pickle.load(f)
                    
                # Load model parameters
                self.q_table = model_data['q_table']
                
                # Check if dimensions match
                if self.q_table.shape != (self.num_states, self.num_actions):
                    print("Model dimensions don't match, initializing new model")
                    self.q_table = np.zeros((self.num_states, self.num_actions))
                else:
                    # Load environment parameters if needed
                    if 'params' in model_data:
                        self.alpha = model_data['params'].get('alpha', self.alpha)
                        self.gamma = model_data['params'].get('gamma', self.gamma)
                        self.epsilon = model_data['params'].get('epsilon', self.epsilon)
                        print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Initializing new model")

# Example usage:
if __name__ == "__main__":
    # Create learning environment
    env = LearningEnvironment()
    
    # Create learning agent
    agent = LearningPathRL(env)
    
    # Train for a small number of episodes for testing
    agent.train(episodes=100)
    
    # Get optimal learning path from first concept
    path = agent.get_optimal_path(0)
    print("\nSuggested learning path:")
    for i, concept_idx in enumerate(path):
        print(f"{i+1}. {env.concepts[concept_idx]}")
