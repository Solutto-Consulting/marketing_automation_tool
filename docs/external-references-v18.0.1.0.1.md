# External References: Content Management Tool v18.0.1.0.1

**Module**: sc_marketing_automation_tool  
**Version**: 18.0.1.0.1  
**Last Updated**: September 21, 2025

---

## Overview

This document provides comprehensive external references for the Content Management Tool, including Odoo core examples, OpenAI API documentation, and external library references. These references ensure stable implementation patterns and maintain compatibility with external systems.

---

## Odoo Core Examples & Patterns

### Settings View Implementation

#### Primary Reference Example
- **File**: `odoo-src/odoo/addons/base/views/res_config_settings_views.xml`
- **Anchor**: `base_setup.res_config_settings_view_form`
- **Usage**: Base inheritance pattern for all module settings views
- **Pattern**:
  ```xml
  <record id="res_config_settings_view_form_inherit_sc" model="ir.ui.view">
    <field name="inherit_id" ref="base_setup.res_config_settings_view_form"/>
    <field name="arch" type="xml">
      <xpath expr="//setting[@id='existing_setting_id']" position="after">
        <setting id="new_setting_id" string="Setting Label">
          <!-- Setting content -->
        </setting>
      </xpath>
    </field>
  </record>
  ```

#### Stable Anchor Examples
- **Settings Sections**: Use `//setting[@id='setting_id']` with position="after" or position="inside"
- **Avoid Brittle Anchors**: Do not use `//div[hasclass('settings')]` or class-based selectors
- **Recommended Anchors**:
  - `//setting[@id='account_setting_payment_terms']` - Accounting section
  - `//setting[@id='website_setting_homepage']` - Website section
  - `//setting[@id='base_setting_language']` - General section

### Odoo 18.0 View Standards

#### List Views
- **Standard**: Use `<list>` tag (not `<tree>`)
- **Example File**: `odoo-src/odoo/addons/base/views/res_partner_views.xml`
- **Pattern**:
  ```xml
  <record id="view_partner_tree" model="ir.ui.view">
    <field name="arch" type="xml">
      <list string="Partners">
        <field name="name"/>
        <field name="email"/>
      </list>
    </field>
  </record>
  ```

#### Kanban Views  
- **Requirement**: Mandatory `default_group_by` attribute
- **Example File**: `odoo-src/odoo/addons/project/views/project_views.xml`
- **Pattern**:
  ```xml
  <record id="view_task_kanban" model="ir.ui.view">
    <field name="arch" type="xml">
      <kanban default_group_by="stage_id">
        <templates>
          <t t-name="kanban-box">
            <!-- Kanban card content -->
          </t>
        </templates>
      </kanban>
    </field>
  </record>
  ```

#### Conditional Attributes (Odoo 18.0)
- **Standard**: Use `invisible`, `readonly`, `required`, `column_invisible`
- **Deprecated**: Avoid legacy `attrs` blocks and `visibility` containers
- **Example**:
  ```xml
  <field name="field_name" invisible="field_condition == False" readonly="state == 'done'"/>
  ```

### Security Implementation Patterns

#### Groups and Access Control
- **Reference File**: `odoo-src/odoo/addons/marketing/security/ir.model.access.csv`
- **Group Definition File**: `odoo-src/odoo/addons/marketing/security/marketing_security.xml`
- **ACL Pattern**:
  ```csv
  id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
  access_model_user,model.name user,model_model_name,group_marketing_user,1,1,1,0
  access_model_manager,model.name manager,model_model_name,group_marketing_manager,1,1,1,1
  ```

#### Record Rules
- **Reference File**: `odoo-src/odoo/addons/base/security/base_security.xml`
- **Multi-company Pattern**:
  ```xml
  <record id="rule_model_company" model="ir.rule">
    <field name="name">Multi-company rule</field>
    <field name="model_id" ref="model_model_name"/>
    <field name="domain_force">['|',('company_id','=',False),('company_id','in',company_ids)]</field>
  </record>
  ```

