import unittest
from src.query_processor import QueryProcessor
from src.knowledge_manager import KnowledgeManager

class TestQueryProcessor(unittest.TestCase):
    def setUp(self):
        km = KnowledgeManager("data/cs_knowledge.json", "data/synonyms.json")
        self.qp = QueryProcessor(km)

    def test_process_query(self):
        # Test processing a query
        pass

if __name__ == "__main__":
    unittest.main()
