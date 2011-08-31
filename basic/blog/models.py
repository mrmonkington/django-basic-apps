import datetime

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords_html

from taggit.managers import TaggableManager
from django_markup.fields import MarkupField
from django_markup.markup import formatter

from basic.blog.managers import PublicManager
from basic.blog import settings
from basic.inlines.parser import inlines

class Category(models.Model):
    """Category model."""
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        db_table = 'blog_categories'
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_category_detail', None, {'slug': self.slug})


class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish', max_length=100)
    author = models.ForeignKey(User, blank=True, null=True)
    markup = MarkupField(default='markdown')
    body = models.TextField(_('body'), )
    body_rendered = models.TextField(editable=True, blank=True, null=True)
    tease = models.TextField(_('tease'), blank=True)
    tease_rendered = models.TextField(editable=True, blank=True, null=True)
    visits = models.IntegerField(_('visits'), default=0, editable=False)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments = models.BooleanField(_('allow comments'), default=True)
    publish = models.DateTimeField(_('publish'), default=datetime.datetime.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = TaggableManager(blank=True)
    objects = PublicManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'blog_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        # Inlines must be rendered before markup in order to properly preserve
        # whitespace
        self.body_rendered = inlines(self.body)
        self.tease_rendered = inlines(self.tease)
        # Render the markup and save it in the body_rendered field.
        self.body_rendered = mark_safe(formatter(self.body_rendered, filter_name=self.markup))
        self.tease_rendered = mark_safe(formatter(self.tease_rendered, filter_name=self.markup))
        # Run the body and tease through Smartypants, if enabled.
        if BLOG_SMARTYPANTS:
            self.body_rendered = mark_safe(formatter(self.body_rendered, filter_name='smartypants')
            self.tease_rendered = mark_safe(formatter(self.tease_rendered, filter_name='smartypants')
        # Call the real save.
        super(Post, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return ('blog_detail', None, {
            'year': self.publish.year,
            'month': self.publish.strftime('%m'),
            'day': self.publish.day,
            'slug': self.slug
        })

    @property
    def excerpt(self):
        """
        Return the excerpt of a post, respecting the auto excerpt settings,
        with a link to continue reading if appropriate.
        """
        # Create the link to continue reading the full post.
        continue_link = """
                   <p class="continue">
                       <a href="%s" title="Continue reading this post">%s</a>
                   </p>
                   """ % (self.get_absolute_url(), settings.BLOG_CONTINUE)

        excerpt = self.tease_rendered
        
        # If auto excerpts are enabled and the post does not have a tease,
        # truncate the body and set that to the tease.
        if settings.BLOG_AUTOEXCERPTS and not self.tease:
            excerpt = truncatewords_html(self.body_rendered,
                                       settings.BLOG_AUTOEXCERPTS)
            # If the auto excerpt is the same as the full body, set the
            # continue link to an empty string so that it is not displayed.
            if excerpt == self.body_rendered:
                continue_link = ""

        # If there is an excerpt, return it followed by the continue link.
        if excerpt:
            return "%s %s" % (excerpt, mark_safe(continue_link))

        # If we're still here, there is no excerpt.
        return False

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)


class BlogRoll(models.Model):
    """Other blogs you follow."""
    name = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    sort_order = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=500, blank=True)
    relationship = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ('sort_order', 'name',)
        verbose_name = _('blog roll')
        verbose_name_plural = _('blog roll')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.url
