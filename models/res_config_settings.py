from odoo import api, fields, models
import requests
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # OpenAI Configuration Fields
    sc_openai_api_key = fields.Char(
        string="OpenAI API Key",
        help="Your OpenAI API key for accessing AI services",
        config_parameter='sc_marketing_automation_tool.openai_api_key',
        password=True,
    )
    
    sc_openai_organization_id = fields.Char(
        string="OpenAI Organization ID",
        help="Your OpenAI Organization ID (optional but recommended)",
        config_parameter='sc_marketing_automation_tool.openai_organization_id',
    )
    
    sc_openai_model = fields.Selection(
        selection='_get_openai_models',
        string="OpenAI Model",
        help="Select the OpenAI model to use for translations",
        config_parameter='sc_marketing_automation_tool.openai_model',
        default='gpt-4o',
    )
    
    # Content Research Agent Configuration
    sc_research_agent_model = fields.Selection(
        selection='_get_openai_models',
        string="Research Agent Model",
        help="Select the OpenAI model for the Content Research Agent",
        config_parameter='sc_marketing_automation_tool.research_agent_model',
        default='gpt-4o',
    )
    
    sc_research_agent_instructions = fields.Text(
        string="Research Agent Instructions",
        help="System instructions for the Content Research Agent",
        config_parameter='sc_marketing_automation_tool.research_agent_instructions',
        default="""You are a content research agent specialized in finding relevant, recent articles and news for content marketing.

Your task is to search the web for articles related to the given topic and return a structured list of content ideas.

For each article you find, provide:
1. The article title
2. The full URL to the article
3. The publication date (if available)
4. A concise summary highlighting the key points and why it would be valuable for content creation

Focus on:
- Recent articles (preferably within the last 6 months)
- Authoritative sources and industry publications
- Trending topics and emerging insights
- Actionable information that can inspire blog content

Return your findings as a JSON list with the specified structure.""",
    )
    
    sc_research_agent_default_query = fields.Text(
        string="Default Research Query",
        help="Default search query that will populate the research wizard",
        config_parameter='sc_marketing_automation_tool.research_agent_default_query',
        default="Find recent articles about digital marketing trends and best practices published after {today}",
    )
    
    # Content Generation Agent Configuration  
    sc_generation_agent_model = fields.Selection(
        selection='_get_openai_models',
        string="Generation Agent Model",
        help="Select the OpenAI model for the Content Generation Agent",
        config_parameter='sc_marketing_automation_tool.generation_agent_model',
        default='gpt-4o',
    )
    
    sc_generation_agent_instructions = fields.Text(
        string="Generation Agent Instructions",
        help="System instructions for the Content Generation Agent",
        config_parameter='sc_marketing_automation_tool.generation_agent_instructions',
        default="""You are a professional content writer specialized in creating engaging blog posts for business audiences.

Your task is to create a complete blog post based on the provided source content and user requirements.

Generate a comprehensive blog post with:
1. An engaging, SEO-friendly title
2. Well-structured HTML content with proper headings, paragraphs, and formatting
3. A compelling meta description for SEO
4. Relevant keywords for content optimization

Content Guidelines:
- Write in a professional yet engaging tone
- Use clear headings and subheadings (H2, H3)
- Include actionable insights and practical advice
- Aim for 800-1500 words depending on the topic
- Ensure content is original and adds value beyond the source material
- Include a strong introduction and conclusion

Return your response as a JSON object with the specified structure containing title, content, meta_description, and keywords.""",
    )
    
    @api.model
    def _get_openai_models(self):
        """Get available OpenAI models dynamically from API"""
        try:
            # Get API key from config parameters
            api_key = self.env['ir.config_parameter'].sudo().get_param(
                'sc_marketing_automation_tool.openai_api_key'
            )
            
            if not api_key:
                _logger.info("OpenAI API key not configured, using fallback models")
                return self._get_fallback_models()
            
            # Make API call to get available models
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Add organization header if available
            org_id = self.env['ir.config_parameter'].sudo().get_param(
                'sc_marketing_automation_tool.openai_organization_id'
            )
            if org_id:
                headers['OpenAI-Organization'] = str(org_id)
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = []
                
                # Filter for GPT models suitable for translation
                for model in models_data.get('data', []):
                    model_id = model.get('id', '')
                    if model_id.startswith('gpt-') and 'instruct' not in model_id.lower():
                        # Create readable name
                        display_name = model_id.replace('gpt-', 'GPT-').replace('-', ' ').title()
                        available_models.append((model_id, display_name))
                
                # Sort models with preferred ones first
                available_models.sort(key=lambda x: (
                    'gpt-4o' not in x[0],  # gpt-4o first
                    'gpt-4' not in x[0],   # then gpt-4
                    'gpt-3.5' not in x[0], # then gpt-3.5
                    x[0]                   # then alphabetical
                ))
                
                if available_models:
                    _logger.info(f"Successfully loaded {len(available_models)} OpenAI models from API")
                    return available_models
                else:
                    _logger.warning("No suitable GPT models found in API response, using fallback")
                    return self._get_fallback_models()
            
            else:
                _logger.warning(f"OpenAI API call failed with status {response.status_code}: {response.text}")
                return self._get_fallback_models()
                
        except requests.exceptions.RequestException as e:
            _logger.warning(f"Network error while fetching OpenAI models: {e}")
            return self._get_fallback_models()
        except Exception as e:
            _logger.warning(f"Unexpected error while fetching OpenAI models: {e}")
            return self._get_fallback_models()
    
    @api.model
    def _get_fallback_models(self):
        """Fallback model list when API call fails or no API key configured"""
        return [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4-turbo', 'GPT-4 Turbo'), 
            ('gpt-4', 'GPT-4'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ]
    
    def set_values(self):
        """Override to refresh model selection when API key changes"""
        # Check if API key is being updated
        old_api_key = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.openai_api_key'
        )
        
        # Call parent to save values
        result = super(ResConfigSettings, self).set_values()
        
        # If API key changed, log it for model refresh
        new_api_key = self.sc_openai_api_key
        if old_api_key != new_api_key and new_api_key:
            _logger.info("OpenAI API key updated, model list will refresh on next load")
        
        return result
