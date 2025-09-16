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
    
    # Agent configuration
    agent_config_id = fields.Many2one(
        'sc.ai.agent.config',
        string="AI Agent Configuration",
        help="The agent configuration used for this task"
    )
    
    user_prompt = fields.Text(
        string="User Custom Instructions",
        help="Additional user instructions for this specific task"
    )
    
    # Agent configuration at execution time (for history)
    agent_model = fields.Char(
        string="Agent Model Used",
        help="OpenAI model used for this task (stored for history)"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions Used",
        help="System instructions used for this task (stored for history)"
    )
    
    @api.depends('generated_ideas_ids')
    def _compute_generated_ideas_count(self):
        """Compute the number of generated ideas"""
        for record in self:
            try:
                # Safe access to the One2many field
                if record.generated_ideas_ids:
                    record.generated_ideas_count = len(record.generated_ideas_ids)
                else:
                    record.generated_ideas_count = 0
            except Exception as e:
                # Log the error and set a safe default
                _logger.warning(f"Error computing generated ideas count for task {record.id}: {e}")
                record.generated_ideas_count = 0
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        """Compute task execution duration"""
        for record in self:
            try:
                if record.started_at and record.completed_at:
                    delta = record.completed_at - record.started_at
                    record.duration = delta.total_seconds() / 60.0  # Convert to minutes
                else:
                    record.duration = 0.0
            except Exception as e:
                # Log the error and set a safe default
                _logger.warning(f"Error computing duration for task {record.id}: {e}")
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
        
        # Reload current record to show updated state
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }
    
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
        
        # Reload current record to show updated state
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }
    
    def action_view_ideas(self):
        """View generated ideas"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Ideas'),
            'res_model': 'sc.content.idea',
            'view_mode': 'list,form',
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
    
    def _prepare_agent_config(self):
        """Prepare agent configuration for execution"""
        self.ensure_one()
        
        # If we have an agent_config_id, use it
        if self.agent_config_id:
            # Store configuration for history
            self.write({
                'agent_model': self.agent_config_id.model,
                'agent_instructions': self.agent_config_id.instructions,
            })
            
            # Combine system instructions with user prompt
            combined_instructions = self.agent_config_id.instructions
            if self.user_prompt:
                combined_instructions += f"\n\nAdditional user instructions:\n{self.user_prompt}"
            
            return {
                'model': self.agent_config_id.model,
                'instructions': combined_instructions,
            }
        
        # Fallback to legacy fields if no agent_config_id
        return {
            'model': self.agent_model or 'gpt-4o',
            'instructions': self.agent_instructions or 'You are a content research agent.',
        }
    
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
    
    @api.model
    def _cron_process_pending_tasks(self):
        """Cron job method to process pending content idea tasks"""
        try:
            # Find draft tasks ready for processing
            pending_tasks = self.search([('state', '=', 'draft')], limit=5)
            
            if not pending_tasks:
                _logger.info("No pending content idea tasks found")
                return
            
            _logger.info(f"Processing {len(pending_tasks)} content idea tasks")
            
            for task in pending_tasks:
                try:
                    task._process_task()
                except Exception as e:
                    _logger.error(f"Failed to process task {task.id}: {str(e)}")
                    task._mark_error(str(e))
                    
        except Exception as e:
            _logger.error(f"Error in content idea task cron job: {str(e)}")
    
    def _process_task(self):
        """Process individual content idea task"""
        self.ensure_one()
        
        if self.state != 'draft':
            return
        
        try:
            # Mark as in progress
            self._mark_in_progress()
            
            # Get agent configuration from the selected agent_config_id or fallback
            agent_config_data = self._prepare_agent_config()
            
            # Process placeholders in search query
            processed_query = self._process_placeholders(self.search_query)
            
            # Perform content research using OpenAI utils
            openai_utils = self.env['openai.utils']
            ideas_data = openai_utils.research_content_ideas(
                agent_config_data['model'],
                agent_config_data['instructions'],
                processed_query,
                self.requested_ideas
            )
            
            # Create content idea records
            idea_records = []
            for idea_data in ideas_data:
                idea_record = self.env['sc.content.idea'].create({
                    'task_id': self.id,
                    'name': idea_data.get('name', 'Untitled Idea'),
                    'url': idea_data.get('url', ''),
                    'publish_date': idea_data.get('publish_date'),
                    'summary': idea_data.get('summary', ''),
                })
                idea_records.append(idea_record)
            
            # Mark as completed
            self._mark_done()
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Content idea task {self.id} failed: {error_msg}")
            self._mark_error(error_msg)
    
    def action_execute_immediately(self):
        """Execute content research task immediately"""
        for task in self.filtered(lambda t: t.state == 'draft'):
            try:
                # Process the task
                task._process_task()
                
                # Return success notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Task Executed Successfully'),
                        'message': _('Content research task "%s" has been executed. Generated %d ideas.') % (task.name, task.generated_ideas_count),
                        'type': 'success',
                        'sticky': False,
                    }
                }
                
            except Exception as e:
                # Log error and show notification
                error_msg = str(e)
                _logger.error("Content idea task %s failed: %s", task.id, error_msg)
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Task Execution Failed'),
                        'message': _('Content research task failed: %s') % error_msg,
                        'type': 'danger',
                        'sticky': True,
                    }
                }
