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
          
                                                    
        if request.META['SERVER_NAME'] == settings.GERMAN_URL:
            
            url = "%s%s?next=%s" % (settings.SITE_URL, reverse('changelang', args=['de'], request.path)
            return HttpResponseRedirect(url)
        
        
        if request.META['SERVER_NAME'] == settings.ITALIAN_URL:
            _changelang(request, 'it')
            if 'CURRENCY' not in request.session: 
                _set_currency(request, 'EUR')
                
            url = '%s%s' % (settings.SITE_URL, request.path)
            return HttpResponseRedirect(url) 
        
        return None
    