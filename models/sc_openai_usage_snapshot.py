from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ScOpenaiUsageSnapshot(models.Model):
    _name = 'sc.openai.usage.snapshot'
    _description = 'OpenAI API Usage Daily Snapshots'
    _order = 'date desc'
    _rec_name = 'date'

    date = fields.Date(
        string="Date",
        required=True,
        unique=True,
        help="The day of the usage data"
    )
    
    prompt_tokens = fields.Integer(
        string="Prompt Tokens",
        default=0,
        help="Total prompt tokens consumed on this date"
    )
    
    completion_tokens = fields.Integer(
        string="Completion Tokens", 
        default=0,
        help="Total completion tokens consumed on this date"
    )
    
    total_tokens = fields.Integer(
        string="Total Tokens",
        compute='_compute_total_tokens',
        store=True,
        help="Sum of prompt and completion tokens"
    )
    
    # Cost estimation fields (approximate)
    estimated_cost = fields.Float(
        string="Estimated Cost (USD)",
        compute='_compute_estimated_cost',
        store=True,
        digits=(10, 4),
        help="Estimated cost based on token usage and model pricing"
    )
    
    # Additional metadata
    fetch_timestamp = fields.Datetime(
        string="Fetched At",
        default=fields.Datetime.now,
        help="When this data was fetched from OpenAI API"
    )
    
    api_response_raw = fields.Text(
        string="Raw API Response",
        help="Raw response from OpenAI Usage API for debugging"
    )
    
    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_total_tokens(self):
        """Compute total tokens as sum of prompt and completion tokens"""
        for record in self:
            record.total_tokens = record.prompt_tokens + record.completion_tokens
    
    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_estimated_cost(self):
        """Compute estimated cost based on token usage"""
        for record in self:
            # Rough cost estimation based on GPT-4 pricing
            # These rates should be configurable in future versions
            prompt_cost_per_1k = 0.03  # $0.03 per 1K prompt tokens
            completion_cost_per_1k = 0.06  # $0.06 per 1K completion tokens
            
            prompt_cost = (record.prompt_tokens / 1000.0) * prompt_cost_per_1k
            completion_cost = (record.completion_tokens / 1000.0) * completion_cost_per_1k
            
            record.estimated_cost = prompt_cost + completion_cost
    
    @api.constrains('prompt_tokens', 'completion_tokens')
    def _check_token_values(self):
        """Validate token values are non-negative"""
        for record in self:
            if record.prompt_tokens < 0:
                raise ValidationError(_("Prompt tokens cannot be negative"))
            if record.completion_tokens < 0:
                raise ValidationError(_("Completion tokens cannot be negative"))
    
    @api.model
    def get_usage_summary(self, days=30):
        """Get usage summary for the last N days"""
        from_date = fields.Date.subtract(fields.Date.today(), days=days)
        
        records = self.search([
            ('date', '>=', from_date)
        ], order='date desc')
        
        if not records:
            return {
                'total_tokens': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_estimated_cost': 0.0,
                'days_with_data': 0,
                'avg_daily_tokens': 0,
            }
        
        total_tokens = sum(records.mapped('total_tokens'))
        total_prompt = sum(records.mapped('prompt_tokens'))
        total_completion = sum(records.mapped('completion_tokens'))
        total_cost = sum(records.mapped('estimated_cost'))
        days_with_data = len(records)
        avg_daily = total_tokens / days_with_data if days_with_data > 0 else 0
        
        return {
            'total_tokens': total_tokens,
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'total_estimated_cost': total_cost,
            'days_with_data': days_with_data,
            'avg_daily_tokens': avg_daily,
        }
    
    @api.model
    def fetch_usage_data_from_api(self):
        """Fetch usage data from OpenAI API and create/update records"""
        # This method will be implemented in the OpenAI utils module
        # to handle the actual API calls and data processing
        openai_utils = self.env['openai.utils']
        return openai_utils.fetch_and_store_usage_data()
    
    def action_refetch_data(self):
        """Manually refetch data for this specific date"""
        self.ensure_one()
        openai_utils = self.env['openai.utils']
        return openai_utils.fetch_usage_data_for_date(self.date)
