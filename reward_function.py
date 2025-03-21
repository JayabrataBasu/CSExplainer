import numpy as np

class RewardFunction:
    """Reward function for the CS learning path reinforcement learning environment"""
    
    def __init__(self, concept_difficulties, prerequisites, learner_profile):
        """
        Initialize the reward function
        
        Args:
            concept_difficulties: Dictionary mapping concepts to their difficulty levels
            prerequisites: Dictionary mapping concepts to their prerequisites
            learner_profile: Profile of the learner including prior knowledge and preferences
        """
        self.concept_difficulties = concept_difficulties
        self.prerequisites = prerequisites
        self.learner_profile = learner_profile
        
        # Reward factors
        self.completion_reward = 10.0
        self.prerequisite_penalty = -5.0
        self.difficulty_factor = 0.5
        self.learning_style_match_bonus = 2.0
        
    def calculate_reward(self, current_state, action, next_state):
        """
        Calculate the reward for taking an action from current state
        
        Args:
            current_state: Current state representation
            action: Action taken (concept to learn)
            next_state: Resulting state after taking the action
            
        Returns:
            Calculated reward value
        """
        # Base reward - inversely proportional to concept difficulty
        if action in self.concept_difficulties:
            difficulty = self.concept_difficulties[action]
            base_reward = 1.0 / (difficulty + 0.1)  # Avoid division by zero
        else:
            base_reward = 1.0
            
        # Check prerequisites - penalize if prerequisites not met
        for prereq in self.prerequisites.get(str(action), []):
            if prereq not in current_state.mastered_concepts:
                return self.prerequisite_penalty
                
        # Bonus for matching learning style
        learning_style_bonus = 0
        if self.learner_profile.get('learning_style') == 'visual' and action in self.learner_profile.get('visual_concepts', []):
            learning_style_bonus = self.learning_style_match_bonus
        
        # Efficiency factor - reward for choosing concepts that unlock many others
        dependent_concepts = sum(1 for concept, prereqs in self.prerequisites.items() if str(action) in prereqs)
        efficiency_factor = 0.2 * dependent_concepts
        
        # Calculate final reward
        reward = base_reward + learning_style_bonus + efficiency_factor
        
        # Terminal state bonus
        if next_state.is_terminal():
            reward += self.completion_reward
            
        return reward
