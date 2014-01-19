from django.conf import settings
from django.contrib.sites.models import Site
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
                                            
        if request.META['SERVER_NAME'] == settings.GERMAN_URL: # CHECK IF THE DOMAIN NAME IS .de
            _changelang(request, 'de') # CHANGE LANGUAGE TO GERMAN
            if 'CURRENCY' not in request.session: 
                _set_currency(request, 'EUR') # CHANGE CURRENCY TO EUR IF NO PREFERENCE ALREADY SET
        
        
        if request.META['SERVER_NAME'] == settings.ITALIAN_URL: # CHECK IF THE DOMAIN NAME IS .de
            _changelang(request, 'it') # CHANGE LANGUAGE TO GERMAN
            if 'CURRENCY' not in request.session: 
                _set_currency(request, 'EUR') # CHANGE CURRENCY TO EUR IF NO PREFERENCE ALREADY SET
        
        return None
    