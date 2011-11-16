from django.template.loaders.filesystem import load_template_source as default_template_loader
from ab.middleware import get_current_request


def load_template_source(template_name, template_dirs=None, 
    template_loader=default_template_loader):
    """If an Experiment exists for this template use template_loader to load it."""    
    
    # CW AMEND Nov 2011 - this way relies on a 'request' object but sometimes
    # like running cron jobs, there is no request object. So now we check if 
    # there is a request object first, and if not, it passes the normal template loader.
    
    try:
        request = get_current_request()
        test_template_name = request.ab.run(template_name)
        return template_loader(test_template_name, template_dirs=template_dirs)
    except:
        return template_loader(template_name, template_dirs=template_dirs)
load_template_source.is_usable = True
        
        