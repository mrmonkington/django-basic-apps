from haystack.indexes import *
from haystack import site
from basic.blog.models import Post

class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Only index published posts."""
        return Post.objects.published()

site.register(Post, PostIndex)
