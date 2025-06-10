from django import template
# import re # No longer needed with markdown library
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
    # Extensions can be added for more features if needed
    html_output = markdown.markdown(value, extensions=['nl2br', 'fenced_code', 'extra'])

    return mark_safe(html_output)

# Remove the old regex-based helper function if it exists and is not used elsewhere
# def format_plan_text_with_html(text):
#    ...