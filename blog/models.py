from django.db import models
from minriver.slugify import smart_slugify


class BlogEntry(models.Model):
    slug = models.SlugField(max_length=80)
    promo_image = models.ImageField(upload_to='images/blog-photos', blank=True, null=True)
    date_added = models.DateField()
    is_gallery = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    content = models.TextField()
    comments_require_captcha = models.BooleanField(default=False, help_text="If ticked, visitors will need to fill in captchas before commenting")
    comments_closed = models.BooleanField(default=False, help_text="If ticked, visitors will not be able to comment on this entry")
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/blog/%s/" % self.slug # important! do not change (for feeds)
     
    def get_content(self):
        return self.summary
       
        
