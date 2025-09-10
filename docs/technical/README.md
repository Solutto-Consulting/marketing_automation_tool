# Technical Documentation: sc_marketing_automation_tool

## Overview

The `sc_marketing_automation_tool` module provides AI-powered content translation capabilities for Odoo blog posts using OpenAI's language models through the openai-agents SDK.

## Architecture

### Core Components

1. **Models**
   - `sc.translation.task`: Manages translation requests and status tracking
   - `blog.post` (extended): Adds translation tracking capabilities
   - `res.config.settings` (extended): OpenAI configuration management
   - `openai.utils`: Utility class for OpenAI integration

2. **Views**
   - Configuration settings view (inherits from base_setup)
   - Translation task management views (list, form, kanban)
   - Blog post form extension with translation history
   - Translation wizard for user input

3. **Background Processing**
   - Cron job for asynchronous translation processing
   - Error handling and retry mechanisms

## Technical Requirements

### External Dependencies
- **Python Package**: `openai-agents >= 0.2.9`
- **Python Version**: 3.9+ (required by openai-agents)

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (set automatically from configuration)
- `OPENAI_ORGANIZATION`: OpenAI Organization ID (optional)

## Database Schema

### sc.translation.task
```sql
CREATE TABLE sc_translation_task (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    blog_post_id INTEGER REFERENCES blog_post(id) ON DELETE CASCADE,
    target_lang_id INTEGER REFERENCES res_lang(id),
    system_instructions TEXT,
    state VARCHAR DEFAULT 'draft',
    error_message TEXT,
    create_date TIMESTAMP,
    write_date TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id)
);
```

### blog.post (extended)
```sql
ALTER TABLE blog_post ADD COLUMN translation_task_ids INTEGER[];
ALTER TABLE blog_post ADD COLUMN translation_in_progress BOOLEAN DEFAULT FALSE;
ALTER TABLE blog_post ADD COLUMN translation_task_count INTEGER;
```

## Integration Details

### OpenAI Agents SDK Integration

The module uses the openai-agents SDK for AI interactions:

```python
from agents import Agent, Runner

agent = Agent(
    name="Odoo Blog Translator",
    instructions=system_instructions,
    model=model_name,
)

result = await Runner.run(agent, prompt)
```

### Translation Workflow

1. **User Action**: Select blog posts and launch wizard
2. **Task Creation**: Create translation tasks in 'draft' state
3. **Cron Processing**: Background cron job processes draft tasks
4. **AI Translation**: OpenAI API performs translation
5. **Content Update**: Blog post content updated with translation using proven context write method
6. **Status Update**: Task marked as 'done' or 'error'

### Translation System (v18.0.1.1.0+)

**CRITICAL**: As of version 18.0.1.1.0, the module uses a completely rewritten translation system that eliminates content corruption issues.

**Key Features:**
- **Unified Context Write Approach**: Uses `with_context(lang=target_lang).write()` for ALL field types
- **Content Preservation**: Mandatory verification that original English content is never overwritten
- **HTML Structure Validation**: Ensures translated content maintains proper HTML structure
- **Auto-Recovery**: Automatic restoration of corrupted content when errors are detected
- **Production-Ready**: Field-tested approach that works reliably without SQL transaction errors

**For detailed implementation guidelines, see**: [`translation-system-guide.md`](./translation-system-guide.md)

### Error Handling

- API connection failures
- Invalid JSON responses from AI
- Rate limiting and timeout handling
- Task retry mechanisms
- **Content corruption prevention and auto-recovery** (v18.0.1.1.0+)
- **SQL transaction error recovery** (v18.0.1.1.0+)

## Security

### Access Control Lists (ACLs)
- Marketing Manager: Full access (CRUD)
- Marketing User: Read and create access

### Groups
- `group_marketing_manager`: Full access to all features
- `group_marketing_user`: Limited access for regular users

## Configuration

### Settings Location
Navigate to: Settings > General Settings > AI Marketing Tools

### Required Configuration
1. OpenAI API Key (required)
2. OpenAI Organization ID (optional)
3. OpenAI Model selection (default: gpt-4o)

### Model Selection
The module dynamically retrieves available models from OpenAI API with fallback to:
- gpt-4o
- gpt-4-turbo
- gpt-3.5-turbo

## Performance Considerations

### Cron Job Optimization
- Processes maximum 10 tasks per run (every 5 minutes)
- Commits after each task to prevent blocking
- Error isolation to prevent task failures from affecting others

### Rate Limiting
- Implements proper error handling for API rate limits
- Automatic retry mechanisms for transient failures

## Monitoring and Debugging

### Logging
- Error logging for API failures
- Debug logging for translation processes
- Task status tracking in database

### Status Tracking
- Real-time status updates in UI
- Error message storage for debugging
- Translation history per blog post

## Troubleshooting

### Common Issues

1. **"openai-agents package not installed"**
   - Solution: `pip install openai-agents`

2. **"OpenAI API key not configured"**
   - Solution: Configure API key in Settings > General Settings

3. **"Translation failed"**
   - Check error message in task details
   - Verify API key validity
   - Check internet connectivity

### Debug Mode
Enable debug logging for detailed information:
```bash
--log-handler odoo.addons.sc_marketing_automation_tool:DEBUG
```

## Extensibility

### Custom Instructions
Users can provide custom instructions to guide AI translation style and tone.

### Language Support
Supports all languages configured in Odoo with `active=True`.

### Model Flexibility
Easily configurable to use different OpenAI models as they become available.

## Version Information

- **Module Version**: 18.0.1.0.0
- **Odoo Version**: 18.0 Community
- **OpenAI Agents Version**: >= 0.2.9
- **Last Updated**: September 2025
