{
    'name': 'SC Marketing Automation Tool',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'AI-powered content management and blog translation automation',
    'description': """
        SC Marketing Automation Tool
        ============================
        
        AI-powered content management tool that automates blog post translation 
        using OpenAI's Agent SDK, providing efficient asynchronous background 
        processing with comprehensive status tracking and error management.
        
        Key Features:
        * Bulk blog post translation with OpenAI Agent SDK
        * Asynchronous background processing via cron jobs
        * User-friendly wizard for translation requests
        * Complete audit trail with chatter integration
        * Multi-language support with custom AI instructions
        * Comprehensive error handling and status management
        
        This module replaces manual Odoo translation workflows with intelligent
        AI-powered automation, significantly reducing time and effort for content
        localization while maintaining quality and consistency.
    """,
    'author': 'Solutto Consulting LLC',
    'maintainer': 'Gilson Rincón <gilson.rincon@soluttoconsulting.com>',
    'website': 'https://soluttoconsulting.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',
        'website_blog',
        'mail',  # Required for chatter integration
    ],
    'external_dependencies': {
        'python': ['openai-agents'],
    },
    'data': [
        # Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        
        # Data
        'data/menu_data.xml',
        'data/ir_actions_server_data.xml',
        'data/ir_cron_data.xml',
        
        # Views
        'views/res_config_settings_views.xml',
        'views/sc_translation_task_views.xml',
        'views/blog_post_views.xml',
        'views/wizard_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 100,
}
