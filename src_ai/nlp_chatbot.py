from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os
import time

class NLPChatbot:
    def __init__(self, model_name="t5-small"):
        self.model_name = model_name
        self.is_model_loaded = False
        
        # Define fallback responses for when model loading fails
        self.fallback_responses = {
            "default": "I'm currently operating in basic mode. This is a computer science concept that involves systematic procedures and algorithms.",
            "algorithm": "An algorithm is a step-by-step procedure for solving a problem or accomplishing a task.",
            "data structure": "Data structures are ways of organizing and storing data to perform operations efficiently.",
            "programming": "Programming is the process of creating a set of instructions that tell a computer how to perform a task.",
            "recursion": "Recursion is a technique where a function calls itself to solve smaller instances of the same problem."
        }
        
        try:
            print(f"Loading NLP model: {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.is_model_loaded = True
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Running in fallback mode with rule-based responses.")

    def generate_response(self, query, max_length=100):
        """
        Generate a response to the user query using the NLP model
        
        Args:
            query: String containing the user's question
            max_length: Maximum length of the generated response
            
        Returns:
            String containing the generated response
        """
        # Clean and preprocess the query
        cleaned_query = self._preprocess_query(query)
        
        # Check if we're in fallback mode
        if not self.is_model_loaded:
            return self._get_fallback_response(cleaned_query)
        
        try:
            # Prepare input
            model_input = f"explain computer science concept: {cleaned_query}"
            inputs = self.tokenizer(model_input, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate response
            start_time = time.time()
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True
            )
            generation_time = time.time() - start_time
            
            # Decode output
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # If response is too short or empty, fall back
            if len(response) < 20:
                return self._get_fallback_response(cleaned_query)
                
            print(f"Response generated in {generation_time:.2f} seconds")
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(cleaned_query)
    
    def _preprocess_query(self, query):
        """Clean and preprocess the query"""
        return query.strip().lower()
    
    def _get_fallback_response(self, query):
        """Get fallback response based on query keywords"""
        for keyword, response in self.fallback_responses.items():
            if keyword in query:
                return response
        return self.fallback_responses["default"]

# Example usage
if __name__ == "__main__":
    chatbot = NLPChatbot()
    test_queries = [
        "Explain binary search.",
        "What is recursion?",
        "How does a hash table work?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = chatbot.generate_response(query)
        print(f"Response: {response}")
