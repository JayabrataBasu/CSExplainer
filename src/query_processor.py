import re
from src.knowledge_manager import KnowledgeManager

class QueryProcessor:
    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.question_patterns = [
            r"what is (?:an? )?(.*?)(?:\?|$)",
            r"explain (?:what )?(.*?)(?:\s+is)?(?:\?|$)",
            r"define (?:an? )?(.*?)(?:\?|$)",
            r"tell me about (.*?)(?:\?|$)"
        ]
        
    def process_query(self, query):
        """Process a user query and return the relevant concept."""
        query = query.lower().strip()
        
        # Check for direct concept match
        for concept in self.knowledge_manager.get_all_concepts():
            if concept.lower() == query:
                return concept
                
        # Try to extract concept using question patterns
        for pattern in self.question_patterns:
            match = re.search(pattern, query.lower())
            if match:
                potential_concept = match.group(1).strip()
                # Check if this is a known concept
                for concept in self.knowledge_manager.get_all_concepts():
                    if concept.lower() == potential_concept.lower():
                        return concept
                    # Handle plural/singular forms
                    if concept.lower() == "data structures" and potential_concept.lower() == "data structure":
                        return concept
                    if concept.lower() == "data structure" and potential_concept.lower() == "data structures":
                        return concept
        
        # Check for partial matches
        for concept in self.knowledge_manager.get_all_concepts():
            # Check if the concept is contained in the query
            if concept.lower() in query.lower():
                return concept
            
            # Handle special cases for common variations
            if concept.lower() == "data structures" and "data structure" in query.lower():
                return concept
            if concept.lower() == "object-oriented programming" and "oop" in query.lower():
                return concept
            if concept.lower() == "operating system" and "os" in query.lower():
                return concept
        
        # Try stemming/lemmatization approach (simplified)
        # Remove common endings and check again
        query_stem = self._simple_stem(query)
        for concept in self.knowledge_manager.get_all_concepts():
            concept_stem = self._simple_stem(concept)
            if concept_stem in query_stem or query_stem in concept_stem:
                return concept
        
        return None
    
    def determine_complexity_level(self, query):
        """Determine the complexity level based on the query."""
        if any(term in query.lower() for term in ["simple", "basic", "beginner", "easy"]):
            return "beginner"
        elif any(term in query.lower() for term in ["advanced", "complex", "detailed", "deep"]):
            return "advanced"
        else:
            return "intermediate"
    
    def _simple_stem(self, text):
        """Very simple stemming function to handle common variations."""
        text = text.lower()
        # Remove common endings
        for suffix in ["s", "ing", "ed", "es"]:
            if text.endswith(suffix):
                text = text[:-len(suffix)]
        return text
