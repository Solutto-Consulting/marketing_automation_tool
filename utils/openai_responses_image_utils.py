"""
OpenAI Direct Images API Generation Utilities

This module provides utilities for generating images using OpenAI's Direct Images API
with the gpt-image-1 model, replacing the legacy DALL-E approach.
"""

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

_logger = logging.getLogger(__name__)

class OpenAIDirectImagesGenerator:
    """
    Image generation using OpenAI Direct Images API with gpt-image-1 model.
    
    This approach uses the gpt-image-1 model through the Direct Images API,
    providing better support and more advanced options than DALL-E.
    """
    
    def __init__(self, env):
        """Initialize with Odoo environment for config access"""
        self.env = env
        self._client = None
    
    @property
    def client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                
                # Get API key from config
                api_key = self.env['ir.config_parameter'].sudo().get_param(
                    'sc_marketing_automation_tool.openai_api_key'
                )
                
                if not api_key:
                    raise Exception("OpenAI API key not configured")
                
                # Get organization ID if available
                org_id = self.env['ir.config_parameter'].sudo().get_param(
                    'sc_marketing_automation_tool.openai_organization_id'
                )
                
                # Initialize client with organization if available
                if org_id:
                    self._client = OpenAI(
                        api_key=api_key,
                        organization=str(org_id)
                    )
                else:
                    self._client = OpenAI(api_key=api_key)
                
            except ImportError:
                raise Exception("OpenAI library not installed. Run: pip install openai")
            except Exception as e:
                _logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        
        return self._client
    
    def generate_image_with_context(
        self, 
        article_title: str, 
        article_content: str, 
        custom_prompt: Optional[str] = None,
        **generation_options
    ) -> Dict[str, Any]:
        """
        Generate an image using the Direct Images API with gpt-image-1 model.
        
        Args:
            article_title: Title of the article
            article_content: Content of the article (for context)
            custom_prompt: Optional custom image prompt
            **generation_options: Image generation options (size, quality, etc.)
            
        Returns:
            Dict with success status, image data, and metadata
        """
        try:
            # Prepare the image prompt with additional options
            prompt = self._prepare_image_prompt(
                article_title, 
                article_content, 
                custom_prompt, 
                **generation_options
            )
            
            # Get generation parameters for direct API
            params = self._get_image_generation_params(prompt, **generation_options)
            
            # Make the API call using direct Images API with monitoring
            _logger.info(f"Generating image using Direct Images API with gpt-image-1")
            start_time = datetime.now()
            
            try:
                response = self.client.images.generate(**params)
                
                # Calculate response time
                end_time = datetime.now()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Extract usage information if available
                input_tokens = 0
                output_tokens = 0
                total_tokens = 0
                
                if hasattr(response, 'usage') and response.usage:
                    input_tokens = getattr(response.usage, 'input_tokens', 0)
                    output_tokens = getattr(response.usage, 'output_tokens', 0)
                    total_tokens = getattr(response.usage, 'total_tokens', input_tokens + output_tokens)
                
                # Log the successful request using centralized logging
                self.env['sc.openai.request.log'].sudo().create_log_entry(
                    model_name='gpt-image-1',
                    operation_type='image_generation',
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    response_time_ms=response_time_ms,
                    status='success',
                    related_model='blog.post',
                    related_record_name=article_title[:100]  # Truncate if needed
                )
                
                _logger.info(f"Image generation logged: {total_tokens} tokens, {response_time_ms}ms response time")
                
            except Exception as api_error:
                # Calculate response time for failed request
                end_time = datetime.now()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Log the failed request
                self.env['sc.openai.request.log'].sudo().create_log_entry(
                    model_name='gpt-image-1',
                    operation_type='image_generation',
                    prompt_tokens=0,
                    completion_tokens=0,
                    response_time_ms=response_time_ms,
                    status='error',
                    error_message=str(api_error)[:500],  # Truncate error message
                    related_model='blog.post',
                    related_record_name=article_title[:100]
                )
                
                # Re-raise the exception to maintain original behavior
                raise api_error
            
            # Get output format for filename extension
            output_format = generation_options.get('output_format', 'png')
            
            # Process response
            return self._process_images_response(response, article_title, prompt, output_format)
            
        except Exception as e:
            error_msg = f"Image generation failed: {str(e)}"
            _logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'image_path': None,
                'image_prompt': custom_prompt or '',
                'metadata': {}
            }
    
    def _prepare_image_prompt(
        self, 
        article_title: str, 
        article_content: str, 
        custom_prompt: Optional[str] = None,
        **prompt_options
    ) -> str:
        """
        Prepare the image prompt for the Direct Images API with support for:
        - Custom prompt templates with placeholders
        - Brand colors integration
        - Style customization
        """
        
        # Extract additional options
        image_style = prompt_options.get('image_style', 'realistic')
        enable_brand_colors = prompt_options.get('enable_brand_colors', False)
        brand_primary_color = prompt_options.get('brand_primary_color', '')
        brand_secondary_color = prompt_options.get('brand_secondary_color', '')
        use_custom_prompt = prompt_options.get('use_custom_prompt', False)
        custom_template = prompt_options.get('custom_image_prompt_template', '')
        target_word_count = prompt_options.get('target_word_count', 800)
        
        # Build brand colors description
        brand_colors_desc = ""
        if enable_brand_colors and (brand_primary_color or brand_secondary_color):
            colors_list = []
            if brand_primary_color:
                colors_list.append(f"primary color: {brand_primary_color}")
            if brand_secondary_color:
                colors_list.append(f"secondary color: {brand_secondary_color}")
            brand_colors_desc = f"Use these brand colors: {', '.join(colors_list)}. "
        
        # Get style description
        style_descriptions = {
            'illustration': 'illustrated style with clean lines and vibrant colors',
            'realistic': 'realistic photographic style with natural lighting',
            'minimalist': 'minimalist design with clean, simple elements',
            'abstract': 'abstract artistic style with creative interpretation',
            'photographic': 'professional photography style with high detail',
            'artistic': 'artistic painterly style with creative expression',
            'modern': 'modern contemporary design with sleek aesthetics',
            'vintage': 'vintage retro style with classic appeal'
        }
        
        style_description = style_descriptions.get(image_style, 'professional style')
        
        if use_custom_prompt and custom_template:
            # Use custom prompt template with placeholder replacement
            prompt_text = custom_template
            
            # Replace placeholders
            placeholders = {
                '{article_title}': article_title,
                '{article_content}': article_content[:500] + "..." if len(article_content) > 500 else article_content,
                '{brand_colors}': brand_colors_desc,
                '{image_style}': style_description,
                '{word_count}': str(target_word_count)
            }
            
            for placeholder, value in placeholders.items():
                prompt_text = prompt_text.replace(placeholder, str(value))
            
            # Ensure text-free requirement is included
            if "NO TEXT" not in prompt_text.upper() and "TEXT-FREE" not in prompt_text.upper():
                prompt_text += "\n\nIMPORTANT: The image must be completely text-free. Do not include any written words, titles, labels, or text overlays."
            
            return prompt_text.strip()
        
        elif custom_prompt:
            # Use direct custom prompt (backward compatibility)
            return custom_prompt.strip()
        
        else:
            # Generate default context-aware prompt with new features
            prompt_text = f"""Create a compelling cover image for a blog article titled "{article_title}".

Article summary: {article_content[:500]}...

Generate a professional, eye-catching image in {style_description} that:
- Represents the main theme of the article visually through symbols, objects, or abstract concepts
- Is suitable for a blog cover image
- Has modern, clean aesthetics
- Would attract readers' attention
- Contains NO TEXT, NO WORDS, NO LETTERS, NO TITLES whatsoever
- Uses only visual elements like icons, illustrations, photography, or abstract designs
- Communicates the theme purely through visual metaphors and imagery

{brand_colors_desc}

Style requirements: Create the image using {style_description}.

IMPORTANT: The image must be completely text-free. Do not include any written words, titles, labels, or text overlays."""
            
            return prompt_text.strip()
    
    def _get_image_generation_params(self, prompt: str, **options) -> Dict[str, Any]:
        """Get image generation parameters for Direct Images API"""
        
        # Default values from Odoo config
        default_size = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.image_default_size', '1024x1024'
        )
        default_quality = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.image_default_quality', 'auto'
        )
        
        # Map quality settings - gpt-image-1 supports: auto, high, medium, low
        quality_map = {
            'standard': 'auto',  # Map legacy standard to auto
            'high': 'high',
            'hd': 'high',        # Map legacy hd to high
            'medium': 'medium',
            'low': 'low',
            'auto': 'auto'
        }
        
        # Map size options for gpt-image-1
        size_map = {
            '1024x1024': '1024x1024',
            '1536x1024': '1536x1024',  # landscape
            '1024x1536': '1024x1536',  # portrait
            '1792x1024': '1536x1024',  # Map to supported landscape
            'auto': 'auto'
        }
        
        params = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,  # gpt-image-1 supports 1-10
            "size": size_map.get(options.get('size', default_size), 'auto'),
            "quality": quality_map.get(options.get('quality', default_quality), 'auto'),
        }
        
        # Add gpt-image-1 specific parameters
        if options.get('output_format'):
            # Ensure valid format for gpt-image-1: png, jpeg, webp
            valid_formats = ['png', 'jpeg', 'webp']
            format_value = options['output_format'].lower()
            if format_value in valid_formats:
                params["output_format"] = format_value
            else:
                _logger.warning(f"Invalid output_format '{format_value}', using 'png' as default")
                params["output_format"] = 'png'
        
        if options.get('background'):
            params["background"] = options['background']  # transparent, opaque, auto
        
        if options.get('moderation'):
            params["moderation"] = options['moderation']  # low, auto
        
        if options.get('partial_images'):
            params["partial_images"] = options['partial_images']  # 0-3
        
        # Note: gpt-image-1 always returns base64, no response_format needed
        
        return params
    
    def _process_images_response(self, response, article_title: str, prompt: str, output_format: str = 'png') -> Dict[str, Any]:
        """Process the Direct Images API response and extract image data"""
        try:
            # Extract image data from response
            # response.data is a list of Image objects with b64_json
            if not response.data or len(response.data) == 0:
                raise Exception("No image data found in response")
            
            # Get the first (and typically only) image
            image_data = response.data[0].b64_json
            
            if not image_data:
                raise Exception("No base64 image data found in response")
            
            # Extract usage information if available
            usage_info = {}
            if hasattr(response, 'usage'):
                usage_info = {
                    'total_tokens': getattr(response.usage, 'total_tokens', 0),
                    'input_tokens': getattr(response.usage, 'input_tokens', 0),
                    'output_tokens': getattr(response.usage, 'output_tokens', 0),
                    'input_tokens_details': getattr(response.usage, 'input_tokens_details', {}),
                }
            
            # Save the image with the correct format
            image_path = self._save_image_to_disk(image_data, article_title, output_format)
            
            return {
                'success': True,
                'image_path': image_path,
                'image_prompt': prompt,
                'metadata': {
                    'model': 'gpt-image-1',
                    'api_method': 'direct_images_api',
                    'usage': usage_info,
                    'created': getattr(response, 'created', None),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to process Images API response: {str(e)}")
    
    def _save_image_to_disk(self, b64_image: str, article_title: str, output_format: str = 'png') -> str:
        """Save base64 image data to disk and return web-accessible file path"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(b64_image)
            
            # Create filename from article title
            safe_title = "".join(c for c in article_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Use the correct file extension based on output format
            file_extension = output_format.lower()
            filename = f"blog_cover_{safe_title}_{timestamp}.{file_extension}"
            
            # Create images directory in module's static folder
            module_path = os.path.dirname(os.path.dirname(__file__))  # Go up from utils/ to module root
            images_dir = os.path.join(module_path, "static", "src", "img", "generated")
            os.makedirs(images_dir, exist_ok=True)
            
            # Save image to module static directory
            file_path = os.path.join(images_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Return web-accessible URL path
            web_url = f"/sc_marketing_automation_tool/static/src/img/generated/{filename}"
            
            _logger.info(f"Image saved to: {file_path}")
            _logger.info(f"Web URL: {web_url}")
            
            return web_url
            
        except Exception as e:
            raise Exception(f"Failed to save image: {str(e)}")
    
    def get_generation_options_from_task(self, task) -> Dict[str, Any]:
        """Extract image generation options from a content generation task"""
        options = {}
        
        # Basic image generation options
        if task.image_size:
            options['size'] = task.image_size
        if task.image_quality:
            options['quality'] = task.image_quality
        if hasattr(task, 'image_output_format') and task.image_output_format:
            options['output_format'] = task.image_output_format
        if hasattr(task, 'image_background') and task.image_background:
            options['background'] = task.image_background
        if hasattr(task, 'image_moderation') and task.image_moderation:
            options['moderation'] = task.image_moderation
        if hasattr(task, 'image_partial_images') and task.image_partial_images:
            options['partial_images'] = task.image_partial_images
        
        # New advanced options
        if hasattr(task, 'image_style') and task.image_style:
            options['image_style'] = task.image_style
        if hasattr(task, 'enable_brand_colors'):
            options['enable_brand_colors'] = task.enable_brand_colors
        if hasattr(task, 'brand_primary_color') and task.brand_primary_color:
            options['brand_primary_color'] = task.brand_primary_color
        if hasattr(task, 'brand_secondary_color') and task.brand_secondary_color:
            options['brand_secondary_color'] = task.brand_secondary_color
        if hasattr(task, 'use_custom_prompt'):
            options['use_custom_prompt'] = task.use_custom_prompt
        if hasattr(task, 'custom_image_prompt_template') and task.custom_image_prompt_template:
            options['custom_image_prompt_template'] = task.custom_image_prompt_template
        if hasattr(task, 'target_word_count') and task.target_word_count:
            options['target_word_count'] = task.target_word_count
        
        return options


def create_responses_image_generator(env):
    """Factory function to create image generator instance"""
    return OpenAIDirectImagesGenerator(env)


# Utility functions for integration
def generate_blog_cover_image(env, article_title: str, article_content: str, **options) -> Dict[str, Any]:
    """
    High-level function to generate blog cover image using Direct Images API
    
    Args:
        env: Odoo environment
        article_title: Title of the blog article
        article_content: Content of the article for context
        **options: Image generation options
        
    Returns:
        Dict with generation result
    """
    generator = create_responses_image_generator(env)
    return generator.generate_image_with_context(
        article_title=article_title,
        article_content=article_content,
        **options
    )