# -*- coding: utf-8 -*-
{
    'name': 'Marketing Automation Tool',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Content Management Tool for Marketing Automation',
    'description': """
        Content Management Tool for Odoo
        
        This module centralizes and simplifies marketing and content management tasks,
        leveraging external automation tools like n8n.
        
        Features:
        - Configuration panel for automation service credentials
        - Semi-automated blog article translation workflow
        - Integration with external translation services
        - Translation status management
        
        Version 1.0 includes:
        - General configuration for n8n API integration
        - Blog post translation workflow with status tracking
        - Callback endpoint for receiving translated content
    """,
    'author': 'Solutto Consulting LLC',
    'maintainer': 'Gilson Rincón <gilson.rincon@soluttoconsulting.com>',
    'website': 'https://soluttoconsulting.com',
    'depends': [
        'base',
        'base_setup',
        'website',
        'website_blog',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/blog_post_view.xml',
        'wizards/blog_post_translation_wizard_view.xml',
        'data/data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
