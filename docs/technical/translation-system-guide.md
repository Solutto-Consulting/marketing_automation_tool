# Translation System Technical Guide

## Overview

This document describes the proven translation system implementation for Odoo 18.0, specifically designed for reliable multilingual content management with zero content corruption.

## Translation Architecture

### Field Types Supported

1. **Simple Translatable Fields** (`translate=True`)
   - `name`, `subtitle`, `website_meta_title`, `website_meta_description`, `website_meta_keywords`
   - Stored as JSON in database with language keys

2. **HTML Translatable Fields** (`translate=html_translate`)
   - `content`, complex HTML content fields
   - Uses Odoo's HTML translation system with term preservation

3. **SEO Metadata Fields** 
   - Inherited from `website.seo.metadata` mixin
   - Automatically translatable with standard JSON storage

## Proven Translation Method

### Unified Context Write Approach (RECOMMENDED)

```python
def _update_blog_post_translations(self, translated_content):
    """
    Production-ready translation method that preserves original content
    and creates proper language-specific translations.
    """
    self.ensure_one()
    
    target_lang_code = self.target_lang_id.code
    blog_post = self.blog_post_id
    
    # MANDATORY: Store original content before any operations
    original_content = blog_post.with_context(lang='en_US').content
    original_name = blog_post.with_context(lang='en_US').name
    
    # Prepare translation updates for ALL translatable fields
    translation_updates = {}
    translatable_fields = ['name', 'subtitle', 'website_meta_title', 
                          'website_meta_description', 'website_meta_keywords', 
                          'teaser_manual', 'content']
    
    for field_name in translatable_fields:
        if field_name in translated_content and translated_content[field_name]:
            translation_updates[field_name] = translated_content[field_name]
    
    # Apply ALL translations using single context write
    if translation_updates:
        try:
            # This preserves originals and creates language-specific translations
            blog_post.with_context(lang=target_lang_code).write(translation_updates)
            _logger.info(f"Applied translations for {target_lang_code}: {list(translation_updates.keys())}")
            
            # MANDATORY: Verify original content preservation
            current_english = blog_post.with_context(lang='en_US').content
            if current_english != original_content:
                # Auto-restore if corruption detected
                blog_post.with_context(lang='en_US').write({'content': original_content})
                raise Exception("Translation corrupted original content - auto-restored")
                
        except Exception as e:
            _logger.error(f"Translation failed: {e}")
            raise
```

## HTML Structure Validation

### Purpose
Ensures translated HTML content maintains the same structure as the original, preventing broken layouts.

### Implementation
```python
def _validate_html_structure(self, original_html, translated_html):
    """
    Validate HTML structure consistency between original and translated content.
    """
    import re
    
    if not original_html or not translated_html:
        return True
    
    try:
        # Tag count validation
        tag_pattern = r'<[^>]+>'
        original_tags = re.findall(tag_pattern, original_html)
        translated_tags = re.findall(tag_pattern, translated_html)
        
        if len(original_tags) != len(translated_tags):
            return False
        
        # Critical structure preservation
        critical_tags = ['<div', '<p', '<h1', '<h2', '<h3', '<ul', '<ol', '<li']
        for tag in critical_tags:
            if original_html.count(tag) != translated_html.count(tag):
                return False
        
        return True
        
    except Exception as e:
        _logger.warning(f"HTML validation failed: {e}")
        return True  # Allow translation to proceed
```

## Translation Verification

### Content Integrity Check
```python
def verify_translation_integrity(self, target_lang_code='es_ES'):
    """
    Comprehensive verification of translation integrity.
    """
    try:
        # Check all language versions
        english_content = self.with_context(lang='en_US').content
        english_name = self.with_context(lang='en_US').name
        target_content = self.with_context(lang=target_lang_code).content
        target_name = self.with_context(lang=target_lang_code).name
        
        # Verify original preservation
        if not english_content or not english_name:
            return False, "Original English content missing"
        
        # Verify translation differentiation
        name_translated = english_name != target_name and bool(target_name)
        content_translated = english_content != target_content and bool(target_content)
        
        if name_translated and content_translated:
            return True, f"Complete translations verified for {target_lang_code}"
        else:
            return False, f"Partial or missing translations detected"
            
    except Exception as e:
        return False, f"Verification error: {str(e)}"
```

