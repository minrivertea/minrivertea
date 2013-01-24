from django import template
from shop.models import Page
from django.shortcuts import get_object_or_404

import re

register = template.Library()

def get_new_url(match):
    # get the new url of a page, based on the id
    m = match.group().split('/')[2]
    try:
        url = get_object_or_404(Page, pk=m).get_absolute_url()
    except:
        url = match.group()
    return url


@register.filter(name='convert_links')
def convert_links(text):
    """ This converts a link_by_id into a slug - it's a helper for WYSIWYG linking """
    url_pattern = re.compile(r'/page/\d+/')
    new_text = url_pattern.sub(get_new_url, text)
    return new_text
    






