#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from shop.models import UniqueProduct, Category, Product, Basket, BasketItem, Shopper, Address
from logistics.models import *
from logistics.views import _create_customer_package

from datetime import datetime

class CustomerPackageTestCase(TestCase):
    
    fixtures = ['shop/fixtures/testdata.xml', 'logistics/fixtures/testdata.xml']    

    def test_customer_package_process(self):
        """check the whole process from customer purchase to package shipped"""
        
        # we're going to order some Jasmine Pearls 100g, make sure a customer
        # package is created, then check that the quantity has dropped
        
        # IMPORTANT - we're going to order all of the available stocks in one go
        quantity = WarehouseItem.objects.filter(
                unique_product__parent_product__slug='jasmine-pearls', 
                sold__isnull=True
                ).count()
                
        shopper = Shopper.objects.all()[0]
        address = Address.objects.all()[0]
        basket = Basket.objects.all()[0]
        up = UniqueProduct.objects.get(parent_product__slug='jasmine-pearls', is_active=True, weight=100, currency__code='GBP')
        basket_item = BasketItem.objects.create(item=up, quantity=quantity, basket=basket)
        
        order = Order.objects.create(
            date_paid=datetime.now(),
            date_confirmed=datetime.now(),
            address=address,
            owner=shopper,
            invoice_id='FAKE123',
            status=Order.STATUS_PAID,
        )
        
        order.items.add(basket_item)
        order.save()
        
        total_stocks = WarehouseItem.objects.filter(unique_product__parent_product__slug='jasmine-pearls').count()
        available_stocks = WarehouseItem.objects.filter(unique_product__parent_product__slug='jasmine-pearls', 
            sold__isnull=True, available__isnull=False).count()

        # FIRST - create a customer package
        _create_customer_package(order)
        
        # SECOND - total number of items shouldn't have changed - make sure this is true
        new_total_stocks = WarehouseItem.objects.filter(unique_product__parent_product__slug='jasmine-pearls').count()
        self.assertEqual(total_stocks, new_total_stocks)
        
        # THIRD - the number of available items should be 0
        new_available_stocks = WarehouseItem.objects.filter(unique_product__parent_product__slug='jasmine-pearls', sold__isnull=True).count()
        self.assertEquals(new_available_stocks, 0)
        

        # FOURTH - now let's try to order 1 more - it should create an extra preorder package for this customer
        basket_item = BasketItem.objects.create(item=up, quantity=1, basket=basket)
        order = Order.objects.create(
            date_paid=datetime.now(),
            date_confirmed=datetime.now(),
            address=address,
            owner=shopper,
            invoice_id='FAKE123',
            status=Order.STATUS_PAID,
        )
        
        order.items.add(basket_item)
        order.save()
        
        _create_customer_package(order)
        
        preorder_package = CustomerPackage.objects.filter(order=order, is_preorder=True)
        self.assertEqual(preorder_package.count(), 1)
    
    def test_monthly_orders(self):
        shopper = Shopper.objects.all()[0]
        address = Address.objects.all()[0]
        basket = Basket.objects.all()[0]
        up = UniqueProduct.objects.get(parent_product__slug='iron-buddha', is_active=True, weight=100, currency__code='GBP')
        basket_item = BasketItem.objects.create(item=up, quantity=2, basket=basket, monthly_order=True, months=12)
        
        order = Order.objects.create(
            date_paid=datetime.now(),
            date_confirmed=datetime.now(),
            address=address,
            owner=shopper,
            invoice_id='FAKE123',
            status=Order.STATUS_PAID,
        )
        
        order.items.add(basket_item)
        order.save()

        # FIRST - create a customer package
        _create_customer_package(order)
        
        # CHECK - WE SHOULD HAVE 12 SEPARATE PACKAGES
        months = 12
        customer_packages = CustomerPackage.objects.filter(order=order).count()
        self.assertEqual(customer_packages, months)
        
        
        # CHECK - WE SHOULD HAVE 11 PACKAGES ARRIVING AFTER THIS MONTH
        from logistics.views import add_months
        next_month = add_months(datetime.now(), 1)
        cp_after_this_month = CustomerPackage.objects.filter(order=order, shipping_due_date__gte=next_month).count()
        self.assertEqual(cp_after_this_month, 11)
        
        
        # CHECK - THERE SHOULD BE 24 IRON BUDDHA WAREHOUSE ITEMS BOUND UP TO THIS ORDER
        items = WarehouseItem.objects.filter(package__order=order, unique_product__parent_product__slug='iron-buddha').count()
        self.assertEqual(items, 24)
        
        
        
        
        
        
        