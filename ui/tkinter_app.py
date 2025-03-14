import tkinter as tk
from tkinter import scrolledtext, ttk
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor
from src.response_formatter import ResponseFormatter

class CSExplainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSExplainer")
        self.root.geometry("800x600")
        
        # Initialize components
        self.knowledge_manager = KnowledgeManager()
        self.query_processor = QueryProcessor(self.knowledge_manager)
        self.response_formatter = ResponseFormatter(self.knowledge_manager)
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Query entry
        query_frame = ttk.Frame(main_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(query_frame, text="Ask about a CS concept:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.query_entry = ttk.Entry(query_frame, width=50)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.query_entry.bind("<Return>", self._on_submit)
        
        submit_button = ttk.Button(query_frame, text="Ask", command=self._on_submit)
        submit_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Response area
        response_frame = ttk.LabelFrame(main_frame, text="Explanation")
        response_frame.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD)
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.response_text.config(state=tk.DISABLED)
        
        # Complexity level selector
        complexity_frame = ttk.Frame(main_frame)
        complexity_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(complexity_frame, text="Explanation Level:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.complexity_var = tk.StringVar(value="intermediate")
        for level in ["beginner", "intermediate", "advanced"]:
            rb = ttk.Radiobutton(
                complexity_frame, 
                text=level.capitalize(), 
                variable=self.complexity_var, 
                value=level
            )
            rb.pack(side=tk.LEFT, padx=(0, 10))
            
        # Suggestions area
        suggestions_frame = ttk.LabelFrame(main_frame, text="Available Concepts")
        suggestions_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, height=4, wrap=tk.WORD)
        self.suggestions_text.pack(fill=tk.X, expand=False, padx=5, pady=5)
        self._populate_suggestions()
        
    def _populate_suggestions(self):
        """Populate the suggestions area with available concepts."""
        concepts = self.knowledge_manager.get_all_concepts()
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete(1.0, tk.END)
        self.suggestions_text.insert(tk.END, ", ".join(concepts))
        self.suggestions_text.config(state=tk.DISABLED)
        
    def _on_submit(self, event=None):
        """Handle query submission."""
        query = self.query_entry.get().strip()
        if not query:
            return
            
        # Process the query
        concept = self.query_processor.process_query(query)
        complexity = self.complexity_var.get()
        
        # Update response area
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        
        if concept:
            response = self.response_formatter.format_explanation(concept, complexity)
            self.response_text.insert(tk.END, response)
        else:
            self.response_text.insert(tk.END, "I couldn't find information about that concept. Please try another query.")
            
        self.response_text.config(state=tk.DISABLED)
