import re
from src.knowledge_manager import KnowledgeManager

class QueryProcessor:
    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        
    def process_query(self, query):
        """
        Process a query to identify the concept being asked about
        
        Args:
            query: User's question as a string
            
        Returns:
            String representing the identified concept, or None if not found
        """
        if not query:
            return None
            
        # Clean query
        query = query.lower().strip()
        
        # Look for exact matches among concept names
        for concept in self.knowledge_manager.get_all_concepts():
            if concept in query:
                return concept
        
        # If no exact match, look for keyword matches
        # This is a simple approach and could be improved
        keywords = self._extract_keywords(query)
        
        for concept in self.knowledge_manager.get_all_concepts():
            concept_info = self.knowledge_manager.get_concept(concept)
            if any(keyword in concept for keyword in keywords):
                return concept
                
        return None
    
    def _extract_keywords(self, query):
        """Extract potential keywords from the query"""
        # Remove common words
        common_words = ["what", "is", "a", "the", "how", "does", "do", "explain", "tell", "me", "about"]
        words = query.split()
        keywords = [word for word in words if word not in common_words]
        return keywords
