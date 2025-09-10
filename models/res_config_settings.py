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
