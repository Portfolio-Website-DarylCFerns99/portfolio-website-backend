from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from dotenv import load_dotenv
from .template_loader import TemplateLoader
from typing import List, Dict, Optional

load_dotenv()

class SendGridEmail:
    def __init__(self):
        self.sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = Email(os.getenv('SENDGRID_FROM_EMAIL', 'your-email@domain.com'))
        self.admin_email = os.getenv('ADMIN_EMAIL', 'your-email@domain.com')
        self.template_loader = TemplateLoader()

    def _format_social_links(self, social_links: List[Dict[str, str]]) -> str:
        """Format social links for the email template."""
        valid_platforms = ['linkedin', 'github', 'twitter', 'instagram', 'facebook']
        formatted_links = []
        
        for link in social_links:
            platform = link.get('platform', '').lower()
            if platform in valid_platforms and link.get('url'):
                formatted_links.append(f'<a href="{link["url"]}" target="_blank">{link["tooltip"]}</a>')
        
        return ' | '.join(formatted_links) if formatted_links else ''

    def send_confirmation_email(self, name: str, email: str, subject: str, message: str, social_links: List[Dict[str, str]], portfolio_url: str, your_name: str) -> None:
        """Send confirmation email to the user who submitted the contact form."""
        html_content = self.template_loader.render_template(
            'confirmation',
            name=name,
            email=email,
            subject=subject,
            message=message,
            social_links=self._format_social_links(social_links),
            portfolio_url=portfolio_url,
            your_name=your_name
        )
        
        user_email = Mail(
            from_email=self.from_email,
            to_emails=To(email),
            subject=f'Thank you for reaching out - {your_name}',
            html_content=Content('text/html', html_content)
        )
        self.sg.send(user_email)

    def send_notification_email(self, name: str, email: str, subject: str, message: str, your_name: str) -> None:
        """Send notification email to the admin about the new contact form submission."""
        html_content = self.template_loader.render_template(
            'notification',
            name=name,
            email=email,
            subject=subject,
            message=message,
            your_name=your_name
        )
        
        notification_email = Mail(
            from_email=self.from_email,
            to_emails=To(self.admin_email),
            subject=f'New Contact Form Submission: {subject}',
            html_content=Content('text/html', html_content)
        )
        self.sg.send(notification_email) 