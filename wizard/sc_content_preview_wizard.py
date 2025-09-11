from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ScContentPreviewWizard(models.TransientModel):
    _name = 'sc.content.preview.wizard'
    _description = 'Content Preview Wizard'

    content_idea_id = fields.Many2one(
        'sc.content.idea',
        string="Content Idea",
        required=True
    )
    
    extraction_success = fields.Boolean(
        string="Extraction Success",
        default=False
    )
    
    extracted_title = fields.Char(
        string="Extracted Title",
        readonly=True
    )
    
    extracted_content = fields.Text(
        string="Extracted Content (Preview)",
        readonly=True,
        help="First 2000 characters of the extracted content"
    )
    
    word_count = fields.Integer(
        string="Word Count",
        readonly=True
    )
    
    reading_time = fields.Integer(
        string="Reading Time (minutes)",
        readonly=True
    )
    
    meta_description = fields.Text(
        string="Meta Description",
        readonly=True
    )
    
    extraction_error = fields.Text(
        string="Extraction Error",
        readonly=True
    )
    
    def action_generate_content_with_full_source(self):
        """Create content generation task using the full extracted content"""
        self.ensure_one()
        
        if not self.extraction_success:
            raise ValidationError(_("Cannot generate content: extraction failed"))
        
        # Create content generation task
        task = self.env['sc.content.generation.task'].create({
            'name': _("Blog post generation for: %s") % self.content_idea_id.name,
            'content_idea_id': self.content_idea_id.id,
            'user_prompt': _("Use the full article content for comprehensive analysis and create an engaging blog post."),
            'state': 'draft',
        })
        
        # Return action to show the task
        return {
            'type': 'ir.actions.act_window',
            'name': _('Content Generation Task'),
            'res_model': 'sc.content.generation.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_close(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
