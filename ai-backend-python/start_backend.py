#!/usr/bin/env python3
"""
Startup script for AI Backend - runs from root directory
"""

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the backend directory
    backend_dir = os.path.join(script_dir, "ai-backend-python")
    
    # Check if the backend directory exists
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory not found at {backend_dir}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Available directories: {os.listdir('.')}")
        sys.exit(1)
    
    # Change to the backend directory
    os.chdir(backend_dir)
    print(f"Changed to directory: {os.getcwd()}")
    
    # Check if start.py exists
    if not os.path.exists("start.py"):
        print(f"Error: start.py not found in {backend_dir}")
        print(f"Available files: {os.listdir('.')}")
        sys.exit(1)
    
    # Start the backend
    print("Starting AI Backend...")
    subprocess.run([sys.executable, "start.py"])

if __name__ == "__main__":
    main() 