# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Analysis', fields ['organisation', 'code']
        db.delete_unique(u'recordings_analysis', ['organisation_id', 'code'])

        # Deleting field 'Analysis.organisation'
        db.delete_column(u'recordings_analysis', 'organisation_id')

        # Adding field 'Analysis.user'
        db.add_column(u'recordings_analysis', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='analyses', to=orm['auth.User']),
                      keep_default=False)

        # Adding unique constraint on 'Analysis', fields ['code', 'user']
        db.create_unique(u'recordings_analysis', ['code', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Analysis', fields ['code', 'user']
        db.delete_unique(u'recordings_analysis', ['code', 'user_id'])

        # Adding field 'Analysis.organisation'
        db.add_column(u'recordings_analysis', 'organisation',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='analyses', to=orm['recordings.Organisation']),
                      keep_default=False)

        # Deleting field 'Analysis.user'
        db.delete_column(u'recordings_analysis', 'user_id')

        # Adding unique constraint on 'Analysis', fields ['organisation', 'code']
        db.create_unique(u'recordings_analysis', ['organisation_id', 'code'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'recordings.analysis': {
            'Meta': {'unique_together': "(('user', 'code'),)", 'object_name': 'Analysis'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'snippets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'analyses'", 'symmetrical': 'False', 'through': u"orm['recordings.AnalysisSet']", 'to': u"orm['recordings.Snippet']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Tag']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analyses'", 'to': u"orm['auth.User']"})
        },
        u'recordings.analysisset': {
            'Meta': {'object_name': 'AnalysisSet'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'set'", 'to': u"orm['recordings.Analysis']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selection_method': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'snippet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'set'", 'to': u"orm['recordings.Snippet']"})
        },
        u'recordings.deployment': {
            'Meta': {'unique_together': "(('site', 'recorder', 'start'),)", 'object_name': 'Deployment'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['recordings.Organisation']"}),
            'recorder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['recordings.Recorder']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployments'", 'to': u"orm['recordings.Site']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'recordings.detector': {
            'Meta': {'unique_together': "(('code', 'version'),)", 'object_name': 'Detector'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
        u'recordings.identification': {
            'Meta': {'object_name': 'Identification'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifications'", 'to': u"orm['recordings.Analysis']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'false_tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'negative_identifications'", 'symmetrical': 'False', 'to': u"orm['recordings.Tag']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scores': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Score']", 'symmetrical': 'False'}),
            'snippet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifications'", 'to': u"orm['recordings.Snippet']"}),
            'true_tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'identifications'", 'symmetrical': 'False', 'to': u"orm['recordings.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifications'", 'to': u"orm['auth.User']"})
        },
        u'recordings.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'recordings.recorder': {
            'Meta': {'unique_together': "(('code', 'organisation'),)", 'object_name': 'Recorder'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recorders'", 'to': u"orm['recordings.Organisation']"})
        },
        u'recordings.recording': {
            'Meta': {'unique_together': "(('datetime', 'deployment'),)", 'object_name': 'Recording'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recordings'", 'to': u"orm['recordings.Deployment']"}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'framerate': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5': ('django.db.models.fields.TextField', [], {}),
            'nchannels': ('django.db.models.fields.IntegerField', [], {}),
            'path': ('django.db.models.fields.TextField', [], {}),
            'sampwidth': ('django.db.models.fields.IntegerField', [], {})
        },
        u'recordings.score': {
            'Meta': {'unique_together': "(('snippet', 'detector'),)", 'object_name': 'Score'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'detector': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scores'", 'to': u"orm['recordings.Detector']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'snippet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scores'", 'to': u"orm['recordings.Snippet']"})
        },
        u'recordings.site': {
            'Meta': {'unique_together': "(('code', 'organisation'),)", 'object_name': 'Site'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sites'", 'to': u"orm['recordings.Organisation']"})
        },
        u'recordings.snippet': {
            'Meta': {'unique_together': "(('recording', 'offset', 'duration'),)", 'object_name': 'Snippet'},
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'favourites'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.FloatField', [], {}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'snippets'", 'to': u"orm['recordings.Recording']"}),
            'sonogram': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'soundcloud': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'recordings.tag': {
            'Meta': {'object_name': 'Tag'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['recordings']