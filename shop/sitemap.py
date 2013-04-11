#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.translation import activate, get_language
from django.contrib.sitemaps import Sitemap
from blog.models import BlogEntry
from shop.models import Product, Page
from itertools import chain

class Sitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        activate(get_language())
        entries = BlogEntry.objects.filter(is_draft=False, title__isnull=False).exclude(title__exact="None")
        products = Product.objects.filter(is_active=True)
        pages = Page.objects.filter(title__isnull=False, content_de__isnull=False)
        result_list = list(chain(entries, products, pages))
        return result_list


class DESitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        activate('de')
        entries = BlogEntry.objects.filter(is_draft=False, title__isnull=False, content__isnull=False).exclude(title__exact="None")
        products = Product.objects.filter(is_active=True)
        pages = Page.objects.filter(title__isnull=False, content_de__isnull=False)
        result_list = list(chain(entries, products, pages))
        return result_list