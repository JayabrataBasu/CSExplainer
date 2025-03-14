import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="CSExplainer - A rule-based computer science concept explainer")
    parser.add_argument("--ui", choices=["tkinter", "gradio"], default="tkinter", help="UI framework to use")
    args = parser.parse_args()
    
    if args.ui == "tkinter":
        import tkinter as tk
        from ui.tkinter_app import CSExplainerApp
        
        root = tk.Tk()
        app = CSExplainerApp(root)
        root.mainloop()
    else:  # gradio
        from ui.gradio_app import GradioApp
        
        app = GradioApp()
        app.launch()

if __name__ == "__main__":
    main()
