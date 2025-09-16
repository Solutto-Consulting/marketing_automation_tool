from odoo import api, fields, models, _

class ScOpenaiModels(models.AbstractModel):
    """
    Centralized OpenAI Models Configuration
    
    This class provides a single source of truth for all OpenAI models
    supported by the Marketing Automation Tool. It ensures consistency
    across all model selection fields throughout the system.
    """
    _name = 'sc.openai.models'
    _description = 'OpenAI Models Configuration'

    @api.model
    def get_text_models(self):
        """
        Get the list of supported OpenAI text models for content generation and research.
        
        Returns:
            list: List of tuples (model_id, model_name) for text models
        """
        return [
            ('gpt-5', 'GPT-5'),
            ('gpt-5-mini', 'GPT-5 Mini'),
            ('gpt-5-nano', 'GPT-5 Nano'),
            ('gpt-4.1', 'GPT-4.1'),
            ('gpt-4.1-mini', 'GPT-4.1 Mini'),
            ('gpt-4.1-nano', 'GPT-4.1 Nano'),
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4o-mini', 'GPT-4o Mini'),
        ]

    @api.model
    def get_image_models(self):
        """
        Get the list of supported OpenAI image generation models.
        
        Returns:
            list: List of tuples (model_id, model_name) for image models
        """
        return [
            ('gpt-image-1', 'GPT-Image-1 (Responses API)'),
        ]

    @api.model
    def get_all_models(self):
        """
        Get all supported OpenAI models (text + image) for logging purposes.
        
        Returns:
            list: List of tuples (model_id, model_name) for all models
        """
        return self.get_text_models() + self.get_image_models() + [('other', 'Other Model')]

    @api.model
    def get_model_display_name(self, model_id):
        """
        Get the display name for a given model ID.
        
        Args:
            model_id (str): The model identifier
            
        Returns:
            str: The display name or 'Unknown Model' if not found
        """
        models_dict = dict(self.get_all_models())
        return models_dict.get(model_id, 'Unknown Model')

    @api.model
    def is_valid_text_model(self, model_id):
        """
        Check if a model ID is a valid text model.
        
        Args:
            model_id (str): The model identifier
            
        Returns:
            bool: True if valid text model, False otherwise
        """
        valid_models = [model[0] for model in self.get_text_models()]
        return model_id in valid_models

    @api.model
    def is_valid_image_model(self, model_id):
        """
        Check if a model ID is a valid image model.
        
        Args:
            model_id (str): The model identifier
            
        Returns:
            bool: True if valid image model, False otherwise
        """
        valid_models = [model[0] for model in self.get_image_models()]
        return model_id in valid_models

    @api.model
    def is_valid_model(self, model_id):
        """
        Check if a model ID is valid (text or image).
        
        Args:
            model_id (str): The model identifier
            
        Returns:
            bool: True if valid model, False otherwise
        """
        return self.is_valid_text_model(model_id) or self.is_valid_image_model(model_id)

    @api.model
    def get_default_text_model(self):
        """
        Get the default text model for new configurations.
        
        Returns:
            str: Default model ID
        """
        return 'gpt-4o'

    @api.model
    def get_default_image_model(self):
        """
        Get the default image model for new configurations.
        
        Returns:
            str: Default image model ID
        """
        return 'gpt-image-1'