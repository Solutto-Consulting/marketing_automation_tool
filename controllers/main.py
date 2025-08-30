# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class MarketingAutomationController(http.Controller):
    
    @http.route('/marketing_tool/translation_callback', type='http', auth='public', methods=['POST'], csrf=False)
    def translation_callback(self, **kwargs):
        """
        Receive translated content from external translation service (n8n)
        
        Expected JSON payload:
        {
            "post_id": 123,
            "source_lang": "es_ES",
            "target_lang": "en_US",
            "translated_content": {
                "name": "Translated Article Title",
                "subtitle": "Translated Article Subtitle",
                "content": "<h1>Translated HTML content...</h1>",
                "website_meta_title": "Translated Meta Title for SEO",
                "website_meta_description": "Translated Meta Description for SEO",
                "website_meta_keywords": "keyword1, keyword2, keyword3"
            }
        }
        """
        try:
            # Validate authentication token
            auth_header = request.httprequest.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                _logger.warning("Translation callback received without proper authorization header")
                return self._error_response("Unauthorized", 401)
            
            # Extract token from header
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Get configured token
            ICPSudo = request.env['ir.config_parameter'].sudo()
            expected_token = ICPSudo.get_param('marketing_automation_tool.automation_token')
            
            if not expected_token or token != expected_token:
                _logger.warning("Translation callback received with invalid token")
                return self._error_response("Invalid authentication token", 401)
            
            # Parse JSON payload
            try:
                if request.httprequest.content_type == 'application/json':
                    payload = json.loads(request.httprequest.data.decode('utf-8'))
                else:
                    # Try to get JSON from form data
                    payload = json.loads(request.httprequest.get_data(as_text=True))
            except (json.JSONDecodeError, ValueError) as e:
                _logger.error(f"Invalid JSON payload in translation callback: {str(e)}")
                return self._error_response("Invalid JSON payload", 400)
            
            # Validate required fields
            required_fields = ['post_id', 'source_lang', 'target_lang', 'translated_content']
            for field in required_fields:
                if field not in payload:
                    _logger.error(f"Missing required field '{field}' in translation callback")
                    return self._error_response(f"Missing required field: {field}", 400)
            
            # Get blog post
            post_id = payload['post_id']
            blog_post = request.env['blog.post'].sudo().browse(post_id)
            
            if not blog_post.exists():
                _logger.error(f"Blog post with ID {post_id} not found")
                return self._error_response("Blog post not found", 404)
            
            # Validate translation status
            if blog_post.translation_status != 'in_progress':
                _logger.warning(f"Received translation for blog post {post_id} but status is not 'in_progress': {blog_post.translation_status}")
                return self._error_response("Blog post is not in translation progress", 400)
            
            # Extract translation data
            source_lang = payload['source_lang']
            target_lang = payload['target_lang']
            translated_content = payload['translated_content']
            
            # Validate translated content
            if not isinstance(translated_content, dict):
                _logger.error("translated_content must be a dictionary")
                return self._error_response("Invalid translated_content format", 400)
            
            # Process the translation
            blog_post.receive_translation(translated_content, target_lang)
            
            _logger.info(f"Successfully processed translation callback for blog post {post_id}, target language: {target_lang}")
            
            return self._success_response("Translation received and processed successfully")
            
        except Exception as e:
            _logger.error(f"Error processing translation callback: {str(e)}")
            
            # Try to update blog post status to failed if we have the post_id
            try:
                if 'post_id' in locals():
                    blog_post = request.env['blog.post'].sudo().browse(post_id)
                    if blog_post.exists():
                        blog_post.write({'translation_status': 'failed'})
            except:
                pass  # Ignore errors in error handling
            
            return self._error_response(f"Internal server error: {str(e)}", 500)
    
    def _success_response(self, message):
        """Return a successful HTTP response"""
        response_data = {
            'status': 'success',
            'message': message
        }
        return request.make_response(
            json.dumps(response_data),
            status=200,
            headers=[('Content-Type', 'application/json')]
        )
    
    def _error_response(self, message, status_code):
        """Return an error HTTP response"""
        response_data = {
            'status': 'error',
            'message': message
        }
        return request.make_response(
            json.dumps(response_data),
            status=status_code,
            headers=[('Content-Type', 'application/json')]
        )
