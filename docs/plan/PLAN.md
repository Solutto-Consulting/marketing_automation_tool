# Implementation Plan: SC Marketing Automation Tool v18.0.1.0.1

## Plan Metadata
- **Module**: sc_marketing_automation_tool
- **Target Version**: 18.0.1.0.1
- **Spec Version**: 18.0.1.0.1
- **Spec Path**: `/home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool/docs/Technical Specifications v18.0.1.0.1.md`
- **Module Path**: `/home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool`
- **Last Updated**: 2025-09-11T17:00:00Z

---

## Module Overview

This version introduces powerful "Agent-based" functionalities moving beyond simple translation to proactive content strategy and creation. The core focus is on implementing two new AI agents: a **Content Research Agent** for generating topic ideas using web search capabilities, and a **Content Generation Agent** for drafting complete blog articles. Additionally, this version implements an OpenAI API usage monitoring dashboard and consolidates all module settings into a dedicated settings section within Odoo for better organization and usability.

---

## Milestones & PR Strategy

### Phase 1: Settings Refactoring & Infrastructure (Foundation)
- [ ] **Task 1** → SP-2: Create dedicated res.config.settings view with Marketing Automation section
- [ ] **Task 2** → SP-2: Migrate existing OpenAI configuration fields to new settings page
- [ ] **Task 3** → SP-2: Create new menu item "Settings > Marketing Automation" with dedicated action
- [ ] **Task 4** → SP-2: Update existing translation feature to use new centralized settings
- [ ] **Task 5**: Add required external libraries to requirements.txt (openai-agents)

### Phase 2: Content Research Agent Implementation
- [ ] **Task 6** → SP-3.1: Create sc.content.idea model with required fields
- [ ] **Task 7** → SP-3.1: Create sc.content.idea.task model with state management
- [ ] **Task 8** → SP-3.2: Add Content Research Agent configuration fields to settings
- [ ] **Task 9** → SP-3.3: Create menu items and tree/form views for content ideas
- [ ] **Task 10** → SP-3.3: Implement sc.generate.ideas.wizard (TransientModel)
- [ ] **Task 11** → SP-3.4: Create cron job for processing research tasks
- [ ] **Task 12** → SP-3.4: Implement OpenAI Agents SDK integration with WebSearchTool
- [ ] **Task 13** → SP-3.4: Add placeholder processing logic ({today} replacement)
- [ ] **Task 14** → SP-3.4: Implement structured JSON response parsing

### Phase 3: Content Generation Agent Implementation
- [ ] **Task 15** → SP-4.1: Create sc.content.generation.task model
- [ ] **Task 16** → SP-4.2: Add Content Generation Agent configuration to settings
- [ ] **Task 17** → SP-4.3: Create generation tasks menu and views
- [ ] **Task 18** → SP-4.3: Implement sc.generate.content.wizard with blog.post integration
- [ ] **Task 19** → SP-4.4: Create cron job for content generation processing
- [ ] **Task 20** → SP-4.4: Implement blog.post creation with structured AI output

### Phase 4: OpenAI Usage Monitoring Dashboard
- [ ] **Task 21** → SP-5.1: Research OpenAI Usage API endpoints and authentication
- [ ] **Task 22** → SP-5.1: Create sc.openai.usage.snapshot model
- [ ] **Task 23** → SP-5.2: Create OpenAI Usage dashboard view with graph components
- [ ] **Task 24** → SP-5.2: Implement "Fetch Latest Data" button functionality
- [ ] **Task 25** → SP-5.2: Create automated nightly cron job for usage data collection

### Phase 5: Security, Testing & Documentation
- [ ] **Task 26**: Implement security groups and ACLs for new models
- [ ] **Task 27**: Create record rules for multi-company environments
- [ ] **Task 28**: Write unit tests for agent functionality and API integrations
- [ ] **Task 29**: Create integration tests for wizard workflows
- [ ] **Task 30**: Update i18n/es_ES.po with new translatable strings
- [ ] **Task 31**: Update README.md and README.es.md files
- [ ] **Task 32**: Update module documentation (functional/technical guides)

---

## Technical Deliverables

### 1. UI/Views Implementation

#### Settings Views
- **Reference Pattern**: Following Odoo 18.0 standards for res.config.settings inheritance
- **Core Example**: Since no specific core example was found in the current workspace, will follow the standard pattern from `base_setup.res_config_settings_view_form` inheritance
- **Views to Create**:
  - `res_config_settings_view_form_inherit_sc_marketing` - Main settings inheritance view
  - Organized sections for:
    - OpenAI API Configuration (migrated fields)
    - Content Research Agent settings
    - Content Generation Agent settings

#### List Views (using `<list>` tag per Odoo 18.0 standards)
- `sc_content_idea_view_tree` - Ideas list with search/filter capabilities
- `sc_content_idea_task_view_tree` - Research tasks with state filtering
- `sc_content_generation_task_view_tree` - Generation tasks management
- `sc_openai_usage_snapshot_view_tree` - Usage statistics table

