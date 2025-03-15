import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os

class PersonalizationEngine:
    def __init__(self, interactions_csv='data/user_interactions.csv'):
        # Initialize with default user levels
        self.default_levels = {0: 'beginner', 1: 'intermediate', 2: 'advanced'}
        
        try:
            if os.path.exists(interactions_csv) and os.path.getsize(interactions_csv) > 0:
                self.data = pd.read_csv(interactions_csv)
                if len(self.data) >= 3:  # Need at least 3 data points for meaningful clustering
                    self.model = KMeans(n_clusters=3, random_state=42)
                    self.model.fit(self.data[['interaction_time', 'questions_asked']])
                    self.has_training_data = True
                else:
                    self.has_training_data = False
            else:
                # Create an empty dataframe with the expected columns
                self.data = pd.DataFrame(columns=['interaction_time', 'questions_asked', 'level'])
                self.has_training_data = False
                
                # Create the file if it doesn't exist
                if not os.path.exists(interactions_csv):
                    # Make sure directory exists
                    os.makedirs(os.path.dirname(interactions_csv), exist_ok=True)
                    self.data.to_csv(interactions_csv, index=False)
        except Exception as e:
            print(f"Error initializing personalization engine: {e}")
            self.data = pd.DataFrame(columns=['interaction_time', 'questions_asked', 'level'])
            self.has_training_data = False

    def predict_user_level(self, user_features):
        """
        Predict the user level based on interaction features
        
        Args:
            user_features: List containing [interaction_time, questions_asked]
            
        Returns:
            String representing user level: 'beginner', 'intermediate', or 'advanced'
        """
        # Simple heuristic if we don't have enough training data
        if not self.has_training_data:
            interaction_time, questions_asked = user_features
            
            if interaction_time < 5 and questions_asked < 3:
                return 'beginner'
            elif interaction_time > 15 or questions_asked > 10:
                return 'advanced'
            else:
                return 'intermediate'
        
        # Use the trained model if available
        try:
            level_idx = self.model.predict([user_features])[0]
            return self.default_levels.get(level_idx, 'intermediate')
        except Exception:
            # Fallback to intermediate if prediction fails
            return 'intermediate'
            
    def record_interaction(self, user_features, predicted_level, interactions_csv='data/user_interactions.csv'):
        """
        Record user interaction data for future training
        
        Args:
            user_features: List containing [interaction_time, questions_asked]
            predicted_level: String representing the predicted level
        """
        interaction_time, questions_asked = user_features
        
        # Convert level to numeric for storage
        level_map = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        level_num = level_map.get(predicted_level, 1)
        
        # Create new row
        new_row = pd.DataFrame({
            'interaction_time': [interaction_time],
            'questions_asked': [questions_asked],
            'level': [level_num]
        })
        
        # Append to data
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        # Save to CSV
        try:
            self.data.to_csv(interactions_csv, index=False)
        except Exception as e:
            print(f"Error saving interaction data: {e}")

# Example usage
if __name__ == "__main__":
    engine = PersonalizationEngine()
    user_features = [15, 3]  # Example features: interaction_time, questions_asked
    level = engine.predict_user_level(user_features)
    print("Predicted user level:", level)
    
    # Record this interaction
    engine.record_interaction(user_features, level)
