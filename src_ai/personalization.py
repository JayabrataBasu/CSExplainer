import pandas as pd
from sklearn.cluster import KMeans

class PersonalizationEngine:
    def __init__(self, interactions_csv='data/user_interactions.csv'):
        self.data = pd.read_csv(interactions_csv)
        self.model = KMeans(n_clusters=3, random_state=42)
        self.model.fit(self.data)

    def predict_user_level(self, user_features):
        level = self.model.predict([user_features])[0]
        levels = {0: 'beginner', 1: 'intermediate', 2: 'advanced'}
        return levels.get(level, 'intermediate')

# Example usage
if __name__ == "__main__":
    engine = PersonalizationEngine()
    user_features = [15, 3]  # Example features: interaction_time, questions_asked
    print("Predicted user level:", engine.predict_user_level(user_features))
