from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, timedelta, date

_logger = logging.getLogger(__name__)

class ScOpenaiModelStatistics(models.Model):
    """Aggregated OpenAI usage statistics by model and time period"""
    _name = 'sc.openai.model.statistics'
    _description = 'OpenAI Model Usage Statistics'
    _order = 'date desc, model_name'
    _rec_name = 'display_name'

    # Period and Model Identification
    date = fields.Date(
        string='Date', 
        required=True, 
        index=True,
        default=fields.Date.today,
        help="Date for this statistics period"
    )
    model_name = fields.Selection(
        selection='_get_model_selection',
        string='Model', 
        required=True, 
        index=True,
        help="OpenAI model for these statistics"
    )
    
    # Aggregated Request Metrics
    total_requests = fields.Integer(
        string='Total Requests',
        default=0,
        help="Total number of API requests for this model on this date"
    )
    successful_requests = fields.Integer(
        string='Successful Requests',
        default=0,
        help="Number of successful API requests"
    )
    failed_requests = fields.Integer(
        string='Failed Requests',
        default=0,
        help="Number of failed API requests"
    )
    
    # Token Usage Metrics
    total_prompt_tokens = fields.Integer(
        string='Total Input Tokens',
        default=0,
        help="Total tokens used for prompts/input"
    )
    total_completion_tokens = fields.Integer(
        string='Total Output Tokens',
        default=0,
        help="Total tokens used for completions/output"
    )
    total_tokens = fields.Integer(
        string='Total Tokens',
        default=0,
        help="Total tokens used (input + output)"
    )
    
    # Cost Metrics
    total_cost = fields.Float(
        string='Total Cost',
        digits=(10, 4),
        default=0.0,
        help="Total cost in USD for this model on this date"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.USD'),
        help="Currency for cost calculations"
    )
    avg_cost_per_request = fields.Float(
        string='Avg Cost per Request',
        compute='_compute_averages',
        store=True,
        digits=(10, 4),
        help="Average cost per request"
    )
    avg_cost_per_token = fields.Float(
        string='Avg Cost per Token',
        compute='_compute_averages',
        store=True,
        digits=(10, 6),
        help="Average cost per token"
    )
    
    # Performance Metrics
    avg_response_time = fields.Float(
        string='Avg Response Time (ms)',
        digits=(8, 2),
        help="Average response time in milliseconds"
    )
    min_response_time = fields.Integer(
        string='Min Response Time (ms)',
        help="Fastest response time recorded"
    )
    max_response_time = fields.Integer(
        string='Max Response Time (ms)',
        help="Slowest response time recorded"
    )
    
    # Success Rate
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True,
        digits=(5, 2),
        help="Percentage of successful requests"
    )
    
    # Operation Type Breakdown (JSON field for detailed breakdown)
    operation_breakdown = fields.Text(
        string='Operation Breakdown',
        help="JSON breakdown of requests by operation type"
    )
    
    # Company Information
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed display fields for form view
    avg_prompt_tokens_display = fields.Char(
        string='Avg Input Tokens',
        compute='_compute_display_fields',
        help="Average prompt tokens per request"
    )
    avg_completion_tokens_display = fields.Char(
        string='Avg Output Tokens', 
        compute='_compute_display_fields',
        help="Average completion tokens per request"
    )
    tokens_per_second_display = fields.Char(
        string='Tokens per Second',
        compute='_compute_display_fields',
        help="Processing speed in tokens per second"
    )
    cost_per_1k_tokens_display = fields.Char(
        string='Cost per 1K Tokens',
        compute='_compute_display_fields',
        help="Cost efficiency per 1000 tokens"
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.model
    def _get_model_selection(self):
        """Get model selection from centralized configuration"""
        openai_models = self.env['sc.openai.models']
        return openai_models.get_all_models()

    @api.depends('model_name', 'date')
    def _compute_display_name(self):
        """Generate display name for the record"""
        for record in self:
            if record.model_name and record.date:
                record.display_name = f"{record.model_name} - {record.date}"
            else:
                record.display_name = "OpenAI Model Statistics"

    @api.depends('successful_requests', 'total_requests')
    def _compute_success_rate(self):
        """Calculate success rate percentage"""
        for record in self:
            if record.total_requests > 0:
                record.success_rate = (record.successful_requests / record.total_requests) * 100
            else:
                record.success_rate = 0.0

    @api.depends('total_requests', 'total_cost', 'total_tokens')
    def _compute_averages(self):
        """Calculate average costs"""
        for record in self:
            # Average cost per request
            if record.total_requests > 0:
                record.avg_cost_per_request = record.total_cost / record.total_requests
            else:
                record.avg_cost_per_request = 0.0
            
            # Average cost per token
            if record.total_tokens > 0:
                record.avg_cost_per_token = record.total_cost / record.total_tokens
            else:
                record.avg_cost_per_token = 0.0

    @api.depends('total_requests', 'total_prompt_tokens', 'total_completion_tokens', 
                 'total_tokens', 'avg_response_time', 'total_cost')
    def _compute_display_fields(self):
        """Calculate display values for form view"""
        for record in self:
            # Average prompt tokens per request
            if record.total_requests > 0:
                record.avg_prompt_tokens_display = str(int(record.total_prompt_tokens / record.total_requests))
            else:
                record.avg_prompt_tokens_display = "0"
            
            # Average completion tokens per request  
            if record.total_requests > 0:
                record.avg_completion_tokens_display = str(int(record.total_completion_tokens / record.total_requests))
            else:
                record.avg_completion_tokens_display = "0"
            
            # Tokens per second calculation
            if record.avg_response_time > 0 and record.total_requests > 0:
                tokens_per_second = round((record.total_tokens / record.total_requests) / (record.avg_response_time / 1000), 2)
                record.tokens_per_second_display = str(tokens_per_second)
            else:
                record.tokens_per_second_display = "N/A"
            
            # Cost per 1K tokens
            if record.total_tokens > 0:
                cost_per_1k = round((record.total_cost / record.total_tokens) * 1000, 4)
                record.cost_per_1k_tokens_display = f"${cost_per_1k}"
            else:
                record.cost_per_1k_tokens_display = "N/A"

    @api.model
    def generate_statistics(self, date_from=None, date_to=None):
        """Generate aggregated statistics from request logs"""
        if date_from is None:
            date_from = fields.Date.today()
        if date_to is None:
            date_to = date_from
        
        request_log_model = self.env['sc.openai.request.log']
        
        current_date = date_from
        generated_count = 0
        
        while current_date <= date_to:
            # Get unique models for this date
            logs_domain = [
                ('timestamp', '>=', current_date),
                ('timestamp', '<', current_date + timedelta(days=1)),
            ]
            
            # Group by model
            models_used = request_log_model.search(logs_domain).mapped('model_used')
            unique_models = list(set(models_used))
            
            for model_name in unique_models:
                if not model_name:
                    continue
                    
                # Check if statistics already exist
                existing = self.search([
                    ('date', '=', current_date),
                    ('model_name', '=', model_name),
                ])
                
                if existing:
                    continue
                
                # Get logs for this model and date
                model_logs = request_log_model.search(logs_domain + [('model_used', '=', model_name)])
                
                if not model_logs:
                    continue
                
                # Calculate aggregated metrics
                total_requests = len(model_logs)
                successful_requests = len(model_logs.filtered(lambda l: l.status == 'success'))
                failed_requests = total_requests - successful_requests
                
                total_prompt_tokens = sum(model_logs.mapped('prompt_tokens'))
                total_completion_tokens = sum(model_logs.mapped('completion_tokens'))
                total_tokens = sum(model_logs.mapped('total_tokens'))
                total_cost = sum(model_logs.mapped('cost_usd'))
                
                # Calculate response time metrics
                response_times = [log.response_time_ms for log in model_logs if log.response_time_ms > 0]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                min_response_time = min(response_times) if response_times else 0
                max_response_time = max(response_times) if response_times else 0
                
                # Create statistics record
                self.create({
                    'date': current_date,
                    'model_name': model_name,
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'total_prompt_tokens': total_prompt_tokens,
                    'total_completion_tokens': total_completion_tokens,
                    'total_tokens': total_tokens,
                    'total_cost': total_cost,
                    'avg_response_time': avg_response_time,
                    'min_response_time': min_response_time,
                    'max_response_time': max_response_time,
                })
                
                generated_count += 1
            
            current_date += timedelta(days=1)
        
        if generated_count > 0:
            _logger.info(f"Generated statistics for {generated_count} missing days")
        
        return generated_count
    
    def action_view_request_logs(self):
        """Open request logs for this model and date"""
        self.ensure_one()
        
        domain = [
            ('model_used', '=', self.model_name),
            ('timestamp', '>=', self.date),
            ('timestamp', '<', self.date + timedelta(days=1)),
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Logs - %s (%s)') % (self.model_name, self.date),
            'res_model': 'sc.openai.request.log',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': domain,
            'context': {
                'search_default_group_by_status': 1,
            }
        }

    def update_daily_statistics(self):
        """Update statistics for today for all models"""
        today = fields.Date.today()
        generated_count = self.generate_statistics(date_from=today, date_to=today)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Statistics Updated'),
                'message': _('Updated statistics for %d models today') % generated_count,
                'type': 'success',
                'sticky': False,
            }
        }

    def generate_missing_statistics(self):
        """Generate statistics for missing days (last 30 days)"""
        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=30)
        
        generated_count = self.generate_statistics(date_from=start_date, date_to=end_date)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Missing Statistics Generated'),
                'message': _('Generated statistics for %d missing days') % generated_count,
                'type': 'success',
                'sticky': False,
            }
        }