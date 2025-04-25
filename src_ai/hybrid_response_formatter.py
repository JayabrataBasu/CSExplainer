import re
import random
import time
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor
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
        
        # Additional properties
        self._ai_cache = {}  # Simple cache for AI responses
        self._quality_thresholds = {
            'min_length': 50,  # Minimum acceptable response length
            'max_repetition': 0.7,  # Maximum acceptable repetition ratio
            'relevancy_threshold': 0.5  # Minimum relevancy score
        }

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
        
        # Normalize query for cache key
        cache_key = f"{query.lower().strip()}_{complexity_level}"
        
        # If AI enhancement is disabled or rule-based response not found
        if not ai_enhancement or rule_based_response.startswith("I don't have information"):
            return rule_based_response
            
        # Try to get response from cache to avoid repeated API calls
        if cache_key in self._ai_cache and time.time() - self._ai_cache[cache_key]['timestamp'] < 3600:
            ai_response = self._ai_cache[cache_key]['response']
        else:
            # Get AI-generated response
            ai_response = self._get_ai_response(query, complexity_level)
            
            # Cache the response
            if ai_response:
                self._ai_cache[cache_key] = {
                    'response': ai_response,
                    'timestamp': time.time()
                }
        
        # Evaluate and ensure AI response quality
        if not self._is_quality_response(ai_response, query, rule_based_response):
            # Try another approach if response is low quality
            enhanced_query = self._enhance_query(query, rule_based_response)
            ai_response = self._get_ai_response(enhanced_query, complexity_level)
            
            # If still poor quality, use rule-based only with a note
            if not self._is_quality_response(ai_response, query, rule_based_response):
                return rule_based_response + "\n\n*AI enhancement unavailable for this query.*"
            
        # Combine responses
        combined_response = self._combine_responses(rule_based_response, ai_response, complexity_level)
        
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
        
    def _get_ai_response(self, query, complexity_level="intermediate"):
        """Get response from the AI model with complexity guidance"""
        # If NLP model is not available, return empty response
        if self.nlp_model is None:
            return None
            
        try:
            # Build a more specific prompt based on complexity level
            level_guidance = {
                "beginner": "using simple analogies and basic concepts",
                "intermediate": "using technical terms with clear explanations",
                "advanced": "with detailed technical implementation and theory"
            }
            
            # Extract concept name for better focus
            concept = self.query_processor.process_query(query)
            context = ""
            if concept:
                context = f" The primary concept is '{concept}'."
                
            prompt = f"Explain the following computer science topic {level_guidance.get(complexity_level, '')}.{context} {query}"
            
            # Generate response with the NLP model
            response = self.nlp_model.generate_response(prompt)
            return response
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return None
            
    def _combine_responses(self, rule_based, ai_generated, complexity_level):
        """
        Combine rule-based and AI-generated responses
        into a coherent explanation with appropriate formatting
        based on complexity level
        """
        # Extract the main title/concept from rule-based response
        title_match = re.match(r'\*\*(.*?):\*\*', rule_based)
        title = title_match.group(1) if title_match else "Concept"
        
        # Identify sections that might be in both responses to avoid duplication
        rule_paragraphs = rule_based.split('\n\n')
        ai_paragraphs = ai_generated.split('\n\n') if ai_generated else []
        
        # Different presentation styles based on complexity level
        if complexity_level == "beginner":
            # For beginners: Simple, clean presentation
            combined = rule_based + "\n\n---\n\n"
            combined += "**Additional Insights:**\n" + self._extract_unique_content(ai_generated, rule_based)
            
        elif complexity_level == "advanced":
            # For advanced: More technical, comprehensive presentation
            # Add a technical deep dive section from AI response
            combined = rule_based + "\n\n---\n\n"
            combined += "**Technical Deep Dive:**\n" + ai_generated
            combined += "\n\n**Sources and References:**\n" + self._generate_references(title)
            
        else:
            # For intermediate: Balanced approach with sections
            unique_ai_content = self._extract_unique_content(ai_generated, rule_based)
            
            combined = rule_based + "\n\n---\n\n"
            combined += "**Enhanced Explanation:**\n" + unique_ai_content
            
            # Add practical examples section if available
            if "example" in ai_generated.lower() or "application" in ai_generated.lower():
                examples = self._extract_examples(ai_generated)
                if examples:
                    combined += "\n\n**Practical Applications:**\n" + examples
        
        return combined

    def _extract_unique_content(self, ai_content, rule_content):
        """Extract content from AI response that isn't already in rule-based response"""
        if not ai_content:
            return ""
            
        # Simple approach: split into sentences and compare
        ai_sentences = re.split(r'(?<=[.!?])\s+', ai_content)
        rule_sentences = re.split(r'(?<=[.!?])\s+', rule_content)
        
        # Simplified content fingerprints for comparison
        rule_fingerprints = [self._get_sentence_fingerprint(s) for s in rule_sentences]
        
        unique_sentences = []
        for sentence in ai_sentences:
            if not any(self._similarity(self._get_sentence_fingerprint(sentence), fp) > 0.7 for fp in rule_fingerprints):
                unique_sentences.append(sentence)
                
        # Return unique content or a fallback message
        if unique_sentences:
            return " ".join(unique_sentences)
        else:
            return "No additional unique insights available from AI enhancement."
            
    def _get_sentence_fingerprint(self, sentence):
        """Create a simple fingerprint of a sentence for comparison"""
        # Remove punctuation and lowercase
        words = re.sub(r'[^\w\s]', '', sentence.lower()).split()
        # Keep only significant words (4+ chars) and sort them
        return " ".join(sorted([w for w in words if len(w) > 3]))
        
    def _similarity(self, fp1, fp2):
        """Simple similarity metric between two fingerprints"""
        if not fp1 or not fp2:
            return 0
        words1 = set(fp1.split())
        words2 = set(fp2.split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / max(len(union), 1)

    def _extract_examples(self, content):
        """Extract examples from AI content"""
        example_paragraphs = []
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if any(term in para.lower() for term in ["example", "application", "use case", "instance"]):
                example_paragraphs.append(para)
                
        if example_paragraphs:
            return "\n\n".join(example_paragraphs)
        return ""

    def _generate_references(self, concept):
        """Generate sample references related to the concept"""
        # Simple placeholder reference generator
        references = [
            f"Smith, J. (2023). Understanding {concept} in Modern Computing. Journal of Computer Science, 42(3), 78-92.",
            f"Advanced {concept} Techniques (2022). MIT Computer Science Documentation.",
            f"https://en.wikipedia.org/wiki/{concept.replace(' ', '_')}"
        ]
        return "\n".join(references)
        
    def _is_quality_response(self, response, query, rule_based):
        """Check if AI response meets quality criteria"""
        if not response:
            return False
            
        # Check length
        if len(response) < self._quality_thresholds['min_length']:
            return False
            
        # Check for repetition (simplified)
        words = response.lower().split()
        unique_words = set(words)
        if len(unique_words) / max(len(words), 1) < (1 - self._quality_thresholds['max_repetition']):
            return False
            
        # Check relevance to query (simplified)
        query_words = set(re.sub(r'[^\w\s]', '', query.lower()).split())
        response_words = set(re.sub(r'[^\w\s]', '', response.lower()).split())
        relevance = len(query_words.intersection(response_words)) / max(len(query_words), 1)
        
        if relevance < self._quality_thresholds['relevancy_threshold']:
            return False
            
        return True
        
    def _enhance_query(self, original_query, rule_based):
        """Enhance the query based on rule-based response to get better AI response"""
        # Extract concept from rule-based response
        concept_match = re.match(r'\*\*(.*?):\*\*', rule_based)
        concept = concept_match.group(1) if concept_match else ""
        
        enhanced_queries = [
            f"Explain {concept} in computer science with examples and applications",
            f"What are the key aspects of {concept} in computing?",
            f"Describe how {concept} works in computer science"
        ]
        
        return random.choice(enhanced_queries) if concept else original_query

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
