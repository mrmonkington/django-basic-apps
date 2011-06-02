import datetime
import re
import time

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from django.views.generic import date_based, list_detail
from django.db.models import Q, F
from django.conf import settings

from basic.blog import settings as blog_settings
from basic.blog.models import *
from basic.tools.constants import STOP_WORDS_RE
from taggit.models import Tag


def post_list(request, page=0, **kwargs):
    return list_detail.object_list(
        request,
        queryset=Post.objects.published(),
        paginate_by=blog_settings.BLOG_PAGESIZE,
        page=page,
        **kwargs
    )
post_list.__doc__ = list_detail.object_list.__doc__


def post_archive_year(request, year, page=0, **kwargs):
    # Date based generic views cannot be paginated. I think pagination is
    # necessary for viewing yearly archives, so we'll use a list generic view
    # filtered by year instead.
    return list_detail.object_list(
        request,
        queryset = Post.objects.published().filter(publish__year=year),
        paginate_by=blog_settings.BLOG_PAGESIZE,
        page=page,
        extra_context={
            'type': 'year',
            'query': year,
            'query_pretty': year
        },
        template_name='blog/post_list.html',
    )
post_archive_year.__doc__ = date_based.archive_year.__doc__


def post_archive_month(request, year, month, **kwargs):
    # Allow both 3-letter month abbreviations and month as decimal number.
    month_format = '%b'
    if len(month) < 3:
        month_format = '%m'

    return date_based.archive_month(
        request,
        year=year,
        month=month,
        month_format=month_format,
        date_field='publish',
        queryset=Post.objects.published(),
        extra_context={
            'type': 'month',
            'query': year + month,
            'query_pretty': time.strftime("%B %Y",
                time.strptime("%s %s" % (month, year), month_format + " %Y")
            )
        },
        template_name='blog/post_list.html',
        **kwargs
    )
post_archive_month.__doc__ = date_based.archive_month.__doc__


def post_archive_day(request, year, month, day, **kwargs):
    # Allow both 3-letter month abbreviations and month as decimal number.
    month_format = '%b'
    if len(month) < 3:
        month_format = '%m'

    return date_based.archive_day(
        request,
        year=year,
        month=month,
        month_format=month_format,
        day=day,
        date_field='publish',
        queryset=Post.objects.published(),
        extra_context={
            'type': 'day',
            'query': year + month + day,
            'query_pretty': time.strftime("%B %-d %Y",
                time.strptime("%s %s %s" % (month, day, year), month_format + " %d %Y")
            )
        },
        template_name='blog/post_list.html',
        **kwargs
    )
post_archive_day.__doc__ = date_based.archive_day.__doc__


def post_detail(request, slug, year, month, day, **kwargs):
    """
    Displays post detail. If user is superuser, view will display 
    unpublished post detail for previewing purposes.
    """

    # Allow both 3-letter month abbreviations and month as decimal number.
    month_format = '%b'
    if len(month) < 3:
        month_format = '%m'

    # This duplicates date_base.object_detail() but allows the view count to be
    # incremented.
    try:
        tt = time.strptime('%s-%s-%s' % (year, month, day), '%%Y-%s-%%d' % month_format)
    except ValueError:
        raise Http404

    # Get the post or 404
    post = get_object_or_404(
        Post,
        slug=slug,
        publish__year=tt.tm_year,
        publish__month=tt.tm_mon,
        publish__day=tt.tm_mday
    )

    # If the user isn't super and the post is not public, do not allow viewing.
    if not request.user.is_superuser and post.status != 2:
        raise Http404

    # If the user's IP is not specified as internal, increase the post's view
    # count.
    if not request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        post.visits = F('visits') + 1
        post.save()

    return date_based.object_detail(
        request,
        year = year,
        month = month,
        month_format = month_format,
        day = day,
        date_field = 'publish',
        slug = slug,
        queryset = Post.objects.all(),
        **kwargs
    )
post_detail.__doc__ = date_based.object_detail.__doc__


def category_list(request, template_name = 'blog/category_list.html', **kwargs):
    """
    Category list

    Template: ``blog/category_list.html``
    Context:
        object_list
            List of categories.
    """
    return list_detail.object_list(
        request,
        queryset=Category.objects.all(),
        template_name=template_name,
        **kwargs
    )

def category_detail(request, slug, page=0, **kwargs):
    """
    Category detail

    Template: ``blog/post_list.html``
    Context:
        object_list
            List of posts specific to the given category.
        category
            Given category.
    """
    category = get_object_or_404(Category, slug__iexact=slug)

    return list_detail.object_list(
        request,
        queryset=category.post_set.published(),
        paginate_by=blog_settings.BLOG_PAGESIZE,
        page=page,
        extra_context={
            'type': 'category',
            'query': category.id,
            'query_pretty': category.title.capitalize()
        },
        template_name='blog/post_list.html',
        **kwargs
    )


def tag_detail(request, slug, page=0, **kwargs):
    """
    Tag detail

    Template: ``blog/post_list.html``
    Context:
        object_list
            List of posts specific to the given tag.
        tag
            Given tag.
    """
    tag = get_object_or_404(Tag, slug__iexact=slug)

    return list_detail.object_list(
        request,
        queryset=Post.objects.filter(tags__name__in=[tag]),
        paginate_by=blog_settings.BLOG_PAGESIZE,
        page=page,
        extra_context={
            'type': 'tag',
            'query': tag.id,
            'query_pretty': tag
        },
        template_name='blog/post_list.html',
        **kwargs
    )


def search(request, template_name='blog/post_search.html'):
    """
    Search for blog posts.

    This template will allow you to setup a simple search form that will try to return results based on
    given search strings. The queries will be put through a stop words filter to remove words like
    'the', 'a', or 'have' to help imporve the result set.

    Template: ``blog/post_search.html``
    Context:
        object_list
            List of blog posts that match given search term(s).
        search_term
            Given search term.
    """
    context = {}
    if request.GET:
        search_term = '%s' % request.GET['q']
        cleaned_search_term = STOP_WORDS_RE.sub('', search_term)
        cleaned_search_term = cleaned_search_term.strip()
        if len(cleaned_search_term) != 0:
            post_list = Post.objects.published().filter(Q(title__icontains=cleaned_search_term) | Q(body__icontains=cleaned_search_term) | Q(tags__name__icontains=cleaned_search_term) | Q(categories__title__icontains=cleaned_search_term)).distinct()
            if len(post_list) > 1:
                context = {'object_list': post_list, 'search_term':search_term}
            else:
                message = 'No results found! Please try a different term.'
                context = {'message': message} 
        else:
            message = 'Search term was too vague. Please try again.'
            context = {'message':message}
    return render_to_response(template_name, context, context_instance=RequestContext(request))
