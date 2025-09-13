from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ScOpenaiDashboard(models.TransientModel):
    _name = 'sc.openai.dashboard'
    _description = 'OpenAI Usage Dashboard'

    # Summary statistics
    total_records = fields.Integer(string="Total Records", readonly=True)
    last_30_days_tokens = fields.Integer(string="Last 30 Days Tokens", readonly=True)
    last_30_days_cost = fields.Float(string="Last 30 Days Cost", readonly=True, digits=(10, 4))
    last_7_days_tokens = fields.Integer(string="Last 7 Days Tokens", readonly=True)
    last_7_days_cost = fields.Float(string="Last 7 Days Cost", readonly=True, digits=(10, 4))
    
    # Status information
    last_fetch_date = fields.Date(string="Last Data Fetch", readonly=True)
    data_available = fields.Boolean(string="Data Available", readonly=True)

    @api.model
    def default_get(self, fields_list):
        """Load dashboard data on creation"""
        result = super().default_get(fields_list)
        
        try:
            # Get usage data from snapshot model
            snapshot_model = self.env['sc.openai.usage.snapshot']
            
            # Get summaries
            summary_30 = snapshot_model.get_usage_summary(days=30)
            summary_7 = snapshot_model.get_usage_summary(days=7)
            
            # Get last fetch date
            last_record = snapshot_model.search([], order='date desc', limit=1)
            last_fetch = last_record.date if last_record else False
            
            result.update({
                'total_records': snapshot_model.search_count([]),
                'last_30_days_tokens': summary_30.get('total_tokens', 0),
                'last_30_days_cost': summary_30.get('total_estimated_cost', 0.0),
                'last_7_days_tokens': summary_7.get('total_tokens', 0),
                'last_7_days_cost': summary_7.get('total_estimated_cost', 0.0),
                'last_fetch_date': last_fetch,
                'data_available': bool(last_record),
            })
            
        except Exception as e:
            _logger.error(f"Error loading dashboard data: {str(e)}")
            result.update({
                'total_records': 0,
                'data_available': False,
            })
        
        return result

    def action_fetch_latest_data(self):
        """Fetch latest data from OpenAI API"""
        try:
            # For now, return a placeholder
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('OpenAI API integration will be implemented in the next version.'),
                    'type': 'info',
                }
            }
        except Exception as e:
            _logger.error(f"Error fetching data: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def action_view_all_records(self):
        """Open all usage records"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('All Usage Records'),
            'res_model': 'sc.openai.usage.snapshot',
            'view_mode': 'list,form',
            'target': 'current',
            'context': {'search_default_last_30_days': 1}
        }

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        # Reload the current dashboard with fresh data
        return {
            'type': 'ir.actions.act_window',
            'name': _('OpenAI Usage Dashboard'),
            'res_model': 'sc.openai.dashboard',
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'}
        }