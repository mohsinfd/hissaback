import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode

class EdgeRedirector:
    """Simulates edge redirector for smart links"""
    
    def __init__(self):
        self.redirect_logs = []
    
    def parse_smart_link(self, url: str) -> Dict[str, Any]:
        """Parse smart link URL and extract parameters"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Extract path parameters
        path_parts = parsed.path.split('/')
        slug = path_parts[-1] if len(path_parts) > 1 else None
        
        return {
            'slug': slug,
            'publisher_id': query_params.get('publisher_id', [None])[0],
            'campaign_id': query_params.get('campaign_id', [None])[0],
            'click_id': query_params.get('click_id', [None])[0],
            'trackier_link': query_params.get('trackier_link', [None])[0],
            'original_url': url
        }
    
    def generate_click_id(self) -> str:
        """Generate a unique click ID"""
        return f"click_{uuid.uuid4().hex[:12]}"
    
    def log_click(self, smart_link_data: Dict[str, Any], user_agent: str, ip_address: str) -> str:
        """Log a click and return click ID"""
        click_id = self.generate_click_id()
        
        log_entry = {
            'click_id': click_id,
            'timestamp': datetime.utcnow().isoformat(),
            'smart_link_data': smart_link_data,
            'user_agent': user_agent,
            'ip_address': ip_address,
            'status': 'tracked'
        }
        
        self.redirect_logs.append(log_entry)
        return click_id
    
    def redirect_to_merchant(self, smart_link_data: Dict[str, Any], click_id: str) -> str:
        """Generate merchant redirect URL with tracking parameters"""
        # Simulate different merchant URLs based on campaign
        campaign_id = smart_link_data.get('campaign_id', '')
        
        if 'flipkart' in campaign_id.lower():
            base_url = "https://www.flipkart.com"
        elif 'amazon' in campaign_id.lower():
            base_url = "https://www.amazon.in"
        else:
            base_url = "https://www.flipkart.com"  # Default
        
        # Add tracking parameters
        tracking_params = {
            'utm_source': 'hissaback',
            'utm_medium': 'affiliate',
            'utm_campaign': smart_link_data.get('campaign_id', ''),
            'click_id': click_id,
            'publisher_id': smart_link_data.get('publisher_id', ''),
            'trackier_link': '1'
        }
        
        merchant_url = f"{base_url}/?{urlencode(tracking_params)}"
        return merchant_url
    
    def process_redirect(self, smart_link_url: str, user_agent: str = "Demo Browser", ip_address: str = "127.0.0.1") -> Dict[str, Any]:
        """Process a smart link redirect"""
        # Parse the smart link
        smart_link_data = self.parse_smart_link(smart_link_url)
        
        # Log the click
        click_id = self.log_click(smart_link_data, user_agent, ip_address)
        
        # Generate merchant redirect URL
        merchant_url = self.redirect_to_merchant(smart_link_data, click_id)
        
        return {
            'click_id': click_id,
            'merchant_url': merchant_url,
            'smart_link_data': smart_link_data,
            'redirect_timestamp': datetime.utcnow().isoformat(),
            'status': 'redirected'
        }
    
    def get_click_logs(self) -> list:
        """Get all click logs"""
        return self.redirect_logs
    
    def get_click_by_id(self, click_id: str) -> Optional[Dict[str, Any]]:
        """Get click log by ID"""
        for log in self.redirect_logs:
            if log['click_id'] == click_id:
                return log
        return None

# Global instance
edge_redirector = EdgeRedirector() 