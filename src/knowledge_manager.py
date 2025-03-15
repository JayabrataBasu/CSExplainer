import json
import os

class KnowledgeManager:
    def __init__(self, knowledge_file='data/cs_knowledge.json'):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """Load the knowledge base from a JSON file"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r') as file:
                    return json.load(file)
            else:
                print(f"Knowledge file not found: {self.knowledge_file}")
                return {}
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {}
    
    def get_concept(self, concept_name):
        """Get information about a specific concept"""
        if not concept_name:
            return None
        
        concept_name = concept_name.lower()
        if concept_name in self.knowledge_base:
            return self.knowledge_base[concept_name]
        return None
    
    def get_all_concepts(self):
        """Get a list of all concept names"""
        return list(self.knowledge_base.keys())
    
    def get_related_concepts(self, concept_name):
        """Get related concepts for a given concept"""
        concept = self.get_concept(concept_name)
        if concept and "related_concepts" in concept:
            return concept["related_concepts"]
        return []
