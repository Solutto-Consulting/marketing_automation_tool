# Implementation Plan: sc_marketing_automation_tool (v18.0.1.0.0)

## Plan Metadata
- **Module Name**: sc_marketing_automation_tool
- **Module Path**: /home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool
- **Spec Path**: /home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool/docs/Technical-specs-v2025-sep-04.md
- **Spec Version**: v2025-sep-04
- **Last Updated**: 2025-09-09T00:00:00Z
- **Target Odoo Version**: 18.0

---

## Module Overview

The **Content Management Tool for Odoo** enhances and automates marketing activities by integrating OpenAI for AI-powered content translation of blog posts. This initial version provides administrators with bulk translation capabilities via a user-friendly wizard, asynchronous background processing through cron jobs, and comprehensive task tracking with status management.

**Key Features:**
- OpenAI integration with centralized configuration
- Bulk blog post translation with AI
- User-friendly translation wizard
- Asynchronous background processing
- Translation task logging and status management
- Error handling and task reset capabilities

---

## External Research

### OpenAI Agents Python Library
- **Library**: openai-agents
- **Installation**: `pip install openai-agents`
- **Official Repository**: https://github.com/openai/openai-agents-python
- **Documentation**: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md
- **Usage Pattern**: Asynchronous Agent/Runner architecture
- **Version**: Latest stable (0.2.9 available)
- **Key Classes**: 
  - `Agent`: Configures AI assistant with instructions and model
  - `Runner`: Executes agent interactions asynchronously

**Integration Requirements**:
- Environment variables for API key/organization ID management
- Async/await pattern within Odoo cron context
- Error handling for API timeouts and rate limits
- JSON-based prompt/response structure for content translation

---

## Core Examples Research

**Settings Configuration Inheritance**:
- **Reference Path**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anchor Strategy**: Use stable `//setting[@id='...']` xpath selectors
- **Inherit ID**: `base_setup.res_config_settings_view_form` (confirmed available)
- **Pattern**: Place settings within `<setting>` blocks with descriptive IDs

---

## Milestone 1: Module Foundation & Configuration

### Task 1 → SP-3.1 & SP-4
**Task**: Module Structure and Dependencies Setup
**Description**: Create base module structure with proper Odoo 18.0 manifest and dependencies
**Technical Instructions**:
- Create `__init__.py` and `__manifest__.py` with dependencies: base, website, website_blog
- Add external library requirements.txt with openai-agents
- Follow Solutto standards: English-only, proper structure, i18n setup
- [ ] Complete

