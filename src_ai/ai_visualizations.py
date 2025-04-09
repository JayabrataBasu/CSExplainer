import matplotlib.pyplot as plt
import numpy as np
import os
import io
import base64
from datetime import datetime

class AIDrivenVisualizer:
    def __init__(self):
        self.visualization_types = {
            'progress': self._create_progress_chart,
            'comparison': self._create_comparison_chart,
            'concept_map': self._create_concept_map,
            'difficulty': self._create_difficulty_chart
        }

    def generate_plot(self, data_points, chart_type='progress', title=None, 
                     labels=None, save_path=None, show_plot=False, return_base64=False):
        """
        Generate visualization based on the specified chart type

        Args:
            data_points: List or NumPy array of data points
            chart_type: Type of chart ('progress', 'comparison', 'concept_map', 'difficulty')
            title: Optional title for the chart
            labels: Optional list of labels for the data points
            save_path: If provided, save the chart to this path
            show_plot: If True, display the plot using plt.show()
            return_base64: If True, return a base64-encoded image for web display
            
        Returns:
            Base64-encoded image if return_base64 is True, otherwise None
        """
        # Convert to numpy array if needed
        data = np.asarray(data_points)
        
        plt.figure(figsize=(8, 5))
        plt.style.use('ggplot')  # Use a nicer style
        
        # Generate the plot based on chart type
        if chart_type in self.visualization_types:
            self.visualization_types[chart_type](data, title, labels)
        else:
            # Default to progress chart if type not recognized
            self._create_progress_chart(data, title, labels)
        
        plt.tight_layout()
        
        # Save to file if path provided
        if save_path:
            try:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Chart saved to {save_path}")
            except Exception as e:
                print(f"Error saving chart: {e}")
        
        # Return base64-encoded image for web display
        if return_base64:
            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            plt.close()
            return base64.b64encode(img.getvalue()).decode()
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return None

    def _create_progress_chart(self, data, title=None, labels=None):
        plt.plot(data, marker='o', color='#1f77b4', linewidth=2)
        plt.fill_between(range(len(data)), data, alpha=0.2, color='#1f77b4')
        plt.title(title or "Learning Progress", fontsize=14)
        plt.xlabel("Concepts", fontsize=12)
        plt.ylabel("Understanding Level", fontsize=12)
        plt.ylim(0, max(data) * 1.2)  # Add some headroom
        plt.grid(True, alpha=0.3)
        
        # Add labels if provided
        if labels and len(labels) == len(data):
            plt.xticks(range(len(data)), labels, rotation=45, ha='right')
    
    def _create_comparison_chart(self, data, title=None, labels=None):
        # For comparison, we expect data to be a 2D array or a list of lists
        if data.ndim == 1:
            # If 1D, split it into two groups for comparison
            mid = len(data) // 2
            data = [data[:mid], data[mid:]]
        
        bar_width = 0.35
        x = np.arange(len(data[0]))
        
        plt.bar(x - bar_width/2, data[0], bar_width, label='Current', color='#2ca02c')
        plt.bar(x + bar_width/2, data[1], bar_width, label='Previous', color='#9467bd')
        
        plt.title(title or "Performance Comparison", fontsize=14)
        plt.xlabel("Metrics", fontsize=12)
        plt.ylabel("Value", fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.legend()
        
        if labels and len(labels) == len(data[0]):
            plt.xticks(x, labels)

    def _create_concept_map(self, data, title=None, labels=None):
        # Create a heatmap/concept map
        plt.imshow(data.reshape((int(np.sqrt(len(data))), -1)), 
                 cmap='viridis', interpolation='nearest')
        plt.colorbar(label="Relationship Strength")
        plt.title(title or "Concept Relationship Map", fontsize=14)
        plt.grid(False)
        
        if labels:
            num = int(np.sqrt(len(data)))
            if len(labels) >= num:
                plt.xticks(range(num), labels[:num], rotation=90)
                plt.yticks(range(num), labels[:num])

    def _create_difficulty_chart(self, data, title=None, labels=None):
        difficulties = data
        
        # Create default labels if none provided
        if not labels or len(labels) != len(difficulties):
            labels = [f"Concept {i+1}" for i in range(len(difficulties))]
            
        # Sort by difficulty for better visualization
        sorted_indices = np.argsort(difficulties)
        sorted_difficulties = difficulties[sorted_indices]
        sorted_labels = [labels[i] for i in sorted_indices]
        
        # Create horizontal bar chart
        plt.barh(range(len(sorted_difficulties)), sorted_difficulties, 
               color=plt.cm.RdYlGn_r(sorted_difficulties/max(sorted_difficulties)))
        plt.yticks(range(len(sorted_difficulties)), sorted_labels)
        plt.title(title or "Concept Difficulty Levels", fontsize=14)
        plt.xlabel("Difficulty", fontsize=12)
        plt.grid(True, alpha=0.3, axis='x')

    def generate_learning_path(self, concepts, difficulties, knowledge_level=0.5, max_concepts=15, 
                             show_connections=True, highlight_concept=None):
        """
        Generate a personalized learning path based on concept difficulties
        and user knowledge level
        
        Args:
            concepts: List of concept names
            difficulties: List of difficulty ratings for each concept
            knowledge_level: Float between 0-1 representing user knowledge
            max_concepts: Maximum number of concepts to display
            show_connections: Whether to draw connections between related concepts
            highlight_concept: Specific concept to highlight in the visualization
            
        Returns:
            Base64-encoded visualization of the suggested learning path
        """
        # Ensure we don't exceed the number of available concepts
        if len(concepts) > max_concepts:
            concepts = concepts[:max_concepts]
            difficulties = difficulties[:max_concepts]
            
        # Adjust difficulties based on knowledge level
        adjusted_difficulties = np.array(difficulties) * (1 - knowledge_level)
        
        # Sort concepts by adjusted difficulty
        sorted_indices = np.argsort(adjusted_difficulties)
        sorted_concepts = [concepts[i] for i in sorted_indices]
        sorted_difficulties = adjusted_difficulties[sorted_indices]
        
        # Create figure with sufficient height for all concepts
        height = max(6, len(sorted_concepts) * 0.4)
        plt.figure(figsize=(10, height))
        
        # Create color map - use different colors for different difficulty ranges
        colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_difficulties)))
        
        # Highlight specific concept if requested
        if highlight_concept:
            for i, concept in enumerate(sorted_concepts):
                if highlight_concept.lower() in concept.lower():
                    colors[i] = [0.8, 0.2, 0.2, 1.0]  # Bright red
                    break
        
        # Create horizontal bars
        bars = plt.barh(range(len(sorted_difficulties)), sorted_difficulties, 
                color=colors, height=0.6)
        
        # Add value labels to the right of each bar
        for i, bar in enumerate(bars):
            width = bar.get_width()
            difficulty_level = ""
            if sorted_difficulties[i] < 0.3:
                difficulty_level = "Easy"
            elif sorted_difficulties[i] < 0.6:
                difficulty_level = "Moderate"
            else:
                difficulty_level = "Advanced"
                
            plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                    difficulty_level,
                    va='center', size=9)
        
        # Add step numbers to the left of concept names
        for i in range(len(sorted_concepts)):
            plt.text(-0.15, i, f"{i+1}.", 
                    ha='right', va='center', 
                    fontweight='bold', fontsize=10)
        
        # Draw connections between concepts if requested
        if show_connections and len(sorted_concepts) > 1:
            for i in range(len(sorted_concepts)-1):
                # Draw a subtle arrow from one concept to the next
                plt.annotate("", 
                            xy=(sorted_difficulties[i+1]*0.5, i+1), 
                            xytext=(sorted_difficulties[i]*0.5, i),
                            arrowprops=dict(arrowstyle="->", color="gray", 
                                            alpha=0.6, connectionstyle="arc3,rad=0.2"))
        
        # Set y-axis ticks with concept names
        plt.yticks(range(len(sorted_difficulties)), sorted_concepts)
        
        # Set chart title and labels
        level_text = "Beginner"
        if knowledge_level < 0.3:
            level_text = "Beginner"
        elif knowledge_level < 0.7:
            level_text = "Intermediate"
        else:
            level_text = "Advanced"
            
        plt.title(f"Personalized Learning Path ({level_text} Level)", fontsize=14)
        plt.xlabel("Adjusted Difficulty", fontsize=12)
        plt.grid(True, alpha=0.3, axis='x')
        
        # Add a legend explaining the color scheme
        plt.text(1.02, 0.02, "Color indicates concept complexity", 
                transform=plt.gca().transAxes, rotation=90, 
                va='bottom', fontsize=9, alpha=0.7)
                
        # Add a note about what the chart shows
        plt.figtext(0.5, 0.01, 
                   f"This path is optimized for your knowledge level ({knowledge_level:.1f}/1.0). Start from the top and work your way down.",
                   ha='center', fontsize=9, style='italic')
                   
        plt.tight_layout()
        
        # Convert to base64 for web display
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        return base64.b64encode(img.getvalue()).decode()

# Example usage:
if __name__ == "__main__":
    visualizer = AIDrivenVisualizer()
    
    # Example 1: Progress chart
    data_points = np.random.rand(10) * 10
    visualizer.generate_plot(data_points, chart_type='progress', show_plot=True)
    
    # Example 2: Difficulty chart with labels
    concepts = ["Algorithms", "Data Structures", "Recursion", "OOP", "Design Patterns"]
    difficulties = np.array([0.7, 0.5, 0.8, 0.4, 0.9])
    visualizer.generate_plot(difficulties, chart_type='difficulty', 
                            labels=concepts, show_plot=True)
    
    # Example 3: Save a chart to file
    today = datetime.now().strftime("%Y%m%d")
    visualizer.generate_plot(data_points, save_path=f"data/charts/progress_{today}.png")
    
    # Example 4: Learning path
    learning_path = visualizer.generate_learning_path(concepts, difficulties, 0.6)
    print("Learning path visualization generated as base64 string")
