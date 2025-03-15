import gradio as gr
import numpy as np
from src_ai.personalization import PersonalizationEngine
from src_ai.nlp_chatbot import NLPChatbot
from src_ai.ai_visualizations import AIDrivenVisualizer

personalizer = PersonalizationEngine()
chatbot_model = NLPChatbot()
visualizer_model = AIDrivenVisualizer()

def ai_response(query, interaction_time, questions_asked):
    user_features = [interaction_time := interaction_time, questions_asked := questions_asked]
    user_level = PersonalizationEngine().predict_user_level(user_features=user_features)

    ai_answer = NLPChatbot().generate_response(query)
    
    plot_data_points = np.random.rand(10)
    AIDrivenVisualizer().generate_plot(plot_data_points)

    return f"User Level: {user_level}\n\nAnswer: {ai_answer}"

iface = gr.Interface(
    fn=ai_response,
    inputs=["text", gr.Number(label="Interaction Time"), gr.Number(label="Questions Asked")],
    outputs="text",
    title="AI-Enhanced CSE Explainer"
)

iface.launch()