---

## OpenAI API Documentation References

### Image Generation API

#### gpt-image-1 Model
- **Endpoint**: `POST https://api.openai.com/v1/images/generations`
- **Documentation**: https://platform.openai.com/docs/api-reference/images/create
- **Model Specification**: gpt-image-1 (latest image generation model)
- **Request Pattern**:
  ```python
  import base64
  from openai import OpenAI
  
  client = OpenAI(api_key="your-api-key")
  response = client.images.generate(
      model="gpt-image-1",
      prompt="A professional blog cover image",
      n=1,
      size="1024x1024",
      quality="auto",
      response_format="b64_json"
  )
  ```

#### Supported Parameters
- **model**: "gpt-image-1" (required)
- **prompt**: Text description (max 1000 characters)
- **n**: Number of images (1-10, default 1)
- **size**: "1024x1024", "1536x1024", "1024x1536"
- **quality**: "auto", "hd"
- **response_format**: "url", "b64_json"
- **style**: "vivid", "natural"

### Chat Completions API

#### Text Generation Models
- **Endpoint**: `POST https://api.openai.com/v1/chat/completions`
- **Documentation**: https://platform.openai.com/docs/api-reference/chat/create
- **Supported Models**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- **Request Pattern**:
  ```python
  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "system", "content": "You are a helpful assistant"},
          {"role": "user", "content": "Generate blog content"}
      ],
      max_tokens=2000,
      temperature=0.7
  )
  ```

### Usage Monitoring API

#### Organization Usage Endpoint
- **Endpoint**: `GET https://api.openai.com/v1/usage`
- **Documentation**: https://platform.openai.com/docs/api-reference/usage
- **Authentication**: Requires organization-level API key
- **Parameters**:
  - `start_date`: YYYY-MM-DD format
  - `end_date`: YYYY-MM-DD format
  - `bucket_width`: "1d" for daily aggregation
- **Response Fields**:
  - `total_tokens`: Total token consumption
  - `total_cost`: Cost in USD
  - `daily_costs`: Daily breakdown array

### Rate Limits and Best Practices

#### Current Rate Limits (as of September 2025)
- **Text Generation**: 3,500 requests/minute (gpt-4o)
- **Image Generation**: 50 requests/minute (gpt-image-1)
- **Usage API**: 100 requests/minute
- **Best Practice**: Implement exponential backoff for rate limit handling

#### Error Handling Patterns
```python
from openai import RateLimitError, APIError
import time

def handle_openai_request(request_func):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return request_func()
        except RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        except APIError as e:
            _logger.error(f"OpenAI API Error: {e}")
            raise
    raise Exception("Max retries exceeded")
```

---

## External Library References

### OpenAI Agents SDK

#### Installation and Version
- **Package**: `openai-agents>=0.2.9`
- **PyPI**: https://pypi.org/project/openai-agents/
- **Documentation**: https://github.com/openai/openai-agents-python
- **Installation**: `pip install openai-agents>=0.2.9`

#### Agent Configuration Pattern
```python
from openai_agents import Agent
from openai_agents.tools import WebSearchTool

# Content Research Agent
research_agent = Agent(
    model="gpt-4o",
    instructions="Research content and provide structured summaries",
    tools=[WebSearchTool()]
)

# Content Generation Agent  
generation_agent = Agent(
    model="gpt-4o",
    instructions="Generate blog posts from research ideas"
)
```

#### WebSearchTool Integration
- **Purpose**: Provides web search capabilities for content research
- **Configuration**: Automatic search engine integration
- **Output Format**: Structured JSON with search results
- **Usage Pattern**:
  ```python
  search_tool = WebSearchTool()
  agent = Agent(
      model="gpt-4o",
      tools=[search_tool],
      instructions="Search for trending topics and summarize findings"
  )
  ```