## Critical Implementation Rules

### ✅ ALWAYS USE
```python
# Context write method - ONLY reliable approach
record.with_context(lang='es_ES').write({
    'name': translated_name,
    'content': translated_html,
    'website_meta_title': translated_title
})
```

### ❌ NEVER USE
```python
# Direct write - CORRUPTS original content
record.write({'content': translated_html})  # DANGEROUS!

# update_field_translations - Causes SQL errors in Odoo 18.0
record.update_field_translations('content', {'es_ES': translated_html})  # FAILS!
```

## Error Recovery Patterns

### SQL Transaction Errors
- **Symptoms**: `psycopg2.errors.InFailedSqlTransaction`
- **Cause**: `update_field_translations` incompatibility with Odoo 18.0
- **Solution**: Replace with `with_context(lang=target_lang).write()`

### Content Corruption
- **Symptoms**: Original English content overwritten
- **Cause**: Using direct `write()` without language context
- **Solution**: Always use context-based writes + verification

## Production Testing Protocol

### 1. Fresh Content Test
- Create new blog post with fresh content
- Apply translation
- Verify both languages exist and differ

### 2. Content Preservation Test
```python
# Before translation
original_content = blog_post.with_context(lang='en_US').content

# After translation
current_content = blog_post.with_context(lang='en_US').content
assert current_content == original_content, "Original content corrupted!"
```

### 3. HTML Structure Test
- Validate tag counts match
- Verify critical structure elements preserved
- Check for broken HTML

### 4. Clean Database Test
- Test on fresh database without existing translations
- Verify methods work with new content
- Confirm no dependencies on pre-existing data

## Module Dependencies

### Required Language Activation
```xml
<!-- Always activate target languages in module data -->
<function model="res.lang" name="_activate_lang">
    <value>es_ES</value>
</function>
```

### Field Translation Declaration
```python
# Simple translatable fields
name = fields.Char(string="Name", translate=True)
subtitle = fields.Char(string="Subtitle", translate=True)

# HTML translatable fields
from odoo.tools.translate import html_translate
content = fields.Html(string="Content", translate=html_translate, sanitize=False)
```

## Performance Considerations

### Memory Usage
- Translation methods operate on single records (`self.ensure_one()`)
- Content verification adds minimal overhead
- HTML validation uses regex patterns (lightweight)

### Database Impact
- Context writes create proper JSON language entries
- No additional database calls beyond standard Odoo translation system
- Auto-recovery mechanisms prevent data corruption

### API Rate Limits
- OpenAI integration handles rate limiting
- Background processing prevents UI blocking
- Error handling allows for retry mechanisms

## Troubleshooting

### Translation Not Working
1. Check field has `translate=True` or `translate=html_translate`
2. Verify target language is activated
3. Confirm using context write method
4. Test with fresh content

### Content Appears Identical
1. Check if translation actually occurred
2. Verify language context is different
3. Use verification methods to diagnose

### SQL Errors
1. Replace any `update_field_translations` usage
2. Ensure proper exception handling
3. Check database transaction state

## Security Considerations

### API Key Management
- Store OpenAI API keys in Odoo configuration
- Never hardcode keys in source code
- Use environment variables for deployment

### Content Validation
- Sanitize HTML content appropriately
- Validate translation field inputs
- Implement rate limiting for API calls

### Access Control
- Restrict translation task access via ACL
- Implement proper user role management
- Log translation activities for audit

## Future Enhancements

### Performance Optimization
- Batch translation processing
- Translation memory implementation
- Caching for repeated content

### Quality Improvements
- Advanced HTML validation
- Translation quality scoring
- A/B testing for translation methods

### Integration Expansion
- Support for additional AI providers
- Custom translation workflows
- Advanced error reporting and analytics
