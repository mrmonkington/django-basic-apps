from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from basic.blog.feeds import BlogPostsFeed, BlogPostsByCategory

urlpatterns = patterns('basic.blog.views',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view='post_detail',
        name='blog_detail'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
        view='post_archive_day',
        name='blog_archive_day'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        view='post_archive_month',
        name='blog_archive_month'
    ),
    url(r'^(?P<year>\d{4})/$',
        view='post_archive_year',
        name='blog_archive_year'
    ),
    url(r'^categories/(?P<slug>[-\w]+)/$',
        view='category_detail',
        name='blog_category_detail'
    ),
    url (r'^categories/$',
        view='category_list',
        name='blog_category_list'
    ),
    url(r'^tags/(?P<slug>[-\w]+)/$',
        view='tag_detail',
        name='blog_tag_detail'
    ),
    url (r'^tags/$',
        direct_to_template,
        {'template': 'blog/tag_list.html'},
        name='blog_tag_list'
    ),
    url (r'^search/$',
        view='search',
        name='blog_search'
    ),
    url(r'^feed/categories/(?P<slug>[^/]+)/$',
        view = BlogPostsByCategory(),
        name = 'feed_category'
    ),
    url(r'^feed/$',
        view = BlogPostsFeed(),
        name = 'feed_latest'
    ),
    url(r'^page/(?P<page>\d+)/$',
        view='post_list',
        name='blog_index_paginated'
    ),
    url(r'^$',
        view='post_list',
        name='blog_index'
    ),
)