#### Form Views
- `sc_content_idea_view_form` - Individual idea details
- `sc_content_idea_task_view_form` - Task tracking with progress indicators
- `sc_content_generation_task_view_form` - Generation task details
- `sc_openai_usage_dashboard_view` - Custom dashboard with graphs

#### Wizard Views
- `sc_generate_ideas_wizard_view_form` - Research parameters input
- `sc_generate_content_wizard_view_form` - Content generation setup

#### Kanban Views (with mandatory `default_group_by`)
- `sc_content_idea_view_kanban` with `default_group_by="task_id"`
- `sc_content_idea_task_view_kanban` with `default_group_by="state"`
- `sc_content_generation_task_view_kanban` with `default_group_by="state"`

### 2. Data Models

#### New Models to Create
1. **sc.content.idea** - Content idea storage
   - Fields: name, url, publish_date, summary, task_id
   - Inherits: `mail.thread` for chatter integration
   
2. **sc.content.idea.task** - Research task tracking
   - Fields: name, search_query, requested_ideas, generated_ideas_ids, state, error_message
   - Inherits: `mail.thread`, `mail.activity.mixin` for full chatter support
   
3. **sc.content.generation.task** - Generation task tracking
   - Fields: name, content_idea_id, user_prompt, generated_blog_post_id, target_blog_id, target_author_id, target_lang_id, state, error_message
   - Inherits: `mail.thread`, `mail.activity.mixin`
   
4. **sc.openai.usage.snapshot** - API usage tracking
   - Fields: date (unique), prompt_tokens, completion_tokens, total_tokens

#### Model Extensions
- **res.config.settings** - Add new configuration fields for agent settings

### 3. Security Implementation

#### Groups & ACLs
- **Group: Marketing Automation User** - Basic access to views and wizards
- **Group: Marketing Automation Manager** - Full access including settings
- **ir.model.access.csv** entries for all new models with appropriate permissions

#### Record Rules
- Multi-company support where applicable
- User-level access restrictions for sensitive operations

### 4. Integrations

#### OpenAI Agents SDK Integration
- **Library**: openai-agents-python (pinned to latest stable version)
- **Components**:
  - Agent initialization with WebSearchTool
  - Structured response handling with JSON parsing
  - Error handling and retry mechanisms
  - Token usage tracking

#### OpenAI Usage API Integration
- **Endpoints**: `/v1/organization/usage/completions`, `/v1/organization/usage/embeddings`
- **Authentication**: Bearer token with OPENAI_ADMIN_KEY
- **Rate Limiting**: Implement proper backoff strategies
- **Data Processing**: Daily aggregation and storage

### 5. Cron Jobs & Background Processing

#### Scheduled Actions
1. **Content Ideas Research Processor**
   - Frequency: Every 5 minutes
   - Processes sc.content.idea.task records in 'draft' state
   - Implements placeholder replacement and AI agent calls

2. **Content Generation Processor** 
   - Frequency: Every 5 minutes
   - Processes sc.content.generation.task records in 'draft' state
   - Creates blog.post records with AI-generated content

3. **OpenAI Usage Data Collector**
   - Frequency: Daily at 2:00 AM
   - Fetches usage statistics from OpenAI API
   - Updates sc.openai.usage.snapshot records

### 6. Chatter Integration

All task tracking models will inherit from `mail.thread` and `mail.activity.mixin`:
- **Dependencies**: Add `"mail"` to `__manifest__.py` depends
- **Form Views**: Include `<chatter/>` element at end of forms (after `</sheet>`)
- **Tracking**: Automated status updates and error logging in chatter
- **Activities**: Manual task assignments and follow-ups

---

## External Libraries Research

### OpenAI Agents Python SDK
- **Library ID**: `/openai/openai-agents-python`
- **Official Documentation**: https://github.com/openai/openai-agents-python
- **Version**: Latest stable (to be pinned in requirements.txt)
- **Key Components**:
  - `Agent` class for AI agent initialization
  - `WebSearchTool` for web research capabilities  
  - `Runner.run()` for asynchronous agent execution
  - Structured output handling with JSON responses
- **Integration Points**:
  - Content Research Agent with web search capabilities
  - Content Generation Agent for blog post creation
  - Error handling and retry mechanisms

### OpenAI Usage API
- **Documentation**: https://platform.openai.com/docs/api-reference/
- **Endpoints**:
  - `GET /v1/organization/usage/completions` - Token usage for completions
  - `GET /v1/organization/usage/embeddings` - Embedding usage statistics
- **Authentication**: Requires `OPENAI_ADMIN_KEY` environment variable
- **Rate Limits**: Standard OpenAI API limits apply
- **Data Format**: Time-bucketed usage data with token counts

---

## Files Map

