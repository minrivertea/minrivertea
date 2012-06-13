import re
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from minriver.shop.views import GetCountry
    

class ChinaMiddleware:
    def process_request(self, request):        
        # don't want to keep validating against images and CSS/JS files
        if re.match('^.+\.(jpg|jpeg|gif|png|ico|css|js)', request.path):
            pass
        else:

            # if they already have a session cookie, then leave it as it is 
            try:
                region = request.session['region']
                pass
                                     
            except:
                # detect if they're in China or not!
                countrycode = GetCountry(request)['countryCode']
                if countrycode == settings.CHINA_REGION_CODE:
                    request.session['region'] = 'china' 
                else:
                    request.session['region'] = 'global'

                        

