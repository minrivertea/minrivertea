# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Wishlist'
        db.delete_table('shop_wishlist')

        # Removing M2M table for field wishlist_items on 'Wishlist'
        db.delete_table(db.shorten_name('shop_wishlist_wishlist_items'))

        # Adding model 'Deal'
        db.create_table('shop_deal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deal_type', self.gf('django.db.models.fields.CharField')(max_length='3')),
        ))
        db.send_create_signal('shop', ['Deal'])

        # Adding M2M table for field items on 'Deal'
        m2m_table_name = db.shorten_name('shop_deal_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('deal', models.ForeignKey(orm['shop.deal'], null=False)),
            ('uniqueproduct', models.ForeignKey(orm['shop.uniqueproduct'], null=False))
        ))
        db.create_unique(m2m_table_name, ['deal_id', 'uniqueproduct_id'])


        # Changing field 'UniqueProduct.is_sale_price'
        db.alter_column('shop_uniqueproduct', 'is_sale_price', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Address.country'
        db.alter_column('shop_address', 'country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Order.reminder_email_sent'
        db.alter_column('shop_order', 'reminder_email_sent', self.gf('django.db.models.fields.NullBooleanField')(null=True))
        # Deleting field 'Product.extra_info'
        db.delete_column('shop_product', 'extra_info')

        # Deleting field 'Product.extra_info_it'
        db.delete_column('shop_product', 'extra_info_it')

        # Deleting field 'Product.extra_info_en'
        db.delete_column('shop_product', 'extra_info_en')

        # Deleting field 'Product.extra_info_de'
        db.delete_column('shop_product', 'extra_info_de')


    def backwards(self, orm):
        # Adding model 'Wishlist'
        db.create_table('shop_wishlist', (
            ('hashkey', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Address'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 16, 0, 0))),
            ('views', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('times_purchased', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Wishlist'])

        # Adding M2M table for field wishlist_items on 'Wishlist'
        m2m_table_name = db.shorten_name('shop_wishlist_wishlist_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wishlist', models.ForeignKey(orm['shop.wishlist'], null=False)),
            ('basketitem', models.ForeignKey(orm['shop.basketitem'], null=False))
        ))
        db.create_unique(m2m_table_name, ['wishlist_id', 'basketitem_id'])

        # Deleting model 'Deal'
        db.delete_table('shop_deal')

        # Removing M2M table for field items on 'Deal'
        db.delete_table(db.shorten_name('shop_deal_items'))


        # Changing field 'UniqueProduct.is_sale_price'
        db.alter_column('shop_uniqueproduct', 'is_sale_price', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Address.country'
        db.alter_column('shop_address', 'country', self.gf('django.db.models.fields.CharField')(default=1, max_length=200))

        # Changing field 'Order.reminder_email_sent'
        db.alter_column('shop_order', 'reminder_email_sent', self.gf('django.db.models.fields.BooleanField')())
        # Adding field 'Product.extra_info'
        db.add_column('shop_product', 'extra_info',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Product.extra_info_it'
        db.add_column('shop_product', 'extra_info_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Product.extra_info_en'
        db.add_column('shop_product', 'extra_info_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Product.extra_info_de'
        db.add_column('shop_product', 'extra_info_de',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'shop.address': {
            'Meta': {'object_name': 'Address'},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'house_name_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'province_state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'town_city': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'shop.basket': {
            'Meta': {'object_name': 'Basket'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']", 'null': 'True'})
        },
        'shop.basketitem': {
            'Meta': {'object_name': 'BasketItem'},
            'basket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Basket']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.UniqueProduct']"}),
            'monthly_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'months': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'shop.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_navigation_item': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'list_order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'long_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'long_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'short_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_it': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        'shop.currency': {
            'Meta': {'object_name': 'Currency'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postage_cost': ('django.db.models.fields.IntegerField', [], {}),
            'postage_discount_threshold': ('django.db.models.fields.IntegerField', [], {}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'shop.deal': {
            'Meta': {'object_name': 'Deal'},
            'deal_type': ('django.db.models.fields.CharField', [], {'max_length': "'3'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shop.UniqueProduct']", 'symmetrical': 'False'})
        },
        'shop.discount': {
            'Meta': {'object_name': 'Discount'},
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'discount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'expiry_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'single_use': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Address']", 'null': 'True'}),
            'affiliate_referrer': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date_confirmed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_paid': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Discount']", 'null': 'True', 'blank': 'True'}),
            'final_amount_paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'final_currency_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'final_discount_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'final_items_list': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hashkey': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'is_confirmed_by_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_giveaway': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shop.BasketItem']", 'db_index': 'True', 'symmetrical': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"}),
            'reminder_email_sent': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        'shop.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'content_de': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'content_it': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_top_nav': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'list_order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Page']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug_it': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'shop.product': {
            'Meta': {'object_name': 'Product'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'body_text_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'brew_temp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'brew_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'brew_weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'farm_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'farm_caption_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'farm_caption_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'farm_caption_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'farm_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_2': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_2_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'image_3': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_3_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'image_4': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_4_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'image_5': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_5_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'list_order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'long_description': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'long_description_de': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'long_description_en': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'long_description_it': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_name_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_caption_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_caption_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_caption_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_it': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'super_short_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'super_short_description_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'super_short_description_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'super_short_description_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'tag_color': ('django.db.models.fields.CharField', [], {'max_length': "'60'", 'null': 'True', 'blank': 'True'}),
            'tag_text': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'tag_text_de': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'tag_text_en': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'tag_text_it': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'})
        },
        'shop.review': {
            'Meta': {'object_name': 'Review'},
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'short_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'shop.shopper': {
            'Meta': {'object_name': 'Shopper'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '20'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'number_referred': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_email_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'twitter_username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'shop.uniqueproduct': {
            'Meta': {'object_name': 'UniqueProduct'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Currency']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_sale_price': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'old_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'parent_product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'special_shipping_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'special_shipping_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'weight_unit': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['shop']