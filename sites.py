from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import re

from shop.utils import _changelang, _set_currency

class DomainTrackerMiddleware(object):
    """
    This checks the current domain name and applies the 
    correct language and/or currency as appropriate.
    """
    
    def process_request(self, request):        
        
        # don't want to keep validating against images and CSS/JS files
        if re.match('^.+\.(jpg|jpeg|gif|png|ico|css|js)', request.path):
            return None
        
        print request.META['HTTP_HOST']
                          
        if request.META['HTTP_HOST'] == settings.GERMAN_URL:                        
            url = "%s%s?next=%s" % (settings.SITE_URL, reverse('changelang', args=['de']), request.path)
            return HttpResponseRedirect(url)
        
        if request.META['HTTP_HOST'] == settings.ITALIAN_URL:
            url = "%s%s?next=%s" % (settings.SITE_URL, reverse('changelang', args=['it']), request.path)
            return HttpResponseRedirect(url)
        
        return None
    