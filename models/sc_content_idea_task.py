from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)

class ScContentIdeaTask(models.Model):
    _name = 'sc.content.idea.task'
    _description = 'Content Idea Generation Task Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string="Task Name",
        required=True,
        default="Content Idea Task",
        tracking=True,
        help="Descriptive name for this generation task"
    )
    
    search_query = fields.Text(
        string="Search Query",
        tracking=True,
        help="The final search query/prompt used for generating ideas"
    )
    
    requested_ideas = fields.Integer(
        string="Requested Ideas",
        default=5,
        help="The number of ideas the user requested"
    )
    
    generated_ideas_ids = fields.One2many(
        'sc.content.idea',
        'task_id',
        string="Generated Ideas",
        help="The ideas created by this task"
    )
    
    generated_ideas_count = fields.Integer(
        string="Generated Count",
        compute='_compute_generated_ideas_count',
        store=True,
        help="Number of ideas actually generated"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string="State", required=True, default='draft', tracking=True)
    
    error_message = fields.Text(
        string="Error Details",
        tracking=True,
        help="Stores error details when task fails"
    )
    
    # Execution tracking fields
    started_at = fields.Datetime(
        string="Started At",
        help="When the task processing started"
    )
    
    completed_at = fields.Datetime(
        string="Completed At", 
        help="When the task was completed"
    )
    
    duration = fields.Float(
        string="Duration (minutes)",
        compute='_compute_duration',
        store=True,
        help="Task execution duration in minutes"
    )
    
    # Agent configuration at execution time
    agent_model = fields.Char(
        string="Agent Model Used",
        help="OpenAI model used for this task"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions Used",
        help="System instructions used for this task"
    )
    
    @api.depends('generated_ideas_ids')
    def _compute_generated_ideas_count(self):
        """Compute the number of generated ideas"""
        for record in self:
            record.generated_ideas_count = len(record.generated_ideas_ids)
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        """Compute task execution duration"""
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds() / 60.0  # Convert to minutes
            else:
                record.duration = 0.0
    
    @api.constrains('requested_ideas')
    def _check_requested_ideas(self):
        """Validate requested ideas count"""
        for record in self:
            if record.requested_ideas <= 0:
                raise ValidationError(_("Requested ideas must be greater than 0"))
            if record.requested_ideas > 20:
                raise ValidationError(_("Maximum 20 ideas can be requested at once"))
    
    def action_start_processing(self):
        """Mark task as ready for processing by cron job"""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft tasks can be started"))
            record.write({
                'state': 'draft',  # Cron will pick it up
            })
            record.message_post(body=_("Task queued for processing"))
    
    def action_retry(self):
        """Reset task to draft state for retry"""
        for record in self:
            if record.state not in ['error', 'done']:
                raise ValidationError(_("Only error or done tasks can be retried"))
            record.write({
                'state': 'draft',
                'error_message': False,
                'started_at': False,
                'completed_at': False,
            })
            record.message_post(body=_("Task reset for retry"))
    
    def action_view_ideas(self):
        """View generated ideas"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Ideas'),
            'res_model': 'sc.content.idea',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id}
        }
    
    def _process_placeholders(self, query):
        """Process placeholders in search query"""
        if not query:
            return query
            
        processed_query = query
        
        # Replace {today} with current date
        today = fields.Date.today().strftime('%Y-%m-%d')
        processed_query = processed_query.replace('{today}', today)
        
        # Add more placeholders as needed in future versions
        
        return processed_query
    
    def _mark_in_progress(self):
        """Mark task as in progress"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'started_at': fields.Datetime.now(),
            'error_message': False,
        })
        self.message_post(body=_("Task processing started"))
    
    def _mark_done(self):
        """Mark task as completed successfully"""
        self.ensure_one()
        self.write({
            'state': 'done',
            'completed_at': fields.Datetime.now(),
        })
        message = _("Task completed successfully. Generated %d ideas.") % self.generated_ideas_count
        self.message_post(body=message)
    
    def _mark_error(self, error_message):
        """Mark task as failed with error message"""
        self.ensure_one()
        self.write({
            'state': 'error',
            'error_message': error_message,
            'completed_at': fields.Datetime.now(),
        })
        self.message_post(body=_("Task failed: %s") % error_message)
