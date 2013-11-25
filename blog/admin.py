from blog.models import BlogEntry, Blogger
from django.contrib import admin

class BlogEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('date_added', 'title', 'is_draft')


admin.site.register(BlogEntry, BlogEntryAdmin)
admin.site.register(Blogger)

