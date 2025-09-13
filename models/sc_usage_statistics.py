from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
from ..utils.openai_cost_utils import create_cost_analyzer_from_config, get_usage_summary

_logger = logging.getLogger(__name__)

class ScUsageStatistics(models.Model):
    _name = 'sc.usage.statistics'
    _description = 'OpenAI Usage Statistics and Cost Analysis'
    _order = 'create_date desc'

    # Period Selection
    period_type = fields.Selection([
        ('current_month', 'Current Month'),
        ('previous_month', 'Previous Month'),
        ('last_30_days', 'Last 30 Days'),
        ('last_7_days', 'Last 7 Days'),
        ('custom', 'Custom Period'),
    ], string="Period", default='current_month', required=True)
    
    custom_start_date = fields.Date(string="Start Date")
    custom_end_date = fields.Date(string="End Date")
    
    # Current Statistics
    total_cost = fields.Float(string="Total Cost", readonly=True)
    currency = fields.Char(string="Currency", readonly=True, default="USD")
    average_daily_cost = fields.Float(string="Average Daily Cost", readonly=True)
    estimated_monthly_cost = fields.Float(string="Estimated Monthly Cost", readonly=True)
    
    # Period Information
    period_start = fields.Date(string="Period Start", readonly=True)
    period_end = fields.Date(string="Period End", readonly=True)
    period_days = fields.Integer(string="Days in Period", readonly=True)
    
    # Trend Analysis
    previous_period_cost = fields.Float(string="Previous Period Cost", readonly=True)
    cost_change_percent = fields.Float(string="Cost Change %", readonly=True)
    is_cost_increasing = fields.Boolean(string="Cost Increasing", readonly=True)
    
    # Project Information
    project_id = fields.Char(string="OpenAI Project ID", readonly=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Ready to Fetch'),
        ('loading', 'Fetching Data'),
        ('loaded', 'Data Loaded'),
        ('error', 'Error'),
    ], string="State", default='draft', readonly=True)
    
    error_message = fields.Text(string="Error Message", readonly=True)
    last_updated = fields.Datetime(string="Last Updated", readonly=True)
    
    # Daily breakdown data (stored as JSON)
    daily_breakdown_json = fields.Text(string="Daily Breakdown Data", readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        """Set default values and try to load current month data"""
        result = super().default_get(fields_list)
        return result
    
    def action_refresh_data(self):
        """Fetch fresh usage data from OpenAI API"""
        self.ensure_one()
        
        try:
            self.write({'state': 'loading', 'error_message': False})
            
            # Get cost analyzer
            analyzer = create_cost_analyzer_from_config(self.env)
            
            # Fetch data based on period type
            if self.period_type == 'current_month':
                response = analyzer.get_current_month_costs()
            elif self.period_type == 'previous_month':
                response = analyzer.get_previous_month_costs()
            elif self.period_type == 'last_30_days':
                response = analyzer.get_costs_for_period(30)
            elif self.period_type == 'last_7_days':
                response = analyzer.get_costs_for_period(7)
            elif self.period_type == 'custom':
                if not self.custom_start_date or not self.custom_end_date:
                    raise UserError(_("Please specify both start and end dates for custom period."))
                
                # Convert dates to timestamps and get data
                from datetime import datetime
                start_datetime = datetime.combine(self.custom_start_date, datetime.min.time())
                end_datetime = datetime.combine(self.custom_end_date, datetime.max.time())
                
                days_diff = (self.custom_end_date - self.custom_start_date).days + 1
                response = analyzer.get_costs_for_period(days_diff)
            else:
                raise UserError(_("Invalid period type selected."))
            
            if response['success']:
                self._update_statistics_from_response(response)
                self.write({
                    'state': 'loaded',
                    'last_updated': fields.Datetime.now()
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Usage statistics updated successfully.'),
                        'type': 'success',
                    }
                }
            else:
                self.write({
                    'state': 'error',
                    'error_message': response.get('error', 'Unknown error occurred')
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': response.get('error', 'Failed to fetch usage data'),
                        'type': 'danger',
                    }
                }
                
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Error refreshing usage statistics: {error_msg}")
            self.write({
                'state': 'error',
                'error_message': error_msg
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': error_msg,
                    'type': 'danger',
                }
            }
    
    def _update_statistics_from_response(self, response):
        """Update statistics fields from API response"""
        summary = response.get('summary', {})
        period = response.get('period', {})
        
        # Parse dates
        from datetime import datetime
        try:
            period_start = datetime.strptime(period.get('start', ''), '%Y-%m-%d').date()
            period_end = datetime.strptime(period.get('end', ''), '%Y-%m-%d').date()
        except:
            period_start = False
            period_end = False
        
        # Store daily breakdown as JSON (serialize datetime objects to strings)
        import json
        daily_breakdown = response.get('daily_breakdown', [])
        
        # Convert datetime objects to strings for JSON serialization
        serializable_breakdown = []
        for day_data in daily_breakdown:
            clean_day_data = {}
            for key, value in day_data.items():
                if key in ['start_time', 'end_time'] and hasattr(value, 'strftime'):
                    # Convert datetime objects to ISO format strings
                    clean_day_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # Keep other values as-is
                    clean_day_data[key] = value
            serializable_breakdown.append(clean_day_data)
        
        daily_breakdown_json = json.dumps(serializable_breakdown)
        
        # Update fields
        self.write({
            'total_cost': summary.get('total_amount', 0.0),
            'currency': summary.get('currency', 'USD'),
            'average_daily_cost': summary.get('average_daily_cost', 0.0),
            'estimated_monthly_cost': summary.get('estimated_monthly_cost', 0.0),
            'period_start': period_start,
            'period_end': period_end,
            'period_days': period.get('days', 0),
            'project_id': response.get('project_id'),
            'daily_breakdown_json': daily_breakdown_json
        })
    
    @api.onchange('period_type')
    def _onchange_period_type(self):
        """Reset custom date fields when period type changes"""
        if self.period_type != 'custom':
            self.custom_start_date = False
            self.custom_end_date = False
    
    def action_view_daily_breakdown(self):
        """Open a detailed view of daily breakdown data"""
        self.ensure_one()
        
        if not self.daily_breakdown_json:
            raise UserError(_("No daily breakdown data available. Please refresh the data first."))
        
        # Parse the daily breakdown data and create temporary records
        import json
        from datetime import datetime
        
        try:
            daily_data = json.loads(self.daily_breakdown_json)
            
            # Clear any existing daily records for this statistics record
            existing_daily = self.env['sc.usage.statistics.daily'].search([
                ('parent_statistics_id', '=', self.id)
            ])
            if existing_daily:
                existing_daily.unlink()
            
            # Create daily records
            daily_records = []
            for day_data in daily_data:
                try:
                    date_obj = datetime.strptime(day_data.get('date', ''), '%Y-%m-%d').date()
                except:
                    date_obj = fields.Date.today()
                
                daily_record = self.env['sc.usage.statistics.daily'].create({
                    'parent_statistics_id': self.id,
                    'date': date_obj,
                    'amount': day_data.get('amount', 0.0),
                    'currency': day_data.get('currency', 'USD').upper()
                })
                daily_records.append(daily_record.id)
            
            _logger.info(f"Created {len(daily_records)} daily breakdown records for statistics {self.id}")
            
            # Return action to show the created daily breakdown records
            return {
                'type': 'ir.actions.act_window',
                'name': _('Daily Cost Breakdown'),
                'res_model': 'sc.usage.statistics.daily',
                'view_mode': 'list',
                'target': 'new',
                'domain': [('parent_statistics_id', '=', self.id)],
                'context': {'default_parent_statistics_id': self.id}
            }
            
        except Exception as e:
            _logger.error(f"Error creating daily breakdown view: {str(e)}")
            raise UserError(_("Error processing daily breakdown data: %s") % str(e))
    
    @api.model
    def get_quick_summary(self):
        """Get a quick summary for dashboard display"""
        try:
            summary_data = get_usage_summary(self.env)
            
            if summary_data['success']:
                current_month = summary_data.get('current_month', {}).get('summary', {})
                trends = summary_data.get('trends', {})
                
                return {
                    'success': True,
                    'current_month_cost': current_month.get('total_amount', 0.0),
                    'currency': current_month.get('currency', 'USD'),
                    'estimated_monthly': current_month.get('estimated_monthly_cost', 0.0),
                    'trend_percentage': trends.get('month_over_month_change', 0.0),
                    'is_increasing': trends.get('is_increasing', False)
                }
            else:
                return {
                    'success': False,
                    'error': summary_data.get('error', 'Unknown error')
                }
                
        except Exception as e:
            _logger.error(f"Error getting quick summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class ScUsageStatisticsDaily(models.Model):
    _name = 'sc.usage.statistics.daily'
    _description = 'Daily Usage Statistics Breakdown'
    _order = 'date desc'

    parent_statistics_id = fields.Many2one('sc.usage.statistics', string="Parent Statistics", required=True, ondelete='cascade')
    date = fields.Date(string="Date", required=True)
    amount = fields.Float(string="Cost", required=True)
    currency = fields.Char(string="Currency", default="USD")