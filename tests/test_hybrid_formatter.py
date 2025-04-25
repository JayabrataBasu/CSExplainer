from src_ai.hybrid_response_formatter import HybridResponseFormatter
from src.knowledge_manager import KnowledgeManager

def test_hybrid_response():
    """Test the hybrid response formatter with different complexity levels"""
    # Initialize formatter
    knowledge_manager = KnowledgeManager()
    formatter = HybridResponseFormatter(knowledge_manager)
    
    # Test queries
    test_queries = [
        "What is a hash table?",
        "Explain binary trees",
        "How does quantum computing work?",
        "What is machine learning?"
    ]
    
    # Test at different complexity levels
    levels = ["beginner", "intermediate", "advanced"]
    
    for query in test_queries:
        print(f"\n===== Testing: {query} =====\n")
        for level in levels:
            print(f"\n--- Complexity Level: {level} ---\n")
            response = formatter.format_hybrid_response(query, complexity_level=level)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("\n" + "-"*50)

if __name__ == "__main__":
    print("Testing Improved Hybrid Response Formatter")
    test_hybrid_response()
