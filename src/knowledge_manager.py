import json
import os

class KnowledgeManager:
    def __init__(self, knowledge_path="data/cs_knowledge.json", synonyms_path="data/synonyms.json"):
        self.knowledge_base = self._load_json(knowledge_path)
        self.synonyms = self._load_json(synonyms_path) if os.path.exists(synonyms_path) else {}
        
    def _load_json(self, file_path):
        """Load a JSON file into a Python dictionary."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}
            
    def get_concept(self, concept_name):
        """Retrieve a concept from the knowledge base."""
        # Try direct match
        if concept_name in self.knowledge_base:
            return self.knowledge_base[concept_name]
            
        # Try through synonyms
        for term, synonyms_list in self.synonyms.items():
            if concept_name in synonyms_list and term in self.knowledge_base:
                return self.knowledge_base[term]
                
        return None
        
    def get_all_concepts(self):
        """Return a list of all concept names in the knowledge base."""
        return list(self.knowledge_base.keys())
        
    def get_related_concepts(self, concept_name):
        """Get related concepts for a given concept."""
        concept = self.get_concept(concept_name)
        if concept and "related_concepts" in concept:
            return concept["related_concepts"]
        return []
