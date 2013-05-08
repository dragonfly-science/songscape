# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Site', fields ['code']
        db.delete_unique(u'recordings_site', ['code'])

        # Adding model 'Analysis'
        db.create_table(u'recordings_analysis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('ubertag', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ubertags', null=True, to=orm['recordings.Tag'])),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='analyses', to=orm['recordings.Organisation'])),
        ))
        db.send_create_signal(u'recordings', ['Analysis'])

        # Adding M2M table for field tags on 'Analysis'
        db.create_table(u'recordings_analysis_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('analysis', models.ForeignKey(orm[u'recordings.analysis'], null=False)),
            ('tag', models.ForeignKey(orm[u'recordings.tag'], null=False))
        ))
        db.create_unique(u'recordings_analysis_tags', ['analysis_id', 'tag_id'])

        # Adding M2M table for field deployments on 'Analysis'
        db.create_table(u'recordings_analysis_deployments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('analysis', models.ForeignKey(orm[u'recordings.analysis'], null=False)),
            ('deployment', models.ForeignKey(orm[u'recordings.deployment'], null=False))
        ))
        db.create_unique(u'recordings_analysis_deployments', ['analysis_id', 'deployment_id'])

        # Adding M2M table for field detectors on 'Analysis'
        db.create_table(u'recordings_analysis_detectors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('analysis', models.ForeignKey(orm[u'recordings.analysis'], null=False)),
            ('detector', models.ForeignKey(orm[u'recordings.detector'], null=False))
        ))
        db.create_unique(u'recordings_analysis_detectors', ['analysis_id', 'detector_id'])

        # Adding unique constraint on 'Analysis', fields ['organisation', 'code']
        db.create_unique(u'recordings_analysis', ['organisation_id', 'code'])

        # Adding model 'Tag'
        db.create_table(u'recordings_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'recordings', ['Tag'])

        # Adding model 'Identification'
        db.create_table(u'recordings_identification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('analysis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['recordings.Analysis'])),
            ('snippet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['recordings.Snippet'])),
            ('comment', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'recordings', ['Identification'])

        # Adding M2M table for field scores on 'Identification'
        db.create_table(u'recordings_identification_scores', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('identification', models.ForeignKey(orm[u'recordings.identification'], null=False)),
            ('score', models.ForeignKey(orm[u'recordings.score'], null=False))
        ))
        db.create_unique(u'recordings_identification_scores', ['identification_id', 'score_id'])

        # Adding M2M table for field tags on 'Identification'
        db.create_table(u'recordings_identification_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('identification', models.ForeignKey(orm[u'recordings.identification'], null=False)),
            ('tag', models.ForeignKey(orm[u'recordings.tag'], null=False))
        ))
        db.create_unique(u'recordings_identification_tags', ['identification_id', 'tag_id'])


        # Changing field 'Detector.code'
        db.alter_column(u'recordings_detector', 'code', self.gf('django.db.models.fields.SlugField')(max_length=32))
        # Adding field 'Deployment.owner'
        db.add_column(u'recordings_deployment', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='deployments', to=orm['recordings.Organisation']),
                      keep_default=False)


        # Changing field 'Signal.code'
        db.alter_column(u'recordings_signal', 'code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32))
        # Adding unique constraint on 'Signal', fields ['code']
        db.create_unique(u'recordings_signal', ['code'])

        # Adding field 'Site.organisation'
        db.add_column(u'recordings_site', 'organisation',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='sites', to=orm['recordings.Organisation']),
                      keep_default=False)


        # Changing field 'Site.code'
        db.alter_column(u'recordings_site', 'code', self.gf('django.db.models.fields.SlugField')(max_length=32))
        # Adding unique constraint on 'Site', fields ['organisation', 'code']
        db.create_unique(u'recordings_site', ['organisation_id', 'code'])


        # Changing field 'Recorder.code'
        db.alter_column(u'recordings_recorder', 'code', self.gf('django.db.models.fields.SlugField')(max_length=32))

        # Changing field 'Organisation.code'
        db.alter_column(u'recordings_organisation', 'code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32))

    def backwards(self, orm):
        # Removing unique constraint on 'Site', fields ['organisation', 'code']
        db.delete_unique(u'recordings_site', ['organisation_id', 'code'])

        # Removing unique constraint on 'Signal', fields ['code']
        db.delete_unique(u'recordings_signal', ['code'])

        # Removing unique constraint on 'Analysis', fields ['organisation', 'code']
        db.delete_unique(u'recordings_analysis', ['organisation_id', 'code'])

        # Deleting model 'Analysis'
        db.delete_table(u'recordings_analysis')

        # Removing M2M table for field tags on 'Analysis'
        db.delete_table('recordings_analysis_tags')

        # Removing M2M table for field deployments on 'Analysis'
        db.delete_table('recordings_analysis_deployments')

        # Removing M2M table for field detectors on 'Analysis'
        db.delete_table('recordings_analysis_detectors')

        # Deleting model 'Tag'
        db.delete_table(u'recordings_tag')

        # Deleting model 'Identification'
        db.delete_table(u'recordings_identification')

        # Removing M2M table for field scores on 'Identification'
        db.delete_table('recordings_identification_scores')

        # Removing M2M table for field tags on 'Identification'
        db.delete_table('recordings_identification_tags')


        # Changing field 'Detector.code'
        db.alter_column(u'recordings_detector', 'code', self.gf('django.db.models.fields.SlugField')(max_length=20))
        # Deleting field 'Deployment.owner'
        db.delete_column(u'recordings_deployment', 'owner_id')


        # Changing field 'Signal.code'
        db.alter_column(u'recordings_signal', 'code', self.gf('django.db.models.fields.SlugField')(max_length=20))
        # Deleting field 'Site.organisation'
        db.delete_column(u'recordings_site', 'organisation_id')


        # Changing field 'Site.code'
        db.alter_column(u'recordings_site', 'code', self.gf('django.db.models.fields.SlugField')(max_length=20, unique=True))
        # Adding unique constraint on 'Site', fields ['code']
        db.create_unique(u'recordings_site', ['code'])


        # Changing field 'Recorder.code'
        db.alter_column(u'recordings_recorder', 'code', self.gf('django.db.models.fields.SlugField')(max_length=20))

        # Changing field 'Organisation.code'
        db.alter_column(u'recordings_organisation', 'code', self.gf('django.db.models.fields.SlugField')(max_length=20, unique=True))

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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'Meta': {'unique_together': "(('organisation', 'code'),)", 'object_name': 'Analysis'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deployments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Deployment']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'detectors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Detector']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analyses'", 'to': u"orm['recordings.Organisation']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Tag']", 'symmetrical': 'False'}),
            'ubertag': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ubertags'", 'null': 'True', 'to': u"orm['recordings.Tag']"})
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
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'detectors'", 'to': u"orm['recordings.Signal']"}),
            'version': ('django.db.models.fields.TextField', [], {})
        },
        u'recordings.identification': {
            'Meta': {'object_name': 'Identification'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['recordings.Analysis']"}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scores': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Score']", 'symmetrical': 'False'}),
            'snippet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['recordings.Snippet']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Tag']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'recordings.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'recordings.recorder': {
            'Meta': {'unique_together': "(('code', 'organisation'),)", 'object_name': 'Recorder'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recorders'", 'to': u"orm['recordings.Organisation']"})
        },
        u'recordings.recording': {
            'Meta': {'unique_together': "(('datetime', 'deployment'),)", 'object_name': 'Recording'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recordings'", 'to': u"orm['recordings.Deployment']"}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nchannels': ('django.db.models.fields.IntegerField', [], {}),
            'path': ('django.db.models.fields.TextField', [], {}),
            'sample_rate': ('django.db.models.fields.IntegerField', [], {}),
            'sha1': ('django.db.models.fields.TextField', [], {})
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
        u'recordings.signal': {
            'Meta': {'object_name': 'Signal'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'recordings.site': {
            'Meta': {'unique_together': "(('code', 'organisation'),)", 'object_name': 'Site'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.FloatField', [], {}),
            'recording': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'snippets'", 'to': u"orm['recordings.Recording']"}),
            'sonogram': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'soundcloud': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'soundfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'recordings.tag': {
            'Meta': {'object_name': 'Tag'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['recordings']