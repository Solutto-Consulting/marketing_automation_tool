# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

import asyncio
import json
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ScTranslationTask(models.Model):
    """AI Translation Task - Manages individual blog post translation requests"""
    
    _name = 'sc.translation.task'
    _description = 'AI Translation Task'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    
    # Core fields
    name = fields.Char(
        string='Task Name', 
        required=True, 
        tracking=True,
        compute='_compute_name',
        store=True,
        help="Automatically generated name based on blog post and target language"
    )
    blog_post_id = fields.Many2one(
        'blog.post', 
        string='Blog Post', 
        required=True, 
        ondelete='cascade',
        tracking=True,
        help="Blog post to be translated"
    )
    target_lang_id = fields.Many2one(
        'res.lang', 
        string='Target Language', 
        required=True,
        tracking=True,
        help="Target language for translation"
    )
    system_instructions = fields.Text(
        string='AI Instructions', 
        help="Custom instructions for AI translation (tone, style, etc.)",
        tracking=True
    )
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='draft', required=True, tracking=True,
       help="Current status of the translation task")
    
    error_message = fields.Text(
        string='Error Details', 
        readonly=True,
        help="Detailed error message if translation fails"
    )
    
    # Translation data
    original_content = fields.Json(
        string='Original Content', 
        readonly=True,
        help="Original blog post content in JSON format"
    )
    translated_content = fields.Json(
        string='Translated Content', 
        readonly=True,
        help="Translated blog post content in JSON format"
    )
    
    # Audit fields
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
        required=True,
        help="Company this task belongs to"
    )
    processed_date = fields.Datetime(
        string='Processed Date', 
        readonly=True,
        help="Date and time when translation was completed"
    )
    processing_duration = fields.Float(
        string='Processing Time (seconds)', 
        readonly=True,
        help="Time taken to complete the translation"
    )
    
    # Computed fields
    status_display = fields.Char(
        string='Status Display',
        compute='_compute_status_display',
        help="Formatted status display for UI"
    )
    
    @api.depends('blog_post_id.name', 'target_lang_id.name')
    def _compute_name(self):
        """Compute task name based on blog post and target language"""
        for record in self:
            if record.blog_post_id and record.target_lang_id:
                record.name = _("Translate '%s' to %s") % (
                    record.blog_post_id.name, 
                    record.target_lang_id.name
                )
            else:
                record.name = _("Translation Task")
    
    @api.depends('state', 'error_message')
    def _compute_status_display(self):
        """Compute status display for badge widget"""
        for record in self:
            if record.state == 'draft':
                record.status_display = _("Draft")
            elif record.state == 'in_progress':
                record.status_display = _("Processing...")
            elif record.state == 'done':
                record.status_display = _("Completed")
            elif record.state == 'error':
                record.status_display = _("Error")
            else:
                record.status_display = record.state.title()
    
    @api.constrains('blog_post_id', 'target_lang_id')
    def _check_duplicate_translation(self):
        """Prevent duplicate active translations for same post+language"""
        for record in self:
            existing = self.search([
                ('blog_post_id', '=', record.blog_post_id.id),
                ('target_lang_id', '=', record.target_lang_id.id),
                ('state', 'in', ['draft', 'in_progress']),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_(
                    "A translation task for this blog post and language already exists. "
                    "Please wait for it to complete or reset it to draft."
                ))
    
    @api.constrains('target_lang_id')
    def _check_published_language(self):
        """Ensure target language is active"""
        for record in self:
            if not record.target_lang_id.active:
                raise ValidationError(_(
                    "Target language '%s' must be active to be used for translation."
                ) % record.target_lang_id.name)
    
    def action_reset_to_draft(self):
        """Reset task to draft state for retry"""
        self.ensure_one()
        if self.state != 'error':
            raise UserError(_("Only tasks in error state can be reset to draft."))
        
        self.write({
            'state': 'draft',
            'error_message': False,
            'processed_date': False,
            'processing_duration': 0.0,
        })
        
        # Reset blog post translation flag if needed
        self.blog_post_id._compute_translation_status()
        
        # Log the reset action
        self.message_post(
            body=_("Translation task reset to draft by %s") % self.env.user.name,
            message_type='notification'
        )
        
        return True
    
    def action_start_processing(self):
        """Mark task as in progress and start processing"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft tasks can be started."))
        
        self.write({
            'state': 'in_progress',
            'processed_date': fields.Datetime.now(),
        })
        
        # Update blog post translation flag
        self.blog_post_id.translation_in_progress = True
        
        # Log the start
        self.message_post(
            body=_("Translation processing started"),
            message_type='notification'
        )
    
    def action_mark_done(self, translated_content, processing_duration=0.0):
        """Mark task as completed with translated content"""
        self.ensure_one()
        
        self.write({
            'state': 'done',
            'translated_content': translated_content,
            'processed_date': fields.Datetime.now(),
            'processing_duration': processing_duration,
            'error_message': False,
        })
        
        # Update blog post translation flag
        self.blog_post_id._compute_translation_status()
        
        # Log completion
        self.message_post(
            body=_("Translation completed successfully in %.2f seconds") % processing_duration,
            message_type='notification'
        )
    
    def action_mark_error(self, error_message):
        """Mark task as error with error details"""
        self.ensure_one()
        
        self.write({
            'state': 'error',
            'error_message': error_message,
            'processed_date': fields.Datetime.now(),
        })
        
        # Update blog post translation flag
        self.blog_post_id._compute_translation_status()
        
        # Log error
        self.message_post(
            body=_("Translation failed: %s") % error_message,
            message_type='notification'
        )
        
        # Create activity for follow-up
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Translation Error - Review Required"),
            note=_("Translation task failed with error: %s") % error_message,
            user_id=self.create_uid.id or self.env.user.id,
        )
    
    @api.model
    def _process_translation_tasks(self):
        """Cron method to process pending translation tasks"""
        tasks = self.search([('state', '=', 'draft')], limit=10)
        
        if not tasks:
            _logger.info("No pending translation tasks found")
            return
        
        _logger.info("Processing %d translation tasks", len(tasks))
        
        for task in tasks:
            try:
                # Start processing
                task.action_start_processing()
                self.env.cr.commit()
                
                # Execute translation
                start_time = datetime.now()
                result = task._execute_translation_async()
                processing_duration = (datetime.now() - start_time).total_seconds()
                
                # Mark as done
                task.action_mark_done(result, processing_duration)
                self.env.cr.commit()
                
                _logger.info("Successfully processed translation task %s in %.2f seconds", 
                           task.name, processing_duration)
                
            except Exception as e:
                _logger.exception("Error processing translation task %s", task.name)
                task.action_mark_error(str(e))
                self.env.cr.commit()
    
    def _execute_translation_async(self):
        """Execute async translation in sync context"""
        self.ensure_one()
        
        # Get OpenAI configuration
        config = self.env['ir.config_parameter'].sudo()
        api_key = config.get_param('sc_marketing_automation.openai_api_key')
        org_id = config.get_param('sc_marketing_automation.openai_org_id')
        model = config.get_param('sc_marketing_automation.openai_model', 'gpt-4o')
        
        if not api_key:
            raise UserError(_("OpenAI API key not configured. Please configure it in Settings > General Settings > AI Marketing Tools."))
        
        # Prepare content for translation
        post = self.blog_post_id
        content = {
            'name': post.name or '',
            'subtitle': post.subtitle or '',
            'content': post.content or '',
            'website_meta_title': post.website_meta_title or '',
            'website_meta_description': post.website_meta_description or '',
            'website_meta_keywords': post.website_meta_keywords or ''
        }
        
        # Store original content
        self.original_content = content
        
        # Import OpenAI service
        try:
            from ..utils.openai_service import OpenAITranslationService
        except ImportError:
            raise UserError(_("OpenAI Agents SDK not installed. Please install 'openai-agents' package."))
        
        # Initialize service and run translation (ensure proper type conversion)
        service = OpenAITranslationService(
            api_key=str(api_key) if api_key else '',
            organization_id=str(org_id) if org_id else None,
            model=str(model) if model else 'gpt-4o'
        )
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.translate_blog_content(
                    content, 
                    'English',  # Assuming source is English
                    self.target_lang_id.name,
                    self.system_instructions or ""
                )
            )
            return result
        finally:
            loop.close()
    
    def unlink(self):
        """Override unlink to update blog post translation status"""
        blog_posts = self.mapped('blog_post_id')
        result = super().unlink()
        
        # Update translation status for affected blog posts
        for post in blog_posts:
            post._compute_translation_status()
            
        return result
    
    @api.model
    def process_pending_translations(self):
        """Cron method: Process pending translation tasks"""
        # Find draft tasks ready for processing
        pending_tasks = self.search([
            ('state', '=', 'draft'),
        ], limit=10)  # Process max 10 at a time to avoid timeout
        
        if not pending_tasks:
            _logger.info("No pending translation tasks found")
            return
        
        _logger.info("Processing %d pending translation tasks", len(pending_tasks))
        
        for task in pending_tasks:
            try:
                task.action_start_processing()
                # Commit after each task to avoid losing progress
                self.env.cr.commit()
            except Exception as e:
                _logger.exception("Failed to process translation task %s: %s", task.name, str(e))
                task.action_mark_error(str(e))
                # Continue with next task even if one fails
                continue
                
        _logger.info("Completed processing pending translation tasks")
    
    @api.model 
    def cleanup_old_tasks(self):
        """Cron method: Clean up old completed/error translation tasks"""
        cutoff_date = fields.Datetime.now() - timedelta(days=30)
        
        old_tasks = self.search([
            ('create_date', '<', cutoff_date),
            ('state', 'in', ['done', 'error']),
        ])
        
        if old_tasks:
            count = len(old_tasks)
            old_tasks.unlink()
            _logger.info("Cleaned up %d old translation tasks", count)
        else:
            _logger.info("No old translation tasks to clean up")
    
    @api.model
    def monitor_translation_health(self):
        """Cron method: Monitor translation system health"""
        # Check for stuck tasks (in_progress for more than 1 hour)
        stuck_cutoff = fields.Datetime.now() - timedelta(hours=1)
        stuck_tasks = self.search([
            ('state', '=', 'in_progress'),
            ('write_date', '<', stuck_cutoff),
        ])
        
        if stuck_tasks:
            _logger.warning("Found %d stuck translation tasks", len(stuck_tasks))
            for task in stuck_tasks:
                task.action_mark_error(_("Task timed out - stuck in processing state"))
                task.message_post(
                    body=_("Task was reset due to timeout (stuck in processing for over 1 hour)"),
                    message_type='notification'
                )
            self.env.cr.commit()
        
        # Check for high error rate (more than 50% errors in last 24 hours)
        recent_cutoff = fields.Datetime.now() - timedelta(hours=24)
        recent_tasks = self.search([('create_date', '>=', recent_cutoff)])
        
        if recent_tasks:
            error_count = len(recent_tasks.filtered(lambda t: t.state == 'error'))
            error_rate = (error_count / len(recent_tasks)) * 100
            
            if error_rate > 50:
                _logger.error(
                    "High translation error rate detected: %.1f%% (%d errors out of %d tasks)",
                    error_rate, error_count, len(recent_tasks)
                )
                
                # Send notification to administrators
                admin_users = self.env.ref('base.group_system').users
                for admin in admin_users:
                    admin.partner_id.message_post(
                        body=_(
                            "SC Marketing Automation: High translation error rate detected (%.1f%%). "
                            "Please check the system configuration and OpenAI API status."
                        ) % error_rate,
                        subject=_("Translation System Health Alert"),
                        message_type='notification'
                    )
        
        _logger.info("Translation health monitoring completed")
