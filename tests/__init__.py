# ...existing code...
# Test script to verify components
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor

km = KnowledgeManager()
qp = QueryProcessor(km)

# Print all available concepts
print(f"Available concepts: {km.get_all_concepts()}")

# Test a few queries
test_queries = ["What is an algorithm?", "algorithm", "data structure"]
for query in test_queries:
    concept = qp.process_query(query)
    print(f"Query: '{query}' → Matched concept: '{concept}'")
