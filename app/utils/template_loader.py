import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class TemplateLoader:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )

    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with the given context variables."""
        template = self.env.get_template(f'emails/{template_name}.html')
        return template.render(**kwargs) 