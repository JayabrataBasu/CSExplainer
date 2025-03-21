import os
from knowledge_graph import KnowledgeGraph
from reward_function import RewardFunction
from llm_knowledge_extractor import LLMKnowledgeExtractor

# Set your API key for the LLM (or set as environment variable)
# os.environ['LLM_API_KEY'] = 'your-api-key'

def main():
    # Initialize the knowledge extractor
    knowledge_extractor = LLMKnowledgeExtractor(knowledge_base_path='data/cs_knowledge.json')
    
    # Initialize the knowledge graph
    knowledge_graph = KnowledgeGraph(knowledge_path='data/cs_knowledge.json')
    
    # Example learner profile
    learner_profile = {
        'prior_knowledge': ['variables', 'loops'],
        'learning_style': 'visual',
        'visual_concepts': ['binary search', 'graphs']
    }
    
    # Initialize the reward function
    reward_function = RewardFunction(knowledge_graph, learner_profile)
    
    # Example current state and next state
    current_state = {
        'mastered_concepts': ['variables', 'loops']
    }
    next_state = {
        'mastered_concepts': ['variables', 'loops', 'binary search'],
        'is_terminal': lambda: False
    }
    
    # Calculate reward for learning binary search
    reward = reward_function.calculate_reward(current_state, "binary search", next_state)
    print(f"Reward for learning 'binary search': {reward}")
    
if __name__ == "__main__":
    main()