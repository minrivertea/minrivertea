from django.db import models
from slugify import smart_slugify
from shop.models import Page

from ckeditor.fields import RichTextField

from taggit.managers import TaggableManager


class BlogEntry(models.Model):
    title = models.CharField(max_length=200, 
        help_text="To make an entry German language only, enter 'None' into the English title field.")
    slug = models.SlugField(max_length=80)
    blogger = models.ForeignKey('Blogger', blank=True, null=True)
    promo_image = models.ImageField(upload_to='images/blog-photos', blank=True, null=True)
    date_added = models.DateField()
    is_draft = models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)
    summary = models.CharField(max_length=200)
    
    content = RichTextField()    
    tags = TaggableManager()
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/blog/%s/" % self.slug # important! do not change (for feeds)

    def get_url_by_id(self):
        url = "/blog/%s/" % self.id
        return url
    
    def get_next(self):
        next = BlogEntry.objects.filter(pk__gt=self.id)
        if next:
            return next[0]
        return None
    
    def get_prev(self):
        prev = BlogEntry.objects.filter(pk__lt=self.id)
        if prev:
            return prev[0]
        return None 
    
     
    def get_content(self):
        return self.summary


class Blogger(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    profile_photo = models.ImageField(upload_to='images/bloggers')
    page = models.ForeignKey(Page, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name
       
        
