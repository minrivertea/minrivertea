# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Blogger'
        db.create_table('blog_blogger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('profile_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('short_bio', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('blog', ['Blogger'])

        # Adding field 'BlogEntry.blogger'
        db.add_column('blog_blogentry', 'blogger',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blog.Blogger'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'BlogEntry.content_en'
        db.alter_column('blog_blogentry', 'content_en', self.gf('ckeditor.fields.RichTextField')(null=True))

        # Changing field 'BlogEntry.content'
        db.alter_column('blog_blogentry', 'content', self.gf('ckeditor.fields.RichTextField')())

        # Changing field 'BlogEntry.content_de'
        db.alter_column('blog_blogentry', 'content_de', self.gf('ckeditor.fields.RichTextField')(null=True))

    def backwards(self, orm):
        # Deleting model 'Blogger'
        db.delete_table('blog_blogger')

        # Deleting field 'BlogEntry.blogger'
        db.delete_column('blog_blogentry', 'blogger_id')


        # Changing field 'BlogEntry.content_en'
        db.alter_column('blog_blogentry', 'content_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'BlogEntry.content'
        db.alter_column('blog_blogentry', 'content', self.gf('django.db.models.fields.TextField')())

        # Changing field 'BlogEntry.content_de'
        db.alter_column('blog_blogentry', 'content_de', self.gf('django.db.models.fields.TextField')(null=True))

    models = {
        'blog.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'blogger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blog.Blogger']", 'null': 'True', 'blank': 'True'}),
            'comments_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_require_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'content_de': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'promo_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'slug_de': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug_en': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'summary_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'summary_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'blog.blogger': {
            'Meta': {'object_name': 'Blogger'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'profile_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'short_bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['blog']