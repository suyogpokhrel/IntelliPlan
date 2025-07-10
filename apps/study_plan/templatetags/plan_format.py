from django import template
from django.utils.safestring import mark_safe
import markdown # Import the markdown library

register = template.Library()

@register.filter
def format_study_plan(value):
    """
    Convert markdown study plan text to HTML using the markdown library.
    """
    if not value:
        return ''

    # Use the markdown library to convert the text to HTML
    html_output = markdown.markdown(value, extensions=['nl2br', 'fenced_code', 'extra'])

    return mark_safe(html_output)

