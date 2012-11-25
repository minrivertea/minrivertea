# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'BlogEntry.is_gallery'
        db.delete_column('blog_blogentry', 'is_gallery')


    def backwards(self, orm):
        # Adding field 'BlogEntry.is_gallery'
        db.add_column('blog_blogentry', 'is_gallery',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    models = {
        'blog.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'comments_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_require_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'promo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'summary_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'summary_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['blog']