# Changelog: sc_marketing_automation_tool

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [18.0.1.0.1] - 2025-09-12

### Added - Agent-Based Content Strategy
- **Content Research Agent**: AI-powered topic discovery using WebSearchTool integration
  - New models: `sc.content.idea`, `sc.content.idea.task`
  - Web search capabilities for trending content ideas
  - Placeholder processing support ({today} replacement)
  - Structured JSON response handling
- **Content Generation Agent**: Complete blog post creation from research ideas
  - New model: `sc.content.generation.task`
  - Blog post drafting with title, content, meta description, and keywords
  - Integration with existing blog.post model
  - Unpublished draft creation for review workflow
- **AI-Powered Image Generation**: Professional blog cover images using gpt-image-1 model
  - OpenAI Direct Images API integration (not Responses API)
  - Advanced image generation parameters (size, quality, format, background)
  - Dynamic format support (PNG, JPEG, WebP)
  - Web-accessible static file storage with proper URL generation
  - Integration with content generation workflow
- **Enhanced OpenAI Usage Monitoring**: Comprehensive API usage tracking and optimization
  - Enhanced model: `sc.openai.usage.snapshot` with persistent data storage
  - Advanced usage dashboard with daily breakdown analysis
  - Image generation cost tracking and monitoring
  - Manual and automatic data synchronization with improved reliability
  - Historical data retention and trend analysis

### Enhanced - Settings Architecture Refactor
- **Centralized Settings**: Moved all configuration from General Settings to dedicated Marketing Automation section
  - New dedicated settings action and menu structure
  - Agent-specific configuration sections
  - Image generation configuration with comprehensive options
  - Enhanced organization and usability
- **OpenAI Direct Images API Integration**: Native gpt-image-1 model support
  - Direct Images API implementation (client.images.generate())
  - Advanced parameter mapping (quality, format, background, moderation)
  - Static file management with web accessibility
  - Error handling and recovery mechanisms
- **OpenAI Agents SDK Integration**: Upgraded from basic OpenAI API to OpenAI Agents SDK (>=0.2.9)
  - WebSearchTool support for content research
  - Structured agent responses with defined schemas
  - Enhanced error handling and agent orchestration
- **Multi-Agent Background Processing**: Separate cron jobs for each agent type
  - Research processor for content idea generation
  - Generation processor for blog post creation
  - Enhanced translation processor with agent improvements
  - Independent error handling and status tracking

### Enhanced - User Interface & Workflows
- **Marketing Automation Menu**: New centralized navigation structure
  - Content Ideas management (All Ideas, Generation Tasks)
  - Content Generation management (Generation Tasks)
  - OpenAI Usage monitoring dashboard with enhanced daily breakdown
  - Centralized settings access with image generation configuration
- **Agent Configuration Wizards**: New user-friendly wizards for content pipeline
  - Research ideas wizard with search query customization
  - Content generation wizard with blog integration and image generation options
  - Enhanced translation wizard with agent improvements
- **Enhanced Task Management**: Improved status tracking across all agent types
  - Color-coded status indicators
  - Detailed error reporting and recovery
  - Task history and audit trails
  - Image generation status tracking and error handling

### Migration - Settings and Data Preservation
- **Automatic Settings Migration**: Seamless migration from General Settings to Marketing Automation
- **Backward Compatibility**: All existing translation functionality preserved and enhanced
- **Data Integrity**: Existing translation tasks and blog posts remain fully functional
- **Configuration Upgrade**: Existing OpenAI credentials automatically migrated to new structure

### Technical - Architecture & Dependencies
- **Multi-Agent Architecture**: Specialized AI agents with dedicated configurations
  - Content Research Agent with WebSearchTool integration
  - Content Generation Agent with blog post creation
  - Image Generation Agent with gpt-image-1 Direct Images API
  - Enhanced Translation Agent with OpenAI Agents SDK
- **OpenAI Direct Images API**: Native gpt-image-1 model integration
  - Static file management with web-accessible URLs
  - Advanced parameter handling (quality, format, background)
  - Error handling and recovery mechanisms
- **Enhanced Data Models**: New and improved models for comprehensive content management
  - Image generation metadata and status tracking
  - Persistent usage data storage with daily breakdown
  - Enhanced error logging and recovery information
- **OpenAI Agents SDK**: External dependency upgrade to >=0.2.9
- **Structured Responses**: JSON-based AI output processing with defined schemas
- **Enhanced Security**: Agent-specific access controls and credential management
- **Improved Error Handling**: Agent-specific error patterns and recovery mechanisms

## [18.0.1.1.0] - 2025-09-10

### Fixed
- **CRITICAL**: Resolved translation content corruption issue where original English content was being overwritten
- **Translation Method**: Replaced unreliable `update_field_translations()` approach with proven `with_context(lang=target_lang).write()` method
- **Content Integrity**: Implemented mandatory content preservation verification in all translation operations
- **Error Recovery**: Added automatic restoration of corrupted content when translation errors are detected

