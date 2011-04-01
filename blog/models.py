from django.db import models
from minriver.slugify import smart_slugify
from sorl.thumbnail.fields import ImageWithThumbnailsField


class BlogEntry(models.Model):
    slug = models.SlugField(max_length=80)
    promo_image = models.ImageField(upload_to='images/blog-photos')
    date_added = models.DateField()
    is_gallery = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    content = models.TextField()
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/blog/%s/" % self.slug
     
    def get_content(self):
        return self.summary
        
    def get_type(self):
        return "Blog"
        
