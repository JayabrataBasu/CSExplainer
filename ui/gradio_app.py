import gradio as gr
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor
from src.response_formatter import ResponseFormatter

class GradioApp:
    def __init__(self):
        self.knowledge_manager = KnowledgeManager()
        self.query_processor = QueryProcessor(self.knowledge_manager)
        self.response_formatter = ResponseFormatter(self.knowledge_manager)
        
    def process_query(self, query, complexity_level):
        """Process a user query and return a formatted response."""
        concept = self.query_processor.process_query(query)
        
        if concept:
            return self.response_formatter.format_explanation(concept, complexity_level)
        else:
            return "I couldn't find information about that concept. Please try another query."
            
    def list_available_concepts(self):
        """Return a string listing all available concepts."""
        concepts = self.knowledge_manager.get_all_concepts()
        return "Available concepts: " + ", ".join(concepts)
        
    def launch(self):
        """Launch the Gradio interface."""
        with gr.Blocks(title="CSExplainer") as demo:
            gr.Markdown("# CSExplainer\nAsk questions about computer science concepts")
            
            with gr.Row():
                with gr.Column():
                    query_input = gr.Textbox(label="Ask about a CS concept", placeholder="What is an algorithm?")
                    complexity = gr.Radio(
                        ["beginner", "intermediate", "advanced"], 
                        label="Explanation Level", 
                        value="intermediate"
                    )
                    submit_btn = gr.Button("Ask")
                    
                with gr.Column():
                    response_output = gr.Markdown(label="Explanation")
                    
            # Display available concepts
            concepts_output = gr.Markdown(self.list_available_concepts())
            
            # Set up event handlers
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input, complexity],
                outputs=response_output
            )
            
        demo.launch()