```
custom-addons/sc_marketing_automation_tool/
├── requirements.txt                           # Updated with openai-agents
├── __manifest__.py                            # Updated dependencies (mail)
├── models/
│   ├── __init__.py                            # Updated imports
│   ├── res_config_settings.py                 # Updated with new fields
│   ├── sc_content_idea.py                     # New model
│   ├── sc_content_idea_task.py                # New model
│   ├── sc_content_generation_task.py          # New model
│   └── sc_openai_usage_snapshot.py           # New model
├── wizard/
│   ├── __init__.py                            # Updated imports
│   ├── sc_generate_ideas_wizard.py           # New wizard
│   └── sc_generate_content_wizard.py         # New wizard
├── views/
│   ├── res_config_settings_views.xml         # New settings inheritance
│   ├── sc_content_idea_views.xml             # New views
│   ├── sc_content_idea_task_views.xml        # New views
│   ├── sc_content_generation_task_views.xml  # New views
│   ├── sc_openai_usage_views.xml             # New dashboard
│   └── menu_items.xml                        # Updated menu structure
├── data/
│   ├── ir_cron_data.xml                      # New cron jobs
│   └── res_groups_data.xml                   # New security groups
├── security/
│   └── ir.model.access.csv                   # Updated ACLs
└── i18n/
    └── es_ES.po                               # Updated translations
```

---

## Testing Strategy

### Unit Tests
- Model method testing for all CRUD operations
- Agent integration testing with mocked API responses
- Configuration field validation testing
- Error handling and state management testing

### Integration Tests
- Complete wizard workflows (ideas generation → content creation)
- Cron job processing with real/mocked external API calls
- Multi-user and multi-company scenarios
- Blog post creation and publishing workflows

### Compliance Testing
- Install/upgrade tests for clean deployment
- Security tests for groups, ACLs, and record rules
- i18n completeness verification
- UI responsiveness and navigation testing

---

## i18n & Documentation

### Internationalization
- **Base Language**: English (all code, comments, technical strings)
- **User Language**: Spanish translation via `i18n/es_ES.po`
- **Translatable Elements**:
  - All user-facing strings in views, wizards, and messages
  - Field labels, help text, and selection options
  - Error messages and notifications
  - Menu items and action names

### Documentation Updates
- **README.md** (English): Updated features list, installation, usage
- **README.es.md** (Spanish): Synchronized translation of README
- **docs/functional/**: User guides for new agent features
- **docs/technical/**: Developer documentation for API integrations
- **CHANGELOG.md**: Version 18.0.1.0.1 feature summary

---

## Risk Assessment & Mitigation

### High-Risk Areas
1. **OpenAI API Integration Complexity**
   - Risk: Agent SDK integration failures or API changes
   - Mitigation: Comprehensive error handling, fallback mechanisms, version pinning

2. **External Dependencies**
   - Risk: openai-agents library compatibility issues
   - Mitigation: Thorough testing, version constraints, alternative library research

3. **Performance with Large Datasets**
   - Risk: Slow response times with many content ideas/tasks
   - Mitigation: Pagination, async processing, database indexing

### Medium-Risk Areas
1. **Settings Migration Complexity**
   - Risk: Data loss during field migration to new settings view
   - Mitigation: Migration scripts, backup procedures, rollback plans

2. **Multi-company Compatibility**
   - Risk: Data isolation issues in multi-company environments
   - Mitigation: Proper record rules, thorough multi-company testing

---

## Acceptance Checklist

### Functional Requirements
- [ ] Content Research Agent generates relevant topic ideas from web search
- [ ] Content Generation Agent creates complete blog posts from ideas
- [ ] OpenAI usage monitoring displays accurate token consumption data
- [ ] All settings consolidated in dedicated Marketing Automation section
- [ ] Wizard workflows are intuitive and error-free
- [ ] Background processing works reliably with proper error handling

### Technical Compliance
- [ ] All views use Odoo 18.0 standards (`<list>` tags, conditional UI)
- [ ] Kanban views define meaningful `default_group_by` attributes
- [ ] Chatter integration implemented correctly with mail dependencies
- [ ] Security groups, ACLs, and record rules provide appropriate access control
- [ ] External libraries properly integrated with error handling
- [ ] Server actions are thin with business logic in model methods

### Quality Assurance
- [ ] Unit and integration tests cover primary business flows
- [ ] Install/upgrade processes complete successfully
- [ ] i18n coverage complete with Spanish translations
- [ ] Documentation updated (README, functional, technical guides)
- [ ] Multi-company environments supported appropriately
- [ ] Performance acceptable under expected load conditions

---

## Plan Changelog

### 2025-09-11T17:00:00Z - Version 18.0.1.0.1 Plan Created
- **Spec Version**: 18.0.1.0.1
- **Summary**: Created comprehensive implementation plan for agent-based content automation features
- **External Research**: 
  - OpenAI Agents Python SDK documentation and integration patterns
  - OpenAI Usage API endpoints and authentication requirements
  - Odoo 18.0 standards compliance for views and conditional UI
- **Milestones**: Defined 5-phase approach with 32 tasks covering settings refactoring, agent implementation, usage monitoring, and quality assurance
- **Risk Assessment**: Identified external dependency and API integration risks with mitigation strategies
