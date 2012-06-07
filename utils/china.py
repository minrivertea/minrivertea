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
                if region == 'global':
                    settings.TEMPLATE_DIRS = settings.TEMPLATE_DIRS
                elif region == 'china':
                    settings.TEMPLATE_DIRS = settings.CHINA_TEMPLATES_DIR
                    
            except:
                # detect if they're in China or not!
                countrycode = GetCountry(request)['countryCode']
                if countrycode == "CN":
                    request.session['region'] = 'china' 
                    settings.TEMPLATE_DIRS = settings.CHINA_TEMPLATES_DIR
            
            print settings.TEMPLATE_DIRS
            

