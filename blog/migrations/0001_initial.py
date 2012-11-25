# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogEntry'
        db.create_table('blog_blogentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=80)),
            ('promo_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')()),
            ('is_gallery', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_draft', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('comments_require_captcha', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comments_closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('blog', ['BlogEntry'])


    def backwards(self, orm):
        # Deleting model 'BlogEntry'
        db.delete_table('blog_blogentry')


    models = {
        'blog.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'comments_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_require_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_gallery': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'promo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['blog']