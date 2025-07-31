#!/usr/bin/env python3
"""
Fix all challenge generation methods to use the correct SckipitService approach
"""

import re

def fix_challenge_methods():
    """Fix all challenge generation methods"""
    
    # Read the file
    with open('app/services/enhanced_adversarial_testing_service.py', 'r') as f:
        content = f.read()
    
    # Define the replacement pattern for all challenge methods
    old_pattern = r'response = await self\.sckipit_service\.generate_answer_with_llm\(prompt\)\s+return self\._parse_scenario_response\(response\)'
    
    new_pattern = '''try:
            # Use SckipitService's ml_service to generate the challenge
            result = await self.sckipit_service.ml_service.generate_with_llm(prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    scenario_content = json.loads(result["content"])
                    return scenario_content
                except json.JSONDecodeError:
                    # Fallback to structured response
                    return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
            else:
                return self._create_fallback_scenario_content(domain_name, complexity, ai_types)
                
        except Exception as e:
            logger.error(f"Error generating {domain_name} challenge: {{str(e)}}")
            return self._create_fallback_scenario_content(domain_name, complexity, ai_types)'''
    
    # Replace all occurrences
    content = re.sub(old_pattern, new_pattern, content)
    
    # Now we need to add the domain_name variable to each method
    # Let's do this manually for each method
    
    # Security challenge
    content = content.replace(
        'async def _generate_security_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:',
        '''async def _generate_security_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "security_challenges"'''
    )
    
    # Creative challenge
    content = content.replace(
        'async def _generate_creative_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:',
        '''async def _generate_creative_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "creative_tasks"'''
    )
    
    # Collaboration challenge
    content = content.replace(
        'async def _generate_collaboration_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:',
        '''async def _generate_collaboration_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "collaboration_competition"'''
    )
    
    # General challenge
    content = content.replace(
        'async def _generate_general_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:',
        '''async def _generate_general_challenge(self, ai_types: List[str], complexity: ScenarioComplexity, adaptive_context: str) -> Dict[str, Any]:
        domain_name = "general"'''
    )
    
    # Write the fixed content back
    with open('app/services/enhanced_adversarial_testing_service.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed all challenge generation methods")

if __name__ == "__main__":
    fix_challenge_methods() 