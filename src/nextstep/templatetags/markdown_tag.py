import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown(text):
    # 1. Convert Markdown to HTML
    html_content = markdown.markdown(text, extensions=["extra", "codehilite"])

    # 2. Define "Safe" tags and attributes
    # You can customize this list based on what you want to allow
    allowed_tags = [
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "ul",
        "strong",
        "p",
        "h1",
        "h2",
        "h3",
        "br",
        "pre",
    ]
    allowed_attrs = {
        "a": ["href", "title"],
        "abbr": ["title"],
        "acronym": ["title"],
    }

    # 3. Clean the HTML
    cleaned_content = bleach.clean(
        html_content, tags=allowed_tags, attributes=allowed_attrs
    )

    # 4. Return as safe string
    return mark_safe(cleaned_content)
