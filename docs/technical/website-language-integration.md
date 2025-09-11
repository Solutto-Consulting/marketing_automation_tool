# Website Language Integration - Blog Article Creation

## Overview

The marketing automation module now automatically detects and uses the website's default language for blog article creation, ensuring that new content is generated in the appropriate language based on the website configuration.

## Implementation Details

### Automatic Language Detection

The system now automatically detects the website's default language through the following mechanism:

1. **Primary Source**: Retrieves the default language from `website.default_lang_id`
2. **Fallback Chain**: 
   - If no website found → Falls back to English (`en_US`)
   - If English not available → Uses first available language in system

### Code Changes

#### Content Generation Task Model (`sc_content_generation_task.py`)

```python
@api.model
def _get_default_website_language(self):
    """Get the default language from the website configuration"""
    try:
        # Get the current website or the first website
        website = self.env['website'].get_current_website()
        if not website:
            website = self.env['website'].search([], limit=1)
        
        # Return the website's default language if available
        if website and website.default_lang_id:
            return website.default_lang_id.id
    except Exception as e:
        _logger.warning(f"Could not get website default language: {e}")
    
    # Fallback to English if website not found or error
    try:
        return self.env.ref('base.lang_en').id
    except Exception:
        # Ultimate fallback - first available language
        lang = self.env['res.lang'].search([], limit=1)
        return lang.id if lang else False
```

#### Field Definition

```python
target_lang_id = fields.Many2one(
    'res.lang',
    string="Language",
    required=True,
    default='_get_default_website_language',
    help="The language for the generated article (uses website default language)"
)
```

#### Blog Post Creation

The blog post creation now uses language context:

```python
# Create the blog post in the specified language context
lang_code = self.target_lang_id.code if self.target_lang_id else 'en_US'
blog_post = self.env['blog.post'].with_context(lang=lang_code).create(blog_post_values)
```

### User Interface Updates

#### Generation Wizard

The content generation wizard now includes a language selection field that:
- Defaults to the website's default language
- Allows manual override if needed
- Is clearly labeled and positioned in the "Generation Settings" section

#### Task Form View

The task form view displays the selected language alongside other configuration fields for transparency and manual editing capability.

## Usage Scenarios

### Scenario 1: English Website
- **Website Config**: `default_lang_id = 'en_US'`
- **Article Creation**: Automatically generates content in English
- **User Experience**: Seamless, no additional configuration needed

### Scenario 2: Spanish Website
- **Website Config**: `default_lang_id = 'es_ES'`
- **Article Creation**: Automatically generates content in Spanish
- **User Experience**: Content is properly localized for Spanish audience

### Scenario 3: Multi-language Website
- **Website Config**: `default_lang_id = 'en_US'`, `language_ids = ['en_US', 'es_ES', 'fr_FR']`
- **Article Creation**: Defaults to English but user can manually select other languages
- **User Experience**: Flexibility to create content in any supported language

## Benefits

1. **Automatic Language Detection**: No manual configuration required for standard cases
2. **Consistency**: All generated content respects website language settings
3. **Flexibility**: Manual override available when needed
4. **Robust Fallbacks**: System continues working even if website configuration is incomplete
5. **Multilingual Support**: Foundation for future multi-language content features

## Future Enhancements

This implementation provides the foundation for:
- Automatic translation workflows
- Language-specific content templates
- Multi-language blog management
- Localized SEO optimization

## Technical Notes

- **Dependency**: Requires `website` module (already in dependencies)
- **Performance**: Language detection is performed once during default value calculation
- **Error Handling**: Comprehensive fallback mechanism prevents failures
- **Logging**: Warning logs help diagnose configuration issues

## Migration Impact

Existing installations will:
- Continue working with current language settings
- Benefit from automatic language detection for new content
- See the language field populated with website defaults
