"""
Code originally by Julien Phalip:
http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
"""
import re

from django.db.models import Q
from basic.tools.constants import STOP_WORDS_RE


def normalize_query(query_string):
    """
    Split the query string into individual keywords, getting rid of unecessary
    spaces and grouping quoted words together.
    """
    find_terms = re.compile(r'"([^"]+)"|(\S+)').findall
    normalize_space = re.compile(r'\s{2,}').sub 

    # Remove stop words from the query
    cleaned_query = STOP_WORDS_RE.sub('', query_string)

    return [normalize_space(' ', (t[0] or t[1]).strip()) for t in find_terms(cleaned_query)] 


def get_query(query_string, search_fields):
    """Return a query which is a combination of Q objects."""
    query = None
    terms = normalize_query(query_string)

    for term in terms:
        or_query = None

        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q

        if query is None:
            query = or_query
        else:
            query = query & or_query

    return query
