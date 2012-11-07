# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'UniqueProduct.price_unit'
        db.delete_column('shop_uniqueproduct', 'price_unit')

        # Deleting field 'UniqueProduct.available_stock'
        db.delete_column('shop_uniqueproduct', 'available_stock')


    def backwards(self, orm):
        
        # Adding field 'UniqueProduct.price_unit'
        db.add_column('shop_uniqueproduct', 'price_unit', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True), keep_default=False)

        # Adding field 'UniqueProduct.available_stock'
        db.add_column('shop_uniqueproduct', 'available_stock', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


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
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'house_name_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'shop.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'long_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'short_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
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
        'shop.discount': {
            'Meta': {'object_name': 'Discount'},
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'discount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'shop.emailinstance': {
            'Meta': {'object_name': 'EmailInstance'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject_line': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'shop.emailsignup': {
            'Meta': {'object_name': 'EmailSignup'},
            'date_signed_up': ('django.db.models.fields.DateField', [], {}),
            'date_unsubscribed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'hashkey': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'shop.notify': {
            'Meta': {'object_name': 'Notify'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']", 'null': 'True', 'blank': 'True'})
        },
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Address']", 'null': 'True'}),
            'date_confirmed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_paid': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_shipped': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Discount']", 'null': 'True', 'blank': 'True'}),
            'hashkey': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'is_confirmed_by_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_giveaway': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shop.BasketItem']", 'db_index': 'True', 'symmetrical': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"}),
            'postage_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'postage_currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Currency']", 'null': 'True', 'blank': 'True'}),
            'reminder_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'review_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sampler_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sampler_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'wishlist_payee': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'shop.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Page']", 'null': 'True', 'blank': 'True'}),
            'promo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'right_side_boxes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'shop.photo': {
            'Meta': {'object_name': 'Photo'},
            'email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'related_product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']", 'null': 'True', 'blank': 'True'}),
            'shopper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"})
        },
        'shop.product': {
            'Meta': {'object_name': 'Product'},
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'body_text_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'coming_soon': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extra_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extra_info_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extra_info_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'long_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'long_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'long_name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_location_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_location_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'map_page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Page']", 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'meta_title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'recommended': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['shop.Product']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'super_short_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'super_short_description_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'super_short_description_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'tag_color': ('django.db.models.fields.CharField', [], {'max_length': "'60'", 'null': 'True', 'blank': 'True'}),
            'tag_text': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'tag_text_de': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'}),
            'tag_text_en': ('django.db.models.fields.CharField', [], {'max_length': "'100'", 'null': 'True', 'blank': 'True'})
        },
        'shop.referee': {
            'Meta': {'object_name': 'Referee'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referred_by': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'shop.review': {
            'Meta': {'object_name': 'Review'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'number_referred': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reminder_email_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'twitter_username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'shop.uniqueproduct': {
            'Meta': {'object_name': 'UniqueProduct'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Currency']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_sale_price': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'old_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'parent_product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'weight_unit': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'shop.wishlist': {
            'Meta': {'object_name': 'Wishlist'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Address']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 7, 8, 50, 24, 132068)'}),
            'hashkey': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"}),
            'times_purchased': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'wishlist_items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shop.BasketItem']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['shop']
