import requests
import logging
from bs4 import BeautifulSoup
from odoo import api, fields, models
from urllib.parse import urljoin, urlparse
import time

_logger = logging.getLogger(__name__)

class WebContentReader(models.AbstractModel):
    """Utility class for reading and extracting content from web pages"""
    _name = 'web.content.reader'
    _description = 'Web Content Reading Utilities'

    @api.model
    def extract_article_content(self, url, timeout=30):
        """
        Extract clean article content from a URL
        
        Args:
            url (str): The URL to extract content from
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: {
                'title': str,
                'content': str,
                'meta_description': str,
                'excerpt': str,
                'word_count': int,
                'reading_time': int,
                'success': bool,
                'error': str
            }
        """
        try:
            # Validate URL
            if not url or not url.startswith(('http://', 'https://')):
                return self._error_response("Invalid URL format")
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Make request with timeout and retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        return self._error_response(f"Failed to fetch URL after {max_retries} attempts: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract meta description
            meta_description = self._extract_meta_description(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            if not content.strip():
                return self._error_response("No readable content found in the article")
            
            # Calculate metrics
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)  # Assume 200 words per minute
            
            # Create excerpt (first 200 words)
            words = content.split()
            excerpt = ' '.join(words[:200])
            if len(words) > 200:
                excerpt += '...'
            
            return {
                'title': title,
                'content': content,
                'meta_description': meta_description,
                'excerpt': excerpt,
                'word_count': word_count,
                'reading_time': reading_time,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            _logger.error(f"Error extracting content from {url}: {str(e)}")
            return self._error_response(f"Content extraction failed: {str(e)}")
    
    def _extract_title(self, soup):
        """Extract page title from HTML"""
        # Try different title sources in order of preference
        title_selectors = [
            'h1',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            '.entry-title',
            '.post-title',
            '.article-title'
        ]
        
        for selector in title_selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element.get('content').strip()
            else:
                element = soup.select_one(selector)
                if element and element.get_text():
                    return element.get_text().strip()
        
        return "Untitled Article"
    
    def _extract_meta_description(self, soup):
        """Extract meta description from HTML"""
        meta_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            'meta[name="twitter:description"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element and element.get('content'):
                return element.get('content').strip()
        
        return ""
    
    def _extract_main_content(self, soup):
        """Extract main article content from HTML"""
        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'iframe']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with unwanted classes/ids
        unwanted_patterns = [
            'advertisement', 'ads', 'sidebar', 'comments', 'social', 
            'share', 'footer', 'header', 'navigation', 'menu'
        ]
        
        for pattern in unwanted_patterns:
            for element in soup.find_all(attrs={'class': lambda x: x and pattern in ' '.join(x).lower()}):
                element.decompose()
            for element in soup.find_all(attrs={'id': lambda x: x and pattern in x.lower()}):
                element.decompose()
        
        # Try to find main content using common patterns
        content_selectors = [
            'article',
            '.entry-content',
            '.post-content',
            '.article-content',
            '.content',
            'main',
            '#content',
            '.post-body',
            '.article-body'
        ]
        
        content_text = ""
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_text = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                if len(content_text.split()) > 50:  # Minimum word threshold
                    break
        
        # Fallback: extract all paragraph text
        if not content_text or len(content_text.split()) < 50:
            paragraphs = soup.find_all('p')
            content_text = ' '.join([p.get_text(separator=' ', strip=True) for p in paragraphs])
        
        # Clean up the text
        content_text = ' '.join(content_text.split())  # Normalize whitespace
        
        return content_text
    
    def _error_response(self, error_message):
        """Return standardized error response"""
        return {
            'title': "",
            'content': "",
            'meta_description': "",
            'excerpt': "",
            'word_count': 0,
            'reading_time': 0,
            'success': False,
            'error': error_message
        }
    
    @api.model
    def test_content_extraction(self, url):
        """Test method for content extraction - useful for debugging"""
        result = self.extract_article_content(url)
        _logger.info(f"Content extraction test for {url}: {result['success']}")
        if result['success']:
            _logger.info(f"Title: {result['title'][:100]}...")
            _logger.info(f"Content length: {result['word_count']} words")
        else:
            _logger.error(f"Extraction failed: {result['error']}")
        return result
