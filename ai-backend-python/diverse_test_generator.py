#!/usr/bin/env python3
"""
Diverse Test Generator
Generates varied and realistic test scenarios
"""

import random
import json
from datetime import datetime
from typing import Dict, Any, List

class DiverseTestGenerator:
    def __init__(self):
        self.test_scenarios = {
            "imperium": [
                {
                    "title": "System Architecture Challenge",
                    "description": "Design a scalable microservices architecture",
                    "complexity": "advanced",
                    "focus": "system_design"
                },
                {
                    "title": "Performance Optimization",
                    "description": "Optimize a slow-running application",
                    "complexity": "intermediate",
                    "focus": "performance"
                },
                {
                    "title": "Code Quality Assessment",
                    "description": "Review and improve code quality",
                    "complexity": "basic",
                    "focus": "code_quality"
                }
            ],
            "guardian": [
                {
                    "title": "Security Vulnerability Assessment",
                    "description": "Identify and fix security vulnerabilities",
                    "complexity": "advanced",
                    "focus": "security"
                },
                {
                    "title": "Access Control Implementation",
                    "description": "Implement secure access controls",
                    "complexity": "intermediate",
                    "focus": "security"
                },
                {
                    "title": "Security Best Practices",
                    "description": "Apply security best practices",
                    "complexity": "basic",
                    "focus": "security"
                }
            ],
            "sandbox": [
                {
                    "title": "Innovative Feature Development",
                    "description": "Create an innovative application feature",
                    "complexity": "advanced",
                    "focus": "innovation"
                },
                {
                    "title": "Experimental Algorithm",
                    "description": "Develop an experimental algorithm",
                    "complexity": "intermediate",
                    "focus": "experimentation"
                },
                {
                    "title": "Creative Problem Solving",
                    "description": "Solve a problem creatively",
                    "complexity": "basic",
                    "focus": "creativity"
                }
            ],
            "conquest": [
                {
                    "title": "User Experience Design",
                    "description": "Design an excellent user experience",
                    "complexity": "advanced",
                    "focus": "ux_design"
                },
                {
                    "title": "Feature Implementation",
                    "description": "Implement user-requested features",
                    "complexity": "intermediate",
                    "focus": "feature_dev"
                },
                {
                    "title": "User Interface Design",
                    "description": "Create an intuitive user interface",
                    "complexity": "basic",
                    "focus": "ui_design"
                }
            ]
        }
    
    def generate_diverse_test(self, test_type: str, ai_type: str) -> Dict[str, Any]:
        """Generate a diverse test scenario"""
        if ai_type not in self.test_scenarios:
            ai_type = "imperium"  # Default fallback
        
        scenarios = self.test_scenarios[ai_type]
        scenario = random.choice(scenarios)
        
        # Add randomization to make tests more diverse
        complexity_modifiers = ["with time constraints", "under pressure", "with limited resources", "in a team environment"]
        modifier = random.choice(complexity_modifiers)
        
        return {
            "title": f"{scenario['title']} {modifier}",
            "description": f"{scenario['description']} {modifier}",
            "complexity": scenario["complexity"],
            "focus": scenario["focus"],
            "ai_type": ai_type,
            "timestamp": datetime.utcnow().isoformat(),
            "diverse_generated": True
        }
    
    def generate_ai_response(self, ai_type: str, scenario: Dict[str, Any]) -> str:
        """Generate a realistic AI response to the scenario"""
        responses = {
            "imperium": f"As {ai_type.title()}, I would approach this {scenario['focus']} challenge systematically...",
            "guardian": f"As {ai_type.title()}, I would ensure security is the primary consideration in this {scenario['focus']} task...",
            "sandbox": f"As {ai_type.title()}, I would explore innovative approaches to this {scenario['focus']} challenge...",
            "conquest": f"As {ai_type.title()}, I would focus on user needs while addressing this {scenario['focus']} requirement..."
        }
        
        return responses.get(ai_type, f"As {ai_type.title()}, I would approach this challenge...")
