=================
Django Basic Apps
=================

Simple apps for Django projects.

To install any of the apps listed simply create a folder on your ``PYTHONPATH`` named 'basic' and place the apps you wish to use in that folder. Then added ``basic.<app_name>`` to your project's ``settings.py`` file. (replace <app_name> with the apps you wish to use, naturally).

Below are a list of per app dependancies:

Revisions
==========

All Apps
--------

* Django Tagging has been replaced in favor of the more actively maintained `django-taggit <https://github.com/alex/django-taggit>`_

Basic.Blog
----------

* Added a visit counter for each post.
* Added `django-markup <https://github.com/bartTC/django-markup/>`_ for markup language support.
* Updated feeds for Django 1.2+
* Added a blog settings file
* Added support for `Django WMD <https://github.com/pigmonkey/django-wmd/>`_
* Added a Wordpress import script (``./manage.py wordpress_import``)
* Tag cloud!
* Massive template clean-up.
* Added an auto-excerpt feature.
* `Disqus <http://disqus.com/>`_ support.

Basic.Media
-----------

* Added a property to access exif data.
* Added an original creation date to all photos, based on exif.

Basic.Search
-----------

* Created a new basic search app based on `Julien Phalip's code <http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap>`_

Dependencies
============

* Basic Inlines are required to use the Blog app
* Django Comments (http://www.djangoproject.com/documentation/add_ons/#comments) are required for the blog app
* django-taggit (https://github.com/alex/django-taggit) is used for tagging
* django-taggit-templatetags (https://github.com/feuervogel/django-taggit-templatetags) is used to generate a tag cloud
* Markdown (http://www.djangoproject.com/documentation/add_ons/#markup)
* BeautifulSoup (http://www.crummy.com/software/BeautifulSoup/) is required to use the blog and, subsequently, the inlines app.
* Dateutil (http://labix.org/python-dateutil)
* Django Registration for the invitations app
* django-disqus (http://github.com/arthurk/django-disqus) is required if Disqus-powered comments are enabled.

Inlines
=======

Inlines is a template filter that can be used in
conjunction with inline markup to insert content objects
into other pieces of content. An example would be inserting
a photo into a blog post body.

An example of the markup is:
  <inline type="media.photo" id="1" />

The type attribute is app_name.model_name and the id is
the object id. Pretty simple.

In your template you would say:
  {% load inlines %}

  {{ post.body|render_inlines }}
