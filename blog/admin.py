from blog.models import BlogEntry, Blogger
from django.contrib import admin

class BlogEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('date_added', 'title', 'tagged_with', 'is_draft')
    
    def tagged_with(self,  obj):
        """Returns a set of tags"""
        return  obj.tags.names()


admin.site.register(BlogEntry, BlogEntryAdmin)
admin.site.register(Blogger)

