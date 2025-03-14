import gradio as gr
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor
from src.response_formatter import ResponseFormatter

class GradioApp:
    def __init__(self):
        self.knowledge_manager = KnowledgeManager()
        self.query_processor = QueryProcessor(self.knowledge_manager)
        self.response_formatter = ResponseFormatter(self.knowledge_manager)
        self.history = []
        
    def process_query(self, query, complexity_level):
        """Process a user query and return a formatted response."""
        if not query.strip():
            return "Please enter a question about a computer science concept."
            
        concept = self.query_processor.process_query(query)
        
        response = ""
        if concept:
            response = self.response_formatter.format_explanation(concept, complexity_level)
        else:
            response = "I couldn't find information about that concept. Please try another query."
            
        # Add to history
        self.history.append((query, complexity_level, response))
        return response
    
    def get_history_items(self):
        """Return a list of previous query-response pairs for the history tab"""
        return [f"Q: {q} (Level: {c})" for q, c, _ in self.history]
    
    def show_history_item(self, selected_item):
        """Return the response for the selected history item"""
        if not selected_item:
            return "Select an item from history to view the explanation"
            
        # Find the matching history item
        for i, (q, c, r) in enumerate(self.history):
            if selected_item == f"Q: {q} (Level: {c})":
                return r
                
        return "History item not found"
            
    def list_available_concepts(self):
        """Return a string listing all available concepts."""
        concepts = self.knowledge_manager.get_all_concepts()
        concept_list = ""
        # Create a more organized display with categories (if available)
        # For now just show in a cleaner format
        for i, concept in enumerate(sorted(concepts)):
            concept_list += f"- {concept}"
            if (i+1) % 3 == 0:
                concept_list += "\n"
            else:
                concept_list += " &nbsp;&nbsp;&nbsp; "
        return concept_list
    
    def record_feedback(self, feedback_type, query, response):
        """Record user feedback about an explanation"""
        # In a real application, this would save the feedback to a database
        print(f"Feedback received: {feedback_type} for query: {query}")
        return "Thank you for your feedback!"
        
    def launch(self):
        """Launch the Gradio interface."""
        # Define a better theme with custom colors
        try:
            # Try using a simple theme that works across Gradio versions
            theme = gr.themes.Soft(
                primary_hue="teal",
                secondary_hue="blue",
            )
        except Exception:
            # Fallback to default theme if there's any issue
            theme = None
        
        with gr.Blocks(title="CSExplainer", theme=theme, css=self._get_custom_css()) as demo:
            # Header with logo
            with gr.Row(elem_classes="header-container"):
                with gr.Column(scale=1):
                    gr.Image(value="https://img.icons8.com/color/96/000000/source-code--v2.png", 
                            show_label=False, height=80, width=80)
                with gr.Column(scale=5):
                    gr.Markdown("""
                    # CSExplainer
                    ### Your interactive guide to understanding computer science concepts
                    """)
            
            # Main content
            with gr.Tabs() as tabs:
                with gr.TabItem("Ask Question", id=0):
                    with gr.Row():
                        with gr.Column(scale=1):
                            query_input = gr.Textbox(
                                label="Your Question",
                                placeholder="What is an algorithm? How does recursion work?",
                                lines=4,
                                elem_classes="query-input"
                            )
                            
                            complexity = gr.Radio(
                                ["beginner", "intermediate", "advanced"], 
                                label="Explanation Level",
                                value="intermediate",
                                elem_classes="complexity-selector"
                            )
                            
                            with gr.Row():
                                clear_btn = gr.Button("Clear")
                                submit_btn = gr.Button("Get Explanation", variant="primary")
                            
                            with gr.Accordion("Available Concepts", open=False):
                                concepts_output = gr.Markdown(self.list_available_concepts())
                        
                        with gr.Column(scale=2):
                            response_box = gr.Markdown(
                                label="Explanation",
                                value="Your explanation will appear here.",
                                elem_classes="explanation-box"
                            )
                            
                            # Feedback components
                            with gr.Row(visible=False) as feedback_row:
                                feedback_msg = gr.Markdown("Was this explanation helpful?")
                                # Add a hidden component to store feedback type
                                feedback_type = gr.Textbox(visible=False)
                                thumbs_up = gr.Button("👍 Yes", size="sm")
                                thumbs_down = gr.Button("👎 No", size="sm")
                            
                            feedback_response = gr.Markdown(visible=False)
                
                with gr.TabItem("History", id=1):
                    with gr.Row():
                        with gr.Column(scale=1):
                            # Create an empty dropdown that will be populated when items are added
                            history_list = gr.Dropdown(
                                label="History",
                                choices=[],
                                value=None,
                                allow_custom_value=True,  # Important to avoid errors with dynamic choices
                                elem_classes="history-dropdown"
                            )
                        with gr.Column(scale=2):
                            history_response = gr.Markdown("Select an item from history to view the explanation")
                
                with gr.TabItem("About", id=2):
                    gr.Markdown("""
                    # About CSExplainer
                    
                    CSExplainer is designed to help you understand complex computer science concepts.
                    Ask questions about algorithms, data structures, programming paradigms, and more.
                    
                    ## Features
                    - Explanations at different complexity levels
                    - Wide range of computer science concepts
                    - Interactive UI for easy learning
                    
                    ## How to use
                    1. Type your question in the input box
                    2. Select the explanation level you prefer
                    3. Click "Get Explanation" to see the answer
                    """)
            
            # Event handlers
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input, complexity],
                outputs=response_box,
                show_progress="minimal"
            ).then(
                fn=lambda: [gr.update(visible=True), gr.update(visible=False)],
                outputs=[feedback_row, feedback_response]
            ).then(
                fn=self.get_history_items,
                outputs=history_list,  # Directly pass the component instead of using a lambda
            )
            
            clear_btn.click(
                fn=lambda: ["", "Your explanation will appear here."],
                outputs=[query_input, response_box]
            )
            
            # Feedback handlers - fix the input handling
            def set_positive_feedback():
                return "positive"
                
            def set_negative_feedback():
                return "negative"
                
            thumbs_up.click(
                fn=set_positive_feedback,
                outputs=feedback_type
            ).then(
                fn=self.record_feedback,
                inputs=[feedback_type, query_input, response_box],
                outputs=feedback_response
            ).then(
                fn=lambda: [gr.update(visible=False), gr.update(visible=True)],
                outputs=[feedback_row, feedback_response]
            )
            
            thumbs_down.click(
                fn=set_negative_feedback,
                outputs=feedback_type
            ).then(
                fn=self.record_feedback,
                inputs=[feedback_type, query_input, response_box],
                outputs=feedback_response
            ).then(
                fn=lambda: [gr.update(visible=False), gr.update(visible=True)],
                outputs=[feedback_row, feedback_response]
            )
            
            # History interaction
            history_list.change(
                fn=self.show_history_item,
                inputs=history_list,
                outputs=history_response
            )
            
        demo.launch()
    
    def _get_custom_css(self):
        """Return custom CSS for the Gradio interface"""
        return """
            .gradio-container * {
                transition: all 0.3s ease-out;
            }
            .header-container {
                margin-bottom: 20px;
                background: linear-gradient(90deg, rgba(0,128,128,0.1) 0%, rgba(0,128,128,0) 100%);
                border-radius: 10px;
                padding: 10px;
            }
            .query-input textarea {
                font-size: 16px;
            }
            .explanation-box {
                min-height: 300px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 8px;
                border-left: 4px solid teal;
                color: #000000 !important; /* Ensuring text is black */
            }
            /* Make sure all text in the explanation area is black */
            .explanation-box * {
                color: #000000 !important;
            }
            .complexity-selector .wrap {
                display: flex;
                gap: 10px;
            }
        """

if __name__ == "__main__":
    app = GradioApp()
    app.launch()