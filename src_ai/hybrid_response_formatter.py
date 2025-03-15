from src.query_processor import QueryProcessor
from src_ai.nlp_chatbot import NLPChatbot

class HybridResponseFormatter:
    def __init__(self):
        self.rule_based_processor = QueryProcessor()
        self.ai_chatbot = NLPChatbot()

    def format_hybrid_response(self, query):
        rule_based_answer = self.rule_based_answer(query=query)
        ai_answer = self.ai_generated_answer(query=query)
        
        return f"{rule_based_answer}\n\nAdditional info: {ai_answer}"

    def rule_based_answer(self, query):
        processor = QueryProcessor()
        return processor.get_response(query)

    def ai_generated_answer(self, query):
        chatbot = NLPChatbot()
        return chatbot.generate_response(query)

# Example usage:
if __name__ == "__main__":
    formatter = HybridResponseFormatter()
    response = formatter.format_response("What is recursion?")
    print(response)
