import requests
import json
import os

class LLMKnowledgeExtractor:
    """Uses LLM to dynamically extract and organize CS knowledge"""
    
    def __init__(self, api_key=None, knowledge_base_path='data/cs_knowledge.json'):
        self.api_key = api_key or os.environ.get('LLM_API_KEY')
        self.knowledge_base_path = knowledge_base_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(knowledge_base_path), exist_ok=True)
        
        # Load existing knowledge if it exists
        if os.path.exists(knowledge_base_path):
            with open(knowledge_base_path, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            # Initialize with empty knowledge base
            self.knowledge_base = {}
            self._save_knowledge_base()
            
    def enrich_concept(self, concept_name):
        """Dynamically enriches a concept with LLM-generated knowledge"""
        concept_name = concept_name.lower()  # Normalize concept name
        
        if concept_name not in self.knowledge_base:
            # Create new concept entry
            self.knowledge_base[concept_name] = {
                "definition": "",
                "complexity_levels": {},
                "prerequisites": [],
                "related_concepts": [],
                "examples": []
            }
            
        # Use LLM to generate or enhance definition
        enriched_definition = self._query_llm(
            f"Provide a comprehensive definition of '{concept_name}' in computer science.")
        self.knowledge_base[concept_name]["definition"] = enriched_definition
        
        # Generate complexity levels
        for level in ["beginner", "intermediate", "advanced"]:
            prompt = f"Explain the computer science concept '{concept_name}' at a {level} level."
            explanation = self._query_llm(prompt)
            self.knowledge_base[concept_name]["complexity_levels"][level] = explanation
            
        # Find prerequisites
        prereq_prompt = f"List 2-3 prerequisite concepts that someone should understand before learning '{concept_name}' in computer science, one per line."
        prereq_response = self._query_llm(prereq_prompt)
        prerequisites = [p.strip().lower() for p in prereq_response.split('\n') if p.strip()]
        self.knowledge_base[concept_name]["prerequisites"] = prerequisites
        
        # Find related concepts
        related_prompt = f"List 3-5 closely related computer science concepts to '{concept_name}', one per line."
        related_response = self._query_llm(related_prompt)
        related_concepts = [rc.strip().lower() for rc in related_response.split('\n') if rc.strip()]
        self.knowledge_base[concept_name]["related_concepts"] = related_concepts
        
        # Generate examples
        examples_prompt = f"Provide 2 practical examples of '{concept_name}' in computer science. For each, include: 1) A name/title, and 2) A description of how it demonstrates the concept."
        examples_response = self._query_llm(examples_prompt)
        
        # Parse examples (simplified)
        examples = []
        current_example = {}
        
        for line in examples_response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Example") or line.startswith("1.") or line.startswith("2."):
                if current_example and 'name' in current_example:
                    examples.append(current_example)
                current_example = {"name": line.split(":", 1)[1].strip() if ":" in line else line}
            elif "name" in current_example and line:
                if "description" not in current_example:
                    current_example["description"] = line
                else:
                    current_example["description"] += " " + line
        
        # Add the last example if it exists
        if current_example and 'name' in current_example:
            examples.append(current_example)
            
        self.knowledge_base[concept_name]["examples"] = examples
        
        # Save updated knowledge base
        self._save_knowledge_base()
        
        return self.knowledge_base[concept_name]
    
    def _query_llm(self, prompt):
        """Queries an LLM API with the given prompt"""
        response = requests.post(
            "https://api.example.com/llm",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt}
        )
        response.raise_for_status()
        return response.json().get("text", "")
        
    def _save_knowledge_base(self):
        """Saves the updated knowledge base to disk"""
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=4)