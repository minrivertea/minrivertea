from django import template
from shop.utils import _get_region

register = template.Library()

# this should convert grams into ounces for the Yanks
def convert_weights(request, weight):
    
    region = _get_region(request)
    print region
    if region == 'US':
        # 100g = 3.5 ounces
        return round((weight / 28.75), 1)
        
    return weight

register.simple_tag(convert_weights)