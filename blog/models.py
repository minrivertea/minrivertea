from django.db import models
from slugify import smart_slugify
from shop.models import Page

from ckeditor.fields import RichTextField

class BlogEntry(models.Model):
    slug = models.SlugField(max_length=80)
    promo_image = models.ImageField(upload_to='images/blog-photos', blank=True, null=True)
    date_added = models.DateField()
    is_draft = models.BooleanField(default=True)
    title = models.CharField(max_length=200, help_text="To make an entry German language only, enter 'None' into the English title field.")
    summary = models.CharField(max_length=200)
    blogger = models.ForeignKey('Blogger', blank=True, null=True)
    content = RichTextField()
    comments_require_captcha = models.BooleanField(default=False, help_text="If ticked, visitors will need to fill in captchas before commenting")
    comments_closed = models.BooleanField(default=False, help_text="If ticked, visitors will not be able to comment on this entry")
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/blog/%s/" % self.slug # important! do not change (for feeds)

    def get_url_by_id(self):
        url = "/blog/%s/" % self.id
        return url
     
    def get_content(self):
        return self.summary


class Blogger(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    profile_photo = models.ImageField(upload_to='images/bloggers')
    page = models.ForeignKey(Page, blank=True, null=True)
    
    def __unicode__(self):
        return self.name
       
        
