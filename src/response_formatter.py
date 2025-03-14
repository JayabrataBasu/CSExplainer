class ResponseFormatter:
    def __init__(self, knowledge_manager):
        self.knowledge_manager = knowledge_manager
        
    def format_explanation(self, concept_name, complexity_level="intermediate"):
        """Format an explanation for a concept at the specified complexity level."""
        concept = self.knowledge_manager.get_concept(concept_name)
        if not concept:
            return f"I don't have information about '{concept_name}'."
            
        # Build the response
        response = []
        
        # Add definition
        if "definition" in concept:
            response.append(f"**{concept_name.title()}**: {concept['definition']}")
            
        # Add complexity-specific explanation
        if "complexity_levels" in concept and complexity_level in concept["complexity_levels"]:
            response.append(f"\n{concept['complexity_levels'][complexity_level]}")
        
        # Add examples if available
        if "examples" in concept and concept["examples"]:
            response.append("\n**Examples:**")
            for example in concept["examples"]:
                response.append(f"- **{example['name']}**: {example['description']}")
                
        # Add related concepts
        if "related_concepts" in concept and concept["related_concepts"]:
            related = concept["related_concepts"]
            response.append(f"\n**Related concepts:** {', '.join(related)}")
            
        return "\n".join(response)
