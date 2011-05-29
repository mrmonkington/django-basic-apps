from django.contrib import admin
from basic.blog.models import *
from basic.blog.forms import PostForm
from basic.blog import settings

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Category, CategoryAdmin)

class PostAdmin(admin.ModelAdmin):
    if settings.BLOG_WMD:
        form = PostForm

    list_display  = ('title', 'publish', 'status', 'visits')
    list_filter   = ('publish', 'categories', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'markup', 'body', 'tease',
                'status', 'allow_comments', 'publish', 'categories', 'tags', )
        }),
        ('Rendered markup', {
            'classes': ('collapse',),
            'fields': ('body_markup',),
        })
    )
admin.site.register(Post, PostAdmin)


class BlogRollAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order',)
    list_editable = ('sort_order',)
admin.site.register(BlogRoll)
