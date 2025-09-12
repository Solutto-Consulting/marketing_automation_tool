from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class ScContentGenerationTask(models.Model):
    _name = 'sc.content.generation.task'
    _description = 'Content Generation Task Tracking for Blog Posts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string="Task Name",
        required=True,
        tracking=True,
        help="Descriptive name for this generation task"
    )
    
    content_idea_id = fields.Many2one(
        'sc.content.idea',
        string="Source Idea",
        ondelete='cascade',
        help="The content idea used as source for generation (optional)"
    )
    
    # Alternative content input (when not using a content idea)
    custom_topic = fields.Char(
        string="Custom Topic",
        help="Topic or title for the blog post (used when not selecting a content idea)"
    )
    
    custom_instructions = fields.Text(
        string="Custom Instructions",
        help="Detailed instructions for content generation (used when not selecting a content idea)"
    )
    
    user_prompt = fields.Text(
        string="Additional Instructions",
        help="Additional instructions from the user for content generation"
    )
    
    target_word_count = fields.Integer(
        string="Target Word Count",
        default=800,
        help="Approximate word count for the generated blog post"
    )
    
    auto_publish = fields.Boolean(
        string="Auto-publish after generation",
        default=False,
        help="Automatically publish the blog post after generation"
    )
    
    generate_meta_tags = fields.Boolean(
        string="Generate SEO meta tags",
        default=True,
        help="Generate SEO meta tags for the blog post"
    )
    
    # Image Generation Configuration
    generate_cover_image = fields.Boolean(
        string="Generate Cover Image",
        default=True,
        help="Automatically generate a cover image for the blog post using DALL-E"
    )
    
    image_prompt_override = fields.Text(
        string="Custom Image Prompt",
        help="Optional: Custom prompt for image generation. If empty, will be generated from the article content."
    )
    
    image_size = fields.Selection(
        selection=[
            ('1024x1024', '1024x1024 (Square)'),
            ('1024x1792', '1024x1792 (Portrait)'),
            ('1792x1024', '1792x1024 (Landscape)'),
            ('512x512', '512x512 (Square - DALL-E 2)'),
            ('256x256', '256x256 (Square - DALL-E 2)'),
        ],
        string="Image Size",
        help="Size for the generated cover image"
    )
    
    image_quality = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('hd', 'HD (Higher detail)'),
        ],
        string="Image Quality",
        help="Quality for the generated image (DALL-E 3 only)"
    )
    
    image_style = fields.Selection(
        selection=[
            ('vivid', 'Vivid (Hyper-real and dramatic)'),
            ('natural', 'Natural (Less hyper-real)'),
        ],
        string="Image Style",
        help="Visual style for the generated image (DALL-E 3 only)"
    )
    
    # Image Generation Results
    generated_image_path = fields.Char(
        string="Generated Image Path",
        help="Local path where the generated image is stored"
    )
    
    image_generation_prompt = fields.Text(
        string="Final Image Prompt",
        help="The actual prompt used for image generation (may be revised by DALL-E)"
    )
    
    image_generation_status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('generating', 'Generating'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        string="Image Generation Status",
        default='pending',
        help="Status of the image generation process"
    )
    
    image_generation_error = fields.Text(
        string="Image Generation Error",
        help="Error details if image generation fails"
    )
    
    generated_blog_post_id = fields.Many2one(
        'blog.post',
        string="Generated Blog Post",
        ondelete='set null',
        help="The resulting blog post created by the agent"
    )
    
    target_blog_id = fields.Many2one(
        'blog.blog',
        string="Target Blog",
        required=True,
        help="The blog where the post will be created"
    )
    
    target_author_id = fields.Many2one(
        'res.partner',
        string="Author",
        help="The author for the generated blog post"
    )
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string="Language",
        required=True,
        default='_get_default_website_language',
        help="The language for the generated article (uses website default language)"
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
        help="The AI agent configuration used for this task"
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
    
    # Content preview fields (computed from source idea)
    source_title = fields.Char(
        string="Source Title",
        related='content_idea_id.name',
        readonly=True
    )
    
    source_summary = fields.Text(
        string="Source Summary",
        related='content_idea_id.summary',
        readonly=True
    )
    
    source_url = fields.Char(
        string="Source URL",
        related='content_idea_id.url',
        readonly=True
    )
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        """Compute task execution duration"""
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds() / 60.0  # Convert to minutes
            else:
                record.duration = 0.0
    
    @api.constrains('content_idea_id', 'custom_topic', 'custom_instructions')
    def _check_content_source(self):
        """Validate that either content idea or custom content is provided"""
        for record in self:
            has_content_idea = bool(record.content_idea_id)
            has_custom_content = bool(record.custom_topic and record.custom_instructions)
            
            if not has_content_idea and not has_custom_content:
                raise ValidationError(_(
                    "Please provide either:\n"
                    "• A Content Idea, OR\n"
                    "• Custom Topic AND Custom Instructions"
                ))
    
    @api.model
    def _get_default_website_language(self):
        """Get the default language from the website configuration"""
        try:
            # Get the current website or the first website
            website = self.env['website'].get_current_website()
            if not website:
                website = self.env['website'].search([], limit=1)
            
            # Return the website's default language if available
            if website and website.default_lang_id:
                return website.default_lang_id.id
        except Exception as e:
            _logger.warning(f"Could not get website default language: {e}")
        
        # Fallback to English if website not found or error
        try:
            return self.env.ref('base.lang_en').id
        except Exception:
            # Ultimate fallback - first available language
            lang = self.env['res.lang'].search([], limit=1)
            return lang.id if lang else False
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-generate task name"""
        for vals in vals_list:
            if not vals.get('name'):
                if vals.get('content_idea_id'):
                    idea = self.env['sc.content.idea'].browse(vals['content_idea_id'])
                    vals['name'] = _("Blog post generation for: %s") % (idea.name or 'Untitled')
                elif vals.get('custom_topic'):
                    vals['name'] = _("Blog post generation: %s") % vals['custom_topic']
                else:
                    vals['name'] = _("Blog post generation task")
        return super().create(vals_list)
    
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
                'generated_blog_post_id': False,
            })
            record.message_post(body=_("Task reset for retry"))

    def action_execute_immediately(self):
        """Execute content generation task immediately"""
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
                        'message': _('Content generation task "%s" has been executed. Blog post created successfully.') % task.name,
                        'type': 'success',
                        'sticky': False,
                    }
                }
                
            except Exception as e:
                # Log error and show notification
                error_msg = str(e)
                _logger.error("Content generation task %s failed: %s", task.id, error_msg)
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Task Execution Failed'),
                        'message': _('Content generation task failed: %s') % error_msg,
                        'type': 'danger',
                        'sticky': True,
                    }
                }
    
    def action_view_blog_post(self):
        """View the generated blog post"""
        self.ensure_one()
        if not self.generated_blog_post_id:
            raise ValidationError(_("No blog post has been generated yet"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Blog Post'),
            'res_model': 'blog.post',
            'res_id': self.generated_blog_post_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _mark_in_progress(self):
        """Mark task as in progress"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'started_at': fields.Datetime.now(),
            'error_message': False,
        })
        self.message_post(body=_("Content generation started"))
    
    def _mark_done(self, blog_post_id):
        """Mark task as completed successfully"""
        self.ensure_one()
        self.write({
            'state': 'done',
            'completed_at': fields.Datetime.now(),
            'generated_blog_post_id': blog_post_id,
        })
        self.message_post(body=_("Content generation completed successfully"))
    
    def _mark_error(self, error_message):
        """Mark task as failed with error message"""
        self.ensure_one()
        self.write({
            'state': 'error',
            'error_message': error_message,
            'completed_at': fields.Datetime.now(),
        })
        self.message_post(body=_("Content generation failed: %s") % error_message)

    @api.model
    def _cron_process_pending_tasks(self):
        """Cron job method to process pending content generation tasks"""
        try:
            # Find draft tasks ready for processing
            pending_tasks = self.search([('state', '=', 'draft')], limit=3)
            
            if not pending_tasks:
                _logger.info("No pending content generation tasks found")
                return
            
            _logger.info(f"Processing {len(pending_tasks)} content generation tasks")
            
            for task in pending_tasks:
                try:
                    task._process_task()
                except Exception as e:
                    _logger.error(f"Failed to process task {task.id}: {str(e)}")
                    task._mark_error(str(e))
                    
        except Exception as e:
            _logger.error(f"Error in content generation task cron job: {str(e)}")

    def _process_task(self):
        """Process individual content generation task"""
        self.ensure_one()
        
        if self.state != 'draft':
            return
        
        try:
            # Mark as in progress
            self._mark_in_progress()
            
            # Get AI agent configuration from task or fallback to active one
            agent_config = self.agent_config_id
            if not agent_config:
                agent_config = self.env['sc.ai.agent.config'].search([('active', '=', True)], limit=1)
                if not agent_config:
                    raise Exception(_("No AI agent configuration available"))
            
            # Store agent configuration used
            self.write({
                'agent_model': agent_config.model,
                'agent_instructions': agent_config.instructions,
            })
            
            # Prepare content source data with full article content
            if self.content_idea_id:
                # Using selected content idea - try to get full content
                content_source = {
                    'name': self.content_idea_id.name or '',
                    'url': self.content_idea_id.url or '',
                    'summary': self.content_idea_id.summary or '',
                }
                
                # Try to extract full content from URL
                if self.content_idea_id.url:
                    try:
                        web_reader = self.env['web.content.reader']
                        extracted_content = web_reader.extract_article_content(self.content_idea_id.url)
                        
                        if extracted_content['success']:
                            content_source.update({
                                'full_title': extracted_content['title'],
                                'full_content': extracted_content['content'],
                                'word_count': extracted_content['word_count'],
                                'reading_time': extracted_content['reading_time'],
                                'meta_description': extracted_content['meta_description'],
                            })
                            _logger.info(f"Successfully extracted {extracted_content['word_count']} words from {self.content_idea_id.url}")
                        else:
                            _logger.warning(f"Failed to extract content from {self.content_idea_id.url}: {extracted_content['error']}")
                            content_source['extraction_error'] = extracted_content['error']
                    except Exception as e:
                        _logger.error(f"Error during content extraction: {str(e)}")
                        content_source['extraction_error'] = str(e)
                
                user_instructions = self.user_prompt or ''
            else:
                # Using custom content
                content_source = {
                    'name': self.custom_topic or '',
                    'url': '',
                    'summary': self.custom_instructions or '',
                }
                user_instructions = self.user_prompt or ''
            
            # Add target word count to instructions
            if self.target_word_count:
                word_count_instruction = f"Target word count: approximately {self.target_word_count} words. "
                user_instructions = word_count_instruction + user_instructions
            
            # Perform content generation using OpenAI utils
            openai_utils = self.env['openai.utils']
            content_data = openai_utils.generate_content(
                agent_config.model,
                agent_config.instructions,
                content_source,
                user_instructions
            )
            
            # Create blog post with generated content
            blog_post = self._create_blog_post(content_data)
            
            # Mark as completed
            self._mark_done(blog_post.id)
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Content generation task {self.id} failed: {error_msg}")
            self._mark_error(error_msg)

    def _create_blog_post(self, content_data):
        """Create a blog post from generated content data"""
        self.ensure_one()
        
        # Validate content data structure
        required_fields = ['title', 'content', 'meta_description', 'keywords']
        if not all(key in content_data for key in required_fields):
            raise Exception(_("Generated content missing required fields: %s") % required_fields)
        
        # Prepare blog post values
        blog_post_values = {
            'name': content_data['title'],
            'content': content_data['content'],
            'blog_id': self.target_blog_id.id,
            'is_published': self.auto_publish,
            'author_id': self.target_author_id.id if self.target_author_id else self.env.user.partner_id.id,
        }
        
        # Add subtitle if provided
        if content_data.get('subtitle'):
            blog_post_values['subtitle'] = content_data['subtitle']
        
        # Add SEO meta tags if enabled
        if self.generate_meta_tags:
            blog_post_values.update({
                'website_meta_description': content_data['meta_description'],
                'website_meta_keywords': content_data['keywords'],
                'website_meta_title': content_data['title'],
            })
        
        # Set language if specified
        lang_code = self.target_lang_id.code if self.target_lang_id else 'en_US'
        
        # Create the blog post in the specified language context
        blog_post = self.env['blog.post'].with_context(lang=lang_code).create(blog_post_values)
        
        # Generate cover image if enabled
        if self.generate_cover_image:
            try:
                image_path = self._generate_and_save_cover_image(
                    content_data['title'],
                    content_data['content']
                )
                
                if image_path:
                    # Update blog post with cover properties containing the generated image
                    import json
                    cover_properties = {
                        "background_color_class": "o_cc o_cc1",  # Default color class
                        "background-image": f"url('{image_path}')",
                        "opacity": "0.4",  # Default opacity
                        "resize_class": "o_half_screen_height"  # Default resize class
                    }
                    blog_post.cover_properties = json.dumps(cover_properties)
                    _logger.info(f"Cover image generated and set in cover_properties for blog post {blog_post.id}")
                else:
                    _logger.warning(f"Cover image generation failed for blog post {blog_post.id}")
                    
            except Exception as e:
                _logger.error(f"Error during cover image generation for blog post {blog_post.id}: {str(e)}")
                # Don't fail the entire task if image generation fails
        
        # Log creation
        _logger.info(f"Created blog post {blog_post.id} for task {self.id}")
        
        return blog_post
    
    def _generate_and_save_cover_image(self, article_title, article_content):
        """
        Generate and save cover image for the blog post
        
        Args:
            article_title (str): Title of the article
            article_content (str): Content of the article
            
        Returns:
            str or None: Path to saved image or None if generation failed
        """
        self.ensure_one()
        
        if not self.generate_cover_image:
            return None
            
        try:
            # Import image utilities
            from ..utils.openai_image_utils import create_image_generator_from_config, get_image_generation_settings
            
            # Update status
            self.image_generation_status = 'generating'
            self.env.cr.commit()  # Commit status change
            
            # Create image generator
            image_generator = create_image_generator_from_config(self.env)
            
            # Get generation settings
            settings = get_image_generation_settings(self.env)
            
            # Use task-specific settings if provided, otherwise use defaults
            model = settings['model']
            size = self.image_size or settings['size']
            quality = self.image_quality or settings['quality']
            style = self.image_style or settings['style']
            
            # Generate image prompt
            prompt = image_generator.generate_image_prompt(
                article_title,
                article_content,
                self.image_prompt_override
            )
            
            # Store the prompt used
            self.image_generation_prompt = prompt
            
            _logger.info(f"Generating cover image for task {self.id} with prompt: {prompt[:100]}...")
            
            # Generate image
            result = image_generator.generate_image(
                prompt=prompt,
                model=model,
                size=size,
                quality=quality,
                style=style
            )
            
            if not result['success']:
                raise Exception(result['error'])
            
            # Create filename and path
            import uuid
            import os
            image_filename = f"blog_cover_{self.id}_{uuid.uuid4().hex[:8]}.png"
            
            # Get the module path for saving the image
            module_path = os.path.dirname(os.path.dirname(__file__))
            image_dir = os.path.join(module_path, 'static', 'src', 'img', 'generated')
            image_path = os.path.join(image_dir, image_filename)
            
            # Save image from base64 data
            image_data = result['data']
            if 'b64_json' in image_data:
                success = image_generator.save_image_from_base64(
                    image_data['b64_json'],
                    image_path
                )
            elif 'url' in image_data:
                success = image_generator.download_image_from_url(
                    image_data['url'],
                    image_path
                )
            else:
                raise Exception("No image data found in response")
            
            if not success:
                raise Exception("Failed to save generated image")
            
            # Store relative path for web access
            relative_path = f"/sc_marketing_automation_tool/static/src/img/generated/{image_filename}"
            self.generated_image_path = relative_path
            self.image_generation_status = 'success'
            
            # Update prompt if it was revised by DALL-E
            if 'revised_prompt' in result and result['revised_prompt']:
                self.image_generation_prompt = result['revised_prompt']
            
            _logger.info(f"Successfully generated and saved cover image for task {self.id}")
            return relative_path
            
        except Exception as e:
            error_msg = f"Error generating cover image: {str(e)}"
            _logger.error(error_msg)
            
            self.image_generation_status = 'failed'
            self.image_generation_error = error_msg
            
            return None

    @api.model
    def _cron_cleanup_old_tasks(self):
        """Clean up old completed and error tasks (older than 30 days)"""
        try:
            cutoff_date = fields.Datetime.now() - timedelta(days=30)
            old_tasks = self.search([
                ('create_date', '<', cutoff_date),
                ('state', 'in', ['done', 'error'])
            ])
            
            count = len(old_tasks)
            if count > 0:
                old_tasks.unlink()
                _logger.info(f"Cleaned up {count} old content generation tasks")
            else:
                _logger.info("No old content generation tasks to clean up")
                
        except Exception as e:
            _logger.error(f"Error cleaning up old content generation tasks: {str(e)}")
