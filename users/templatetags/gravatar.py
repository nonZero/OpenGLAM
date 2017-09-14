import urllib.parse

from django.utils import html

import hashlib
from django import template

register = template.Library()

BASE = "//gravatar.com/avatar/"


@register.filter()
def gravatar_url(email, size=24):
    size = int(size)
    assert 1 <= size <= 2048
    """ Uses to get correct url to gravatar email. """
    if not email:
        return ""
    code = hashlib.md5(email.encode('utf-8')).hexdigest()
    query = urllib.parse.urlencode({
        's': str(size),
        'd': 'retro'
    })
    return "{}{}.jpg?{}".format(BASE, code, query)


@register.filter()
def gravatar(email, size=24):
    size = int(size)
    assert 1 <= size <= 2048
    if not email:
        return ""

    url = html.escape(gravatar_url(email, size))
    return html.mark_safe(
        '<img width="{0}" height="{0}" src="{1}"/>'.format(size, url))
