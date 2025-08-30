# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Marketing Automation Configuration
    marketing_automation_url = fields.Char(
        string='Automation Hub URL (n8n)',
        config_parameter='marketing_automation_tool.automation_url',
        help="Base URL of the n8n automation hub endpoint"
    )
    marketing_automation_token = fields.Char(
        string='Authentication Token',
        config_parameter='marketing_automation_tool.automation_token',
        password=True,
        help="Security token for authenticating requests to the automation service"
    )

    @api.model
    def get_values(self):
        """Override to retrieve configuration parameters"""
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            marketing_automation_url=ICPSudo.get_param('marketing_automation_tool.automation_url', ''),
            marketing_automation_token=ICPSudo.get_param('marketing_automation_tool.automation_token', ''),
        )
        return res

    def set_values(self):
        """Override to store configuration parameters"""
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('marketing_automation_tool.automation_url', self.marketing_automation_url or '')
        ICPSudo.set_param('marketing_automation_tool.automation_token', self.marketing_automation_token or '')
