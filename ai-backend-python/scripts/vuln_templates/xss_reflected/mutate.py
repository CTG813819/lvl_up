#!/usr/bin/env python3
"""
AI Mutation Script for XSS Template
This script modifies the vulnerable app to make it more dynamic and challenging.
"""

import os
import sys
import random
import string
import json
import re
from pathlib import Path

class VulnAppMutator:
    def __init__(self, template_path):
        self.template_path = Path(template_path)
        self.config_path = self.template_path / "config.json"
        self.app_path = self.template_path / "app" / "app.py"
        
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
    
    def generate_random_string(self, length=8):
        """Generate a random string for obfuscation."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def mutate_xss_vectors(self, content):
        """Add obfuscation to XSS vectors to make them harder to detect."""
        # Simple mutation - add random comments
        content = re.sub(
            r'(<script>|</script>)',
            lambda m: f"{m.group(1)} <!--{self.generate_random_string(4)}-->",
            content
        )
        return content
    
    def apply_mutations(self):
        """Apply all mutations to the template."""
        print(f"Applying mutations to {self.template_path}")
        
        # Read the original app.py
        with open(self.app_path, 'r') as f:
            content = f.read()
        
        # Apply mutations based on configuration
        mutation_opts = self.config.get('mutation_options', {})
        
        if mutation_opts.get('vuln_obfuscation', False):
            print("Applying XSS vector obfuscation...")
            content = self.mutate_xss_vectors(content)
        
        # Write the mutated content back
        with open(self.app_path, 'w') as f:
            f.write(content)
        
        print("Mutations applied successfully!")
        return True

def main():
    """Main function to run mutations."""
    if len(sys.argv) != 2:
        print("Usage: python mutate.py <template_path>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    mutator = VulnAppMutator(template_path)
    mutator.apply_mutations()

if __name__ == "__main__":
    main() 