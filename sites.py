from django.conf import settings
from django.contrib.sites.models import Site


from shop.utils import _changelang, _set_currency


class DomainTrackerMiddleware(object):
    """
    This checks the current domain name and applies the 
    correct language and/or currency as appropriate.
    """
    
    def process_request(self, request):
        
        # CHECK IF THE DOMAIN NAME IS .de
        if Site.objects.get_current().domain == 'www.minrivertea.de':
        
            # CHANGE LANGUAGE TO GERMAN
            _changelang(request, 'de')
            
            # CHANGE CURRENCY TO EUR
            _set_currency(request, 'EUR')
        
        
        # WE RETURN NONE AND IT CONTINUES PROCESSING THE REQUEST AS NORMAL
        return None
    