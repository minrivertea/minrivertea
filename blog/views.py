from minriver.blog.models import BlogEntry
from minriver.shop.models import Product
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#render shortcut
def render(request, template, context_dict=None, **kwargs):
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )

def index(request):
    objects = BlogEntry.objects.filter(is_draft=False, is_gallery=False).order_by('-date_added')
      
    try:
        p = int(request.GET.get('page', '1'))
    except ValueError:
        p = 1
    
    paginator = Paginator(objects, 10) 
    # If page request (9999) is out of range, deliver last page of results.
    try:
        entries = paginator.page(p)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    
    teas = Product.objects.filter(is_active=True).order_by('?')[:2]
                       
    return render(request, "blog/home.html", locals())
    
    
@csrf_protect   
def blog_entry(request, slug):
    entry = get_object_or_404(BlogEntry, slug=slug)
    other_entries = BlogEntry.objects.exclude(id=entry.id).order_by('?')[:2]
    teas = Product.objects.filter(is_active=True).order_by('?')[:2]
    return render(request, "blog/entry.html", locals())
  