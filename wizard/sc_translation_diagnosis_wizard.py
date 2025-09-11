from odoo import api, fields, models, _


class TranslationDiagnosisWizard(models.TransientModel):
    _name = 'sc.translation.diagnosis.wizard'
    _description = 'Translation Diagnosis Wizard'
    
    task_id = fields.Many2one('sc.translation.task', string='Translation Task')
    blog_post_id = fields.Many2one('blog.post', string='Blog Post')
    diagnosis_text = fields.Text('Diagnosis Results', readonly=True)
    
    def action_retranslate(self):
        """Apply fix translation from diagnosis wizard"""
        if self.task_id:
            return self.task_id.action_retranslate_blog_post()
        else:
            return {'type': 'ir.actions.act_window_close'}
