{
    # Module Identity
    'name': 'AI Content Management Tool for Odoo',
    'version': '18.0.1.0.1',
    'summary': 'AI-powered content automation with research and generation agents',
    'description': """
AI Content Management Tool for Odoo
====================================

This module enhances and automates marketing activities within the Odoo ecosystem 
by integrating Artificial Intelligence for content automation and strategy.

Key Features (v18.0.1.0.1):
* Content Research Agent: AI-powered topic idea generation using web search
* Content Generation Agent: Automated blog post creation from research ideas
* OpenAI usage monitoring and cost tracking dashboard
* Centralized settings in dedicated Marketing Automation section
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
    
    # Module Classification
    'category': 'Marketing',
    'license': 'OPL-1',
    
    # Author and Support Information
    'author': 'Solutto Consulting LLC',
    'website': 'https://soluttoconsulting.com',
    'support': 'support@soluttoconsulting.com',
    
    # Pricing Information
    'price': 25.00,
    'currency': 'USD',
    
    # Dependencies
    'depends': [
        'base',
        'website',
        'website_blog',
        'mail',
    ],
    'external_dependencies': {
        'python': ['asyncio', 'tiktoken', 'python-dateutil'],
    },
    
    # Data Files (load order is critical)
    'data': [
        # Security must come first
        'security/sc_marketing_automation_tool_security.xml',
        'security/ir.model.access.csv',
        
        # Data and configuration (basic setup)
        'data/ir_cron_data.xml',
        
        # Views (must load before menus that reference them)
        # AI agent config views MUST load before settings views (action dependency)
        'views/sc_ai_agent_config_views.xml',
        'views/res_config_settings_views.xml',
        'views/sc_content_idea_views.xml',
        'views/sc_content_idea_task_views.xml',
        'views/sc_content_generation_task_views.xml',
        
        # OpenAI monitoring views - actions MUST load before menus
        'views/sc_openai_request_log_views.xml',
        'views/sc_openai_model_statistics_views.xml',
        
        # Wizard views (contain actions referenced by menus)
        'views/sc_generate_ideas_wizard_views.xml',
        'views/sc_generate_content_wizard_views.xml',
        'views/sc_content_preview_wizard_views.xml',
        
        # Data that depends on views/actions (load after views)
        'data/sc_ai_agent_config_data.xml',
        
        # Menus must load LAST (after all actions are defined)
        'views/menu_views.xml',
    ],
    
    # Demo Data
    'demo': [],
    
    # Test Files
    'test': [],
    
    # Static Resources
    'images': ['static/description/banner.png'],
    
    # Installation Properties
    'installable': True,
    'auto_install': False,
    'application': True,
}
