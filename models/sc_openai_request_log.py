from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import json
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class ScOpenaiRequestLog(models.Model):
    """Individual OpenAI Request Logging for detailed tracking and analysis"""
    _name = 'sc.openai.request.log'
    _description = 'OpenAI Individual Request Log'
    _order = 'timestamp desc'
    _rec_name = 'display_name'

    # Identification and Timestamp
    timestamp = fields.Datetime(
        string='Request Time', 
        default=fields.Datetime.now, 
        required=True, 
        index=True,
        help="Exact timestamp when the OpenAI request was made"
    )
    request_id = fields.Char(
        string='Request ID', 
        index=True,
        help="OpenAI request identifier for debugging purposes"
    )
    
    # Model and Operation Details
    model_used = fields.Selection(
        selection='_get_model_selection',
        string='OpenAI Model', 
        required=True, 
        index=True,
        help="OpenAI model used for this request"
    )
    
    operation_type = fields.Selection([
        ('translation', 'Content Translation'),
        ('generation', 'Content Generation'),
        ('image_generation', 'Image Generation'),
        ('analysis', 'Content Analysis'),
        ('research', 'Web Research'),
        ('other', 'Other Operation'),
    ], string='Operation Type', required=True, index=True)
    
    # Token Usage Metrics
    prompt_tokens = fields.Integer(
        string='Input Tokens', 
        help="Number of tokens in the input prompt"
    )
    completion_tokens = fields.Integer(
        string='Output Tokens', 
        help="Number of tokens in the AI response"
    )
    total_tokens = fields.Integer(
        string='Total Tokens', 
        compute='_compute_total_tokens', 
        store=True,
        help="Sum of input and output tokens"
    )
    
    # Performance and Cost Metrics
    response_time_ms = fields.Integer(
        string='Response Time (ms)', 
        help="Time taken for the OpenAI API to respond"
    )
    estimated_cost = fields.Monetary(
        string='Estimated Cost', 
        currency_field='currency_id',
        help="Estimated cost based on token usage and model pricing"
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self._get_default_currency(),
        required=True
    )
    
    # Request Status
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'), 
        ('timeout', 'Timeout'),
        ('rate_limited', 'Rate Limited'),
    ], string='Status', default='success', required=True)
    
    error_message = fields.Text(
        string='Error Details',
        help="Error message if the request failed"
    )
    
    # Related Record Information
    related_model = fields.Char(
        string='Related Model',
        help="Odoo model that triggered this request (e.g., 'blog.post')"
    )
    related_record_id = fields.Integer(
        string='Related Record ID',
        help="ID of the Odoo record that triggered this request"
    )
    related_record_name = fields.Char(
        string='Related Record',
        help="Name of the related record for easy identification"
    )
    
    # Additional Context
    user_id = fields.Many2one(
        'res.users', 
        string='User',
        default=lambda self: self.env.user,
        help="User who initiated the request"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    # Performance metrics
    cost_per_token = fields.Float(
        string='Cost per Token',
        compute='_compute_cost_per_token',
        digits=(12, 8),
        help="Average cost per token for this request"
    )
    
    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_total_tokens(self):
        """Calculate total tokens from input and output"""
        for record in self:
            record.total_tokens = (record.prompt_tokens or 0) + (record.completion_tokens or 0)
    
    @api.depends('model_used', 'operation_type', 'timestamp')
    def _compute_display_name(self):
        """Generate a user-friendly display name"""
        for record in self:
            if record.timestamp:
                time_str = record.timestamp.strftime('%Y-%m-%d %H:%M')
                record.display_name = f"{record.model_used or 'Unknown'} - {record.operation_type or 'Unknown'} ({time_str})"
            else:
                record.display_name = f"{record.model_used or 'Unknown'} - {record.operation_type or 'Unknown'}"
    
    @api.depends('estimated_cost', 'total_tokens')
    def _compute_cost_per_token(self):
        """Calculate cost per token"""
        for record in self:
            if record.total_tokens and record.estimated_cost:
                record.cost_per_token = record.estimated_cost / record.total_tokens
            else:
                record.cost_per_token = 0.0
    
    @api.model
    def _get_model_selection(self):
        """Get model selection from centralized configuration"""
        openai_models = self.env['sc.openai.models']
        return openai_models.get_all_models()
    
    @api.model
    def _get_default_currency(self):
        """Get default currency from company"""
        return self.env.company.currency_id
    
    @api.model
    def create_log_entry(self, model_name, operation_type, prompt_tokens=0, completion_tokens=0, 
                        response_time_ms=0, status='success', error_message=None, request_id=None,
                        related_model=None, related_record_id=None, related_record_name=None):
        """
        Convenient method to create a log entry from OpenAI response data
        
        Args:
            model_name (str): OpenAI model used
            operation_type (str): Type of operation performed
            prompt_tokens (int): Number of input tokens
            completion_tokens (int): Number of output tokens
            response_time_ms (int): Response time in milliseconds
            status (str): Request status
            error_message (str): Error message if failed
            request_id (str): OpenAI request ID
            related_model (str): Related Odoo model name
            related_record_id (int): Related record ID
            related_record_name (str): Related record name
            
        Returns:
            sc.openai.request.log: Created log record
        """
        try:
            # Calculate estimated cost
            estimated_cost = self._calculate_estimated_cost(model_name, prompt_tokens, completion_tokens)
            
            # Create log entry
            log_entry = self.create({
                'model_used': model_name,
                'operation_type': operation_type,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'response_time_ms': response_time_ms,
                'estimated_cost': estimated_cost,
                'status': status,
                'error_message': error_message,
                'request_id': request_id,
                'related_model': related_model,
                'related_record_id': related_record_id,
                'related_record_name': related_record_name,
            })
            
            _logger.info(f"Created OpenAI request log: {log_entry.display_name}")
            return log_entry
            
        except Exception as e:
            _logger.error(f"Failed to create OpenAI request log: {str(e)}")
            # Don't raise exception to avoid breaking the main OpenAI flow
            return False
    
    @api.model
    def _calculate_estimated_cost(self, model_name, prompt_tokens, completion_tokens):
        """
        Calculate estimated cost based on current OpenAI pricing
        
        Note: Prices are approximate and may change. For exact billing, 
        use OpenAI's usage dashboard.
        """
        # Current approximate pricing (as of September 2025)
        # Prices per 1K tokens
        pricing = {
            'gpt-4o': {'input': 0.0050, 'output': 0.0150},
            'gpt-4o-mini': {'input': 0.0001, 'output': 0.0004},
            'gpt-4-turbo': {'input': 0.0100, 'output': 0.0300},
            'gpt-4': {'input': 0.0300, 'output': 0.0600},
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.0020},
        }
        
        if model_name not in pricing:
            # Default to GPT-4o pricing for unknown models
            model_pricing = pricing['gpt-4o']
        else:
            model_pricing = pricing[model_name]
        
        # Calculate cost
        input_cost = (prompt_tokens / 1000) * model_pricing['input']
        output_cost = (completion_tokens / 1000) * model_pricing['output']
        total_cost = input_cost + output_cost
        
        return round(total_cost, 6)  # Round to 6 decimal places for precision
    
    def action_view_related_record(self):
        """Open the related Odoo record that triggered this request"""
        self.ensure_one()
        
        if not self.related_model or not self.related_record_id:
            raise ValidationError(_("No related record information available."))
        
        try:
            # Try to find the related record
            related_record = self.env[self.related_model].browse(self.related_record_id)
            if not related_record.exists():
                raise ValidationError(_("Related record no longer exists."))
            
            # Return action to open the record
            return {
                'type': 'ir.actions.act_window',
                'name': f"Related {self.related_model}",
                'res_model': self.related_model,
                'res_id': self.related_record_id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except KeyError:
            raise ValidationError(_("Invalid related model: %s") % self.related_model)
    
    @api.model
    def get_usage_summary_by_model(self, date_from=None, date_to=None):
        """
        Get usage summary grouped by model for dashboard display
        
        Args:
            date_from (date): Start date for filtering
            date_to (date): End date for filtering
            
        Returns:
            list: Summary data by model
        """
        domain = []
        
        if date_from:
            domain.append(('timestamp', '>=', date_from))
        if date_to:
            domain.append(('timestamp', '<=', date_to))
        
        # Query to get aggregated data by model
        query = """
            SELECT 
                model_used,
                COUNT(*) as total_requests,
                SUM(prompt_tokens) as total_prompt_tokens,
                SUM(completion_tokens) as total_completion_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(estimated_cost) as total_cost,
                AVG(response_time_ms) as avg_response_time,
                COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM sc_openai_request_log 
            WHERE %s
            GROUP BY model_used
            ORDER BY total_cost DESC
        """ % (self._where_calc(domain).split('WHERE ')[1] if domain else '1=1')
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        
        return results
    
    @api.model
    def cleanup_old_logs(self, days_to_keep=90):
        """
        Clean up old log entries to prevent database bloat
        
        Args:
            days_to_keep (int): Number of days of logs to retain
        """
        cutoff_date = fields.Datetime.now() - timedelta(days=days_to_keep)
        old_logs = self.search([('timestamp', '<', cutoff_date)])
        
        if old_logs:
            count = len(old_logs)
            old_logs.unlink()
            _logger.info(f"Cleaned up {count} old OpenAI request logs older than {days_to_keep} days")
            
        return count
    
    def action_cleanup_old_logs(self):
        """Action method to cleanup old logs with user feedback"""
        try:
            count = self.cleanup_old_logs(days_to_keep=90)
            
            if count > 0:
                message = _('Successfully cleaned up %d old request logs.') % count
                notification_type = 'success'
            else:
                message = _('No old logs found to clean up.')
                notification_type = 'info'
                
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Cleanup Complete'),
                    'message': message,
                    'type': notification_type,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error during log cleanup: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to cleanup logs: %s') % str(e),
                    'type': 'danger',
                }
            }
    
    def action_view_related_record(self):
        """Open the related Odoo record that triggered this OpenAI request"""
        self.ensure_one()
        
        if not self.related_model or not self.related_record_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Related Record'),
                    'message': _('This request is not linked to any specific Odoo record.'),
                    'type': 'info',
                }
            }
        
        try:
            # Verify the record still exists
            related_record = self.env[self.related_model].browse(self.related_record_id)
            if not related_record.exists():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Record Not Found'),
                        'message': _('The related record no longer exists in the system.'),
                        'type': 'warning',
                    }
                }
            
            # Open the related record
            return {
                'type': 'ir.actions.act_window',
                'name': _('Related Record: %s') % (self.related_record_name or self.related_model),
                'res_model': self.related_model,
                'res_id': self.related_record_id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except Exception as e:
            _logger.error(f"Error opening related record: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to open related record: %s') % str(e),
                    'type': 'danger',
                }
            }