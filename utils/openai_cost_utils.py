import requests
import logging
from datetime import datetime, timedelta
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenAICostAnalyzer:
    """Utility class for OpenAI usage and cost analysis"""
    
    def __init__(self, admin_key, project_id=None):
        """Initialize OpenAI cost analyzer with admin credentials"""
        self.admin_key = admin_key
        self.project_id = project_id
        self.base_url = "https://api.openai.com/v1"
        
    def _get_headers(self):
        """Get headers for OpenAI API requests"""
        return {
            "Authorization": f"Bearer {self.admin_key}",
            "Content-Type": "application/json"
        }
    
    def get_organization_costs(self, start_time=None, end_time=None, limit=100):
        """
        Get organization costs from OpenAI API
        
        Args:
            start_time (int): Unix timestamp for start time (optional)
            end_time (int): Unix timestamp for end time (optional)
            limit (int): Maximum number of results to return
            
        Returns:
            dict: API response with cost data
        """
        try:
            url = f"{self.base_url}/organization/costs"
            
            # Prepare query parameters
            params = {"limit": limit}
            
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            if self.project_id:
                params["project_id"] = self.project_id
            
            _logger.info(f"Fetching OpenAI costs with params: {params}")
            
            # Make API request
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                _logger.info(f"Successfully fetched {len(result.get('data', []))} cost buckets")
                return {
                    'success': True,
                    'data': result
                }
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Cost data request timed out"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during cost data fetch: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error during cost data fetch: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_costs_for_period(self, days_back=30):
        """
        Get costs for a specific period (last N days)
        
        Args:
            days_back (int): Number of days to look back
            
        Returns:
            dict: Processed cost data with totals and breakdown
        """
        # Calculate timestamps
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        # Get raw cost data
        response = self.get_organization_costs(
            start_time=start_timestamp,
            end_time=end_timestamp
        )
        
        if not response['success']:
            return response
        
        # Process the data
        return self._process_cost_data(response['data'], start_time, end_time)
    
    def get_current_month_costs(self):
        """Get costs for the current month"""
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        start_timestamp = int(start_of_month.timestamp())
        end_timestamp = int(now.timestamp())
        
        response = self.get_organization_costs(
            start_time=start_timestamp,
            end_time=end_timestamp
        )
        
        if not response['success']:
            return response
        
        return self._process_cost_data(response['data'], start_of_month, now)
    
    def get_previous_month_costs(self):
        """Get costs for the previous month"""
        now = datetime.now()
        
        # First day of current month
        start_of_current_month = datetime(now.year, now.month, 1)
        
        # Last day of previous month
        end_of_previous_month = start_of_current_month - timedelta(days=1)
        
        # First day of previous month
        start_of_previous_month = datetime(
            end_of_previous_month.year, 
            end_of_previous_month.month, 
            1
        )
        
        start_timestamp = int(start_of_previous_month.timestamp())
        end_timestamp = int(end_of_previous_month.timestamp())
        
        response = self.get_organization_costs(
            start_time=start_timestamp,
            end_time=end_timestamp
        )
        
        if not response['success']:
            return response
        
        return self._process_cost_data(response['data'], start_of_previous_month, end_of_previous_month)
    
    def _process_cost_data(self, raw_data, start_time, end_time):
        """
        Process raw cost data into useful statistics
        
        Args:
            raw_data (dict): Raw API response data
            start_time (datetime): Period start time
            end_time (datetime): Period end time
            
        Returns:
            dict: Processed cost statistics
        """
        try:
            buckets = raw_data.get('data', [])
            
            # Initialize totals
            total_amount = 0.0
            currency = 'usd'
            daily_costs = []
            
            # Process each bucket
            for bucket in buckets:
                bucket_start = datetime.fromtimestamp(bucket.get('start_time', 0))
                bucket_end = datetime.fromtimestamp(bucket.get('end_time', 0))
                
                bucket_total = 0.0
                
                # Sum up all results in this bucket
                for result in bucket.get('results', []):
                    amount_info = result.get('amount', {})
                    amount_value = amount_info.get('value', 0.0)
                    currency = amount_info.get('currency', 'usd')
                    
                    bucket_total += amount_value
                    total_amount += amount_value
                
                daily_costs.append({
                    'date': bucket_start.strftime('%Y-%m-%d'),
                    'start_time': bucket_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': bucket_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': bucket_total,
                    'currency': currency
                })
            
            # Calculate additional statistics
            days_in_period = (end_time - start_time).days + 1
            average_daily_cost = total_amount / days_in_period if days_in_period > 0 else 0.0
            
            # Estimate monthly cost if this is not a full month
            if days_in_period < 30:
                estimated_monthly_cost = average_daily_cost * 30
            else:
                estimated_monthly_cost = total_amount
            
            return {
                'success': True,
                'period': {
                    'start': start_time.strftime('%Y-%m-%d'),
                    'end': end_time.strftime('%Y-%m-%d'),
                    'days': days_in_period
                },
                'summary': {
                    'total_amount': total_amount,
                    'currency': currency.upper(),
                    'average_daily_cost': average_daily_cost,
                    'estimated_monthly_cost': estimated_monthly_cost
                },
                'daily_breakdown': daily_costs,
                'project_id': self.project_id
            }
            
        except Exception as e:
            error_msg = f"Error processing cost data: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}


