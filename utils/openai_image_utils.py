import os
import requests
import base64
import logging
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenAIImageGenerator:
    """Utility class for OpenAI DALL-E image generation"""
    
    def __init__(self, api_key, organization_id=None):
        """Initialize OpenAI image generator with API credentials"""
        self.api_key = api_key
        self.organization_id = organization_id
        self.base_url = "https://api.openai.com/v1"
        
    def _get_headers(self):
        """Get headers for OpenAI API requests"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.organization_id:
            headers["OpenAI-Organization"] = str(self.organization_id)
            
        return headers
    
    def generate_image_prompt(self, article_title, article_content, custom_prompt=None):
        """Generate an appropriate image prompt based on article content"""
        if custom_prompt:
            return custom_prompt.strip()
        
        # Extract key themes from the article
        prompt_base = f"Create a professional, visually appealing cover image for a blog article titled '{article_title}'"
        
        # Add content-based context if available
        if article_content:
            # Extract first 200 characters for context
            content_snippet = article_content[:200].strip()
            if content_snippet:
                prompt_base += f". The article discusses: {content_snippet}"
        
        # Add style guidelines
        prompt_base += ". The image should be modern, clean, and suitable for a professional blog. No text or typography should be included in the image."
        
        return prompt_base
    
    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", style="vivid"):
        """
        Generate an image using OpenAI DALL-E API
        
        Args:
            prompt (str): Text description for image generation
            model (str): DALL-E model to use ('dall-e-3' or 'dall-e-2')
            size (str): Image size (1024x1024, 1024x1792, 1792x1024 for DALL-E 3)
            quality (str): Image quality ('standard' or 'hd') - DALL-E 3 only
            style (str): Image style ('vivid' or 'natural') - DALL-E 3 only
            
        Returns:
            dict: Response with image URL or base64 data
        """
        try:
            url = f"{self.base_url}/images/generations"
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "n": 1,  # Number of images to generate
                "size": size,
                "response_format": "b64_json"  # Return base64 encoded image
            }
            
            # Add DALL-E 3 specific parameters
            if model == "dall-e-3":
                payload["quality"] = quality
                payload["style"] = style
            
            _logger.info(f"Generating image with DALL-E {model}, size: {size}, quality: {quality}, style: {style}")
            _logger.debug(f"Image prompt: {prompt[:100]}...")
            
            # Make API request
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=60  # 60 second timeout for image generation
            )
            
            if response.status_code == 200:
                result = response.json()
                _logger.info("Image generated successfully")
                return {
                    'success': True,
                    'data': result['data'][0],
                    'revised_prompt': result['data'][0].get('revised_prompt'),  # DALL-E 3 may revise prompt
                }
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Image generation request timed out"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during image generation: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error during image generation: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def save_image_from_base64(self, base64_data, file_path):
        """
        Save base64 image data to file
        
        Args:
            base64_data (str): Base64 encoded image data
            file_path (str): Full path where to save the image
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Decode and save image
            image_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            _logger.info(f"Image saved successfully to: {file_path}")
            return True
            
        except Exception as e:
            _logger.error(f"Error saving image to {file_path}: {str(e)}")
            return False
    
    def download_image_from_url(self, image_url, file_path):
        """
        Download image from URL and save to file
        
        Args:
            image_url (str): URL of the image to download
            file_path (str): Full path where to save the image
            
        Returns:
            bool: True if downloaded successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            _logger.info(f"Image downloaded successfully to: {file_path}")
            return True
            
        except Exception as e:
            _logger.error(f"Error downloading image from {image_url} to {file_path}: {str(e)}")
            return False


def create_image_generator_from_config(env):
    """
    Create OpenAI image generator from system configuration
    
    Args:
        env: Odoo environment
        
    Returns:
        OpenAIImageGenerator: Configured image generator instance
        
    Raises:
        UserError: If OpenAI API key is not configured
    """
    config = env['ir.config_parameter'].sudo()
    
    api_key = config.get_param('sc_marketing_automation_tool.openai_api_key')
    if not api_key:
        raise UserError(_("OpenAI API key is not configured. Please configure it in Marketing Automation Tool settings."))
    
    organization_id = config.get_param('sc_marketing_automation_tool.openai_organization_id')
    
    return OpenAIImageGenerator(api_key, organization_id)


def get_image_generation_settings(env):
    """
    Get image generation settings from system configuration
    
    Args:
        env: Odoo environment
        
    Returns:
        dict: Image generation settings
    """
    config = env['ir.config_parameter'].sudo()
    
    return {
        'model': config.get_param('sc_marketing_automation_tool.image_generation_model', 'dall-e-3'),
        'size': config.get_param('sc_marketing_automation_tool.image_default_size', '1024x1024'),
        'quality': config.get_param('sc_marketing_automation_tool.image_default_quality', 'standard'),
        'style': config.get_param('sc_marketing_automation_tool.image_default_style', 'vivid'),
    }