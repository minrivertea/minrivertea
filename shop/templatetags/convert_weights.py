from django import template
from shop.utils import _get_region, weight_converter


register = template.Library()

# this should convert grams into ounces for the Yanks
def convert_weights(request, weight):
    
    region = _get_region(request)
    if region == 'US':
        # 100g = 3.5 ounces
        return weight_converter(weight)
        
    return weight

register.simple_tag(convert_weights)