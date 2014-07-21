import mailchimp
import django.dispatch
from django.conf import settings


update_mailing_list = django.dispatch.Signal(providing_args=["email_address", "lang_code"])



def get_mailchimp_api():
    return mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY) #your api key here


def update_mailchimp(sender, **kwargs):
    """
    Updates the mailchimp list automatically
    """
    
    list_id = ''
    if kwargs['lang_code'] == 'en':
        list_id = settings.MAILCHIMP_EN_LIST_ID
    
    if kwargs['lang_code'] == 'it':
        list_id = settings.MAILCHIMP_IT_LIST_ID
    
    if kwargs['lang_code'] == 'de':
        list_id = settings.MAILCHIMP_DE_LIST_ID
        
    email = kwargs['email_address']
    
    try:
        m = get_mailchimp_api()
        m.lists.subscribe(list_id, {'email':email})
    except mailchimp.ListAlreadySubscribedError:
        pass
    except mailchimp.Error, e:
        print ""
    return 
    
    return 
update_mailing_list.connect(update_mailchimp)    
    
