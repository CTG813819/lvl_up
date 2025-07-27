import os
import json
import asyncio
from typing import Optional, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from app.services.anthropic_service import anthropic_rate_limited_call

class AdvancedCodeGenerator:
    """
    Advanced code generation service using Anthropic, local transformer models, and robust templates.
    """
    
    def __init__(self):
        self.local_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models for code generation."""
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

    async def generate_dart_code(self, description: str, complexity: str = "medium") -> str:
        """Generate Dart code for Flutter extensions using Anthropic, local model, or template."""
        prompt = (
            "You are an expert Flutter developer. "
            "Generate a complete, robust Dart widget for the following feature description. "
            "Always include: import 'package:flutter/material.dart';. "
            "Do NOT use package imports for the extension file itself. "
            "Do NOT import the extension file by name. "
            "The widget must have a build method and return a valid widget. "
            f"Description: {description} (complexity: {complexity})"
        )
        # 1. Try Anthropic
        try:
            code = await anthropic_rate_limited_call(prompt, ai_name="sandbox", model="claude-3-5-sonnet-20241022", max_tokens=1024)
            code = self._postprocess_dart_code(code)
            if self._is_valid_dart_code(code):
                return code
        except Exception as e:
            print(f"Anthropic code generation failed: {e}")

        # 2. Try local model
        if self.local_model:
            try:
                code = await self._generate_with_local_model(description, complexity)
                code = self._postprocess_dart_code(code)
                if self._is_valid_dart_code(code):
                    return code
            except Exception as e:
                print(f"Local model code generation failed: {e}")

        # 3. Fallback to template
        code = await self._generate_with_template(description, complexity)
        code = self._postprocess_dart_code(code)
        return code

    async def generate_code(self, description: str, complexity: str = "medium") -> str:
        # For non-Dart code, fallback to template or local model
        try:
            if self.local_model:
                return await self._generate_with_local_model(description, complexity)
            return await self._generate_with_template(description, complexity)
        except Exception as e:
            print(f"Code generation failed: {e}")
            return await self._generate_with_template(description, complexity)

    async def _generate_with_local_model(self, description: str, complexity: str) -> str:
        prompt = self._build_prompt(description, complexity, "local")
        try:
            result = self.local_model(prompt, max_length=512, temperature=0.7)
            return result[0]['generated_text']
        except Exception as e:
            print(f"Local model generation failed: {e}")
            return await self._generate_with_template(description, complexity)

    async def _generate_with_template(self, description: str, complexity: str) -> str:
        template = self._get_template_for_complexity(complexity)
        code = template.replace("{description}", description)
        code = code.replace("{complexity}", complexity)
        return code

    def _build_prompt(self, description: str, complexity: str, model_type: str) -> str:
        if model_type == "local":
            return f"Generate Flutter code for: {description} (complexity: {complexity})"
        else:
            return f"Create a Flutter widget for: {description}"

    def _get_template_for_complexity(self, complexity: str) -> str:
        if complexity == "high":
            return """
import 'package:flutter/material.dart';

class GeneratedWidget extends StatefulWidget {
  const GeneratedWidget({Key? key}) : super(key: key);

  @override
  State<GeneratedWidget> createState() => _GeneratedWidgetState();
}

class _GeneratedWidgetState extends State<GeneratedWidget> {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Text('{description} - {complexity} complexity'),
    );
  }
}
"""
        else:
            return """
import 'package:flutter/material.dart';

class GeneratedWidget extends StatelessWidget {
  const GeneratedWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Text('{description}');
  }
}
"""

    def _postprocess_dart_code(self, code: str) -> str:
        # Remove any bad imports or self-imports
        lines = code.splitlines()
        lines = [l for l in lines if "package:the_codex/extensions" not in l and not l.strip().startswith("import './")]
        # Ensure required import is present
        if not any("import 'package:flutter/material.dart';" in l for l in lines):
            lines.insert(0, "import 'package:flutter/material.dart';")
        # Remove duplicate imports
        seen = set()
        cleaned_lines = []
        for l in lines:
            if l.strip().startswith("import"):
                if l not in seen:
                    cleaned_lines.append(l)
                    seen.add(l)
            else:
                cleaned_lines.append(l)
        return "\n".join(cleaned_lines)

    def _is_valid_dart_code(self, code: str) -> bool:
        # Basic checks: has class, build method, return statement
        return (
            "class " in code and
            "Widget build(BuildContext context)" in code and
            "return" in code
        ) 