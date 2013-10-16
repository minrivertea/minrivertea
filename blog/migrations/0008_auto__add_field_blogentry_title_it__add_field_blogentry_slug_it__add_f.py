# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BlogEntry.title_it'
        db.add_column('blog_blogentry', 'title_it',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BlogEntry.slug_it'
        db.add_column('blog_blogentry', 'slug_it',
                      self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=80, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BlogEntry.summary_it'
        db.add_column('blog_blogentry', 'summary_it',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'BlogEntry.content_it'
        db.add_column('blog_blogentry', 'content_it',
                      self.gf('ckeditor.fields.RichTextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BlogEntry.title_it'
        db.delete_column('blog_blogentry', 'title_it')

        # Deleting field 'BlogEntry.slug_it'
        db.delete_column('blog_blogentry', 'slug_it')

        # Deleting field 'BlogEntry.summary_it'
        db.delete_column('blog_blogentry', 'summary_it')

        # Deleting field 'BlogEntry.content_it'
        db.delete_column('blog_blogentry', 'content_it')


    models = {
        'blog.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'blogger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blog.Blogger']", 'null': 'True', 'blank': 'True'}),
            'comments_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_require_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'content_de': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'content_it': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'promo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_it': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'summary_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'summary_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'summary_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'blog.blogger': {
            'Meta': {'object_name': 'Blogger'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Page']", 'null': 'True', 'blank': 'True'}),
            'profile_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'})
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
        }
    }

    complete_apps = ['blog']