### Task 2 → SP-4
**Task**: OpenAI Configuration Settings
**Description**: Implement res.config.settings inheritance for OpenAI credentials
**Technical Instructions**:
- Inherit from `base_setup.res_config_settings_view_form` (reference: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`)
- Use stable anchor: `//setting[@id='partner_autocomplete']` with `position="after"`
- Create AI Marketing Tools section with fields: sc_openai_api_key (password=True), sc_openai_organization_id, sc_openai_model (Selection)
- Implement dynamic model selection via OpenAI API call with fallback defaults
- [ ] Complete

### Task 3 → SP-4
**Task**: Dynamic Model Selection Implementation
**Description**: API-driven OpenAI model selection with fallback
**Technical Instructions**:
- Method to call OpenAI v1/models endpoint
- Filter models (gpt- prefix), return tuple list for Selection field
- Fallback to ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'] on API failure
- Default: gpt-4o
- [ ] Complete

---

## Milestone 2: Data Models & Core Logic

### Task 4 → SP-5.1
**Task**: Translation Task Model
**Description**: Create sc.translation.task model for tracking translations
**Technical Instructions**:
- Model: sc.translation.task
- Fields: name (Char, required), blog_post_id (Many2one, ondelete='cascade'), target_lang_id (Many2one), system_instructions (Text), state (Selection: draft/in_progress/done/error), error_message (Text)
- Inherit mail.thread for chatter integration (add "mail" to depends)
- [ ] Complete

### Task 5 → SP-5.2
**Task**: Blog Post Extension
**Description**: Extend blog.post model with translation tracking
**Technical Instructions**:
- Inherit blog.post model
- Add fields: translation_task_ids (One2many), translation_in_progress (Boolean, default=False)
- Ensure proper relationship with sc.translation.task
- [ ] Complete

---

## Milestone 3: User Interface & Views

### Task 6 → SP-6.1
**Task**: Server Action Implementation
**Description**: Create "Translate with AI" server action for blog.post
**Technical Instructions**:
- ir.actions.server record targeting blog.post model
- Action launches sc.translate.blog.post.wizard
- Apply Odoo 18.0 standards: use `<list>` instead of `<tree>`
- [ ] Complete

### Task 7 → SP-6.2
**Task**: Translation Wizard
**Description**: Create wizard for translation input
**Technical Instructions**:
- Transient model: sc.translate.blog.post.wizard
- Fields: target_lang_id (Many2one with domain: website_published=True), system_instructions (Text)
- Form view with modal dialog presentation
- Buttons: Translate (action) and Cancel
- [ ] Complete

### Task 8 → SP-6.3
**Task**: Translation Task Views
**Description**: Create management views for translation tasks
**Technical Instructions**:
- Menu: Marketing Automation > Content Translation > Translation Tasks
- List view: name, blog_post_id, target_lang_id, state (widget="badge" with decorations)
- Form view: all details, error_message (conditional), "Reset to Draft" button
- Kanban view with meaningful default_group_by (MANDATORY: use state field)
- [ ] Complete

### Task 9 → SP-6.4
**Task**: Blog Post Form Enhancement
**Description**: Add translation history to blog.post form
**Technical Instructions**:
- Add "Translation History" page to notebook
- Display translation_task_ids as tree view
- Include chatter at form end (after </sheet>)
- [ ] Complete

---

## Milestone 4: Business Logic & AI Integration

### Task 10 → SP-7.1
**Task**: Translation Wizard Logic
**Description**: Implement wizard action for task creation
**Technical Instructions**:
- Process active_ids from context (selected blog posts)
- Skip posts with translation_in_progress=True
- Create sc.translation.task records with state='draft'
- Set blog_post.translation_in_progress=True
- User notification for skipped posts
- [ ] Complete

### Task 11 → SP-7.2 & SP-3.2
**Task**: OpenAI Integration Utility
**Description**: Create async AI translation function using openai-agents SDK
**Technical Instructions**:
- Create utility module for openai-agents integration
- Async function: perform_ai_translation(model_name, system_instructions, prompt)
- Agent configuration with proper instructions and model selection
- Environment variable setup for API credentials
- Error handling for API failures, timeouts, rate limits
- [ ] Complete

### Task 12 → SP-7.2
**Task**: Cron Job Implementation
**Description**: Background processing for translation tasks
**Technical Instructions**:
- ir.cron record: runs every 5 minutes
- Search sc.translation.task with state='draft', limit 10 per run
- For each task: update to in_progress, prepare data, build prompt, execute AI call
- JSON structure for blog fields: name, subtitle, content, website_meta_title, website_meta_description, website_meta_keywords
- Update blog post with translated content and task state
- Comprehensive error handling with error_message logging
- [ ] Complete

---

## Milestone 5: Security & Permissions

### Task 13 → Security
**Task**: Access Control Implementation
**Description**: Create security groups, ACLs, and record rules
**Technical Instructions**:
- Groups: Marketing Manager (full access), Marketing User (read/create)
- ir.model.access.csv for sc.translation.task model
- Record rules for multi-company environments if applicable
- Least privilege principle with admin maintaining full access
- [ ] Complete

### Task 14 → Security
**Task**: Environment Variables Security
**Description**: Secure API key management
**Technical Instructions**:
- Document environment variable setup for OpenAI credentials
- Ensure no hardcoded secrets in code
- Implement proper credential validation in configuration
- [ ] Complete

---

## Milestone 6: Testing & Quality Assurance

### Task 15 → Testing
**Task**: Unit Test Suite
**Description**: Comprehensive test coverage for core functionality
**Technical Instructions**:
- Test wizard task creation logic
- Test cron job processing (mock OpenAI calls)
- Test configuration settings validation
- Test error handling scenarios
- Install/upgrade tests
- [ ] Complete

### Task 16 → Testing
**Task**: Integration Tests
**Description**: End-to-end workflow testing
**Technical Instructions**:
- Test complete translation workflow
- Test multi-language scenarios
- Test error recovery and task reset
- Performance testing for bulk operations
- [ ] Complete

---

## Milestone 7: Documentation & Localization

### Task 17 → i18n
**Task**: Internationalization Setup
**Description**: Create and maintain translation files
**Technical Instructions**:
- Create i18n/es_ES.po file
- Mark all user-facing strings with _() using English base strings
- Ensure model descriptions, field labels, and help texts are translatable
- [ ] Complete

### Task 18 → Documentation
**Task**: Module Documentation
**Description**: Create comprehensive documentation
**Technical Instructions**:
- README.md (English) and README.es.md (Spanish) at module root
- Functional documentation in docs/functional/
- Technical documentation in docs/technical/
- Installation and configuration guides
- User manuals with screenshots
- [ ] Complete

---

## Milestones & PR Strategy

### Milestone 1: Foundation (Tasks 1-3)
- [x] Task 1: Module Structure and Dependencies Setup
- [x] Task 2: OpenAI Configuration Settings  
- [x] Task 3: Dynamic Model Selection Implementation

### Milestone 2: Data Models (Tasks 4-5)
- [x] Task 4: Translation Task Model
- [x] Task 5: Blog Post Extension

### Milestone 3: User Interface (Tasks 6-9)
- [x] Task 6: Server Action Implementation
- [x] Task 7: Translation Wizard
- [x] Task 8: Translation Task Views
- [x] Task 9: Blog Post Form Enhancement

### Milestone 4: Business Logic (Tasks 10-12)
- [x] Task 10: Translation Wizard Logic
- [x] Task 11: OpenAI Integration Utility
- [x] Task 12: Cron Job Implementation

### Milestone 5: Security (Tasks 13-14)
- [x] Task 13: Access Control Implementation
- [x] Task 14: Environment Variables Security

### Milestone 6: Testing (Tasks 15-16)
- [ ] Task 15: Unit Test Suite
- [ ] Task 16: Integration Tests

### Milestone 7: Documentation (Tasks 17-18)
- [x] Task 17: Internationalization Setup
- [x] Task 18: Module Documentation

---

## Acceptance Checklist

### Odoo 18.0 Standards Compliance
- [ ] All list views use `<list>` instead of `<tree>`
- [ ] Conditional UI uses `invisible`, `readonly`, `required`, `column_invisible` (no legacy `attrs`)
- [ ] Kanban view defines meaningful `default_group_by` (state field)
- [ ] Chatter integration properly implemented where applicable
- [ ] Settings view uses stable anchors from core examples

### Technical Requirements
- [ ] OpenAI agents SDK properly integrated with async/await pattern
- [ ] Dynamic model selection with API fallback implemented
- [ ] Comprehensive error handling for API failures and timeouts
- [ ] Environment variables used for secure credential management
- [ ] Cron job handles bulk processing with appropriate limits

### Quality Assurance
- [ ] Security groups and ACLs implemented with least privilege
- [ ] Unit and integration tests cover primary business flows
- [ ] Install/upgrade tests pass successfully
- [ ] Multi-company compatibility where applicable

### Documentation & Localization
- [ ] i18n/es_ES.po file created and maintained
- [ ] English base strings properly marked for translation
- [ ] README.md and README.es.md files present and synchronized
- [ ] Technical and functional documentation complete
- [ ] Installation and configuration guides provided

### External Dependencies
- [ ] requirements.txt includes openai-agents with pinned version
- [ ] External library integration documented with official links
- [ ] API rate limits and timeout handling implemented
- [ ] Graceful degradation for API unavailability

---

## Plan Changelog

### 2025-09-09T00:00:00Z - v2025-sep-04 - Initial Plan Creation
- Created comprehensive implementation plan for sc_marketing_automation_tool v18.0.1.0.0
- **External Research**: 
  - OpenAI Agents Python library (official repo: https://github.com/openai/openai-agents-python)
  - Core settings configuration patterns from base_setup module
- Structured plan into 7 milestones with 18 detailed tasks
- Incorporated Solutto standards and Odoo 18.0 compliance requirements
- Defined security, testing, and documentation requirements
- Included acceptance checklist with compliance gates

### 2025-09-09T01:00:00Z - v2025-sep-04 - Implementation Completed
- **Milestones 1-5 and 7 COMPLETED** (16/18 tasks)
- **Core Implementation**:
  - Module scaffold with proper Odoo 18.0 manifest and structure
  - OpenAI integration using official openai-agents SDK
  - Configuration settings with stable anchor from base_setup core example
  - Translation task model with mail.thread integration and chatter
  - Blog post extension with translation tracking
  - Complete UI implementation using `<list>` views (Odoo 18.0 standard)
  - Kanban with `default_group_by="state"` (compliance requirement)
  - Translation wizard with modal presentation
  - Server action using Model Methods First pattern
  - Cron job for background processing with error handling
  - Security groups and ACLs implementation
  - Complete Spanish i18n translation
  - Technical and functional documentation

- **Compliance Verification**:
  - ✅ All views use `<list>` instead of `<tree>`
  - ✅ Conditional UI uses modern attributes (no legacy `attrs`)
  - ✅ Kanban defines meaningful `default_group_by`
  - ✅ Chatter integration with `mail` dependency
  - ✅ Settings use stable anchor from core examples
  - ✅ Environment variables for API security
  - ✅ Server actions follow Model Methods First pattern

- **Remaining**: Testing implementation (Tasks 15-16) - Ready for manual testing phase
