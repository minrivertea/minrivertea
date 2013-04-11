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
        
        # THIS CHECKS IF THIS SESSION CAME FROM AN AFFILIATE REFERRAL
        if request.GET.get(settings.AFFILIATE_URL_VARIABLE):
            try:
                cookie = request.session[settings.AFFILIATE_SESSION_KEY]
                request.delete_cookie(settings.AFFILIATE_SESSION_KEY)
            except:
                pass
                        
            request.session[settings.AFFILIATE_SESSION_KEY] = request.GET.get(settings.AFFILIATE_URL_VARIABLE)
            
            print request.session[settings.AFFILIATE_SESSION_KEY]
        
        

        
        # WE RETURN NONE AND IT CONTINUES PROCESSING THE REQUEST AS NORMAL
        return None
    