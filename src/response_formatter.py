class ResponseFormatter:
    def __init__(self, knowledge_manager):
        self.knowledge_manager = knowledge_manager
        
    def format_explanation(self, concept_name, complexity_level="intermediate"):
        """
        Format an explanation for a concept at the specified complexity level
        
        Args:
            concept_name: Name of the concept to explain
            complexity_level: Desired complexity ('beginner', 'intermediate', 'advanced')
            
        Returns:
            Formatted explanation as a string
        """
        concept = self.knowledge_manager.get_concept(concept_name)
        
        if not concept:
            return f"I don't have information about {concept_name} in my knowledge base."
        
        # Get the appropriate explanation based on complexity level
        explanation_key = f"{complexity_level}_explanation"
        if explanation_key not in concept:
            explanation_key = "intermediate_explanation"  # Fall back to intermediate
            if explanation_key not in concept:
                explanation_key = "definition"  # Last resort
        
        explanation = concept.get(explanation_key, "No explanation available.")
        
        # Format response with Markdown
        name = concept.get("name", concept_name.title())
        response = f"**{name}:** {concept.get('definition', '')}\n\n"
        response += explanation
        
        # Add related concepts if available
        related = concept.get("related_concepts", [])
        if related:
            response += "\n\n**Related concepts:** " + ", ".join(related)
        
        return response
