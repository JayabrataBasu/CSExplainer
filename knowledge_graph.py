import networkx as nx
import json

class KnowledgeGraph:
    def __init__(self, knowledge_path='data/cs_knowledge.json'):
        # Load CS knowledge
        with open(knowledge_path, 'r') as f:
            self.cs_knowledge = json.load(f)
            
        # Create knowledge graph
        self.graph = nx.DiGraph()
        
        # Build graph from knowledge
        self._build_graph()
        
    def _build_graph(self):
        """Constructs a dynamic knowledge graph from CS concepts"""
        for concept, details in self.cs_knowledge.items():
            self.graph.add_node(concept, **details)
            for prereq in details.get('prerequisites', []):
                self.graph.add_edge(prereq, concept)
            
    def get_concept_centrality(self, concept):
        """Returns how central a concept is in the knowledge graph"""
        centrality = nx.degree_centrality(self.graph)
        return centrality.get(concept, 0)
        
    def get_knowledge_frontier(self, mastered_concepts):
        """Identifies concepts that are just beyond the learner's current knowledge"""
        frontier = set()
        for concept in mastered_concepts:
            for neighbor in self.graph.successors(concept):
                if all(prereq in mastered_concepts for prereq in self.graph.predecessors(neighbor)):
                    frontier.add(neighbor)
        return list(frontier)
        
    def get_concept_difficulty(self, concept, learner_level='beginner'):
        """Get dynamic difficulty assessment for a concept"""
        base_difficulty = self.graph.nodes[concept].get('difficulty', 1)
        if learner_level == 'beginner':
            return base_difficulty
        elif learner_level == 'intermediate':
            return base_difficulty * 0.8
        elif learner_level == 'advanced':
            return base_difficulty * 0.6
        return base_difficulty
        
    def get_prerequisites(self, concept):
        """Get prerequisites for a concept"""
        return list(self.graph.predecessors(concept))
               
    def get_dependent_concepts(self, concept):
        """Get concepts that depend on this concept"""
        return list(self.graph.successors(concept))