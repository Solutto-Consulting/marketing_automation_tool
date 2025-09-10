# Functional User Guide: Content Management Tool for Odoo v18.0.1.0.0

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [AI Configuration](#ai-configuration)
4. [Blog Translation Workflow](#blog-translation-workflow)
5. [Task Management](#task-management)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Version-Specific Features](#version-specific-features)

---

## Overview

The Content Management Tool for Odoo v18.0.1.0.0 is the initial stable release that provides AI-powered blog post translation capabilities. This version introduces the core translation workflow using OpenAI integration and establishes the foundation for automated content management.

### Key Features in v18.0.1.0.0
- ✅ OpenAI API integration with secure configuration
- ✅ Bulk blog post translation capabilities  
- ✅ User-friendly translation wizard
- ✅ Background processing for translation tasks
- ✅ Translation task tracking and status management
- ✅ Error handling and task reset capabilities
- ✅ Multi-language support (English/Spanish)

### Version Context
This documentation covers features available in **version 18.0.1.0.0** (September 2025). Advanced translation features and corruption fixes were introduced in later versions.

---

## Getting Started

### Prerequisites
- Odoo 18.0 Community or Enterprise
- Administrator access to configure OpenAI settings
- Valid OpenAI API account and credentials
- Blog module installed and configured

### Initial Setup Checklist
1. ✅ Install the Content Management Tool module
2. ✅ Configure OpenAI API credentials in settings
3. ✅ Verify blog posts are available for translation
4. ✅ Test translation workflow with sample content

---

## AI Configuration

### Accessing Configuration Settings

**Navigation**: Settings → General Settings → AI Marketing Tools

**Note**: This section appears in the General Settings page after installing the module.

### Configuration Fields

#### 1. OpenAI API Key (Required)
- **Field**: SC OpenAI API Key
- **Type**: Password field (hidden input)
- **Purpose**: Authenticates requests to OpenAI services
- **Security**: Never share or expose this key

#### 2. OpenAI Organization ID (Optional)
- **Field**: SC OpenAI Organization ID  
- **Type**: Text field
- **Purpose**: Links requests to your OpenAI organization
- **Note**: Recommended for organization-level usage tracking

#### 3. AI Model Selection (Required)
- **Field**: SC OpenAI Model
- **Type**: Selection dropdown
- **Default**: gpt-4o
- **Available Options**: 
  - gpt-4o (Recommended)
  - gpt-4-turbo
  - gpt-3.5-turbo
  - Additional models loaded dynamically from OpenAI API

### Dynamic Model Loading
The system automatically fetches available OpenAI models when you have a valid API key configured. If the API is unavailable, fallback models are provided.

### Configuration Tips
- Use **gpt-4o** for highest quality translations
- Use **gpt-3.5-turbo** for faster, cost-effective translations
- Organization ID helps track usage across teams

---

## Blog Translation Workflow

### Step 1: Select Blog Posts

1. Navigate to **Website → Blogs → Blog Posts**
2. Use the list view to see all available blog posts
3. Select one or more blog posts using checkboxes
4. Click **Action** dropdown in the top menu

### Step 2: Launch Translation Wizard

1. From the Action menu, select **"Translate with AI"**
2. The translation wizard opens in a modal dialog
3. Wizard shows context of selected blog posts

### Step 3: Configure Translation

#### Target Language Selection
- **Field**: Target Language
- **Options**: Only languages published on the website
- **Requirement**: At least one language must be active

#### System Instructions (Optional)
- **Field**: System Instructions
- **Purpose**: Guide AI translation style and tone
- **Examples**:
  - "Maintain professional business tone"
  - "Use casual, friendly language"
  - "Preserve technical terminology"
  - "Adapt cultural references for local audience"

### Step 4: Execute Translation

1. Click **"Translate"** button to start the process
2. Wizard closes and returns to blog post list
3. Translation tasks are created in "Draft" status
4. Background processing begins automatically

### Step 5: Monitor Progress

Translation tasks are processed asynchronously:

- **Draft**: Task created, waiting for processing
- **In Progress**: AI translation is running
- **Done**: Translation completed successfully
- **Error**: Translation failed (see error details)

---

## Task Management

### Accessing Translation Tasks

**Navigation**: Marketing Automation → Content Translation → Translation Tasks

### Task List View

The task list displays:
- **Task Name**: Descriptive name with blog post and language
- **Blog Post**: Link to the original blog post
- **Target Language**: Destination language for translation
- **Status**: Current task state with color coding
  - 🔵 Draft/In Progress (Blue)
  - 🟢 Done (Green)  
  - 🔴 Error (Red)

### Task Details

Click on any task to view detailed information:
- Complete task configuration
- Error messages (if applicable)
- Creation and completion timestamps
- System instructions used

### Task Actions

#### Reset to Draft
- **Available**: Only for tasks in "Error" status
- **Purpose**: Allows retrying failed translations
- **Effect**: Changes status back to "Draft" for reprocessing

**Note**: Use this action when OpenAI API issues are resolved or configuration is corrected.

### Task History

From any blog post form:
1. Open the blog post record
2. Navigate to **"Translation History"** tab
3. View all translation attempts for that post
4. Track translation status over time

---

## Troubleshooting

### Common Issues

#### 1. Translation Tasks Stuck in "Draft"
**Symptoms**: Tasks remain in draft status for extended periods

**Possible Causes**:
- OpenAI API credentials not configured
- API key invalid or expired
- Network connectivity issues
- Cron job not running

**Solutions**:
- Verify API configuration in Settings
- Check OpenAI account status and credits
- Restart Odoo server to reset cron jobs
- Check server logs for specific errors

#### 2. Translation Fails with API Errors
**Symptoms**: Tasks move to "Error" status with API-related messages

**Possible Causes**:
- API rate limits exceeded
- Insufficient OpenAI credits
- Invalid model selection
- Content too large for processing

**Solutions**:
- Wait for rate limit reset (typically 1 minute)
- Add credits to OpenAI account
- Switch to available model (gpt-3.5-turbo)
- Break large content into smaller posts

#### 3. Poor Translation Quality
**Symptoms**: Translations are incorrect or inappropriate

**Possible Causes**:
- Suboptimal system instructions
- Wrong model selection
- Complex source content

**Solutions**:
- Refine system instructions with specific guidance
- Upgrade to gpt-4o model for better quality
- Test with simpler content first
- Provide context-specific instructions

### Error Messages Reference

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "API key not configured" | OpenAI credentials missing | Configure API key in Settings |
| "Model not available" | Selected model unavailable | Choose different model |
| "Rate limit exceeded" | Too many API requests | Wait and retry |
| "Content too long" | Blog post exceeds API limits | Reduce content length |

---

## Best Practices

### Content Preparation
1. **Review Source Content**: Ensure original blog posts are complete and well-formatted
2. **Optimize Length**: Keep posts under 4000 words for best results
3. **Clean Formatting**: Remove excessive HTML or special characters
4. **Test Incrementally**: Start with shorter posts to validate configuration

### Translation Strategy
1. **Language Planning**: Prioritize target languages based on audience needs
2. **Batch Processing**: Group similar content for consistent translations
3. **Quality Review**: Always review AI translations before publishing
4. **Backup Original**: Keep original content safe (automatic in this version)

### System Instructions Guidelines
1. **Be Specific**: Provide clear, detailed instructions
2. **Include Context**: Mention industry, audience, and purpose
3. **Set Tone**: Specify formal, casual, technical, or conversational style
4. **Cultural Adaptation**: Request local cultural considerations

### Performance Optimization
1. **Schedule Translations**: Run during off-peak hours for faster processing
2. **Monitor Resources**: Track API usage and costs
3. **Batch Wisely**: Process 5-10 posts at a time for optimal performance
4. **Regular Maintenance**: Reset failed tasks and clean up completed ones

---

## Version-Specific Features

### New in v18.0.1.0.0 (September 2025)
- **Initial Release**: First stable version with core translation functionality
- **OpenAI Integration**: Complete integration with openai-agents SDK
- **Background Processing**: Asynchronous translation with cron job management
- **Task Tracking**: Comprehensive status management and error handling
- **Security Implementation**: Proper access controls and credential management
- **Bilingual Support**: English and Spanish interface translations
- **Documentation**: Complete functional and technical documentation

### Architecture Highlights
- **Odoo 18.0 Compliance**: Uses modern `<list>` views and proper conditionals
- **Mail Integration**: Chatter support for translation tasks
- **Kanban Views**: Meaningful grouping by task status
- **Stable Anchors**: Core settings inheritance from base_setup module

### Known Limitations in v18.0.1.0.0
- Translation processing limited to 10 tasks per cron cycle
- No automatic retry mechanism for API failures
- Manual task reset required for error recovery
- Basic error reporting without detailed diagnostics

**Note**: Enhanced features and improvements are available in later versions (18.0.1.1.0+).

---

## External References

### Core Settings Implementation
- **Reference**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anchor Used**: `//setting[@id='partner_autocomplete']` with `position="after"`
- **Pattern**: Stable xpath selectors following Odoo 18.0 standards

### Official Documentation
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **OpenAI API Documentation**: https://platform.openai.com/docs
- **Odoo 18.0 Translation System**: https://www.odoo.com/documentation/18.0/

---

*Documentation Version: 18.0.1.0.0 | Last Updated: September 2025*
