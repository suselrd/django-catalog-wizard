# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SearchLog'
        db.create_table(u'catalog_searchlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('querystring', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'catalog', ['SearchLog'])


    def backwards(self, orm):
        # Deleting model 'SearchLog'
        db.delete_table(u'catalog_searchlog')


    models = {
        u'catalog.modelcontexttemplate': {
            'Meta': {'unique_together': "(('model', 'context'),)", 'object_name': 'ModelContextTemplate'},
            'context': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'catalog.searchlog': {
            'Meta': {'object_name': 'SearchLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'querystring': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['catalog']