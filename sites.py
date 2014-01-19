from django.conf import settings
from django.contrib.sites.models import Site
import re

import logging

logger = logging.getLogger(__name__)

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
        
        
        
        try:    
            logger.error(request.META['HTTP_REFERER'])
            referer = request.META['HTTP_REFERER']
            if referer == settings.GERMAN_URL:
                _changelang(request, 'de') # CHANGE LANGUAGE 
                if 'CURRENCY' not in request.session: 
                    _set_currency(request, 'EUR') # CHANGE CURRENCY TO EUR 
                                
            if referer == settings.ITALIAN_URL:
                _changelang(request, 'it') # CHANGE LANGUAGE
                if 'CURRENCY' not in request.session: 
                    _set_currency(request, 'EUR') # CHANGE CURRENCY TO EUR
            
        except:
            pass
                       
        return None
    