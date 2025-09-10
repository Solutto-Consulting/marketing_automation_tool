import asyncio
import os
import json
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class OpenAIUtils(models.AbstractModel):
    """Utility class for OpenAI integration using openai-agents SDK"""
    _name = 'openai.utils'
    _description = 'OpenAI Integration Utilities'

    @api.model
    def get_available_models(self):
        """Retrieve available OpenAI models via API call with fallback"""
        try:
            # Get API credentials
            api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
            if not api_key:
                _logger.warning("OpenAI API key not configured, using fallback models")
                return self._get_fallback_models()
            
            # Set environment variable for openai-agents
            os.environ['OPENAI_API_KEY'] = api_key
            
            org_id = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_organization_id')
            if org_id:
                os.environ['OPENAI_ORGANIZATION'] = org_id
            
            # Try to get models from OpenAI API
            # Note: openai-agents doesn't expose direct model listing, so we'll use fallback
            # In a real implementation, you might use the openai library directly for model listing
            return self._get_fallback_models()
            
        except Exception as e:
            _logger.warning("Failed to retrieve OpenAI models: %s, using fallback", str(e))
            return self._get_fallback_models()
    
    @api.model
    def _get_fallback_models(self):
        """Fallback model list when API call fails"""
        return [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ]
    
    @api.model
    async def perform_ai_translation(self, model_name, system_instructions, prompt):
        """
        Performs translation using the OpenAI Agents SDK.
        
        Args:
            model_name (str): The OpenAI model to use
            system_instructions (str): Instructions for the AI agent
            prompt (str): The translation prompt
            
        Returns:
            str: The translated content from the AI
        """
        try:
            # Import here to avoid import errors if package not installed
            from agents import Agent, Runner
            
            # Create agent with enhanced instructions for HTML consistency
            enhanced_instructions = f"""You are a professional translator specializing in web content translation. 

CORE MISSION: Translate content while maintaining perfect HTML structure consistency.

CRITICAL RULES:
1. PRESERVE HTML STRUCTURE: Never alter, remove, or add HTML tags, attributes, or formatting
2. PARAGRAPH CONSISTENCY: Maintain the exact same number of paragraphs and their structure
3. SEMANTIC ACCURACY: Provide precise, context-appropriate translations
4. TONE PRESERVATION: Maintain the original tone and style of the content

SPECIFIC REQUIREMENTS FOR HTML CONTENT:
- Keep ALL HTML tags exactly as they are: <p>, <div>, <span>, <strong>, <em>, <a>, <img>, etc.
- Preserve ALL attributes: class, style, id, href, src, alt, etc.
- Maintain paragraph breaks: If original has 3 paragraphs, translation must have 3 paragraphs
- Keep empty elements: <p><br></p> should remain <p><br></p>
- Preserve formatting: Line breaks, spacing, and indentation
- Translate ONLY the text content inside tags, never the tags themselves

{system_instructions or 'Focus on accuracy and maintaining the professional tone of the original content.'}"""
            
            agent = Agent(
                name="Odoo Blog Content Translator",
                instructions=enhanced_instructions,
                model=model_name,
            )
            
            # Execute translation
            result = await Runner.run(agent, prompt)
            return result.final_output
            
        except ImportError:
            _logger.error("openai-agents package not installed. Please install with: pip install openai-agents")
            raise Exception("OpenAI Agents SDK not available. Please install the required package.")
        except Exception as e:
            _logger.error("AI translation failed: %s", str(e))
            raise Exception(f"Translation failed: {str(e)}")
    
    @api.model
    def translate_blog_content(self, blog_post, target_language, system_instructions=None):
        """
        Translate blog post content using AI
        
        Args:
            blog_post: blog.post record
            target_language: res.lang record
            system_instructions: Optional custom instructions
            
        Returns:
            dict: Translated content
        """
        # Get configuration
        config = self.env['res.config.settings'].sudo()
        api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
        org_id = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_organization_id')
        model_name = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_model') or 'gpt-4o'
        
        if not api_key:
            raise Exception("OpenAI API key not configured. Please configure it in Settings > General Settings > AI Marketing Tools.")
        
        # Set environment variables
        os.environ['OPENAI_API_KEY'] = api_key
        if org_id:
            os.environ['OPENAI_ORGANIZATION'] = org_id
        
        # Prepare content for translation - ALL TRANSLATABLE FIELDS
        source_content = {
            # Basic fields
            'name': blog_post.name or '',
            'subtitle': blog_post.subtitle or '',
            'content': blog_post.content or '',
            
            # SEO fields (from website.seo.metadata mixin)
            'website_meta_title': blog_post.website_meta_title or '',
            'website_meta_description': blog_post.website_meta_description or '',
            'website_meta_keywords': blog_post.website_meta_keywords or '',
            
            # Teaser fields
            'teaser_manual': blog_post.teaser_manual or '',
        }
        
        # Build enhanced translation prompt with HTML consistency instructions
        source_lang = blog_post.website_id.default_lang_id.name if blog_post.website_id.default_lang_id else 'English'
        target_lang = target_language.name
        
        prompt = f"""Translate the values in the following JSON object from {source_lang} to {target_lang}.

CRITICAL HTML CONSISTENCY REQUIREMENTS:
1. For the "content" field: PRESERVE ALL HTML tags, structure, and formatting exactly as they appear
2. Maintain the same number of paragraphs (<p> tags), headings, lists, and other HTML elements
3. Keep all HTML attributes (class, style, id) unchanged
4. Only translate the TEXT CONTENT inside HTML tags, never the tags themselves
5. Preserve the exact same paragraph breaks and structure
6. Maintain any embedded links, images, or other media elements
7. If there are empty paragraphs (<p><br></p>), keep them exactly as they are

EXAMPLE:
Original: <p>Hello <strong>world</strong>!</p><p><br></p><p>Second paragraph.</p>
Correct:  <p>Hola <strong>mundo</strong>!</p><p><br></p><p>Segundo párrafo.</p>
WRONG:    <p>Hola mundo! Segundo párrafo.</p> (structure changed)

For all other fields (name, subtitle, etc.): Translate the text content normally.

Respond ONLY with the translated JSON object, maintaining the exact same key structure.

JSON to translate:
{json.dumps(source_content, ensure_ascii=False, indent=2)}"""
        
        # Execute translation asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            translated_content_str = loop.run_until_complete(
                self.perform_ai_translation(model_name, system_instructions, prompt)
            )
        finally:
            loop.close()
        
        # Parse translated content
        try:
            # Clean response to extract JSON
            translated_content_str = translated_content_str.strip()
            if translated_content_str.startswith('```json'):
                translated_content_str = translated_content_str[7:]
            if translated_content_str.endswith('```'):
                translated_content_str = translated_content_str[:-3]
            
            translated_content = json.loads(translated_content_str)
            return translated_content
            
        except json.JSONDecodeError as e:
            _logger.error("Failed to parse AI response as JSON: %s", str(e))
            _logger.error("AI Response: %s", translated_content_str)
            raise Exception("AI returned invalid JSON format. Please try again.")
