# Functional User Guide: Content Management Tool for Odoo v18.0.1.0.1

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [AI Configuration](#ai-configuration)
4. [Content Research Agent](#content-research-agent)
5. [Content Generation Agent](#content-generation-agent)
6. [Blog Translation Workflow](#blog-translation-workflow)
7. [Usage Monitoring](#usage-monitoring)
8. [Task Management](#task-management)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Version-Specific Features](#version-specific-features)

---

## Overview

The Content Management Tool for Odoo v18.0.1.0.1 introduces powerful **agent-based content strategy** capabilities, moving beyond simple translation to proactive content research and generation. This version represents a major evolution in AI-powered content management for Odoo.

### Key Features in v18.0.1.0.1
- ✅ **Content Research Agent**: AI-powered topic discovery using web search
- ✅ **Content Generation Agent**: Automated blog post creation from research ideas
- ✅ **OpenAI Usage Monitoring**: Daily usage tracking and cost optimization
- ✅ **Centralized Settings**: Dedicated Marketing Automation configuration section
- ✅ **Enhanced Translation System**: Improved with OpenAI Agents SDK
- ✅ **Multi-Agent Background Processing**: Separate cron jobs for each agent
- ✅ **Structured AI Responses**: JSON-based content generation with defined schemas

### Version Context
This documentation covers features available in **version 18.0.1.0.1** (September 2025). This represents a significant expansion from the translation-focused v18.0.1.0.0 to a comprehensive content strategy platform.

---

## Getting Started

### Prerequisites
- Odoo 18.0 Community or Enterprise
- Administrator access to configure OpenAI settings
- Valid OpenAI API account with organization access
- OpenAI Agents SDK dependency (>=0.2.9)
- Blog module installed and configured

### Initial Setup Checklist
1. ✅ Install the Content Management Tool module
2. ✅ Configure OpenAI API credentials in Marketing Automation settings
3. ✅ Set up Content Research Agent configuration
4. ✅ Configure Content Generation Agent settings
5. ✅ Verify OpenAI Usage monitoring is functional
6. ✅ Test complete content pipeline from research to publication

### New in v18.0.1.0.1: Agent-Based Architecture
This version introduces two specialized AI agents that work together to create a complete content strategy pipeline:

- **Content Research Agent**: Discovers trending topics and generates content ideas
- **Content Generation Agent**: Creates complete blog post drafts from research ideas
- **Enhanced Translation Agent**: Improved translation capabilities with better error handling

---

## AI Configuration

### Centralized Settings Location
All AI configuration has been moved from General Settings to a dedicated section:

**Navigation**: Settings → Marketing Automation

This new centralized approach provides better organization and dedicated configuration for each AI agent.

### Accessing Configuration Settings

**Navigation**: Settings → General Settings → AI Marketing Tools

**Note**: This section appears in the General Settings page after installing the module.

### Configuration Fields

#### 1. General OpenAI Configuration
- **OpenAI API Key** (Required): Authenticates all requests to OpenAI services
- **OpenAI Organization ID** (Optional): Links requests to your organization for usage tracking
- **OpenAI Model** (Required): Default model for translation tasks (gpt-4o recommended)

#### 2. Content Research Agent Configuration
- **Research Agent Model**: Specific model for content research tasks
- **Research Agent Instructions**: System instructions that guide topic discovery behavior
- **Default Search Query**: Pre-filled search query template with placeholder support

#### 3. Content Generation Agent Configuration  
- **Generation Agent Model**: Specific model for blog post creation
- **Generation Agent Instructions**: System instructions for blog writing style and structure

### Dynamic Model Loading
The system automatically fetches available OpenAI models when you have a valid API key configured. Each agent can use different models optimized for their specific tasks.

### Configuration Tips
- Use **gpt-4o** for highest quality research and generation
- Use **gpt-3.5-turbo** for faster, cost-effective operations
- Customize agent instructions to match your brand voice and content style

---

## Content Research Agent

The Content Research Agent uses web search capabilities to discover trending topics and generate relevant content ideas for your blog.

### Research Workflow

#### Step 1: Access Content Ideas
1. Navigate to **Marketing Automation → Content Ideas → All Ideas**
2. Click **Generate Content Ideas** button to open the wizard

#### Step 2: Configure Research Request
- **Search Query**: Enter or modify the search terms (supports {today} placeholder)
- **Number of Suggestions**: Specify how many ideas to generate (default: 5)
- **Example Query**: "Latest trends in digital marketing {today}"

#### Step 3: Background Processing
- The system creates a research task and processes it in the background
- Monitor progress in **Marketing Automation → Content Ideas → Generation Tasks**
- Tasks progress through: Draft → In Progress → Done/Error

#### Step 4: Review Generated Ideas
Each generated idea includes:
- **Title**: Headline from source article
- **URL**: Link to original source
- **Publication Date**: When the source was published
- **Summary**: AI-generated summary of key points

### Research Best Practices
- Use specific, targeted search queries for better results
- Include date placeholders like {today} for timely content
- Review source credibility before using ideas
- Customize research agent instructions for your industry focus

---

## Content Generation Agent

The Content Generation Agent takes research ideas and creates complete blog post drafts ready for review and publication.

### Generation Workflow

#### Step 1: Access Content Generation
1. Navigate to **Website → Blogs → Blog Posts**
2. Click **Generate Content** button in the header
3. This opens the content generation wizard

#### Step 2: Configure Generation Request
- **Content Idea**: Select from previously generated research ideas
- **User Prompt**: Add specific instructions or requirements
- **Target Blog**: Choose which blog to publish to
- **Author**: Select the post author
- **Language**: Set the content language

#### Step 3: Background Processing
- The system creates a generation task for background processing
- Monitor progress in **Marketing Automation → Content Generation → Generation Tasks**
- Tasks include full content creation pipeline

#### Step 4: Review Generated Content
Generated blog posts include:
- **Title**: Optimized headline based on research
- **Content**: Full HTML formatted blog post content
- **Meta Description**: SEO-optimized description
- **Keywords**: Relevant tags for discovery
- **Publication Status**: Initially saved as unpublished draft

### Generation Best Practices
- Provide clear, specific user prompts for better results
- Review and edit generated content before publishing
- Customize generation agent instructions for consistent brand voice
- Use generation tasks to track content creation pipeline

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

## Usage Monitoring

The Usage Monitoring feature provides insights into OpenAI API consumption, helping you track costs and optimize usage across all AI agents.

### Accessing Usage Dashboard

**Navigation**: Marketing Automation → OpenAI Usage

### Dashboard Features

#### 1. Usage Statistics
- **Daily Token Consumption**: Prompt tokens, completion tokens, and totals
- **Cost Tracking**: Monitor API spending patterns
- **Usage Trends**: 30-day historical view with graphs

#### 2. Manual Data Sync
- **Fetch Latest Data** button: Manually refresh usage statistics
- **Automatic Sync**: Daily cron job updates usage data automatically
- **Data Range**: Up to 90 days of historical usage data

#### 3. Usage Analysis
- **Breakdown by Agent**: See which agents consume the most tokens
- **Cost Optimization**: Identify opportunities to reduce API costs
- **Usage Patterns**: Track peak usage times and trends

### Understanding Usage Metrics

#### Token Types
- **Prompt Tokens**: Input text sent to OpenAI (your content and instructions)
- **Completion Tokens**: AI-generated responses (translations, content, ideas)
- **Total Tokens**: Sum of prompt and completion tokens for billing

#### Cost Management Tips
- Monitor daily usage to stay within budget limits
- Use gpt-3.5-turbo for cost-effective operations when quality allows
- Optimize agent instructions to reduce prompt token usage
- Review usage patterns to identify optimization opportunities

### Usage Monitoring Best Practices
- Check usage dashboard weekly to track spending
- Set up internal alerts based on daily token consumption
- Review agent efficiency and optimize instructions regularly
- Use usage data to make informed decisions about model selection

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
