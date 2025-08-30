# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BlogPost(models.Model):
    _inherit = 'blog.post'

    # Translation status field
    translation_status = fields.Selection([
        ('not_translated', 'Not Translated'),
        ('in_progress', 'Sent for Translation'),
        ('completed', 'Translated'),
        ('failed', 'Translation Error'),
    ], string='Translation Status', default='not_translated', tracking=True)

    def action_send_to_translate(self):
        """Open wizard to select target language for translation"""
        self.ensure_one()
        
        # Check if article is already in progress
        if self.translation_status == 'in_progress':
            raise UserError(_("This article is already being translated. Please wait for the process to complete."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send to Translate'),
            'res_model': 'blog.post.translation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_post_ids': [(6, 0, self.ids)],
                'active_ids': self.ids,
                'active_model': 'blog.post',
            }
        }

    def send_to_translation_service(self, target_lang):
        """Send blog post to external translation service (n8n)"""
        self.ensure_one()
        
        # Get configuration parameters
        ICPSudo = self.env['ir.config_parameter'].sudo()
        automation_url = ICPSudo.get_param('marketing_automation_tool.automation_url')
        automation_token = ICPSudo.get_param('marketing_automation_tool.automation_token')
        
        # Validate configuration parameters
        if not automation_url or not isinstance(automation_url, str):
            raise UserError(_("Please configure a valid automation hub URL in Settings > General Settings."))
        
        if not automation_token or not isinstance(automation_token, str):
            raise UserError(_("Please configure a valid automation token in Settings > General Settings."))
        
        # Get current language (source language)
        source_lang = self.env.context.get('lang', 'en_US')
        
        # Get base URL for callback
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        callback_url = f"{base_url}/marketing_tool/translation_callback"
        
        # Prepare content to translate
        content_to_translate = {
            'name': self.name or '',
            'subtitle': self.subtitle or '',
            'content': self.content or '',
            'website_meta_title': self.website_meta_title or '',
            'website_meta_description': self.website_meta_description or '',
            'website_meta_keywords': self.website_meta_keywords or '',
        }
        
        # Prepare payload for n8n
        payload = {
            'post_id': self.id,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'callback_url': callback_url,
            'content_to_translate': content_to_translate,
        }
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {automation_token}',
        }
        
        try:
            # Update status to in_progress before sending
            self.write({'translation_status': 'in_progress'})
            
            # Send request to n8n
            response = requests.post(
                automation_url,
                json=payload,
                headers=headers,
                timeout=30  # 30 seconds timeout
            )
            
            response.raise_for_status()
            
            _logger.info(f"Successfully sent blog post {self.id} to translation service. Target language: {target_lang}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _("Article sent to translation service successfully!"),
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
            
        except requests.exceptions.RequestException as e:
            # Update status to failed
            self.write({'translation_status': 'failed'})
            
            error_msg = f"Failed to send article to translation service: {str(e)}"
            _logger.error(error_msg)
            
            raise UserError(_("Failed to connect to translation service. Please check the configuration and try again.\n\nError: %s") % str(e))
        
        except Exception as e:
            # Update status to failed
            self.write({'translation_status': 'failed'})
            
            error_msg = f"Unexpected error sending article to translation service: {str(e)}"
            _logger.error(error_msg)
            
            raise UserError(_("An unexpected error occurred. Please contact the administrator.\n\nError: %s") % str(e))

    def receive_translation(self, translated_content, target_lang):
        """Process received translation from external service"""
        self.ensure_one()
        
        try:
            # Store translations using ir.translation (suppress type checking for Odoo dynamic models)
            translation_model = self.env['ir.translation']  # type: ignore
            
            # Fields to translate
            translatable_fields = {
                'name': translated_content.get('name', ''),
                'subtitle': translated_content.get('subtitle', ''),
                'content': translated_content.get('content', ''),
                'website_meta_title': translated_content.get('website_meta_title', ''),
                'website_meta_description': translated_content.get('website_meta_description', ''),
                'website_meta_keywords': translated_content.get('website_meta_keywords', ''),
            }
            
            # Create or update translations
            for field_name, translated_value in translatable_fields.items():
                if translated_value:  # Only store non-empty translations
                    # Check if translation already exists
                    existing_translation = translation_model.search([  # type: ignore
                        ('name', '=', f'blog.post,{field_name}'),  # type: ignore
                        ('res_id', '=', self.id),  # type: ignore
                        ('lang', '=', target_lang),  # type: ignore
                        ('type', '=', 'model'),  # type: ignore
                    ])
                    
                    if existing_translation:
                        # Update existing translation
                        existing_translation.write({'value': translated_value})  # type: ignore
                    else:
                        # Create new translation
                        translation_model.create({  # type: ignore
                            'name': f'blog.post,{field_name}',  # type: ignore
                            'res_id': self.id,  # type: ignore
                            'lang': target_lang,  # type: ignore
                            'type': 'model',  # type: ignore
                            'src': getattr(self, field_name) or '',  # type: ignore
                            'value': translated_value,  # type: ignore
                            'state': 'translated',  # type: ignore
                        })
            
            # Update translation status
            self.write({'translation_status': 'completed'})
            
            _logger.info(f"Successfully received and stored translation for blog post {self.id}. Target language: {target_lang}")
            
            return True
            
        except Exception as e:
            # Update status to failed
            self.write({'translation_status': 'failed'})
            
            error_msg = f"Error processing received translation for blog post {self.id}: {str(e)}"
            _logger.error(error_msg)
            
            raise

    @api.constrains('translation_status')
    def _check_translation_status(self):
        """Validate translation status transitions"""
        for post in self:
            # Log status changes for debugging
            if post.translation_status:
                _logger.info(f"Blog post {post.id} translation status: {post.translation_status}")
