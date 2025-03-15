from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class NLPChatbot:
    def __init__(self, model_name="t5-small"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def generate_response(self, query):
        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
if __name__ == "__main__":
    chatbot = NLPChatbot()
    response = chatbot.generate_response("Explain binary search.")
    print(response)
