import re
from src.query_processor import QueryProcessor
from src.knowledge_manager import KnowledgeManager
from src.response_formatter import ResponseFormatter
from src_ai.nlp_chatbot import NLPChatbot

class HybridResponseFormatter:
    """
    Combines rule-based knowledge with AI-enhanced content
    for more comprehensive explanations
    """
    def __init__(self, knowledge_manager=None):
        """Initialize with knowledge manager or create a new one"""
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.query_processor = QueryProcessor(self.knowledge_manager)
        self.response_formatter = ResponseFormatter(self.knowledge_manager)
        
        # Optional: Initialize NLP model (lazy loading)
        self._nlp_model = None
        
    @property
    def nlp_model(self):
        """Lazy load the NLP model when needed"""
        if self._nlp_model is None:
            try:
                self._nlp_model = NLPChatbot()
            except Exception as e:
                print(f"Error loading NLP model: {e}")
                # Return None if model can't be loaded
        return self._nlp_model
        
    def format_hybrid_response(self, query, complexity_level="intermediate", ai_enhancement=True):
        """
        Generate a hybrid response combining rule-based knowledge with AI enhancements
        
        Args:
            query: User's question
            complexity_level: Desired explanation complexity ('beginner', 'intermediate', 'advanced')
            ai_enhancement: Whether to include AI-generated enhancements
            
        Returns:
            Combined response as formatted text
        """
        # Get rule-based response
        rule_based_response = self._get_rule_based_response(query, complexity_level)
        
        # If AI enhancement is disabled or rule-based response not found
        if not ai_enhancement or rule_based_response.startswith("I don't have information"):
            return rule_based_response
        
        # Get AI-generated response
        ai_response = self._get_ai_response(query)
        
        # If AI response couldn't be generated
        if ai_response is None or ai_response == "":
            return rule_based_response
            
        # Combine responses
        combined_response = self._combine_responses(rule_based_response, ai_response)
        
        return combined_response
        
    def _get_rule_based_response(self, query, complexity_level):
        """Get response from the rule-based system"""
        # Process query to find relevant concept
        concept = self.query_processor.process_query(query)
        
        # If no concept found, return default message
        if not concept:
            return "I don't have information about that topic in my knowledge base."
            
        # Format explanation for the identified concept
        return self.response_formatter.format_explanation(concept, complexity_level)
        
    def _get_ai_response(self, query):
        """Get response from the AI model"""
        # If NLP model is not available, return empty response
        if self.nlp_model is None:
            return None
            
        try:
            # Generate response with the NLP model
            response = self.nlp_model.generate_response(query)
            return response
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return None
            
    def _combine_responses(self, rule_based, ai_generated):
        """
        Combine rule-based and AI-generated responses
        into a coherent explanation
        """
        # Extract the main title/concept from rule-based response
        title_match = re.match(r'\*\*(.*?):\*\*', rule_based)
        title = title_match.group(1) if title_match else "Concept"
        
        # Create section for additional insights
        ai_section = "\n\n## Additional Insights\n" + ai_generated
        
        # Combine with clear separation
        combined = (
            rule_based + 
            "\n\n---\n\n" +
            "**AI-Enhanced Explanation:**\n" + 
            ai_generated
        )
        
        return combined
        
    def suggest_related_queries(self, query, num_suggestions=3):
        """
        Generate related questions that the user might want to ask next
        
        Args:
            query: User's current question
            num_suggestions: Number of suggestions to generate
            
        Returns:
            List of suggested follow-up questions
        """
        # Identify concept from the query
        concept = self.query_processor.process_query(query)
        if not concept:
            return []
            
        # Get related concepts
        related_concepts = self.knowledge_manager.get_related_concepts(concept)
        
        # Generate follow-up questions based on related concepts
        suggestions = []
        
        # Question templates
        templates = [
            "What is {}?",
            "How does {} work?",
            "Explain the relationship between {} and {}.",
            "What are the applications of {}?",
            "Compare {} and {}."
        ]
        
        # Add questions about the main concept
        suggestions.append(f"Tell me more about {concept}.")
        suggestions.append(f"What are advanced applications of {concept}?")
        
        # Add questions about related concepts
        for rc in related_concepts[:min(5, len(related_concepts))]:
            template = templates[len(suggestions) % len(templates)]
            
            if "{}" in template and template.count("{}") > 1:
                # Template has two placeholders
                suggestions.append(template.format(concept, rc))
            else:
                # Template has one placeholder
                suggestions.append(template.format(rc))
                
            # Break if we have enough suggestions
            if len(suggestions) >= num_suggestions:
                break
                
        return suggestions[:num_suggestions]

# Example usage
if __name__ == "__main__":
    formatter = HybridResponseFormatter()
    
    # Test queries
    test_queries = [
        "What is recursion?",
        "Explain hash tables",
        "How do algorithms work?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = formatter.format_hybrid_response(query)
        print(f"Response:\n{response[:150]}...\n")
        
        suggestions = formatter.suggest_related_queries(query)
        print("Suggested follow-up questions:")
        for suggestion in suggestions:
            print(f"- {suggestion}")
        print("----------------------------------------")
