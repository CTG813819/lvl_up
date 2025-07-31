#!/usr/bin/env python3
"""
AI Mutation Script for SQL Injection Template
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
    
    def mutate_table_names(self):
        """Randomly change table names to make attacks more challenging."""
        original_tables = self.config.get('mutation_options', {}).get('table_names', ['users', 'products'])
        new_tables = []
        
        for table in original_tables:
            # 50% chance to rename table
            if random.random() > 0.5:
                prefix = random.choice(['tbl_', 'data_', 'app_', 'sys_'])
                suffix = self.generate_random_string(4)
                new_table = f"{prefix}{table}_{suffix}"
                new_tables.append(new_table)
            else:
                new_tables.append(table)
        
        return new_tables
    
    def mutate_column_names(self):
        """Randomly change column names."""
        original_columns = self.config.get('mutation_options', {}).get('column_names', ['id', 'username', 'password'])
        new_columns = []
        
        for col in original_columns:
            # 30% chance to rename column
            if random.random() > 0.7:
                prefix = random.choice(['col_', 'field_', 'attr_'])
                suffix = self.generate_random_string(3)
                new_col = f"{prefix}{col}_{suffix}"
                new_columns.append(new_col)
            else:
                new_columns.append(col)
        
        return new_columns
    
    def obfuscate_sql_queries(self, content):
        """Add obfuscation to SQL queries to make them harder to detect."""
        # Add random whitespace and comments
        content = re.sub(
            r'(SELECT|FROM|WHERE|AND|OR)',
            lambda m: f"{m.group(1)} /*{self.generate_random_string(4)}*/",
            content
        )
        
        # Add random string concatenation
        content = re.sub(
            r"'([^']*)'",
            lambda m: f"'{m.group(1)}' + '{self.generate_random_string(2)}'",
            content
        )
        
        return content
    
    def add_complexity(self, content):
        """Add complexity to make the app more challenging."""
        # Add random error handling
        error_handlers = [
            "try:",
            "    pass",
            "except Exception as e:",
            f"    print(f'Error: {{e}}')",
            "    return None"
        ]
        
        # Insert error handling in strategic places
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add error handling after SQL queries
            if 'cursor.execute(' in line and i + 1 < len(lines):
                if 'try:' not in lines[i-1] if i > 0 else True:
                    new_lines.extend([''] + error_handlers + [''])
        
        return '\n'.join(new_lines)
    
    def mutate_credentials(self):
        """Randomly change credentials."""
        new_credentials = {}
        for user, cred in self.config.get('credentials', {}).items():
            if random.random() > 0.7:  # 30% chance to change
                username, password = cred.split(':')
                new_username = f"{username}_{self.generate_random_string(3)}"
                new_password = f"{password}_{self.generate_random_string(3)}"
                new_credentials[user] = f"{new_username}:{new_password}"
            else:
                new_credentials[user] = cred
        
        return new_credentials
    
    def apply_mutations(self):
        """Apply all mutations to the template."""
        print(f"Applying mutations to {self.template_path}")
        
        # Read the original app.py
        with open(self.app_path, 'r') as f:
            content = f.read()
        
        # Apply mutations based on configuration
        mutation_opts = self.config.get('mutation_options', {})
        
        if mutation_opts.get('vuln_obfuscation', False):
            print("Applying SQL query obfuscation...")
            content = self.obfuscate_sql_queries(content)
        
        if mutation_opts.get('code_complexity') in ['medium', 'high']:
            print("Adding code complexity...")
            content = self.add_complexity(content)
        
        # Update table and column names
        if mutation_opts.get('randomization', False):
            new_tables = self.mutate_table_names()
            new_columns = self.mutate_column_names()
            
            # Replace table names in the code
            for old_table, new_table in zip(['users', 'products'], new_tables):
                content = content.replace(f"'{old_table}'", f"'{new_table}'")
                content = content.replace(f'"{old_table}"', f'"{new_table}"')
            
            # Replace column names
            for old_col, new_col in zip(['username', 'password', 'email', 'role'], new_columns):
                content = content.replace(f"'{old_col}'", f"'{new_col}'")
                content = content.replace(f'"{old_col}"', f'"{new_col}"')
        
        # Update credentials
        new_credentials = self.mutate_credentials()
        for user, cred in new_credentials.items():
            username, password = cred.split(':')
            # Update credential insertion in the code
            content = re.sub(
                rf"'{user}', '[^']*'",
                f"'{user}', '{password}'",
                content
            )
        
        # Write the mutated content back
        with open(self.app_path, 'w') as f:
            f.write(content)
        
        # Update config with new values
        self.config['credentials'] = new_credentials
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("Mutations applied successfully!")
        return True

def main():
    """Main function to run mutations."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python mutate.py <template_path>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    mutator = VulnAppMutator(template_path)
    mutator.apply_mutations()

if __name__ == "__main__":
    main() 