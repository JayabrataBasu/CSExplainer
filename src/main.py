#!/usr/bin/env python3
"""
Visual Scene Understanding AI - Main Application
"""

import argparse
import os
import sys

from ml.detection import object_detector
from symbolic.reasoning import scene_reasoner
from nlg.generation import text_generator
from interface.cli import display_results

def parse_arguments():
    parser = argparse.ArgumentParser(description='Visual Scene Understanding AI')
    parser.add_argument('--image', type=str, help='Path to input image')
    parser.add_argument('--model', type=str, default='default', help='Object detection model to use')
    parser.add_argument('--output', type=str, help='Path to output results')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # 1. Detect objects in the image
    detected_objects = object_detector.detect(args.image, model=args.model)
    
    # 2. Apply symbolic reasoning to understand relationships
    scene_understanding = scene_reasoner.analyze(detected_objects)
    
    # 3. Generate natural language description
    description = text_generator.generate_description(scene_understanding)
    
    # 4. Display or save results
    display_results(args.image, detected_objects, scene_understanding, description, 
                   output_path=args.output, verbose=args.verbose)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