def create_cost_analyzer_from_config(env):
    """
    Create OpenAI cost analyzer from system configuration
    
    Args:
        env: Odoo environment
        
    Returns:
        OpenAICostAnalyzer: Configured cost analyzer instance
        
    Raises:
        UserError: If OpenAI admin key is not configured
    """
    config = env['ir.config_parameter'].sudo()
    
    admin_key = config.get_param('sc_marketing_automation_tool.openai_admin_key')
    if not admin_key:
        raise UserError(_("OpenAI Admin Key is not configured. Please configure it in Marketing Automation Tool settings to view usage statistics."))
    
    project_id = config.get_param('sc_marketing_automation_tool.openai_project_id')
    
    return OpenAICostAnalyzer(admin_key, project_id)


def get_usage_summary(env):
    """
    Get a comprehensive usage summary
    
    Args:
        env: Odoo environment
        
    Returns:
        dict: Usage summary with current month, previous month, and trends
    """
    try:
        analyzer = create_cost_analyzer_from_config(env)
        
        # Get current and previous month data
        current_month = analyzer.get_current_month_costs()
        previous_month = analyzer.get_previous_month_costs()
        last_30_days = analyzer.get_costs_for_period(30)
        
        if not all([current_month['success'], previous_month['success'], last_30_days['success']]):
            errors = []
            if not current_month['success']:
                errors.append(f"Current month: {current_month.get('error', 'Unknown error')}")
            if not previous_month['success']:
                errors.append(f"Previous month: {previous_month.get('error', 'Unknown error')}")
            if not last_30_days['success']:
                errors.append(f"Last 30 days: {last_30_days.get('error', 'Unknown error')}")
            
            return {
                'success': False,
                'error': "Failed to fetch some usage data: " + "; ".join(errors)
            }
        
        # Calculate trends
        current_total = current_month.get('summary', {}).get('total_amount', 0.0)
        previous_total = previous_month.get('summary', {}).get('total_amount', 0.0)
        
        if previous_total > 0:
            month_over_month_change = ((current_total - previous_total) / previous_total) * 100
        else:
            month_over_month_change = 0.0
        
        return {
            'success': True,
            'current_month': current_month,
            'previous_month': previous_month,
            'last_30_days': last_30_days,
            'trends': {
                'month_over_month_change': month_over_month_change,
                'is_increasing': month_over_month_change > 0
            }
        }
        
    except Exception as e:
        error_msg = f"Error getting usage summary: {str(e)}"
        _logger.error(error_msg)
        return {'success': False, 'error': error_msg}