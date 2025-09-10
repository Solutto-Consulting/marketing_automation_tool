from odoo import api, fields, models

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
        """Get available OpenAI models dynamically"""
        try:
            openai_utils = self.env['openai.utils']
            return openai_utils.get_available_models()
        except Exception:
            # Fallback if utils not available
            return [
                ('gpt-4o', 'GPT-4o'),
                ('gpt-4-turbo', 'GPT-4 Turbo'),
                ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
            ]
