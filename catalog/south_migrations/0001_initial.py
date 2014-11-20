# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ModelContextTemplate'
        db.create_table(u'catalog_modelcontexttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('context', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'catalog', ['ModelContextTemplate'])

        # Adding unique constraint on 'ModelContextTemplate', fields ['model', 'context']
        db.create_unique(u'catalog_modelcontexttemplate', ['model', 'context'])


    def backwards(self, orm):
        # Removing unique constraint on 'ModelContextTemplate', fields ['model', 'context']
        db.delete_unique(u'catalog_modelcontexttemplate', ['model', 'context'])

        # Deleting model 'ModelContextTemplate'
        db.delete_table(u'catalog_modelcontexttemplate')


    models = {
        u'catalog.modelcontexttemplate': {
            'Meta': {'unique_together': "(('model', 'context'),)", 'object_name': 'ModelContextTemplate'},
            'context': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalog']