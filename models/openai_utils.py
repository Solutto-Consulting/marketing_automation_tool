import asyncio
import os
import json
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class OpenAIUtils(models.AbstractModel):
    """Utility class for OpenAI integration using openai-agents SDK with monitoring"""
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
            
            # Execute research with monitoring
            result = await self._monitored_ai_request(
                agent, 
                prompt, 
                model_name,
                related_model='sc.content.idea.task',
                related_record_name=f'Content Research: {search_query[:50]}'
            )
            
            # Parse the JSON response
            try:
                response_text = result.final_output.strip()
                _logger.info("Raw agent response: %s", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                
                # Handle markdown JSON blocks
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Handle markdown JSON blocks without language specification
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Clean up any extra whitespace
                response_text = response_text.strip()
                
                # Try to extract JSON from mixed content
                if not response_text.startswith('[') and not response_text.startswith('{'):
                    # Look for JSON array in the response
                    import re
                    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                    if json_match:
                        response_text = json_match.group(0)
                    else:
                        raise ValueError("No valid JSON array found in response")
                
                _logger.info("Cleaned response for parsing: %s", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                
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
    def research_content_ideas(self, model_name, system_instructions, search_query, num_ideas=5):
        """
        Synchronous wrapper for content research
        
        Args:
            model_name (str): The OpenAI model to use
            system_instructions (str): Instructions for the research agent
            search_query (str): The search query for finding content ideas
            num_ideas (int): Number of ideas to generate
            
        Returns:
            list: List of content ideas with structure [{'name': str, 'url': str, 'publish_date': str, 'summary': str}]
        """
        try:
            # Get API configuration from Odoo settings
            api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
            org_id = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_organization_id')
            
            if not api_key:
                raise Exception("OpenAI API key not configured. Please configure it in Settings > General Settings > AI Marketing Tools.")
            
            # Set environment variables for OpenAI Agents SDK
            os.environ['OPENAI_API_KEY'] = api_key
            if org_id:
                os.environ['OPENAI_ORGANIZATION'] = org_id
            
            # Run the async method synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.perform_content_research(model_name, system_instructions, search_query, num_ideas)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            _logger.error("Content research synchronous wrapper failed: %s", str(e))
            raise

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
            
            # Execute content generation with monitoring
            result = await self._monitored_ai_request(
                agent, 
                prompt,
                model_name,
                related_model='sc.content.generation.task',
                related_record_name=f'Content Generation: {content_idea.get("name", "Custom Content")[:50]}'
            )
            
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

    @api.model
    def generate_content(self, model_name, system_instructions, content_source, user_prompt=""):
        """
        Synchronous wrapper for content generation
        
        Args:
            model_name (str): The OpenAI model to use
            system_instructions (str): Instructions for the generation agent
            content_source (dict): Content source with name, url, summary fields
            user_prompt (str): Additional user instructions
            
        Returns:
            dict: Generated content with structure {'title': str, 'content': str, 'meta_description': str, 'keywords': str}
        """
        try:
            # Get API configuration from Odoo settings
            api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
            org_id = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_organization_id')
            
            if not api_key:
                raise Exception("OpenAI API key not configured in settings")
            
            # Configure environment variables for agents SDK
            import os
            os.environ['OPENAI_API_KEY'] = str(api_key)
            if org_id:
                os.environ['OPENAI_ORGANIZATION'] = str(org_id)
            
            # Run the async function synchronously
            import asyncio
            
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, we need to run in a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self.perform_content_generation(model_name, system_instructions, content_source, user_prompt)
                        )
                        return future.result()
                else:
                    return loop.run_until_complete(
                        self.perform_content_generation(model_name, system_instructions, content_source, user_prompt)
                    )
            except RuntimeError:
                # No event loop in current thread, create new one
                return asyncio.run(
                    self.perform_content_generation(model_name, system_instructions, content_source, user_prompt)
                )
                
        except Exception as e:
            _logger.error("Content generation failed: %s", str(e))
            raise Exception(f"Content generation failed: {str(e)}")

    # Monitoring Methods
    @api.model
    def _setup_openai_monitoring(self):
        """Setup OpenAI monitoring if not already configured"""
        try:
            # Import monitoring logger
            from . import openai_request_logger
            
            # Initialize monitoring
            openai_request_logger.setup_monitoring()
            
        except ImportError:
            _logger.warning("OpenAI request logger not available")
        except Exception as e:
            _logger.warning("Failed to setup OpenAI monitoring: %s", str(e))

    @api.model
    async def _monitored_ai_request(self, agent, prompt, model_name, related_model=None, related_record_id=None, related_record_name=None):
        """Execute AI request with monitoring and logging"""
        import time
        import tiktoken
        
        start_time = time.time()
        request_data = {
            'model': model_name,
            'prompt': prompt,
            'related_model': related_model,
            'related_record_id': related_record_id,
            'related_record_name': related_record_name,
            'start_time': start_time
        }
        
        try:
            # Import Runner for execution
            from agents import Runner
            
            # Execute the agent request
            result = await Runner.run(agent, prompt)
            
            # Calculate metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            # Count tokens using tiktoken
            try:
                encoding = tiktoken.encoding_for_model(model_name)
                input_tokens = len(encoding.encode(prompt))
                output_tokens = len(encoding.encode(result.final_output))
            except Exception:
                # Fallback token counting
                input_tokens = len(prompt.split()) * 1.3  # Rough estimate
                output_tokens = len(result.final_output.split()) * 1.3
            
            # Log successful request
            self._log_openai_request(
                model=model_name,
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                total_tokens=int(input_tokens + output_tokens),
                response_time_ms=int(response_time * 1000),
                success=True,
                operation_type='generation',  # Default to generation for content creation
                error_message=None,
                related_model=related_model,
                related_record_id=related_record_id,
                related_record_name=related_record_name
            )
            
            return result
            
        except Exception as e:
            # Log failed request
            end_time = time.time()
            response_time = end_time - start_time
            
            self._log_openai_request(
                model=model_name,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                response_time_ms=int(response_time * 1000),
                success=False,
                operation_type='generation',  # Default to generation for content creation
                error_message=str(e),
                related_model=related_model,
                related_record_id=related_record_id,
                related_record_name=related_record_name
            )
            
            raise

    @api.model
    def _log_openai_request(self, model, input_tokens, output_tokens, total_tokens, 
                           response_time_ms, success, operation_type='generation', error_message=None,
                           related_model=None, related_record_id=None, related_record_name=None):
        """Log OpenAI request to database"""
        try:
            # Calculate cost estimation (rough pricing for common models)
            cost_per_1k_input = 0.03 if 'gpt-4' in model else 0.001  # USD
            cost_per_1k_output = 0.06 if 'gpt-4' in model else 0.002  # USD
            
            estimated_cost = (
                (input_tokens / 1000) * cost_per_1k_input +
                (output_tokens / 1000) * cost_per_1k_output
            )
            
            # Create request log record
            self.env['sc.openai.request.log'].sudo().create({
                'model_used': model,
                'operation_type': operation_type,
                'prompt_tokens': input_tokens,
                'completion_tokens': output_tokens,
                'total_tokens': total_tokens,
                'estimated_cost': estimated_cost,
                'response_time_ms': response_time_ms,
                'status': 'success' if success else 'error',
                'error_message': error_message,
                'related_model': related_model,
                'related_record_id': related_record_id,
                'related_record_name': related_record_name,
            })
            
            # Update model statistics
            self._update_model_statistics(model, input_tokens, output_tokens, estimated_cost, success)
            
        except Exception as e:
            _logger.warning("Failed to log OpenAI request: %s", str(e))

    @api.model 
    def _update_model_statistics(self, model, input_tokens, output_tokens, cost, success):
        """Update aggregated model statistics"""
        try:
            today = fields.Date.today()
            
            # Find or create statistics record for today
            stats = self.env['sc.openai.model.statistics'].sudo().search([
                ('model_name', '=', model),
                ('date', '=', today)
            ], limit=1)
            
            if not stats:
                stats = self.env['sc.openai.model.statistics'].sudo().create({
                    'model_name': model,
                    'date': today,
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_prompt_tokens': 0,
                    'total_completion_tokens': 0,
                    'total_cost': 0.0,
                    'avg_response_time': 0.0
                })
            
            # Update statistics
            new_total_requests = stats.total_requests + 1
            new_successful = stats.successful_requests + (1 if success else 0)
            new_failed = stats.failed_requests + (0 if success else 1)
            
            stats.write({
                'total_requests': new_total_requests,
                'successful_requests': new_successful,
                'failed_requests': new_failed,
                'total_prompt_tokens': stats.total_prompt_tokens + input_tokens,
                'total_completion_tokens': stats.total_completion_tokens + output_tokens,
                'total_cost': stats.total_cost + cost,
            })
            
        except Exception as e:
            _logger.warning("Failed to update model statistics: %s", str(e))
