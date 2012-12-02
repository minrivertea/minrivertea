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
        quantity = WarehouseItem.objects.filter(unique_product__parent_product__slug='jasmine-pearls', sold__isnull=True).count()
                
        shopper = Shopper.objects.all()[0]
        address = Address.objects.all()[0]
        basket = Basket.objects.all()[0]
        up = UniqueProduct.objects.get(parent_product__slug='jasmine-pearls', is_active=True, weight=100, currency__code='GBP')
        basket_item = BasketItem.objects.create(item=up, quantity=quantity, basket=basket)
        
        order = Order.objects.create(
            is_paid=True,
            date_paid=datetime.now(),
            is_confirmed_by_user=True,
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
            is_paid=True,
            date_paid=datetime.now(),
            is_confirmed_by_user=True,
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
        
        
        
        
        
        