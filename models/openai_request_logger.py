"""
OpenAI Request Interceptor for transparent monitoring and logging.

This module provides a transparent way to capture OpenAI API request metrics
without modifying the existing translation workflow.
"""

import time
import logging
import json
from typing import Optional, Dict, Any
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class OpenAIRequestInterceptor:
    """
    Transparent interceptor for OpenAI requests using the openai-agents SDK.
    
    This class wraps the OpenAI Agents SDK to automatically capture:
    - Request metrics (tokens, timing, costs)
    - Response status and errors
    - Model usage statistics
    
    The interceptor is designed to be completely transparent - it doesn't
    change the behavior of existing code, just adds monitoring capabilities.
    """
    
    def __init__(self, odoo_env):
        """
        Initialize the interceptor with Odoo environment context.
        
        Args:
            odoo_env: Odoo environment for database operations
        """
        self.env = odoo_env
        self._original_runner = None
        self._monitoring_enabled = True
        
    def enable_monitoring(self):
        """Enable request monitoring and logging"""
        self._monitoring_enabled = True
        _logger.info("OpenAI request monitoring enabled")
        
    def disable_monitoring(self):
        """Disable request monitoring (for debugging or performance)"""
        self._monitoring_enabled = False
        _logger.info("OpenAI request monitoring disabled")
    
    async def run_with_monitoring(self, agent, prompt, **kwargs):
        """
        Execute an OpenAI Agents run with automatic monitoring.
        
        This method wraps the original Runner.run() to capture metrics
        while maintaining complete compatibility with existing code.
        
        Args:
            agent: OpenAI Agent instance
            prompt (str): Input prompt
            **kwargs: Additional arguments passed to Runner.run()
            
        Returns:
            Same result as original Runner.run()
        """
        # Import here to avoid import errors if package not installed
        try:
            from agents import Runner
        except ImportError:
            _logger.error("openai-agents package not available")
            raise Exception("OpenAI Agents SDK not installed")
        
        # Start timing
        start_time = time.time()
        request_start = time.perf_counter()
        
        # Initialize tracking variables
        model_name = getattr(agent, 'model', 'unknown')
        operation_type = self._detect_operation_type(prompt)
        request_id = None
        status = 'success'
        error_message = None
        prompt_tokens = 0
        completion_tokens = 0
        
        try:
            # Estimate input tokens (rough estimation)
            prompt_tokens = self._estimate_tokens(prompt)
            
            # Execute the original request
            result = await Runner.run(agent, prompt, **kwargs)
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Estimate output tokens
            if hasattr(result, 'final_output'):
                completion_tokens = self._estimate_tokens(str(result.final_output))
            
            # Try to extract additional metadata if available
            if hasattr(result, '_request_id'):
                request_id = result._request_id
                
        except Exception as e:
            # Calculate response time even for errors
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Log the error
            status = 'error'
            error_message = str(e)
            _logger.error(f"OpenAI request failed: {error_message}")
            
            # Re-raise the original exception to maintain existing behavior
            raise
            
        finally:
            # Log the request metrics (even if the request failed)
            if self._monitoring_enabled:
                try:
                    self._log_request_metrics(
                        model_name=model_name,
                        operation_type=operation_type,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        response_time_ms=response_time_ms,
                        status=status,
                        error_message=error_message,
                        request_id=request_id
                    )
                except Exception as log_error:
                    # Don't let logging errors break the main flow
                    _logger.error(f"Failed to log OpenAI request metrics: {log_error}")
        
        return result
    
    def _detect_operation_type(self, prompt):
        """
        Detect the type of operation based on the prompt content.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            str: Operation type classification
        """
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['translate', 'translation', 'traduci', 'traduc']):
            return 'translation'
        elif any(word in prompt_lower for word in ['generate', 'create', 'write', 'compose']):
            return 'generation'
        elif any(word in prompt_lower for word in ['analyze', 'analysis', 'research', 'summarize']):
            return 'analysis'
        elif any(word in prompt_lower for word in ['search', 'find', 'lookup', 'browse']):
            return 'research'
        else:
            return 'other'
    
    def _estimate_tokens(self, text):
        """
        Estimate token count for text.
        
        This is a rough estimation. For exact counts, you would need
        to use tiktoken library with the specific model's tokenizer.
        
        Args:
            text (str): Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        if not text:
            return 0
            
        # Simple estimation: roughly 4 characters per token
        # This is approximate and varies by language and content
        try:
            # Try using tiktoken if available for more accurate counting
            try:
                import tiktoken
                # Use gpt-4 encoding as a reasonable default
                encoding = tiktoken.encoding_for_model("gpt-4")
                return len(encoding.encode(text))
            except ImportError:
                # Fallback to simple estimation
                return max(1, len(text) // 4)
        except Exception:
            # Fallback to very simple estimation
            return max(1, len(str(text).split()) + len(str(text)) // 20)
    
    def _log_request_metrics(self, model_name, operation_type, prompt_tokens, 
                           completion_tokens, response_time_ms, status, 
                           error_message=None, request_id=None):
        """
        Log request metrics to the database.
        
        Args:
            model_name (str): OpenAI model used
            operation_type (str): Type of operation
            prompt_tokens (int): Input tokens
            completion_tokens (int): Output tokens  
            response_time_ms (int): Response time in milliseconds
            status (str): Request status
            error_message (str): Error message if failed
            request_id (str): OpenAI request ID
        """
        try:
            # Create log entry using the model method
            log_model = self.env['sc.openai.request.log']
            
            log_model.create_log_entry(
                model_name=model_name,
                operation_type=operation_type,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time_ms=response_time_ms,
                status=status,
                error_message=error_message,
                request_id=request_id
            )
            
            # Update daily statistics asynchronously
            self._update_daily_statistics_async(model_name)
            
        except Exception as e:
            # Log error but don't raise to avoid breaking main flow
            _logger.error(f"Failed to log OpenAI request metrics: {str(e)}")
    
    def _update_daily_statistics_async(self, model_name):
        """
        Update daily statistics in the background.
        
        Args:
            model_name (str): Model to update statistics for
        """
        try:
            # Update today's statistics
            stats_model = self.env['sc.openai.model.statistics']
            stats_model.update_daily_statistics()
            
        except Exception as e:
            _logger.error(f"Failed to update daily statistics: {str(e)}")
    
    def set_related_record_context(self, model_name, record_id, record_name=None):
        """
        Set context for the next request to link it to a specific Odoo record.
        
        Args:
            model_name (str): Odoo model name (e.g., 'blog.post')
            record_id (int): Record ID
            record_name (str): Optional record name for display
        """
        self._context_model = model_name
        self._context_record_id = record_id
        self._context_record_name = record_name
    
    def clear_context(self):
        """Clear the current record context"""
        self._context_model = None
        self._context_record_id = None
        self._context_record_name = None


class OpenAIMonitoringMixin(models.AbstractModel):
    """
    Mixin to add OpenAI monitoring capabilities to any model.
    
    Models that inherit from this mixin can easily set up monitoring
    for their OpenAI requests.
    """
    _name = 'openai.monitoring.mixin'
    _description = 'OpenAI Monitoring Mixin'
    
    def _get_openai_interceptor(self):
        """
        Get or create an OpenAI request interceptor for this environment.
        
        Returns:
            OpenAIRequestInterceptor: Interceptor instance
        """
        if not hasattr(self, '_openai_interceptor'):
            self._openai_interceptor = OpenAIRequestInterceptor(self.env)
        return self._openai_interceptor
    
    def _setup_openai_monitoring(self):
        """
        Set up OpenAI monitoring with agents SDK logging.
        
        This method configures the OpenAI Agents SDK to provide
        detailed logging while maintaining backward compatibility.
        """
        try:
            # Enable verbose logging for the agents SDK
            from agents import enable_verbose_stdout_logging
            enable_verbose_stdout_logging()
            
            # Configure the agents logger
            import logging
            agents_logger = logging.getLogger("openai.agents")
            agents_logger.setLevel(logging.INFO)
            
            # Add a handler if it doesn't exist
            if not agents_logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                agents_logger.addHandler(handler)
            
            _logger.info("OpenAI Agents SDK monitoring configured successfully")
            
        except ImportError:
            _logger.warning("OpenAI Agents SDK not available for monitoring setup")
        except Exception as e:
            _logger.error(f"Failed to setup OpenAI monitoring: {str(e)}")
    
    async def _monitored_ai_request(self, agent, prompt, related_model=None, 
                                   related_record_id=None, related_record_name=None):
        """
        Execute a monitored AI request with automatic logging.
        
        Args:
            agent: OpenAI Agent instance
            prompt (str): Input prompt
            related_model (str): Related Odoo model name
            related_record_id (int): Related record ID
            related_record_name (str): Related record name
            
        Returns:
            Same as original Runner.run()
        """
        interceptor = self._get_openai_interceptor()
        
        # Set context if provided
        if related_model and related_record_id:
            interceptor.set_related_record_context(
                related_model, related_record_id, related_record_name
            )
        
        try:
            # Execute the request with monitoring
            result = await interceptor.run_with_monitoring(agent, prompt)
            return result
        finally:
            # Clear context after request
            interceptor.clear_context()