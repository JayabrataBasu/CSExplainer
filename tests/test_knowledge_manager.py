import unittest
from src.knowledge_manager import KnowledgeManager

class TestKnowledgeManager(unittest.TestCase):
    def setUp(self):
        self.km = KnowledgeManager("data/cs_knowledge.json", "data/synonyms.json")

    def test_load_knowledge_base(self):
        # Test loading the knowledge base
        
        pass

    def test_load_synonyms(self):
        # Test loading the synonyms
        pass

    def test_query(self):
        # Test querying the knowledge base
        pass

if __name__ == "__main__":
    unittest.main()
