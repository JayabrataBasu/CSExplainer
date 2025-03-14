# CSExplainer

A lightweight, rule-based system that provides explanations for fundamental Computer Science concepts.

## Features

- Structured knowledge base of CS concepts stored in JSON
- Simple text-processing mechanism to match user queries to relevant topics
- Multiple complexity levels for explanations (beginner, intermediate, advanced)
- Choice of user interfaces (Tkinter or Gradio)
- Runs efficiently on standard Windows laptops without requiring a GPU

## Installation

1. Clone this repository:
git clone https://github.com/yourusername/CSExplainer.git
cd CSExplainer

2. Install the required dependencies:
pip install -r requirements.txt



## Usage

Run the application with the default Tkinter interface:
python main.py

text

Or use the Gradio web interface:
python main.py --ui gradio

## Project Structure

```
CSExplainer/
│
├── data/
│   ├── cs_knowledge.json       # Main knowledge base
│   └── synonyms.json           # Optional: term synonyms for better matching
│
├── src/
│   ├── __init__.py
│   ├── knowledge_manager.py    # Handles loading and querying the knowledge base
│   ├── query_processor.py      # Processes user queries and matches to concepts
│   ├── response_formatter.py   # Formats explanations for display
│   └── utils.py                # Helper functions
│
├── ui/
│   ├── __init__.py
│   ├── tkinter_app.py          # Tkinter implementation
│   └── gradio_app.py           # Gradio implementation
│
├── tests/
│   ├── __init__.py
│   ├── test_knowledge_manager.py
│   ├── test_query_processor.py
│   └── test_response_formatter.py
│
├── main.py                     # Entry point for the application
├── requirements.txt            # Dependencies
└── README.md                   # Project documentation
```
