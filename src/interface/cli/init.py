"""
Command-line interface for the visual scene understanding system
"""

def display_results(image_path, detected_objects, scene_understanding, description, 
                   output_path=None, verbose=False):
    """
    Display or save the results of scene analysis
    
    Args:
        image_path: Path to the input image
        detected_objects: List of detected objects
        scene_understanding: Dictionary of scene relationships
        description: Natural language description of the scene
        output_path: Path to save results (optional)
        verbose: Whether to display detailed information
    """
    print("\n" + "="*50)
    print(f"ANALYSIS RESULTS FOR: {image_path}")
    print("="*50)
    
    print("\nDETECTED OBJECTS:")
    for i, obj in enumerate(detected_objects):
        print(f"  {i+1}. {obj['class']} (confidence: {obj['confidence']:.2f})")
    
    print("\nSCENE DESCRIPTION:")
    print(f"  {description}")
    
    if verbose:
        print("\nDETAILED RELATIONSHIPS:")
        for rel_type, relationships in scene_understanding['functional_relationships'].items():
            if relationships:
                print(f"  {rel_type.replace('_', ' ').title()}:")
                for rel in relationships:
                    print(f"    - {rel[0]} -> {rel[1]}")
    
    if output_path:
        print(f"\nResults saved to: {output_path}")
        # In a real implementation, this would save the results to a file
    
    print("\n" + "="*50 + "\n")
