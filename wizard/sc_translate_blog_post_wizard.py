from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ScTranslateBlogPostWizard(models.TransientModel):
    _name = 'sc.translate.blog.post.wizard'
    _description = 'Blog Post Translation Wizard'
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string="Target Language",
        required=True,
        domain=[('active', '=', True)],
        help="Select the target language for translation"
    )
    
    system_instructions = fields.Text(
        string="AI Instructions",
        help="Optional instructions to guide the AI's tone and style for the translation"
    )
    
    blog_post_ids = fields.Many2many(
        'blog.post',
        string="Blog Posts",
        help="Blog posts selected for translation"
    )
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        
        # Get selected blog posts from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['blog_post_ids'] = [(6, 0, active_ids)]
            
        return res
    
    def action_translate(self):
        """Execute the translation process"""
        if not self.blog_post_ids:
            raise UserError(_("No blog posts selected for translation."))
        
        if not self.target_lang_id:
            raise UserError(_("Please select a target language."))
        
        # Check API configuration
        api_key = self.env['ir.config_parameter'].sudo().get_param('sc_marketing_automation_tool.openai_api_key')
        if not api_key:
            raise UserError(_(
                "OpenAI API key not configured. "
                "Please configure it in Settings > General Settings > AI Marketing Tools."
            ))
        
        created_tasks = []
        skipped_posts = []
        
        for blog_post in self.blog_post_ids:
            # Skip posts already in translation
            if blog_post.translation_in_progress:
                skipped_posts.append(blog_post.name)
                continue
            
            # Check if translation to this language already exists
            existing_task = self.env['sc.translation.task'].search([
                ('blog_post_id', '=', blog_post.id),
                ('target_lang_id', '=', self.target_lang_id.id),
                ('state', 'in', ['draft', 'in_progress'])
            ], limit=1)
            
            if existing_task:
                skipped_posts.append(f"{blog_post.name} (already queued)")
                continue
            
            # Create translation task
            task_vals = {
                'blog_post_id': blog_post.id,
                'target_lang_id': self.target_lang_id.id,
                'system_instructions': self.system_instructions,
                'state': 'draft',
            }
            
            task = self.env['sc.translation.task'].create(task_vals)
            created_tasks.append(task)
            
            # Mark blog post as in progress
            blog_post.write({'translation_in_progress': True})
        
        # Handle the result and close the wizard
        if created_tasks:
            # Success case - just close the wizard
            # The user can see the tasks in the Translation Tasks menu
            return {'type': 'ir.actions.act_window_close'}
        elif skipped_posts:
            # Show warning about skipped posts
            message = _("All selected posts were skipped: %s") % ", ".join(skipped_posts)
            raise UserError(message)
        else:
            raise UserError(_("No translation tasks were created."))
    
    def action_cancel(self):
        """Cancel the wizard"""
        return {'type': 'ir.actions.act_window_close'}
