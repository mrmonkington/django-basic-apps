from django import forms
from basic.blog.models import Post

# Attempt to import WMDWidget from Django WMD.
# If it's around, create a form that uses the widget on the body field of a
# post.
try:
    from wmd.widgets import WMDWidget

    class PostForm(forms.ModelForm):
        body = forms.CharField(widget=WMDWidget)
        class Meta:
            model = Post
except ImportError:
    pass