### Python Dependencies

#### Core Requirements
- **Python**: 3.9+ (recommended 3.11+)
- **openai**: Latest version for API compatibility
- **openai-agents**: v0.2.9+ for agent orchestration
- **requests**: For HTTP request handling
- **json**: For structured data processing

#### Odoo Integration Requirements
- **Odoo**: 18.0 Community or Enterprise
- **Dependencies**: base, website, website_blog, mail
- **Module Structure**: Standard Odoo module layout
- **Security**: Proper groups and ACL configuration

---

## Integration Patterns

### Settings View Integration

#### Inheritance Pattern
Follow stable inheritance patterns to avoid conflicts with other modules:

```xml
<!-- CORRECT: Stable anchor with position -->
<xpath expr="//setting[@id='website_setting_domain']" position="after">
  <setting id="sc_marketing_setting" string="Marketing Automation">
    <!-- Content -->
  </setting>
</xpath>

<!-- INCORRECT: Brittle class-based selector -->
<xpath expr="//div[hasclass('settings')]" position="inside">
  <!-- Avoid this pattern -->
</xpath>
```

#### Required Dependencies
Ensure proper dependencies in `__manifest__.py`:
```python
'depends': [
    'base',
    'website',  # If using website settings
    'website_blog',  # For blog integration
    'mail',  # For chatter functionality
],
```

### API Integration Patterns

#### OpenAI Client Initialization
```python
from openai import OpenAI
import logging

_logger = logging.getLogger(__name__)

class OpenAIIntegration:
    def __init__(self, api_key, organization_id=None):
        self.client = OpenAI(
            api_key=api_key,
            organization=organization_id
        )
    
    def generate_content(self, prompt, model="gpt-4o"):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            _logger.error(f"Content generation failed: {e}")
            raise
```

#### Error Handling Strategy
Implement comprehensive error handling for external API calls:
```python
def safe_api_call(self, api_function, *args, **kwargs):
    """Wrapper for safe API calls with proper error handling"""
    try:
        return api_function(*args, **kwargs)
    except RateLimitError:
        # Implement backoff strategy
        _logger.warning("Rate limit hit, implementing backoff")
        raise
    except APIError as e:
        _logger.error(f"API Error: {e}")
        raise
    except Exception as e:
        _logger.error(f"Unexpected error: {e}")
        raise
```

---

## Version Compatibility

### Odoo Version Support
- **Primary**: Odoo 18.0 (Community and Enterprise)
- **View Standards**: Odoo 18.0 specific patterns (list views, conditional attributes)
- **API Compatibility**: Current Odoo ORM and framework patterns

### OpenAI API Compatibility
- **API Version**: v1 (current stable)
- **Model Support**: Latest models including gpt-4o and gpt-image-1
- **Feature Support**: Chat completions, image generation, usage monitoring

### External Library Compatibility
- **openai-agents**: v0.2.9+ required for agent orchestration
- **Python**: 3.9+ required, 3.11+ recommended
- **OpenAI Python**: Latest version for API compatibility

---

## Maintenance Notes

### Regular Updates Required
1. **OpenAI API Changes**: Monitor API documentation for model updates and feature changes
2. **Odoo Core Examples**: Verify anchor stability in major Odoo version updates
3. **External Libraries**: Keep openai-agents SDK updated for new features and security fixes
4. **Rate Limits**: Monitor OpenAI rate limit changes and adjust implementation accordingly

### Deprecation Tracking
1. **Legacy Odoo Patterns**: Remove `attrs` usage and `<tree>` views as they become deprecated
2. **OpenAI Models**: Track model deprecation announcements and migration paths
3. **API Endpoints**: Monitor for API versioning changes and update accordingly

---

**Last Updated**: September 21, 2025  
**Module Version**: v18.0.1.0.1  
**API Compatibility**: OpenAI API v1, Odoo 18.0