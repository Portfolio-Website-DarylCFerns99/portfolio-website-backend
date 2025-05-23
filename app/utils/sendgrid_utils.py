from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from ..config.settings import settings
from typing import List, Dict, Optional

class SendGridEmail:
    def __init__(self):
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = Email(settings.SENDGRID_FROM_EMAIL)
        self.admin_email = settings.ADMIN_EMAIL
        
        # Dynamic template IDs
        self.notification_template_id = settings.SENDGRID_NOTIFICATION_TEMPLATE_ID
        self.confirmation_template_id = settings.SENDGRID_CONFIRMATION_TEMPLATE_ID

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
        
        user_email = Mail(
            from_email=self.from_email,
            to_emails=To(email)
        )
        
        # Set the dynamic template ID and data
        user_email.template_id = self.confirmation_template_id
        user_email.dynamic_template_data = template_data
        
        self.sg.send(user_email)

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
        
        notification_email = Mail(
            from_email=self.from_email,
            to_emails=To(self.admin_email)
        )
        
        # Set the dynamic template ID and data
        notification_email.template_id = self.notification_template_id
        notification_email.dynamic_template_data = template_data
        
        self.sg.send(notification_email) 