# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

import requests
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    """Add OpenAI configuration to general settings"""
    
    _inherit = 'res.config.settings'
    
    # OpenAI Configuration
    sc_openai_api_key = fields.Char(
        string='OpenAI API Key',
        password=True,
        config_parameter='sc_marketing_automation.openai_api_key',
        help="Your OpenAI API key for AI translation services"
    )
    
    sc_openai_organization_id = fields.Char(
        string='OpenAI Organization ID',
        config_parameter='sc_marketing_automation.openai_org_id',
        help="Optional: Your OpenAI Organization ID"
    )
    
    sc_openai_model = fields.Selection(
        selection='_get_openai_models',
        string='OpenAI Model',
        default='gpt-4o',
        config_parameter='sc_marketing_automation.openai_model',
        help="OpenAI model to use for translations"
    )
    
    def _get_openai_models(self):
        """Get available OpenAI models dynamically or return defaults"""
        # Default fallback models
        default_models = [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ]
        
        try:
            # Try to get API key from config
            api_key = self.env['ir.config_parameter'].sudo().get_param(
                'sc_marketing_automation.openai_api_key'
            )
            
            if not api_key:
                _logger.info("OpenAI API key not configured, using default model list")
                return default_models
            
            # Try to fetch models from OpenAI API
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            
            org_id = self.env['ir.config_parameter'].sudo().get_param(
                'sc_marketing_automation.openai_org_id'
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
                
                # Filter for GPT models suitable for chat/text generation
                available_models = []
                for model in models_data.get('data', []):
                    model_id = model.get('id', '')
                    if model_id.startswith('gpt-') and 'turbo' in model_id.lower():
                        available_models.append((model_id, model_id.upper()))
                
                # Sort models by name and add defaults if none found
                if available_models:
                    available_models.sort(key=lambda x: x[0])
                    return available_models
                else:
                    _logger.warning("No suitable GPT models found in OpenAI API response")
                    return default_models
            else:
                _logger.warning("Failed to fetch OpenAI models: HTTP %d", response.status_code)
                return default_models
                
        except Exception as e:
            _logger.warning("Error fetching OpenAI models: %s", str(e))
            return default_models
    
    def action_test_openai_connection(self):
        """Test OpenAI API connection with current settings"""
        self.ensure_one()
        
        if not self.sc_openai_api_key:
            raise UserError(_("Please enter an OpenAI API key before testing the connection."))
        
        try:
            headers = {
                'Authorization': f'Bearer {self.sc_openai_api_key}',
                'Content-Type': 'application/json',
            }
            
            if self.sc_openai_organization_id:
                headers['OpenAI-Organization'] = self.sc_openai_organization_id
            
            # Test with a simple models API call
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Connection Successful"),
                        'message': _("OpenAI API connection test passed successfully!"),
                        'type': 'success',
                    }
                }
            elif response.status_code == 401:
                raise UserError(_("Invalid API key. Please check your OpenAI API key."))
            elif response.status_code == 403:
                raise UserError(_("Access forbidden. Please check your API key permissions and organization ID."))
            else:
                raise UserError(_("Connection failed with HTTP status %d: %s") % (
                    response.status_code, response.text
                ))
                
        except requests.exceptions.Timeout:
            raise UserError(_("Connection timeout. Please check your internet connection."))
        except requests.exceptions.RequestException as e:
            raise UserError(_("Connection error: %s") % str(e))
        except Exception as e:
            raise UserError(_("Unexpected error: %s") % str(e))
    
    @api.model
    def get_openai_config(self):
        """Get OpenAI configuration for use in other parts of the system"""
        config = self.env['ir.config_parameter'].sudo()
        
        return {
            'api_key': config.get_param('sc_marketing_automation.openai_api_key'),
            'organization_id': config.get_param('sc_marketing_automation.openai_org_id'),
            'model': config.get_param('sc_marketing_automation.openai_model', 'gpt-4o'),
        }
