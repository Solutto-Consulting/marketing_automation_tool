# AI Marketing Tools Settings Implementation

## Overview
The AI Marketing Tools module follows Odoo 18.0 standard patterns for configuration settings, implementing an `<app>` section in the general settings instead of creating a dedicated settings page.

## Implementation Pattern
Following the Odoo 18.0 standard pattern observed in the `website` module:

### Structure
```xml
<app data-string="AI Marketing Tools" string="AI Marketing Tools" name="sc_marketing_automation_tool" groups="base.group_system">
    <block title="OpenAI Integration" id="openai_integration_settings">
        <setting id="sc_openai_api_key_setting" string="OpenAI API Key" help="...">
            <!-- Field configuration -->
        </setting>
    </block>
    
    <block title="AI Agent Management" id="ai_agent_management">
        <setting id="sc_agent_config_setting" string="AI Agent Configuration System" help="...">
            <!-- Field configuration -->
        </setting>
    </block>
</app>
```

### Key Components

1. **App Declaration**: Creates a sidebar entry in general settings
2. **Block Organization**: Groups related settings logically
3. **Setting Elements**: Individual configuration items
4. **Standard Action**: Uses default res.config.settings action

### Benefits

- **Consistency**: Follows Odoo core module patterns
- **Accessibility**: Integrated with standard settings interface
- **Maintenance**: Easier to maintain and extend
- **User Experience**: Familiar interface for users

## File Structure

- `views/res_config_settings_views.xml`: Single view inheritance
- `views/menu_views.xml`: No additional settings menu needed
- `__manifest__.py`: No custom assets required

## Access
Users can access the AI Marketing Tools settings through:
Settings → AI Marketing Tools (sidebar)

## Version
Implemented according to Odoo 18.0 standards as referenced in the website module.