import numpy as np

class RewardFunction:
    """Reward function for the CS learning path reinforcement learning environment"""
    
    def __init__(self, knowledge_graph, learner_profile):
        """
        Initialize the reward function with a dynamic knowledge graph
        
        Args:
            knowledge_graph: KnowledgeGraph instance with concept relationships
            learner_profile: Profile of the learner including prior knowledge and preferences
        """
        self.knowledge_graph = knowledge_graph
        self.learner_profile = learner_profile
        
        # Reward factors
        self.completion_reward = 10.0
        self.prerequisite_penalty = -5.0
        self.difficulty_factor = 0.5
        self.learning_style_match_bonus = 2.0
        
    def calculate_reward(self, current_state, action, next_state):
        """
        Calculate the reward for taking an action from current state with fluid knowledge
        
        Args:
            current_state: Current state representation
            action: Action taken (concept to learn)
            next_state: Resulting state after taking the action
            
        Returns:
            Calculated reward value
        """
        # Base reward - using dynamic difficulty assessment
        learner_level = self.learner_profile.get('level', 'beginner')
        difficulty = self.knowledge_graph.get_concept_difficulty(action, learner_level)
        base_reward = 1.0 / (difficulty + 0.1)  # Avoid division by zero
            
        # Check prerequisites - using knowledge graph relationships
        prerequisites = self.knowledge_graph.get_prerequisites(action)
        for prereq in prerequisites:
            if prereq not in current_state.mastered_concepts:
                return self.prerequisite_penalty * (1.0 - self.learner_profile.get('risk_tolerance', 0.5))
                
        # Importance factor - rewards concepts that are more central in knowledge graph
        centrality = self.knowledge_graph.get_concept_centrality(action)
        importance_factor = 3.0 * centrality
        
        # Learning style match using topic characteristics
        learning_style_bonus = 0
        learner_style = self.learner_profile.get('learning_style', 'visual')
        
        # Check examples for matching content types
        if action in self.knowledge_graph.graph.nodes:
            examples = self.knowledge_graph.graph.nodes[action].get('examples', [])
            for example in examples:
                if self._matches_learning_style(example, learner_style):
                    learning_style_bonus += self.learning_style_match_bonus
                    break
        
        # Knowledge frontier bonus - encourage exploration at the right difficulty
        frontier_bonus = 0
        if action in self.knowledge_graph.get_knowledge_frontier(current_state.mastered_concepts):
            frontier_bonus = 2.0
            
        # Efficiency factor - reward for choosing concepts that unlock many others
        dependent_concepts = len(self.knowledge_graph.get_dependent_concepts(action))
        efficiency_factor = 0.2 * dependent_concepts
        
        # Calculate final reward
        reward = base_reward + learning_style_bonus + importance_factor + frontier_bonus + efficiency_factor
        
        # Terminal state bonus
        if next_state.is_terminal():
            reward += self.completion_reward
            
        return reward
        
    def _matches_learning_style(self, example, learning_style):
        """Determine if an example matches the learner's preferred style"""
        if isinstance(example, dict):
            example_name = example.get('name', '').lower()
            example_desc = example.get('description', '').lower()
        else:
            example_name = ''
            example_desc = str(example).lower()
        
        visual_keywords = ['diagram', 'graph', 'visual', 'image', 'picture']
        practical_keywords = ['implementation', 'application', 'example', 'project']
        theoretical_keywords = ['theorem', 'proof', 'concept', 'theory', 'mathematical']
        
        if learning_style == 'visual':
            return any(kw in example_name or kw in example_desc for kw in visual_keywords)
        elif learning_style == 'practical':
            return any(kw in example_name or kw in example_desc for kw in practical_keywords)
        elif learning_style == 'theoretical':
            return any(kw in example_name or kw in example_desc for kw in theoretical_keywords)
            
        return False
