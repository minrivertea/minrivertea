from emailer.models import *
from django.contrib import admin

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_unsubscribed', 'language')
    list_filter = ('language',)


admin.site.register(Subscriber, SubscriberAdmin)    
admin.site.register(Newsletter)
admin.site.register(EmailInstance)


