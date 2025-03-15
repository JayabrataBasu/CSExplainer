import gradio as gr
import numpy as np
import time
import os
import base64
from PIL import Image
import io
from datetime import datetime

from src.knowledge_manager import KnowledgeManager
from src_ai.personalization import PersonalizationEngine
from src_ai.nlp_chatbot import NLPChatbot
from src_ai.ai_visualizations import AIDrivenVisualizer
from src_ai.hybrid_response_formatter import HybridResponseFormatter
from src_ai.reinforcement_learning import LearningPathRL, LearningEnvironment

class AIEnhancedGradioApp:
    def __init__(self):
        """Initialize the AI-enhanced CSExplainer Gradio interface"""
        # Core components
        self.knowledge_manager = KnowledgeManager()
        
        # AI components
        self.personalizer = PersonalizationEngine()
        self.chatbot = NLPChatbot()
        self.visualizer = AIDrivenVisualizer()
        self.response_formatter = HybridResponseFormatter(self.knowledge_manager)
        
        # Session state
        self.session = {
            "interaction_time": 0,
            "questions_asked": 0,
            "user_level": "intermediate",
            "history": [],
            "concepts_explored": {},
            "start_time": time.time()
        }
        
        # Initialize RL components
        try:
            env = LearningEnvironment(concepts=self.knowledge_manager.get_all_concepts())
            self.rl_agent = LearningPathRL(env)
            # Pre-train a bit to have meaningful suggestions
            self.rl_agent.train(episodes=10)
        except Exception as e:
            print(f"Error initializing RL agent: {e}")
            self.rl_agent = None
            
    def process_query(self, query, complexity_level, use_ai, interaction_time, questions_asked):
        """
        Process a user query and return a formatted response
        
        Args:
            query: User's question text
            complexity_level: Desired explanation level
            use_ai: Whether to use AI enhancements
            interaction_time: Time user has spent interacting (minutes)
            questions_asked: Number of questions already asked
            
        Returns:
            Tuple of (response text, visualization image, follow-up questions)
        """
        if not query.strip():
            return "Please enter a question about a computer science concept.", None, []
        
        # Update session
        self.session["interaction_time"] = float(interaction_time)
        self.session["questions_asked"] = int(questions_asked) + 1
        
        # Determine user level with personalization engine
        user_features = [self.session["interaction_time"], self.session["questions_asked"]]
        user_level = self.personalizer.predict_user_level(user_features)
        self.session["user_level"] = user_level
        
        # Override complexity level if user specified
        if complexity_level and complexity_level != "auto":
            explanation_level = complexity_level
        else:
            explanation_level = user_level
        
        # Track concepts explored
        start_time = time.time()
        
        # Generate response
        if use_ai:
            response = self.response_formatter.format_hybrid_response(
                query, 
                complexity_level=explanation_level,
                ai_enhancement=True
            )
        else:
            # Use rule-based only
            response = self.response_formatter.format_hybrid_response(
                query, 
                complexity_level=explanation_level,
                ai_enhancement=False
            )
        
        # Measure processing time
        processing_time = time.time() - start_time
        print(f"Response generated in {processing_time:.2} seconds")
        
        # Generate visualization based on query and response
        viz_image = self._generate_visualization(query, response, user_level)
        
        # Generate suggested follow-up questions
        follow_up_questions = self.response_formatter.suggest_related_queries(query)
        
        # Record this interaction
        self.personalizer.record_interaction(
            user_features=[interaction_time, questions_asked],
            predicted_level=user_level
        )
        
        # Add to history
        self.session["history"].append({
            "query": query,
            "response": response,
            "level": explanation_level,
            "timestamp": time.time()
        })
        
        return response, viz_image, follow_up_questions
    
    def _generate_visualization(self, query, response, user_level):
        """Generate a relevant visualization based on the query and response"""
        try:
            # Track concepts and their exploration counts
            concept_match = self.response_formatter.query_processor.process_query(query)
            
            if concept_match:
                if concept_match in self.session["concepts_explored"]:
                    self.session["concepts_explored"][concept_match] += 1
                else:
                    self.session["concepts_explored"][concept_match] = 1
            
            # Determine visualization type based on query content
            if "compare" in query.lower() or "versus" in query.lower() or "vs" in query.lower():
                chart_type = "comparison"
            elif "difficulty" in query.lower() or "hard" in query.lower() or "easy" in query.lower():
                chart_type = "difficulty"
            elif "related" in query.lower() or "connection" in query.lower():
                chart_type = "concept_map"
            else:
                chart_type = "progress"
            
            # Generate data for visualization
            if chart_type == "progress":
                # Show progress of explored concepts
                concepts = list(self.session["concepts_explored"].keys())
                values = list(self.session["concepts_explored"].values())
                if len(concepts) < 2:  # Not enough data, show sample data
                    concepts = self.knowledge_manager.get_all_concepts()[:10]
                    values = np.random.rand(len(concepts)) * 10
                
                # Create visualization
                viz_b64 = self.visualizer.generate_plot(
                    data_points=values,
                    chart_type="progress",
                    labels=concepts,
                    title="Concept Exploration Progress",
                    return_base64=True
                )
                
            elif chart_type == "difficulty":
                # Show concept difficulties adjusted to user level
                concepts = self.knowledge_manager.get_all_concepts()[:15]
                # Generate random difficulties weighted by user level
                level_factor = {"beginner": 0.8, "intermediate": 0.5, "advanced": 0.2}.get(user_level, 0.5)
                difficulties = np.random.rand(len(concepts)) * level_factor + (1 - level_factor) * 0.5
                
                # Create visualization
                viz_b64 = self.visualizer.generate_plot(
                    data_points=difficulties,
                    chart_type="difficulty",
                    labels=concepts,
                    title=f"Concept Difficulty ({user_level.capitalize()} Level)",
                    return_base64=True
                )
                
            elif chart_type == "concept_map":
                # Create a relationship map for concepts
                related_concepts = []
                # Get primary concept
                concept = self.response_formatter.query_processor.process_query(query)
                if concept:
                    # Find related concepts
                    related_concepts = self.knowledge_manager.get_related_concepts(concept)
                    related_concepts = [concept] + related_concepts
                
                if len(related_concepts) < 3:
                    # Not enough relationships, use sample data
                    related_concepts = self.knowledge_manager.get_all_concepts()[:9]
                
                # Create map data (NxN matrix)
                n = min(len(related_concepts), 9)  # Limit to 9 for readability
                concepts = related_concepts[:n]
                map_data = np.random.rand(n*n) * 0.8 + 0.2  # Relationship strengths
                
                # Create visualization
                viz_b64 = self.visualizer.generate_plot(
                    data_points=map_data,
                    chart_type="concept_map",
                    labels=concepts,
                    title="Concept Relationships",
                    return_base64=True
                )
                
            else:  # comparison chart
                # Compare difficulty across different aspects
                aspects = ["Learning Time", "Complexity", "Prerequisites", "Applications"]
                # Generate two sets of data
                data_1 = np.random.rand(len(aspects)) * 0.7 + 0.3
                data_2 = np.random.rand(len(aspects)) * 0.7 + 0.3
                comparison_data = np.vstack((data_1, data_2))
                
                # Create visualization
                viz_b64 = self.visualizer.generate_plot(
                    data_points=comparison_data,
                    chart_type="comparison",
                    labels=aspects,
                    title="Concept Comparison",
                    return_base64=True
                )
            
            # Convert base64 string to image
            if viz_b64:
                img_data = base64.b64decode(viz_b64)
                img = Image.open(io.BytesIO(img_data))
                return img
                
        except Exception as e:
            print(f"Error generating visualization: {e}")
        
        return None
    
    def get_learning_path(self, starting_concept="algorithm", knowledge_level=0.5):
        """
        Generate a suggested learning path using reinforcement learning
        
        Args:
            starting_concept: Concept to start from
            knowledge_level: User's knowledge level (0-1)
            
        Returns:
            Image showing the learning path
        """
        try:
            if self.rl_agent is None:
                # Fall back to simple path
                return None
                
            # Find the index of the starting concept
            start_idx = 0
            concepts = self.knowledge_manager.get_all_concepts()
            for idx, concept in enumerate(concepts):
                if starting_concept.lower() in concept.lower():
                    start_idx = idx
                    break
            
            # Get optimal path
            path_indices = self.rl_agent.get_optimal_path(start_idx)
            path_concepts = [self.rl_agent.env.concepts[i] for i in path_indices]
            
            # Get difficulties
            difficulties = [self.rl_agent.env.difficulty[i] for i in path_indices]
            
            # Generate learning path visualization
            knowledge_level = float(knowledge_level)
            viz_b64 = self.visualizer.generate_learning_path(
                path_concepts[:10],  # Limit to 10 concepts
                difficulties[:10],
                knowledge_level
            )
            
            # Convert to image
            if viz_b64:
                img_data = base64.b64decode(viz_b64)
                img = Image.open(io.BytesIO(img_data))
                return img
            
        except Exception as e:
            print(f"Error generating learning path: {e}")
            
        return None
    
    def update_metrics(self, interaction_time, questions_asked):
        """Update interaction metrics"""
        # Validate and update values
        try:
            interaction_time = float(interaction_time)
            questions_asked = int(questions_asked)
            
            # Update session
            self.session["interaction_time"] = interaction_time
            self.session["questions_asked"] = questions_asked
            
            # Predict user level
            user_level = self.personalizer.predict_user_level([interaction_time, questions_asked])
            
            return f"User level: {user_level.capitalize()}"
        except:
            return "Invalid input. Please enter numeric values."
    
    def get_concepts_list(self):
        """Get a list of all concepts in the knowledge base"""
        concepts = self.knowledge_manager.get_all_concepts()
        return sorted(concepts)
    
    def launch(self):
        """Launch the Gradio interface"""
        # Define a modern theme
        theme = gr.themes.Soft(
            primary_hue="teal",
            secondary_hue="blue",
        )
        
        # Create the interface
        with gr.Blocks(title="AI-Enhanced CSExplainer", theme=theme, css=self._get_custom_css()) as demo:
            # Header section
            with gr.Row(elem_classes="header-container"):
                with gr.Column(scale=1):
                    gr.Image(value="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", 
                            show_label=False, height=80, width=80)
                with gr.Column(scale=5):
                    gr.Markdown("""
                    # AI-Enhanced CSExplainer
                    ### Interactive computer science learning with AI assistance
                    """)
            
            # Main tabs
            with gr.Tabs() as tabs:
                # Main explanation interface tab
                with gr.TabItem("Ask & Learn", id=0):
                    with gr.Row():
                        # Left section: Input controls
                        with gr.Column(scale=2):
                            query_input = gr.Textbox(
                                label="Your Question",
                                placeholder="What is recursion? How do hash tables work?",
                                lines=4,
                                elem_classes="query-input"
                            )
                            
                            with gr.Row():
                                with gr.Column(scale=1):
                                    complexity = gr.Radio(
                                        ["beginner", "intermediate", "advanced", "auto"], 
                                        label="Explanation Complexity",
                                        value="auto",
                                        elem_classes="complexity-selector"
                                    )
                                    
                                    use_ai_enhance = gr.Checkbox(
                                        label="Use AI Enhancement",
                                        value=True
                                    )
                                    
                                with gr.Column(scale=1):
                                    interaction_time = gr.Number(
                                        label="Interaction Time (minutes)",
                                        value=5.0,
                                        step=0.5
                                    )
                                    
                                    questions_asked = gr.Number(
                                        label="Questions Asked",
                                        value=0,
                                        step=1
                                    )
                                    
                                    user_level_indicator = gr.Textbox(
                                        label="Detected User Level",
                                        value="User level: Intermediate",
                                        interactive=False
                                    )
                                    
                                    update_metrics_btn = gr.Button("Update Metrics")
                            
                            with gr.Row():
                                clear_btn = gr.Button("Clear")
                                submit_btn = gr.Button("Get Explanation", variant="primary")
                            
                        # Right section: Explanation output
                        with gr.Column(scale=3):
                            response_md = gr.Markdown(
                                label="Explanation",
                                value="Your explanation will appear here.",
                                elem_classes="explanation-box"
                            )
                            
                            # Visualization section
                            viz_output = gr.Image(
                                label="Concept Visualization", 
                                type="pil",
                                height=400
                            )
                            
                            # Follow-up questions
                            with gr.Accordion("Suggested follow-up questions", open=False):
                                suggested_questions = gr.Dataset(
                                    components=["text"],
                                    label="Click on a question to ask it",
                                    samples=[],
                                    elem_classes="suggested-questions"
                                )
                
                # Learning path recommendation tab
                with gr.TabItem("Learning Path", id=1):
                    with gr.Row():
                        with gr.Column(scale=1):
                            starting_concept = gr.Dropdown(
                                label="Starting Concept",
                                choices=self.get_concepts_list(),
                                value="algorithm",
                                elem_classes="concept-selector"
                            )
                            
                            knowledge_slider = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.5,
                                step=0.1,
                                label="Your Knowledge Level",
                                info="0 = Beginner, 1 = Expert"
                            )
                            
                            generate_path_btn = gr.Button(
                                "Generate Learning Path",
                                variant="primary"
                            )
                            
                        with gr.Column(scale=2):
                            path_visualization = gr.Image(
                                label="Suggested Learning Path",
                                type="pil",
                                elem_classes="learning-path-viz"
                            )
                            
                            path_explanation = gr.Markdown(
                                """
                                The learning path shows recommended concepts to learn in order, 
                                with adjusted difficulty levels based on your knowledge.
                                
                                Start with the concepts at the top (easier) and progress downward.
                                """
                            )
                
                # About tab
                with gr.TabItem("About AI Features", id=2):
                    gr.Markdown(
                        """
                        # AI-Enhanced Features in CSExplainer
                        
                        This version of CSExplainer incorporates several AI technologies to improve your learning experience:
                        
                        ### 1. Personalized Learning
                        The system adapts to your knowledge level by tracking your interactions and adjusts explanations accordingly.
                        
                        ### 2. AI-Enhanced Explanations
                        Combines rule-based knowledge with natural language processing to provide more comprehensive explanations.
                        
                        ### 3. Interactive Visualizations
                        AI-generated visualizations help you understand concepts and their relationships.
                        
                        ### 4. Learning Path Recommendations
                        Uses reinforcement learning to suggest an optimal path through computer science concepts based on your current knowledge.
                        
                        ### 5. Related Questions
                        Intelligently suggests follow-up questions to deepen your understanding.
                        """
                    )
            
            # Event handlers
            def ask_suggested_question(evt: gr.SelectData):
                selected_question = evt.value[0] 
                return selected_question
            
            # Event handler for the submit button
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input, complexity, use_ai_enhance, interaction_time, questions_asked],
                outputs=[response_md, viz_output, suggested_questions]
            )
            
            # Clear button
            clear_btn.click(
                fn=lambda: ["", "Your explanation will appear here.", None, []],
                outputs=[query_input, response_md, viz_output, suggested_questions]
            )
            
            # Update metrics button
            update_metrics_btn.click(
                fn=self.update_metrics,
                inputs=[interaction_time, questions_asked],
                outputs=[user_level_indicator]
            )
            
            # Learning path button
            generate_path_btn.click(
                fn=self.get_learning_path,
                inputs=[starting_concept, knowledge_slider],
                outputs=[path_visualization]
            )
            
            # Handle clicking on suggested questions
            suggested_questions.select(
                ask_suggested_question,
                None,
                query_input
            ).then(
                fn=self.process_query,
                inputs=[query_input, complexity, use_ai_enhance, interaction_time, questions_asked],
                outputs=[response_md, viz_output, suggested_questions]
            )
            
        # Start the interface
        demo.launch()
    
    def _get_custom_css(self):
        """Return custom CSS for the Gradio interface"""
        return """
            .gradio-container * {
                transition: all 0.3s ease-out;
            }
            .header-container {
                margin-bottom: 20px;
                background: linear-gradient(135deg, rgba(0,128,128,0.2) 0%, rgba(0,128,128,0) 100%);
                border-radius: 10px;
                padding: 10px;
                border-left: 4px solid teal;
            }
            .query-input textarea {
                font-size: 16px;
            }
            .explanation-box {
                min-height: 400px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 8px;
                border-left: 4px solid teal;
                color: #000000 !important; /* Ensuring text is black */
                overflow-y: auto;
            }
            /* Make sure all text in the explanation area is black */
            .explanation-box * {
                color: #000000 !important;
            }
            .complexity-selector .wrap {
                display: flex;
                gap: 10px;
            }
            .suggested-questions {
                cursor: pointer;
            }
            .suggested-questions:hover {
                background-color: rgba(0, 128, 128, 0.1);
            }
            .learning-path-viz {
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """

# Launch the app if run directly
if __name__ == "__main__":
    app = AIEnhancedGradioApp()
    app.launch()
