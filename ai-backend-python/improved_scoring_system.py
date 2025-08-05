#!/usr/bin/env python3
"""
Improved Scoring System
Provides realistic and varied test scores
"""

import random
import math
from typing import Dict, Any

class ImprovedScoringSystem:
    def __init__(self):
        self.base_scores = {
            "basic": (60, 85),
            "intermediate": (50, 80),
            "advanced": (40, 75),
            "expert": (30, 70),
            "master": (20, 65),
            "legendary": (10, 60)
        }
    
    def calculate_realistic_score(self, ai_type: str, difficulty: str, performance_factors: Dict[str, Any]) -> float:
        """Calculate a realistic test score"""
        
        # Get base score range for difficulty
        min_score, max_score = self.base_scores.get(difficulty, (50, 80))
        
        # Apply AI-specific modifiers
        ai_modifiers = {
            "imperium": 1.1,  # Slightly better at systematic tasks
            "guardian": 1.05,  # Good at security tasks
            "sandbox": 0.95,   # May be less consistent
            "conquest": 1.0    # Balanced
        }
        
        modifier = ai_modifiers.get(ai_type, 1.0)
        
        # Apply performance factors
        time_factor = performance_factors.get("time_taken", 0.5)
        accuracy_factor = performance_factors.get("accuracy", 0.8)
        complexity_factor = performance_factors.get("complexity_handled", 0.7)
        
        # Calculate base score
        base_score = random.uniform(min_score, max_score)
        
        # Apply modifiers
        final_score = base_score * modifier * time_factor * accuracy_factor * complexity_factor
        
        # Add some randomness for realism
        final_score += random.uniform(-5, 5)
        
        # Ensure score is within reasonable bounds
        final_score = max(0, min(100, final_score))
        
        return round(final_score, 2)
    
    def generate_performance_factors(self, ai_type: str, test_type: str) -> Dict[str, Any]:
        """Generate realistic performance factors"""
        return {
            "time_taken": random.uniform(0.6, 1.0),
            "accuracy": random.uniform(0.7, 0.95),
            "complexity_handled": random.uniform(0.5, 0.9),
            "innovation_level": random.uniform(0.3, 0.8),
            "error_count": random.randint(0, 3)
        }
