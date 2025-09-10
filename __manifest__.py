{
    'name': 'Content Management Tool for Odoo',
    'version': '18.0.1.1.0',
    'category': 'Marketing',
    'summary': 'AI-powered content translation and marketing automation tools',
    'description': """
Content Management Tool for Odoo
=================================

This module enhances and automates marketing activities within the Odoo ecosystem 
by integrating Artificial Intelligence for content translation processes.

Key Features:
* OpenAI integration with centralized configuration
* Bulk blog post translation with AI using proven, corruption-free methods
* User-friendly translation wizard
* Asynchronous background processing
* Translation task logging and status management
* Error handling and task reset capabilities
* HTML structure validation for complex content
* Content preservation verification and auto-recovery

Technical Improvements (v18.0.1.1.0):
* CRITICAL FIX: Eliminated content corruption issues in translation system
* Unified context write approach for all translatable field types
* Production-ready translation methods with zero data loss
* Enhanced error recovery and diagnostic capabilities

Technical Requirements:
* External Python library: openai-agents
* OpenAI API credentials required
* Python 3.9+ recommended
    """,
    'author': 'Solutto Consulting LLC',
    'website': 'https://soluttoconsulting.com',
    'support': 'support@soluttoconsulting.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'website_blog', 
        'mail',
    ],
    'external_dependencies': {
        'python': ['asyncio'],
    },
    'data': [
        # Security must come first
        'security/sc_marketing_automation_tool_security.xml',
        'security/ir.model.access.csv',
        # Data and configuration
        'data/cron_jobs.xml',
        'data/server_actions.xml',
        # Views
        'views/res_config_settings_views.xml',
        'views/sc_translation_task_views.xml',
        'views/blog_post_views.xml',
        'views/menu_views.xml',
        # Wizard views
        'wizard/sc_translate_blog_post_wizard_views.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
