from odoo import api, fields, models, _
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
    
    # Administrative Configuration for Usage Statistics
    sc_openai_admin_key = fields.Char(
        string="OpenAI Admin Key",
        help="OpenAI admin/service key with organization:read scope for usage statistics",
        config_parameter='sc_marketing_automation_tool.openai_admin_key',
    )
    
    sc_openai_project_id = fields.Char(
        string="OpenAI Project ID",
        help="OpenAI project ID for usage tracking and cost analysis",
        config_parameter='sc_marketing_automation_tool.openai_project_id',
    )
    
    # Image Generation Configuration (gpt-image-1)
    sc_image_generation_model = fields.Selection(
        selection='_get_image_models',
        string="Image Generation Model",
        help="Image generation model (gpt-image-1 via Responses API)",
        config_parameter='sc_marketing_automation_tool.image_generation_model',
        default='gpt-image-1',
    )
    
    sc_image_default_size = fields.Selection(
        selection=[
            ('1024x1024', '1024x1024 (Square)'),
            ('1024x1792', '1024x1792 (Portrait)'),
            ('1792x1024', '1792x1024 (Landscape)'),
            ('1536x1024', '1536x1024 (Widescreen)'),
            ('1024x1536', '1024x1536 (Tall)'),
        ],
        string="Default Image Size",
        help="Default size for generated images (gpt-image-1)",
        config_parameter='sc_marketing_automation_tool.image_default_size',
        default='1024x1024',
    )
    
    sc_image_default_quality = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('high', 'High (HD quality)'),
        ],
        string="Default Image Quality",
        help="Default quality for generated images (gpt-image-1)",
        config_parameter='sc_marketing_automation_tool.image_default_quality',
        default='standard',
    )
    
    sc_image_default_output_format = fields.Selection(
        selection=[
            ('png', 'PNG'),
            ('jpeg', 'JPEG'),
            ('webp', 'WebP'),
        ],
        string="Default Output Format",
        help="Default output format for generated images",
        config_parameter='sc_marketing_automation_tool.image_default_output_format',
        default='png',
    )
    
    sc_image_default_background = fields.Selection(
        selection=[
            ('opaque', 'Opaque'),
            ('transparent', 'Transparent'),
        ],
        string="Default Background",
        help="Default background type for generated images",
        config_parameter='sc_marketing_automation_tool.image_default_background',
        default='opaque',
    )
    
    sc_image_default_moderation = fields.Selection(
        selection=[
            ('auto', 'Auto'),
            ('strict', 'Strict'),
            ('relaxed', 'Relaxed'),
        ],
        string="Default Moderation Level",
        help="Default content moderation level for image generation",
        config_parameter='sc_marketing_automation_tool.image_default_moderation',
        default='auto',
    )
    
    # Content Research Agent Configuration
    sc_research_agent_model = fields.Selection(
        selection='_get_openai_models',
        string="Research Agent Model",
        help="Select the OpenAI model for the Content Research Agent",
        config_parameter='sc_marketing_automation_tool.research_agent_model',
        default='gpt-4o',
    )
    
    sc_enable_agent_config = fields.Boolean(
        string="Enable AI Agent Configurations",
        help="Enable advanced AI agent configuration management",
        config_parameter='sc_marketing_automation_tool.enable_agent_config',
        default=True,
    )
    
    # Content Generation Agent Configuration  
    sc_generation_agent_model = fields.Selection(
        selection='_get_openai_models',
        string="Generation Agent Model",
        help="Select the OpenAI model for the Content Generation Agent",
        config_parameter='sc_marketing_automation_tool.generation_agent_model',
        default='gpt-4o',
    )
    
    @api.model
    def _get_openai_models(self):
        """Get available OpenAI models from centralized configuration"""
        try:
            openai_models = self.env['sc.openai.models']
            return openai_models.get_text_models()
        except Exception as e:
            _logger.warning(f"Error loading centralized models, using fallback: {e}")
            return self._get_fallback_models()
    
    @api.model
    def _get_fallback_models(self):
        """Fallback model list when centralized config fails"""
        return [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4o-mini', 'GPT-4o Mini'),
        ]
    
    @api.model
    def _get_image_models(self):
        """Get available image generation models from centralized configuration"""
        try:
            openai_models = self.env['sc.openai.models']
            return openai_models.get_image_models()
        except Exception as e:
            _logger.warning(f"Error loading centralized image models, using fallback: {e}")
            return [('gpt-image-1', 'GPT-Image-1 (Responses API)')]
    
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
    
    def action_view_usage_statistics(self):
        """Open the usage statistics view"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('OpenAI Usage Statistics'),
            'res_model': 'sc.usage.statistics',
            'view_mode': 'list,form',
            'target': 'current',
            'context': {}
        }
