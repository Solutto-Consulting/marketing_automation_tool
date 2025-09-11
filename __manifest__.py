{
    'name': 'Content Management Tool for Odoo',
    'version': '18.0.1.0.1',
    'category': 'Marketing',
    'summary': 'AI-powered content automation with research and generation agents',
    'description': """
Content Management Tool for Odoo
=================================

This module enhances and automates marketing activities within the Odoo ecosystem 
by integrating Artificial Intelligence for content automation and strategy.

Key Features (v18.0.1.0.1):
* Content Research Agent: AI-powered topic idea generation using web search
* Content Generation Agent: Automated blog post creation from research ideas
* OpenAI usage monitoring and cost tracking dashboard
* Centralized settings in dedicated Marketing Automation section
* Legacy translation features with proven corruption-free methods
* Asynchronous background processing with cron jobs
* Task tracking and status management
* Comprehensive error handling and recovery

Agent-Based Automation:
* WebSearchTool integration for content research
* Structured JSON response processing
* Placeholder replacement system ({today} support)
* Multi-language content generation support

Technical Improvements:
* OpenAI Agents SDK integration
* Usage API monitoring with daily snapshots
* Enhanced settings organization and management
* Production-ready agent orchestration

Technical Requirements:
* External Python library: openai-agents>=0.2.9
* OpenAI API credentials with organization access
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
        'data/ir_cron_data.xml',
        'data/server_actions.xml',
        # Views (must load before menus that reference them)
        'views/res_config_settings_views.xml',
        'views/sc_translation_task_views.xml',
        'views/sc_content_idea_views.xml',
        'views/sc_content_idea_task_views.xml',
        'views/sc_content_generation_task_views.xml',
        'views/sc_openai_usage_views.xml',
        'views/blog_post_views.xml',
        # Wizard views (contain actions referenced by menus)
        'wizard/sc_translate_blog_post_wizard_views.xml',
        'views/sc_generate_ideas_wizard_views.xml',
        'views/sc_generate_content_wizard_views.xml',
        # Menus must load LAST (after all actions are defined)
        'views/menu_views.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
