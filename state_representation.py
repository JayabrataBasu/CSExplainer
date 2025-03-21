import numpy as np

class State:
    """Representation of a learning state in the CS learning path"""
    
    def __init__(self, concepts, prerequisites, learner_profile):
        """
        Initialize a state representation
        
        Args:
            concepts: List of concepts in the curriculum
            prerequisites: Dictionary mapping concepts to their prerequisites
            learner_profile: Profile of the learner including prior knowledge
        """
        self.concepts = concepts
        self.prerequisites = prerequisites
        self.learner_profile = learner_profile
        self.mastered_concepts = set(learner_profile.get('mastered_concepts', []))
        self.learning_goal = learner_profile.get('learning_goal', None)
        
        # Build state vector
        self.state_vector = self._build_state_vector()
        
    def _build_state_vector(self):
        """Build a vector representation of the state"""
        # Initialize a vector with 0s for each concept (0 = not mastered)
        vector = np.zeros(len(self.concepts))
        
        # Set mastered concepts to 1
        for concept_id in self.mastered_concepts:
            if 0 <= concept_id < len(self.concepts):
                vector[concept_id] = 1
                
        return vector
        
    def update(self, mastered_concept):
        """
        Update the state after a concept has been mastered
        
        Args:
            mastered_concept: ID of the newly mastered concept
        """
        if 0 <= mastered_concept < len(self.concepts):
            self.mastered_concepts.add(mastered_concept)
            self.state_vector[mastered_concept] = 1
            
    def get_available_concepts(self):
        """
        Get concepts that are available to learn based on prerequisites
        
        Returns:
            List of available concept IDs
        """
        available = []
        
        for concept_id in range(len(self.concepts)):
            # Skip already mastered concepts
            if concept_id in self.mastered_concepts:
                continue
                
            # Check if all prerequisites are mastered
            prereqs_mastered = True
            for prereq in self.prerequisites.get(str(concept_id), []):
                if int(prereq) not in self.mastered_concepts:
                    prereqs_mastered = False
                    break
                    
            if prereqs_mastered:
                available.append(concept_id)
                
        return available
        
    def is_terminal(self):
        """Check if the state is terminal (learning goal achieved)"""
        if self.learning_goal is None:
            # If no specific goal, check if all concepts are mastered
            return len(self.mastered_concepts) == len(self.concepts)
        else:
            # Check if learning goal is mastered
            return self.learning_goal in self.mastered_concepts
