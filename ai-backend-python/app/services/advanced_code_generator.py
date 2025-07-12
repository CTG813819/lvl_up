import os
import json
import asyncio
from typing import Optional, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class AdvancedCodeGenerator:
    """
    Advanced code generation service using local transformer models only.
    Anthropic removed to prevent authentication errors and timeouts.
    """
    
    def __init__(self):
        self.local_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models for code generation."""
        # Initialize local model if available
        try:
            model_path = os.getenv('LOCAL_MODEL_PATH', './models/code_generator')
            if os.path.exists(model_path):
                self.local_model = pipeline(
                    "text-generation",
                    model=model_path,
                    device=0 if torch.cuda.is_available() else -1
                )
                print(f"✅ Local model loaded from {model_path}")
            else:
                print("⚠️ Local model not found, using template generation")
        except Exception as e:
            print(f"⚠️ Failed to load local model: {e}")
    
    async def generate_code(self, description: str, complexity: str = "medium") -> str:
        """Generate code based on description and complexity."""
        try:
            # Try local model first
            if self.local_model:
                return await self._generate_with_local_model(description, complexity)
            
            # Fallback to template generation
            return await self._generate_with_template(description, complexity)
            
        except Exception as e:
            print(f"Code generation failed: {e}")
            return await self._generate_with_template(description, complexity)
    
    async def _generate_with_local_model(self, description: str, complexity: str) -> str:
        """Generate code using local transformer model."""
        prompt = self._build_prompt(description, complexity, "local")
        
        try:
            result = self.local_model(prompt, max_length=512, temperature=0.7)
            return result[0]['generated_text']
        except Exception as e:
            print(f"Local model generation failed: {e}")
            return await self._generate_with_template(description, complexity)
    
    async def _generate_with_template(self, description: str, complexity: str) -> str:
        """Generate code using template-based approach."""
        template = self._get_template_for_complexity(complexity)
        
        # Simple template-based generation
        code = template.replace("{description}", description)
        code = code.replace("{complexity}", complexity)
        
        return code
    
    def _build_prompt(self, description: str, complexity: str, model_type: str) -> str:
        """Build prompt for code generation."""
        if model_type == "local":
            return f"Generate Flutter code for: {description} (complexity: {complexity})"
        else:
            return f"Create a Flutter widget for: {description}"
    
    def _get_template_for_complexity(self, complexity: str) -> str:
        """Get template based on complexity level."""
        if complexity == "high":
            return '''
class {description}Widget extends StatefulWidget {
  const {description}Widget({Key? key}) : super(key: key);

  @override
  State<{description}Widget> createState() => _State();
}

class _State extends State<{description}Widget> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Text('{description} - {complexity} complexity'),
    );
  }
}
'''
        else:
            return '''
class {description}Widget extends StatelessWidget {
  const {description}Widget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Text('{description}');
  }
}
''' 