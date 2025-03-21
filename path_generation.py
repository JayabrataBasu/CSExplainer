import numpy as np

def generate_learning_path(agent, environment, start_concept, target_concept=None, max_steps=100):
    """
    Generate an optimal learning path using the trained RL agent
    
    Args:
        agent: Trained RL agent
        environment: Learning environment
        start_concept: Starting concept ID
        target_concept: Target concept ID (None if targeting all concepts)
        max_steps: Maximum number of steps in the path
        
    Returns:
        List of concepts representing the optimal learning path
    """
    # Initialize environment with the starting concept
    state = environment.reset(start_concept=start_concept)
    
    path = [start_concept]
    visited = set([start_concept])
    step_count = 0
    
    while step_count < max_steps:
        # Get action with highest Q-value
        q_values = agent.q_table[state]
        
        # Filter out already visited concepts
        valid_actions = []
        valid_q_values = []
        
        for action, q_value in enumerate(q_values):
            if action not in visited and action in environment.get_available_actions(state):
                valid_actions.append(action)
                valid_q_values.append(q_value)
        
        # If no valid actions or reached target, terminate
        if not valid_actions or (target_concept is not None and target_concept in visited):
            break
            
        # Select best action
        action = valid_actions[np.argmax(valid_q_values)] if valid_q_values else -1
        
        if action == -1:
            break
            
        # Take action
        next_state, _, done, _ = environment.step(action)
        
        # Update path
        path.append(action)
        visited.add(action)
        state = next_state
        step_count += 1
        
        if done:
            break
    
    return path
