"""
These blog settings should not be edited directly.
Instead, overwrite them in the main project's setting file.
"""
from django.conf import settings
from django.contrib.sites.models import Site

# The name of the blog.
# This defaults to the name of the site.
BLOG_NAME = getattr(settings, 'BLOG_NAME', Site.objects.get_current().name)

# A short description of what the blog is about.
BLOG_DESCRIPTION = getattr(settings, 'BLOG_DESCRIPTION', 'A basic Django blog')

# If set to true, the Markdown WMD editor from Django WMD will be used on the
# body field of all posts.
BLOG_WMD = getattr(settings, 'BLOG_WMD', False)
