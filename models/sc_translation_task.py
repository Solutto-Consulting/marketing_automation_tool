import logging
import json
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ScTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'AI Translation Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    name = fields.Char(
        string="Task Name",
        required=True,
        tracking=True,
        translate=True,
        help="Descriptive name for the translation task"
    )
    
    blog_post_id = fields.Many2one(
        'blog.post',
        string="Blog Post",
        required=True,
        ondelete='cascade',
        tracking=True,
        help="The blog post to be translated"
    )
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string="Target Language",
        required=True,
        tracking=True,
        help="The target language for the translation"
    )
    
    system_instructions = fields.Text(
        string="System Instructions",
        translate=True,
        help="Optional instructions provided to guide the AI model's tone and style"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string="Status", required=True, default='draft', tracking=True)
    
    error_message = fields.Text(
        string="Error Message",
        help="Stores error details if the task fails"
    )
    
    # Computed fields for better UX
    blog_post_title = fields.Char(
        related='blog_post_id.name',
        string="Blog Post Title",
        readonly=True
    )
    
    target_language_name = fields.Char(
        related='target_lang_id.name',
        string="Target Language Name",
        readonly=True
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set automatic task names"""
        for vals in vals_list:
            if not vals.get('name') and vals.get('blog_post_id') and vals.get('target_lang_id'):
                blog_post = self.env['blog.post'].browse(vals['blog_post_id'])
                target_lang = self.env['res.lang'].browse(vals['target_lang_id'])
                vals['name'] = f"Translate '{blog_post.name}' to {target_lang.name}"
        
        return super().create(vals_list)
    
    def action_reset_to_draft(self):
        """Reset task to draft state for retry"""
        for task in self:
            task.write({
                'state': 'draft',
                'error_message': False,
            })
            # Reset blog post flag
            task.blog_post_id.write({'translation_in_progress': False})
            
        return True
    
    def action_set_in_progress(self):
        """Set task to in progress state"""
        for task in self:
            task.write({'state': 'in_progress'})
            task.blog_post_id.write({'translation_in_progress': True})
        return True
    
    def action_set_done(self):
        """Set task to done state"""
        for task in self:
            task.write({'state': 'done'})
            task.blog_post_id.write({'translation_in_progress': False})
        return True
    
    def action_set_error(self, error_message):
        """Set task to error state with message"""
        for task in self:
            task.write({
                'state': 'error',
                'error_message': error_message,
            })
            task.blog_post_id.write({'translation_in_progress': False})
        return True
    
    def action_process_translation(self):
        """Process this translation task manually"""
        for task in self.filtered(lambda t: t.state == 'draft'):
            try:
                # Set task to in progress
                task.action_set_in_progress()
                
                # Perform translation
                openai_utils = self.env['openai.utils']
                translated_content = openai_utils.translate_blog_content(
                    task.blog_post_id,
                    task.target_lang_id,
                    task.system_instructions
                )
                
                # Update translations using simple approach
                task._update_blog_post_translations(translated_content)
                
                # Mark task as done
                task.action_set_done()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Translation Completed',
                        'message': f'Blog post "{task.blog_post_id.name}" has been translated to {task.target_lang_id.name}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
                
            except Exception as e:
                # Log error and mark task as failed
                error_msg = str(e)
                _logger.error("Translation task %s failed: %s", task.id, error_msg)
                
                task.action_set_error(error_msg)
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Translation Failed',
                        'message': f'Error: {error_msg}',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
    
    def _validate_html_structure_consistency(self, original_html, translated_html):
        """
        Validate that translated HTML maintains the same structure as the original.
        Returns (is_valid, issues_found)
        """
        import re
        
        if not original_html or not translated_html:
            return True, []
        
        issues = []
        
        try:
            # Extract HTML tags from both versions
            tag_pattern = r'<[^>]+>'
            original_tags = re.findall(tag_pattern, original_html)
            translated_tags = re.findall(tag_pattern, translated_html)
            
            # Compare tag count
            if len(original_tags) != len(translated_tags):
                issues.append(f"Tag count mismatch: original has {len(original_tags)} tags, translated has {len(translated_tags)} tags")
            
            # Compare paragraph structure
            p_pattern = r'<p[^>]*>.*?</p>'
            original_paragraphs = re.findall(p_pattern, original_html, re.DOTALL)
            translated_paragraphs = re.findall(p_pattern, translated_html, re.DOTALL)
            
            if len(original_paragraphs) != len(translated_paragraphs):
                issues.append(f"Paragraph count mismatch: original has {len(original_paragraphs)} paragraphs, translated has {len(translated_paragraphs)} paragraphs")
            
            # Check for critical structural tags
            critical_tags = ['<div', '<p', '<h1', '<h2', '<h3', '<h4', '<h5', '<h6', '<ul', '<ol', '<li', '<table', '<tr', '<td']
            for tag in critical_tags:
                original_count = original_html.count(tag)
                translated_count = translated_html.count(tag)
                if original_count != translated_count:
                    issues.append(f"Structure tag '{tag}' count mismatch: original has {original_count}, translated has {translated_count}")
            
            # Check for empty paragraphs preservation
            empty_p_pattern = r'<p[^>]*><br\s*/?></p>'
            original_empty = len(re.findall(empty_p_pattern, original_html))
            translated_empty = len(re.findall(empty_p_pattern, translated_html))
            
            if original_empty != translated_empty:
                issues.append(f"Empty paragraph count mismatch: original has {original_empty}, translated has {translated_empty}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            _logger.warning(f"HTML structure validation failed: {e}")
            return True, []  # Allow translation to proceed if validation fails

    def _update_blog_post_translations(self, translated_content):
        """
        Update blog post translations using proper Odoo 18.0 translation API.
        
        CRITICAL FIX: The previous approach using with_context(lang=target_lang).write()
        was OVERWRITING original content instead of creating translations.
        
        CORRECT APPROACH: Use update_field_translations() method for each field type:
        - Simple translatable fields (translate=True): use {lang: value} format
        - HTML translatable fields (translate=html_translate): use {lang: {original: translated}} format
        
        This is the SAME approach used by Odoo's core website_blog module.
        """
        self.ensure_one()
        
        target_lang_code = self.target_lang_id.code
        blog_post = self.blog_post_id
        
        # Store original English content for validation
        original_english_content = blog_post.with_context(lang='en_US').content
        original_english_name = blog_post.with_context(lang='en_US').name
        
        _logger.info(f"Starting PROPER translation update for {target_lang_code}")
        _logger.info(f"Original English content length: {len(original_english_content) if original_english_content else 0}")
        
        # Validate HTML structure consistency for content field
        if 'content' in translated_content and translated_content['content'] and original_english_content:
            is_valid, issues = self._validate_html_structure_consistency(
                original_english_content, 
                translated_content['content']
            )
            
            if not is_valid:
                _logger.warning(f"HTML structure validation failed for {target_lang_code}:")
                for issue in issues:
                    _logger.warning(f"  - {issue}")
                # Continue with translation but log the issues
        
        try:
            # Handle different field types with proper translation methods
            
            # 1. Simple translatable fields (translate=True)
            simple_fields = ['name', 'subtitle', 'website_meta_title', 
                           'website_meta_description', 'website_meta_keywords', 'teaser_manual']
            
            for field_name in simple_fields:
                if field_name in translated_content and translated_content[field_name]:
                    translation_dict = {target_lang_code: translated_content[field_name]}
                    blog_post.update_field_translations(field_name, translation_dict)
                    _logger.info(f"Updated simple translation for {field_name}")
            
            # 2. HTML translatable fields (translate=html_translate)
            # For HTML fields, we need to use term mapping format
            if 'content' in translated_content and translated_content['content']:
                original_content = original_english_content.strip()
                translated_html = translated_content['content'].strip()
                
                if original_content and translated_html:
                    # Term mapping format for html_translate fields
                    content_mapping = {original_content: translated_html}
                    translation_dict = {target_lang_code: content_mapping}
                    blog_post.update_field_translations('content', translation_dict)
                    _logger.info(f"Updated HTML translation for content using term mapping")
            
            # Verify that original English content is preserved
            current_english_content = blog_post.with_context(lang='en_US').content
            current_english_name = blog_post.with_context(lang='en_US').name
            
            if current_english_content != original_english_content:
                _logger.error("CRITICAL: Original English content was overwritten despite using proper API!")
                # This should not happen with update_field_translations, but let's be safe
                raise Exception("Translation API corrupted original content - this should not happen")
            
            # Verify translations are working correctly
            translated_name = blog_post.with_context(lang=target_lang_code).name
            translated_content_field = blog_post.with_context(lang=target_lang_code).content
            
            # Content integrity check
            name_translated = original_english_name != translated_name and bool(translated_name)
            content_translated = original_english_content != translated_content_field and bool(translated_content_field)
            
            _logger.info(f"Verification - English name: {original_english_name[:50]}...")
            _logger.info(f"Verification - {target_lang_code} name: {translated_name[:50] if translated_name else 'None'}...")
            _logger.info(f"Verification - Name translated: {name_translated}")
            _logger.info(f"Verification - Content translated: {content_translated}")
            _logger.info(f"Verification - {target_lang_code} content length: {len(translated_content_field) if translated_content_field else 0}")
            
            if name_translated and content_translated:
                _logger.info(f"SUCCESS: All translations applied correctly for {target_lang_code}")
            else:
                _logger.warning(f"Translation verification failed - some fields may not have been translated properly")
            
        except Exception as e:
            _logger.error(f"Translation update failed: {str(e)}")
            raise
    
    def action_validate_html_structure(self):
        """Validate HTML structure consistency between original and translated content"""
        self.ensure_one()
        
        try:
            # Get original and translated content
            original_content = self.blog_post_id.with_context(lang='en_US').content
            translated_content = self.blog_post_id.with_context(lang=self.target_lang_id.code).content
            
            if not original_content:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'No Original Content',
                        'message': 'No English content found to validate against.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            if not translated_content:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'No Translated Content',
                        'message': f'No {self.target_lang_id.name} content found to validate.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            # Validate HTML structure
            is_valid, issues = self._validate_html_structure_consistency(original_content, translated_content)
            
            if is_valid:
                message = f'✅ HTML structure is consistent between English and {self.target_lang_id.name} versions.'
                msg_type = 'success'
            else:
                issues_text = '\n'.join([f'• {issue}' for issue in issues])
                message = f'⚠️ HTML structure inconsistencies found:\n{issues_text}'
                msg_type = 'warning'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'HTML Structure Validation',
                    'message': message,
                    'type': msg_type,
                    'sticky': msg_type != 'success',
                }
            }
                
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Validation Error',
                    'message': f'Error validating HTML structure: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_verify_translations(self):
        """Verify if translations are working properly"""
        self.ensure_one()
        
        try:
            # Check English content
            english_name = self.blog_post_id.with_context(lang='en_US').name
            english_content = self.blog_post_id.with_context(lang='en_US').content
            
            # Check target language content
            target_name = self.blog_post_id.with_context(lang=self.target_lang_id.code).name
            target_content = self.blog_post_id.with_context(lang=self.target_lang_id.code).content
            
            # Analyze translation status
            name_translated = english_name != target_name and bool(target_name)
            content_translated = english_content != target_content and bool(target_content)
            
            if name_translated and content_translated:
                message = f'✅ Translations working correctly. Both name and content are translated to {self.target_lang_id.name}.'
                msg_type = 'success'
            elif name_translated:
                message = f'⚠️ Name translated but content may not be. Check {self.target_lang_id.name} content.'
                msg_type = 'warning'
            elif content_translated:
                message = f'⚠️ Content translated but name may not be. Check {self.target_lang_id.name} name.'
                msg_type = 'warning'
            else:
                message = f'❌ No translations found for {self.target_lang_id.name}. Content is identical in both languages.'
                msg_type = 'danger'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Translation Verification',
                    'message': message,
                    'type': msg_type,
                    'sticky': msg_type != 'success',
                }
            }
                
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Verification Error',
                    'message': f'Error checking translations: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    @api.model
    def cron_process_translation_tasks(self):
        """Process pending translation tasks (called by cron)"""
        # Search for draft tasks with limit to avoid overloading
        tasks = self.search([('state', '=', 'draft')], limit=10)
        
        if not tasks:
            return
        
        for task in tasks:
            try:
                # Set task to in progress and commit
                task.action_set_in_progress()
                self.env.cr.commit()
                
                # Perform translation
                openai_utils = self.env['openai.utils']
                translated_content = openai_utils.translate_blog_content(
                    task.blog_post_id,
                    task.target_lang_id,
                    task.system_instructions
                )
                
                # CRITICAL FIX: Use Odoo's proper translation system
                # Update each translatable field individually using the translation API
                task._update_blog_post_translations(translated_content)
                
                # Mark task as done
                task.action_set_done()
                self.env.cr.commit()
                
            except Exception as e:
                # Log error and mark task as failed
                error_msg = str(e)
                _logger.error("Translation task %s failed: %s", task.id, error_msg)
                
                task.action_set_error(error_msg)
                self.env.cr.commit()
