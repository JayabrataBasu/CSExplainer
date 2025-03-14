"""
Natural language generation for scene descriptions
"""

class SceneDescriptionGenerator:
    """Generates natural language descriptions of scenes based on symbolic analysis"""
    
    def __init__(self):
        self.templates = {
            'person_umbrella': [
                "There is a person using an umbrella.",
                "A person is holding an umbrella, possibly to shield from rain or sun.",
                "The image shows someone with an umbrella."
            ],
            'person': [
                "There is a person in the scene.",
                "A person can be seen in the image.",
                "The image contains a human figure."
            ],
            'spatial': {
                'above': "{obj1} is positioned above {obj2}.",
                'below': "{obj1} is located below {obj2}.",
                'left_of': "{obj1} is to the left of {obj2}.",
                'right_of': "{obj1} is to the right of {obj2}."
            },
            'functional': {
                'is_holding': "{obj1} is holding {obj2}.",
                'is_using': "{obj1} is using {obj2}."
            }
        }
    
    def _get_class_name(self, obj_id, objects_list):
        """Get the class name for an object ID"""
        # Extract the index from obj_id (e.g., "obj_0" -> 0)
        try:
            index = int(obj_id.split('_')[1])
            return objects_list[index]['class']
        except (IndexError, ValueError):
            return "unknown object"
    
    def _describe_objects(self, objects):
        """Generate descriptions of individual objects"""
        descriptions = []
        for obj in objects:
            if obj['class'] == 'person':
                descriptions.append(self.templates['person'][0])
        return descriptions
    
    def _describe_relationships(self, scene_data):
        """Generate descriptions of relationships between objects"""
        descriptions = []
        objects_list = scene_data['objects']
        
        # Check for specific object combinations
        has_person = any(obj['class'] == 'person' for obj in objects_list)
        has_umbrella = any(obj['class'] == 'umbrella' for obj in objects_list)
        
        if has_person and has_umbrella:
            descriptions.append(self.templates['person_umbrella'][0])
        
        # Describe functional relationships
        for rel_type, relationships in scene_data['functional_relationships'].items():
            if relationships:
                for rel in relationships:
                    obj1 = self._get_class_name(rel[0], objects_list)
                    obj2 = self._get_class_name(rel[1], objects_list)
                    template = self.templates['functional'].get(rel_type)
                    if template:
                        descriptions.append(template.format(obj1=obj1, obj2=obj2))
        
        return descriptions
    
    def generate(self, scene_data):
        """
        Generate a natural language description of the scene
        
        Args:
            scene_data: Dictionary containing objects and their relationships
            
        Returns:
            String containing the scene description
        """
        descriptions = []
        
        # Describe individual objects
        descriptions.extend(self._describe_objects(scene_data['objects']))
        
        # Describe relationships
        descriptions.extend(self._describe_relationships(scene_data))
        
        # Combine descriptions into a paragraph
        return " ".join(descriptions)

def generate_description(scene_data):
    """
    Generate a natural language description of the scene
    
    Args:
        scene_data: Dictionary containing objects and their relationships
        
    Returns:
        String containing the scene description
    """
    generator = SceneDescriptionGenerator()
    return generator.generate(scene_data)
