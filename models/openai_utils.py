import asyncio
import os
import json
import logging
from odoo import api, fields, models

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

    @api.model
    async def perform_content_research(self, model_name, system_instructions, search_query, num_ideas=5):
        """
        Perform content research using OpenAI Agents SDK with WebSearchTool
        
        Args:
            model_name (str): The OpenAI model to use
            system_instructions (str): Instructions for the research agent
            search_query (str): The search query for finding content ideas
            num_ideas (int): Number of ideas to generate
            
        Returns:
            list: List of content ideas with structure [{'name': str, 'url': str, 'publish_date': str, 'summary': str}]
        """
        try:
            # Import here to avoid import errors if package not installed
            from agents import Agent, Runner, WebSearchTool
            
            # Create agent with WebSearchTool
            agent = Agent(
                name="Content Research Agent",
                instructions=system_instructions,
                model=model_name,
                tools=[WebSearchTool()],
            )
            
            # Build structured prompt for content research
            prompt = f"""
Search for recent articles and content related to: {search_query}

Please find {num_ideas} relevant articles and return them as a JSON list with the following structure:

[
  {{
    "name": "Article title",
    "url": "Full URL to the article",
    "publish_date": "Publication date in YYYY-MM-DD format (or null if not available)",
    "summary": "Concise summary highlighting key points and content marketing value"
  }}
]

Focus on finding:
- Recent, high-quality articles from authoritative sources
- Content that would be valuable for business/marketing audiences
- Articles with actionable insights and practical information
- Diverse perspectives and sources when possible

Return ONLY the JSON array, no additional text or explanation.
"""
            
            # Execute research
            result = await Runner.run(agent, prompt)
            
            # Parse the JSON response
            try:
                response_text = result.final_output.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                ideas = json.loads(response_text)
                
                # Validate the structure
                if not isinstance(ideas, list):
                    raise ValueError("Response must be a JSON list")
                
                for idea in ideas:
                    if not all(key in idea for key in ['name', 'url', 'summary']):
                        raise ValueError("Each idea must have name, url, and summary fields")
                
                return ideas
                
            except (json.JSONDecodeError, ValueError) as e:
                _logger.error("Failed to parse research response: %s", str(e))
                _logger.error("Agent Response: %s", result.final_output)
                raise Exception(f"Agent returned invalid response format: {str(e)}")
            
        except ImportError:
            _logger.error("openai-agents package not installed. Please install with: pip install openai-agents")
            raise Exception("OpenAI Agents SDK not available. Please install the required package.")
        except Exception as e:
            _logger.error("Content research failed: %s", str(e))
            raise Exception(f"Content research failed: {str(e)}")

    @api.model
    async def perform_content_generation(self, model_name, system_instructions, content_idea, user_prompt=""):
        """
        Generate blog content using OpenAI Agents SDK
        
        Args:
            model_name (str): The OpenAI model to use
            system_instructions (str): Instructions for the generation agent
            content_idea (dict): Content idea with name, url, summary fields
            user_prompt (str): Additional user instructions
            
        Returns:
            dict: Generated content with structure {'title': str, 'content': str, 'meta_description': str, 'keywords': str}
        """
        try:
            # Import here to avoid import errors if package not installed
            from agents import Agent, Runner
            
            # Create content generation agent
            agent = Agent(
                name="Content Generation Agent",
                instructions=system_instructions,
                model=model_name,
            )
            
            # Build structured prompt for content generation
            prompt = f"""
Based on the following source content, create a comprehensive blog post:

SOURCE CONTENT:
Title: {content_idea.get('name', '')}
URL: {content_idea.get('url', '')}
Summary: {content_idea.get('summary', '')}

ADDITIONAL INSTRUCTIONS:
{user_prompt or 'Create engaging, professional content suitable for a business audience.'}

Generate a complete blog post and return it as a JSON object with the following structure:

{{
  "title": "SEO-friendly blog post title",
  "content": "Complete HTML content with proper headings and formatting",
  "meta_description": "Compelling meta description for SEO (150-160 characters)",
  "keywords": "Relevant keywords separated by commas"
}}

Content Requirements:
- Create original content that adds value beyond the source material
- Use proper HTML structure with H2/H3 headings for organization
- Aim for 800-1500 words of engaging, actionable content
- Include a strong introduction and conclusion
- Write in a professional yet engaging tone
- Ensure content is SEO-optimized and business-focused

Return ONLY the JSON object, no additional text or explanation.
"""
            
            # Execute content generation
            result = await Runner.run(agent, prompt)
            
            # Parse the JSON response
            try:
                response_text = result.final_output.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                content = json.loads(response_text)
                
                # Validate the structure
                required_fields = ['title', 'content', 'meta_description', 'keywords']
                if not all(key in content for key in required_fields):
                    raise ValueError(f"Response must contain all required fields: {required_fields}")
                
                return content
                
            except (json.JSONDecodeError, ValueError) as e:
                _logger.error("Failed to parse generation response: %s", str(e))
                _logger.error("Agent Response: %s", result.final_output)
                raise Exception(f"Agent returned invalid response format: {str(e)}")
            
        except ImportError:
            _logger.error("openai-agents package not installed. Please install with: pip install openai-agents")
            raise Exception("OpenAI Agents SDK not available. Please install the required package.")
        except Exception as e:
            _logger.error("Content generation failed: %s", str(e))
            raise Exception(f"Content generation failed: {str(e)}")

    @api.model
    def fetch_and_store_usage_data(self):
        """
        Fetch usage data from OpenAI API and store in snapshots
        
        Returns:
            dict: Summary of fetched data
        """
        try:
            import requests
            from datetime import datetime, timedelta
            
            # Get API credentials
            api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
            if not api_key:
                raise Exception("OpenAI API key not configured")
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            org_id = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_organization_id')
            if org_id:
                headers['OpenAI-Organization'] = str(org_id)
            
            # Calculate date range (last 90 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            
            # Note: OpenAI Usage API endpoint structure may vary
            # This is a placeholder implementation - actual endpoint needs to be researched
            usage_endpoints = [
                'https://api.openai.com/v1/organization/usage/completions',
                'https://api.openai.com/v1/organization/usage/embeddings',
            ]
            
            total_records_updated = 0
            
            for endpoint in usage_endpoints:
                try:
                    # Make API call
                    params = {
                        'start_time': int(start_date.timestamp()),
                        'end_time': int(end_date.timestamp()),
                        'bucket_width': '1d',  # Daily buckets
                    }
                    
                    response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Process the response (structure depends on actual API)
                    # This is a placeholder - actual implementation needs API research
                    if 'data' in data:
                        for bucket in data['data']:
                            # Extract date and token counts
                            # Actual field names depend on API structure
                            date = datetime.fromtimestamp(bucket.get('start_time', 0)).date()
                            prompt_tokens = bucket.get('prompt_tokens', 0)
                            completion_tokens = bucket.get('completion_tokens', 0)
                            
                            # Create or update snapshot record
                            snapshot = self.env['sc.openai.usage.snapshot'].search([('date', '=', date)], limit=1)
                            if snapshot:
                                snapshot.write({
                                    'prompt_tokens': snapshot.prompt_tokens + prompt_tokens,
                                    'completion_tokens': snapshot.completion_tokens + completion_tokens,
                                    'fetch_timestamp': fields.Datetime.now(),
                                    'api_response_raw': json.dumps(bucket),
                                })
                            else:
                                self.env['sc.openai.usage.snapshot'].create({
                                    'date': date,
                                    'prompt_tokens': prompt_tokens,
                                    'completion_tokens': completion_tokens,
                                    'fetch_timestamp': fields.Datetime.now(),
                                    'api_response_raw': json.dumps(bucket),
                                })
                            
                            total_records_updated += 1
                
                except requests.exceptions.RequestException as e:
                    _logger.warning("Failed to fetch from %s: %s", endpoint, str(e))
                    continue
            
            return {
                'success': True,
                'records_updated': total_records_updated,
                'message': f"Successfully updated {total_records_updated} usage records"
            }
            
        except Exception as e:
            _logger.error("Failed to fetch usage data: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to fetch usage data: {str(e)}"
            }