### Enhanced
- **HTML Structure Validation**: Comprehensive validation for blog post content to ensure HTML consistency across languages
- **Translation Verification**: New verification methods to confirm translation integrity and content preservation
- **Blog Post Specialist Methods**: Dedicated translation methods specifically designed for complex HTML content (blog posts, CMS content)
- **Error Handling**: Enhanced error patterns with clear recovery steps and diagnostic information

### Added
- **Production-Ready Translation Pattern**: Field-tested and verified translation approach that works reliably for ALL field types
- **Content Preservation Verification**: Automatic verification that original English content is never overwritten
- **HTML Tag Validation**: Structure validation for critical HTML tags (div, p, h1-h6, ul, ol, li) to maintain formatting
- **Translation Testing Protocol**: Comprehensive testing guidelines for fresh content, content preservation, and clean database scenarios

### Removed
- **Non-functional "Restore Original Content" Button**: Removed misleading button that only showed notifications without actual restoration functionality
- **Deprecated Translation Methods**: Eliminated unreliable `update_field_translations()` usage that caused SQL transaction errors
- **Excessive Debug Dependencies**: Cleaned up temporary files and debugging artifacts for production readiness

### Technical Improvements
- **Unified Context Write Approach**: Single, reliable method for all translatable field types (simple text, HTML content, SEO metadata)
- **Auto-Recovery Mechanisms**: Automatic detection and restoration of content corruption during translation operations
- **Field-Type Awareness**: Proper handling of different translation field types (`translate=True` vs `translate=html_translate`)
- **SQL Transaction Stability**: Eliminated transaction conflicts that caused translation failures in Odoo 18.0

### Documentation Updates
- **Translation Guidelines**: Updated development guidelines with proven best practices for Odoo 18.0 translation system
- **Error Recovery Patterns**: Documented common translation issues and their solutions
- **Production Readiness Checklist**: Clear requirements for deploying translation functionality
- **Testing Protocols**: Comprehensive testing guidelines for translation integrity

### Performance Improvements
- **Reduced Error Rates**: Eliminated content corruption issues that required manual intervention
- **Simplified Codebase**: Removed complex, unreliable methods in favor of proven, straightforward approaches
- **Better Error Reporting**: More accurate error messages with actionable recovery steps

## [18.0.1.0.0] - 2025-09-09

### Added
- **Initial Release**: Content Management Tool for Odoo with AI-powered blog post translation
- **OpenAI Integration**: Complete integration with OpenAI Agents SDK for professional translations
- **Translation Wizard**: User-friendly wizard for selecting target languages and providing AI instructions
- **Task Management**: Comprehensive translation task tracking with status management (draft/in_progress/done/error)
- **Background Processing**: Asynchronous cron job for handling translation requests without UI blocking
- **Configuration Interface**: Settings panel for OpenAI API credentials and model selection
- **Security Framework**: Role-based access control with Marketing Manager and Marketing User roles
- **Multi-language Support**: Complete Spanish translation (es_ES.po) with English base
- **Error Handling**: Robust error management with detailed error messages and task retry capabilities
- **Blog Integration**: Seamless integration with Odoo Website Blog module including translation history

### Technical Implementation
- **Models**: 
  - `sc.translation.task` with mail.thread integration for chatter support
  - Extended `blog.post` model with translation tracking fields
  - Extended `res.config.settings` for OpenAI configuration
  - `openai.utils` utility class for AI operations
- **Views**: 
  - Odoo 18.0 compliant views using `<list>` instead of `<tree>`
  - Kanban view with meaningful `default_group_by="state"`
  - Modal wizard for translation configuration
  - Settings view with stable anchor from base_setup core example
- **Security**: 
  - Access control lists (ACL) for proper permission management
  - Security groups for different user roles
  - Environment variable handling for API credentials
- **Background Jobs**: 
  - Cron job processing up to 10 tasks every 5 minutes
  - Error isolation and recovery mechanisms
- **Server Actions**: 
  - Model Methods First pattern implementation
  - "Translate with AI" action in blog post list view

### Dependencies
- **Odoo Modules**: base, website, website_blog, mail
- **External Python Package**: openai-agents >= 0.2.9
- **Python Version**: 3.9+ recommended

### Documentation
- **Technical Documentation**: Complete technical specifications and architecture guide
- **Functional Documentation**: User guide with best practices and troubleshooting
- **API Documentation**: OpenAI integration patterns and error handling
- **Multi-language README**: English and Spanish documentation

### Configuration Requirements
- OpenAI API key (required)
- OpenAI Organization ID (optional but recommended)
- Active target languages in Odoo

### Known Limitations
- Requires internet connectivity for AI translation services
- OpenAI API usage costs apply based on content length and model selection
- Translation quality depends on source content structure and AI model capabilities

### Future Enhancements
- Unit and integration test suite implementation
- Support for additional AI providers
- Advanced translation memory features
- Batch translation optimization
- Translation quality metrics and reporting

---

**Module Information:**
- **Author**: Gilson Rincón, CEO & Founder, Solutto Consulting LLC
- **License**: LGPL-3
- **Support**: support@soluttoconsulting.com
- **Website**: https://soluttoconsulting.com
