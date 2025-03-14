import tkinter as tk
from tkinter import scrolledtext, ttk, font
from src.knowledge_manager import KnowledgeManager
from src.query_processor import QueryProcessor
from src.response_formatter import ResponseFormatter

class CSExplainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSExplainer")
        self.root.geometry("900x700")
        
        # Configure styles
        self._configure_styles()
        
        # Initialize components
        self.knowledge_manager = KnowledgeManager()
        self.query_processor = QueryProcessor(self.knowledge_manager)
        self.response_formatter = ResponseFormatter(self.knowledge_manager)
        
        self._setup_ui()
        
    def _configure_styles(self):
        """Configure custom styles for the application"""
        # Get default font family
        default_font = font.nametofont("TkDefaultFont")
        self.default_family = default_font.cget("family")
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5", font=(self.default_family, 10))
        style.configure("TButton", font=(self.default_family, 10))
        style.configure("TRadiobutton", background="#f5f5f5", font=(self.default_family, 10))
        style.configure("Title.TLabel", font=(self.default_family, 16, "bold"))
        style.configure("Subtitle.TLabel", font=(self.default_family, 12, "bold"))
        style.configure("TLabelframe", background="#f5f5f5")
        style.configure("TLabelframe.Label", background="#f5f5f5", font=(self.default_family, 11, "bold"))
        
    def _setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="CSExplainer", style="Title.TLabel")
        title_label.pack(pady=(0, 5))
        subtitle_label = ttk.Label(main_frame, text="Your guide to understanding computer science concepts", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 20))
        
        # Split into two columns
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column: Query and controls
        left_frame = ttk.Frame(content_frame, padding="0 0 10 0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Query entry
        query_frame = ttk.LabelFrame(left_frame, text="Ask a Question")
        query_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.query_entry = ttk.Entry(query_frame, width=50, font=(self.default_family, 10))
        self.query_entry.pack(fill=tk.X, expand=True, padx=10, pady=10)
        self.query_entry.bind("<Return>", self._on_submit)
        
        # Button frame
        button_frame = ttk.Frame(query_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self._clear_query)
        clear_button.pack(side=tk.LEFT)
        
        submit_button = ttk.Button(button_frame, text="Get Explanation", command=self._on_submit)
        submit_button.pack(side=tk.RIGHT)
        
        # Complexity level selector
        complexity_frame = ttk.LabelFrame(left_frame, text="Explanation Level")
        complexity_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.complexity_var = tk.StringVar(value="intermediate")
        
        complexity_inner_frame = ttk.Frame(complexity_frame)
        complexity_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for level in ["beginner", "intermediate", "advanced"]:
            rb = ttk.Radiobutton(
                complexity_inner_frame, 
                text=level.capitalize(), 
                variable=self.complexity_var, 
                value=level
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # Suggestions area
        suggestions_frame = ttk.LabelFrame(left_frame, text="Available Concepts")
        suggestions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.suggestions_text = scrolledtext.ScrolledText(
            suggestions_frame, 
            height=8, 
            wrap=tk.WORD,
            font=(self.default_family, 10)
        )
        self.suggestions_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right column: Response area
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        response_frame = ttk.LabelFrame(right_frame, text="Explanation")
        response_frame.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame, 
            wrap=tk.WORD,
            font=(self.default_family, 10)
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.response_text.config(state=tk.DISABLED)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        footer_label = ttk.Label(
            footer_frame, 
            text="CSExplainer - Helping you understand computer science concepts",
            anchor=tk.CENTER
        )
        footer_label.pack(fill=tk.X)
        
        # Populate suggestions
        self._populate_suggestions()
        
    def _clear_query(self):
        """Clear the query entry field"""
        self.query_entry.delete(0, tk.END)
        
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