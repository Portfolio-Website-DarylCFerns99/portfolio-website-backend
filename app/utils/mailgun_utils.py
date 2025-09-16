import os
import json
import requests
from typing import List, Dict, Optional

from ..config.settings import settings

class MailgunEmail:
    def __init__(self):
        self.base_url = settings.MAILGUN_API_URL
        self.api_key = settings.MAILGUN_API_KEY
        self.from_email = settings.MAILGUN_FROM_EMAIL
        self.admin_email = settings.ADMIN_EMAIL
        
        # Dynamic template IDs
        self.notification_template_id = settings.MAILGUN_NOTIFICATION_TEMPLATE_ID
        self.confirmation_template_id = settings.MAILGUN_CONFIRMATION_TEMPLATE_ID

    def _format_social_links(self, social_links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format social links for the email template."""
        valid_platforms = ['linkedin', 'github', 'twitter', 'instagram', 'facebook']
        formatted_links = []
        
        for link in social_links:
            platform = link.get('platform', '').lower()
            if platform in valid_platforms and link.get('url'):
                formatted_links.append({
                    'platform': platform,
                    'url': link['url'],
                    'tooltip': link.get('tooltip', platform.title())
                })
        
        return formatted_links

    def send_confirmation_email(self, name: str, email: str, subject: str, message: str, social_links: List[Dict[str, str]], portfolio_url: str, your_name: str) -> None:
        """Send confirmation email to the user who submitted the contact form."""
        
        # Prepare dynamic template data
        template_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'social_links': self._format_social_links(social_links),
            'portfolio_url': portfolio_url,
            'your_name': your_name
        }
        
        res = requests.post(
            f"{self.base_url}/messages",
            auth=("api", self.api_key),
            data={
                "from": self.from_email,
                "to": [email],
                "subject": subject,
                "template": self.confirmation_template_id,
                "t:variables": json.dumps(template_data)
            }
        )

        # print(res.status_code, res.text)
        if res.status_code != 200:
            res.raise_for_status()
        

    def send_notification_email(self, name: str, email: str, subject: str, message: str, your_name: str) -> None:
        """Send notification email to the admin about the new contact form submission."""
        
        # Prepare dynamic template data
        template_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'your_name': your_name
        }
        
        res = requests.post(
            f"{self.base_url}/messages",
            auth=("api", self.api_key),
            data={
                "from": self.from_email,
                "to": [email],
                "subject": subject,
                "template": self.notification_template_id,
                "t:variables": json.dumps(template_data)
            }
        )

        # print(res.status_code, res.text)
        if res.status_code != 200:
            res.raise_for_status()
