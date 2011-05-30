"""
Import Wordpress posts from an XML file into Django basic blog.

To generate the XML file, login to the Wordpress Dashboard. Navigate to
    Tools -> Export
and select "Posts" rather than "All content".

Props to:
    http://blog.sejo.be/2010/02/14/import-wordpress-django-mingus/
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from basic.blog.models import Post, Category
import xml.etree.ElementTree as ET
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports Wordpress posts from an XML file into Django basic blog'
    args = 'filename.xml'

    def handle(self, *args, **options):
        try:
            file = args[0]
        except IndexError:
            raise CommandError('No file was specified')

        try:
            tree = ET.parse(file)
        except IOError:
            raise CommandError("%s could not be found" % file)

        wp = 'http://wordpress.org/export/1.1/'

        for item in tree.findall('channel/item'):
            # Get the post's slug
            slug = item.find('{%s}post_name' % (wp)).text

            # Unpublished posts will not have anything in their name tag (which
            # is used to hold the slug), so we have to create the slug from the
            # title.
            if slug is None:
                slug = slugify(item.find('title').text)

            print 'Importing post "%s"...' % slug

            # If the post is already in the database, get it. Otherwise create
            # it.
            try:
                post = Post.objects.get(slug=slug)
            except:
                post = Post()
                post.title = item.find('title').text
                post.slug = item.find('{%s}post_name' % (wp)).text
                post.body = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
                post.created = item.find('{%s}post_date' % (wp)).text

                # If the post was published, set its status to public. Otherwise make
                # it a draft.
                if item.find('{%s}status' % (wp)).text == 'publish':
                    post.status = 2
                else:
                    post.status = 1
                    # Unpublished posts will not have a timestamp associated
                    # with them. We'll set the creation date to now.
                    post.created = datetime.now()

                # Set publish time to the creation time.
                post.publish = post.created
                
                # Post must be saved before we apply tags or comments.
                post.save()

            # Get all tags and categories. They look like this, respectively:
            #   <category domain="post_tag" nicename="a tag">a tag</category>
            #   <category domain="category" nicename="a category">a category</category>
            descriptors = item.findall('category')
            categories = []
            for descriptor in descriptors:
                if descriptor.attrib['domain'] == 'post_tag':
                    # Add the tag to the post
                    post.tags.add(descriptor.text)
                if descriptor.attrib['domain'] == 'category':
                    category = descriptor.text
                    # If the category exists, add it to the model. Otherwise,
                    # create the category, then add it.
                    try:
                        cat = Category.objects.get(slug=slugify(category))
                    except:
                        cat = Category(title=category, slug=slugify(category))
                        cat.save()
                    post.categories.add(cat)

            # Save the post again, this time with tags and categories.
            post.save()

            # Get and save the comments.
            comments = item.findall('{%s}comment' % (wp))
            for comment in comments:
                # When I was importing my posts, I stumbled upon a comment that
                # somehow had no author email associated with it. If that is
                # the case, don't bother importing the comment.
                email = comment.find('{%s}comment_author_email' % (wp)).text
                if email is None:
                    continue

                c = Comment()
                c.user_name = comment.find('{%s}comment_author' % (wp)).text
                c.user_email = comment.find('{%s}comment_author_email' % (wp)).text
                c.comment = comment.find('{%s}comment_content' % (wp)).text
                c.submit_date = comment.find('{%s}comment_date' % (wp)).text
                c.content_type = ContentType.objects.get(app_label='blog', model='post')
                c.object_pk = post.id
                c.site_id = Site.objects.get_current().id
                c.save()
