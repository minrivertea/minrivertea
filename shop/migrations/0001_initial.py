# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Product'
        db.create_table('shop_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=80, db_index=True)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('meta_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('super_short_description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
            ('long_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_2', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_2_caption', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('image_3', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_3_caption', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('image_4', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_4_caption', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('image_5', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_5_caption', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Category'], null=True, blank=True)),
            ('is_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('coming_soon', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Product'])

        # Adding model 'Category'
        db.create_table('shop_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('long_title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=80, db_index=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')()),
            ('short_description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('shop', ['Category'])

        # Adding model 'UniqueProduct'
        db.create_table('shop_uniqueproduct', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('weight_unit', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('price_unit', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('parent_product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('available_stock', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_sale_price', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('old_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('shop', ['UniqueProduct'])

        # Adding model 'Shopper'
        db.create_table('shop_shopper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('number_referred', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('subscribed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('twitter_username', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Shopper'])

        # Adding model 'Review'
        db.create_table('shop_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('short_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Review'])

        # Adding model 'Address'
        db.create_table('shop_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'])),
            ('house_name_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address_line_1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address_line_2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('town_city', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal('shop', ['Address'])

        # Adding model 'Basket'
        db.create_table('shop_basket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'], null=True)),
        ))
        db.send_create_signal('shop', ['Basket'])

        # Adding model 'BasketItem'
        db.create_table('shop_basketitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.UniqueProduct'])),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('basket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Basket'])),
        ))
        db.send_create_signal('shop', ['BasketItem'])

        # Adding model 'Discount'
        db.create_table('shop_discount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discount_code', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('discount_value', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Discount'])

        # Adding model 'Order'
        db.create_table('shop_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_confirmed_by_user', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_confirmed', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_giveaway', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_paid', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Address'], null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'])),
            ('discount', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Discount'], null=True, blank=True)),
            ('invoice_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('hashkey', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sampler_email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sampler_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reminder_email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('review_email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Order'])

        # Adding M2M table for field items on 'Order'
        db.create_table('shop_order_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm['shop.order'], null=False)),
            ('basketitem', models.ForeignKey(orm['shop.basketitem'], null=False))
        ))
        db.create_unique('shop_order_items', ['order_id', 'basketitem_id'])

        # Adding model 'WeLike'
        db.create_table('shop_welike', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('shop', ['WeLike'])

        # Adding model 'Photo'
        db.create_table('shop_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shopper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'])),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published_homepage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('related_product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'], null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Photo'])

        # Adding model 'Referee'
        db.create_table('shop_referee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('referred_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Shopper'])),
        ))
        db.send_create_signal('shop', ['Referee'])

        # Adding model 'Notify'
        db.create_table('shop_notify', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Notify'])

        # Adding model 'Page'
        db.create_table('shop_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Page'], null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('right_side_boxes', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Page'])


    def backwards(self, orm):
        
        # Deleting model 'Product'
        db.delete_table('shop_product')

        # Deleting model 'Category'
        db.delete_table('shop_category')

        # Deleting model 'UniqueProduct'
        db.delete_table('shop_uniqueproduct')

        # Deleting model 'Shopper'
        db.delete_table('shop_shopper')

        # Deleting model 'Review'
        db.delete_table('shop_review')

        # Deleting model 'Address'
        db.delete_table('shop_address')

        # Deleting model 'Basket'
        db.delete_table('shop_basket')

        # Deleting model 'BasketItem'
        db.delete_table('shop_basketitem')

        # Deleting model 'Discount'
        db.delete_table('shop_discount')

        # Deleting model 'Order'
        db.delete_table('shop_order')

        # Removing M2M table for field items on 'Order'
        db.delete_table('shop_order_items')

        # Deleting model 'WeLike'
        db.delete_table('shop_welike')

        # Deleting model 'Photo'
        db.delete_table('shop_photo')

        # Deleting model 'Referee'
        db.delete_table('shop_referee')

        # Deleting model 'Notify'
        db.delete_table('shop_notify')

        # Deleting model 'Page'
        db.delete_table('shop_page')


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
            'meta_description': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        },
        'shop.discount': {
            'Meta': {'object_name': 'Discount'},
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'discount_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'reminder_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'review_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sampler_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sampler_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        'shop.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Page']", 'null': 'True', 'blank': 'True'}),
            'right_side_boxes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Category']", 'null': 'True', 'blank': 'True'}),
            'coming_soon': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
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
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'}),
            'super_short_description': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'shop.referee': {
            'Meta': {'object_name': 'Referee'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referred_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Shopper']"})
        },
        'shop.review': {
            'Meta': {'object_name': 'Review'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'short_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'shop.shopper': {
            'Meta': {'object_name': 'Shopper'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'number_referred': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'twitter_username': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'shop.uniqueproduct': {
            'Meta': {'object_name': 'UniqueProduct'},
            'available_stock': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_sale_price': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'old_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'parent_product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'price_unit': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'weight_unit': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'shop.welike': {
            'Meta': {'object_name': 'WeLike'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['shop']
