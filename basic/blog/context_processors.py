from basic.blog import settings

def blog_settings(request):
    """
    Add blog settings to the context, making them available to templates.
    """
    return {
        'blog_name': settings.BLOG_NAME,
        'blog_description': settings.BLOG_DESCRIPTION,
        'blog_excerpts': settings.BLOG_EXCERPTS
    }
