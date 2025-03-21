import numpy as np
import os
from knowledge_graph import KnowledgeGraph
from reward_function import RewardFunction
from llm_knowledge_extractor import LLMKnowledgeExtractor

class CSLearningEnvironment:
    """RL environment for CS learning path planning"""
    
    def __init__(self, knowledge_path='data/cs_knowledge.json', use_llm=True):
        self.knowledge_path = knowledge_path
        self.use_llm = use_llm
        
        # Initialize knowledge graph
        self.knowledge_graph = KnowledgeGraph(knowledge_path=knowledge_path)
        
        # Initialize reward function
        self.reward_function = RewardFunction(self.knowledge_graph, self.learner_profile)
        
        self.reset()
        
    def reset(self):
        """Reset the environment to initial state"""
        self.current_state = State()
        self.learner_profile = {}
        
    def step(self, action):
        """Take a step in the environment"""
        reward = self.reward_function.calculate_reward(self.current_state, action, self.current_state)
        
        # Update state
        new_mastered = self.current_state.mastered_concepts.copy()
        if action not in new_mastered:
            new_mastered.append(action)
            
        next_state = State(mastered_concepts=new_mastered)
        
        done = self._is_curriculum_complete(next_state)
        
        return next_state, reward, done, {}
        
    def get_available_actions(self):
        """Get all available actions from current state"""
        return [concept for concept in self.knowledge_graph.concepts if concept not in self.current_state.mastered_concepts]
        
    def _is_curriculum_complete(self, state):
        """Check if the curriculum is complete"""
        return len(state.mastered_concepts) == len(self.knowledge_graph.concepts)
        
    def set_learner_profile(self, profile):
        """Update the learner profile"""
        self.learner_profile = profile

class State:
    """State representation for the CS learning environment"""
    
    def __init__(self, mastered_concepts=None):
        self.mastered_concepts = mastered_concepts if mastered_concepts is not None else []
        
    def is_terminal(self):
        """Placeholder for terminal state check"""
        return False