# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

import asyncio
import json
import os
import logging
from typing import Dict, Any

_logger = logging.getLogger(__name__)


class OpenAITranslationService:
    """Service class for OpenAI Agent SDK integration"""
    
    def __init__(self, api_key: str, organization_id: str = None, model: str = 'gpt-4o'):
        """Initialize OpenAI service with credentials and model"""
        # Set environment variables for OpenAI SDK
        os.environ['OPENAI_API_KEY'] = api_key
        if organization_id:
            os.environ['OPENAI_ORG_ID'] = organization_id
        self.model = model
        
        _logger.info("OpenAI Translation Service initialized with model: %s", model)
    
    async def translate_blog_content(
        self, 
        content_json: Dict[str, Any], 
        source_lang: str, 
        target_lang: str, 
        system_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Translate blog content using OpenAI Agent SDK
        
        Args:
            content_json (dict): Blog post content fields
            source_lang (str): Source language code
            target_lang (str): Target language code  
            system_instructions (str): Custom AI instructions
            
        Returns:
            dict: Translated content with same structure
            
        Raises:
            Exception: For API-related errors or validation errors
        """
        
        try:
            # Import OpenAI Agents SDK
            from agents import Agent, Runner
        except ImportError as e:
            raise ImportError(
                "OpenAI Agents SDK not installed. Please install 'openai-agents' package."
            ) from e
        
        # Prepare system instructions
        base_instructions = f"""
You are a professional translator specializing in blog content translation.
Translate the provided JSON content from {source_lang} to {target_lang}.

CRITICAL RULES:
1. Maintain the exact JSON structure - never change the keys
2. Translate only the VALUES, never the KEYS
3. Preserve all HTML tags and formatting exactly as they are
4. Adapt cultural references appropriately for the target audience
5. Maintain the original tone and style unless specified otherwise
6. Return ONLY valid JSON with no additional text or explanations
7. If a value is empty or null, keep it empty or null

{system_instructions}

Example format:
Input: {{"title": "Hello World", "content": "<p>Welcome</p>"}}
Output: {{"title": "Hola Mundo", "content": "<p>Bienvenido</p>"}}
        """
        
        # Build translation prompt
        prompt = f"""
Translate the values in the following JSON object from {source_lang} to {target_lang}.
Respond ONLY with the translated JSON object, maintaining the exact same key structure.

JSON to translate:
{json.dumps(content_json, indent=2, ensure_ascii=False)}
        """
        
        try:
            # Create agent and execute translation
            agent = Agent(
                name="Odoo Blog Translator",
                instructions=base_instructions.strip(),
                model=self.model
            )
            
            _logger.info("Starting translation from %s to %s using model %s", 
                        source_lang, target_lang, self.model)
            
            # Execute translation
            result = await Runner.run(agent, prompt.strip())
            
            if not result or not result.final_output:
                raise ValueError("Empty response from OpenAI Agent")
            
            _logger.info("Translation completed, processing response")
            
            # Parse and validate response
            response_text = result.final_output.strip()
            
            # Try to extract JSON if response contains extra text
            if not response_text.startswith('{'):
                # Look for JSON block in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    response_text = response_text[start_idx:end_idx + 1]
            
            try:
                translated_content = json.loads(response_text)
            except json.JSONDecodeError as e:
                _logger.error("Invalid JSON response from AI: %s", response_text)
                raise ValueError(f"Invalid JSON response from AI: {e}")
            
            # Validate that all original keys are present
            if not isinstance(translated_content, dict):
                raise ValueError("Response is not a JSON object")
            
            for key in content_json.keys():
                if key not in translated_content:
                    _logger.warning("Missing key '%s' in translation response", key)
                    translated_content[key] = content_json[key]  # Keep original
            
            _logger.info("Translation validation successful")
            return translated_content
            
        except Exception as e:
            _logger.exception("Error during OpenAI Agent execution")
            raise Exception(f"Translation failed: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test OpenAI connection with a simple request"""
        try:
            from agents import Agent, Runner
            
            agent = Agent(
                name="Test Agent",
                instructions="Respond with exactly: TEST_SUCCESS",
                model=self.model
            )
            
            result = await Runner.run(agent, "Test connection")
            return "TEST_SUCCESS" in (result.final_output or "")
            
        except Exception as e:
            _logger.exception("Connection test failed")
            raise Exception(f"Connection test failed: {str(e)}")
    
    @classmethod
    def validate_content(cls, content_json: Dict[str, Any]) -> bool:
        """Validate content structure before translation"""
        if not isinstance(content_json, dict):
            return False
        
        required_fields = ['name', 'content']
        for field in required_fields:
            if field not in content_json:
                return False
        
        return True
    
    @classmethod
    def estimate_tokens(cls, content_json: Dict[str, Any]) -> int:
        """Estimate token count for content (rough approximation)"""
        total_chars = sum(len(str(value)) for value in content_json.values() if value)
        # Rough estimation: ~4 characters per token
        return total_chars // 4
    
    @classmethod
    def calculate_cost_estimate(cls, token_count: int, model: str = 'gpt-4o') -> float:
        """Calculate estimated cost based on token count and model"""
        # Rough pricing estimates (as of 2024, subject to change)
        pricing = {
            'gpt-4o': 0.00001,  # $0.01 per 1K tokens
            'gpt-4-turbo': 0.00001,
            'gpt-3.5-turbo': 0.000002,  # $0.002 per 1K tokens
        }
        
        rate = pricing.get(model, 0.00001)  # Default to GPT-4o pricing
        return token_count * rate
