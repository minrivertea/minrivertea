from django import template
from shop.utils import _get_region, weight_converter
from shop.models import Page

import re

register = template.Library()

@register.filter(name='convert_links')
def convert_links(text):
    
    m = re.match('href="/page/3/"', text)
    if m:
        print m.group()
    
    return text