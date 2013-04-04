from django.conf import settings

class AffiliateTrackerMiddleware(object):
    """
    This checks if the incoming URL has a tracking
    parameter appended for the affiliate scheme and
    sets a cookie if it does. The cookie then only
    gets checked later on the order-complete page
    when we call the affiliate scheme tracking codes
    to register a successful purchase.
    """
    
    def process_request(self, request):
        
        if request.GET.get('sales_adforce'):
            try:
                cookie = request.session['ADFORCE']
                request.delete_cookie("ADFORCE")
            except:
                pass
            
            request.session['ADFORCE'] = "1"
        
        # WE RETURN NONE AND IT CONTINUES PROCESSING THE REQUEST AS NORMAL
        return None
    