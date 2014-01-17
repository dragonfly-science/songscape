# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organisation'
        db.create_table(u'recordings_organisation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Organisation'])

        # Adding model 'Site'
        db.create_table(u'recordings_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sites', to=orm['recordings.Organisation'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Site'])

        # Adding unique constraint on 'Site', fields ['code', 'organisation']
        db.create_unique(u'recordings_site', ['code', 'organisation_id'])

        # Adding model 'Recorder'
        db.create_table(u'recordings_recorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recorders', to=orm['recordings.Organisation'])),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Recorder'])

        # Adding unique constraint on 'Recorder', fields ['code', 'organisation']
        db.create_unique(u'recordings_recorder', ['code', 'organisation_id'])

        # Adding model 'Deployment'
        db.create_table(u'recordings_deployment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployments', to=orm['recordings.Site'])),
            ('recorder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployments', to=orm['recordings.Recorder'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployments', to=orm['recordings.Organisation'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Deployment'])

        # Adding unique constraint on 'Deployment', fields ['site', 'recorder', 'start']
        db.create_unique(u'recordings_deployment', ['site_id', 'recorder_id', 'start'])

        # Adding model 'Recording'
        db.create_table(u'recordings_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recordings', to=orm['recordings.Deployment'])),
            ('md5', self.gf('django.db.models.fields.TextField')()),
            ('framerate', self.gf('django.db.models.fields.IntegerField')()),
            ('sampwidth', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('nchannels', self.gf('django.db.models.fields.IntegerField')()),
            ('path', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'recordings', ['Recording'])

        # Adding unique constraint on 'Recording', fields ['datetime', 'deployment']
        db.create_unique(u'recordings_recording', ['datetime', 'deployment_id'])

        # Adding model 'Tag'
        db.create_table(u'recordings_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'recordings', ['Tag'])

        # Adding model 'Snippet'
        db.create_table(u'recordings_snippet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording', self.gf('django.db.models.fields.related.ForeignKey')(related_name='snippets', to=orm['recordings.Recording'])),
            ('offset', self.gf('django.db.models.fields.FloatField')()),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('sonogram', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('soundcloud', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('soundfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Snippet'])

        # Adding unique constraint on 'Snippet', fields ['recording', 'offset', 'duration']
        db.create_unique(u'recordings_snippet', ['recording_id', 'offset', 'duration'])

        # Adding model 'Detector'
        db.create_table(u'recordings_detector', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'recordings', ['Detector'])

        # Adding unique constraint on 'Detector', fields ['code', 'version']
        db.create_unique(u'recordings_detector', ['code', 'version'])

        # Adding model 'Score'
        db.create_table(u'recordings_score', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snippet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='scores', to=orm['recordings.Snippet'])),
            ('detector', self.gf('django.db.models.fields.related.ForeignKey')(related_name='scores', to=orm['recordings.Detector'])),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'recordings', ['Score'])

        # Adding unique constraint on 'Score', fields ['snippet', 'detector']
        db.create_unique(u'recordings_score', ['snippet_id', 'detector_id'])

        # Adding model 'Analysis'
        db.create_table(u'recordings_analysis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('ubertag', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ubertags', null=True, to=orm['recordings.Tag'])),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='analyses', to=orm['recordings.Organisation'])),
        ))
        db.send_create_signal(u'recordings', ['Analysis'])

        # Adding unique constraint on 'Analysis', fields ['organisation', 'code']
        db.create_unique(u'recordings_analysis', ['organisation_id', 'code'])

        # Adding M2M table for field tags on 'Analysis'
        db.create_table(u'recordings_analysis_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('analysis', models.ForeignKey(orm[u'recordings.analysis'], null=False)),
            ('tag', models.ForeignKey(orm[u'recordings.tag'], null=False))
        ))
        db.create_unique(u'recordings_analysis_tags', ['analysis_id', 'tag_id'])

        # Adding model 'AnalysisSet'
        db.create_table(u'recordings_analysisset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('analysis', self.gf('django.db.models.fields.related.ForeignKey')(related_name='set', to=orm['recordings.Analysis'])),
            ('snippet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='set', to=orm['recordings.Snippet'])),
            ('selection_method', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'recordings', ['AnalysisSet'])

        # Adding model 'Identification'
        db.create_table(u'recordings_identification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='identifications', to=orm['auth.User'])),
            ('analysis', self.gf('django.db.models.fields.related.ForeignKey')(related_name='identifications', to=orm['recordings.Analysis'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('snippet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='identifications', to=orm['recordings.Snippet'])),
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

        # Adding M2M table for field true_tags on 'Identification'
        db.create_table(u'recordings_identification_true_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('identification', models.ForeignKey(orm[u'recordings.identification'], null=False)),
            ('tag', models.ForeignKey(orm[u'recordings.tag'], null=False))
        ))
        db.create_unique(u'recordings_identification_true_tags', ['identification_id', 'tag_id'])

        # Adding M2M table for field false_tags on 'Identification'
        db.create_table(u'recordings_identification_false_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('identification', models.ForeignKey(orm[u'recordings.identification'], null=False)),
            ('tag', models.ForeignKey(orm[u'recordings.tag'], null=False))
        ))
        db.create_unique(u'recordings_identification_false_tags', ['identification_id', 'tag_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Analysis', fields ['organisation', 'code']
        db.delete_unique(u'recordings_analysis', ['organisation_id', 'code'])

        # Removing unique constraint on 'Score', fields ['snippet', 'detector']
        db.delete_unique(u'recordings_score', ['snippet_id', 'detector_id'])

        # Removing unique constraint on 'Detector', fields ['code', 'version']
        db.delete_unique(u'recordings_detector', ['code', 'version'])

        # Removing unique constraint on 'Snippet', fields ['recording', 'offset', 'duration']
        db.delete_unique(u'recordings_snippet', ['recording_id', 'offset', 'duration'])

        # Removing unique constraint on 'Recording', fields ['datetime', 'deployment']
        db.delete_unique(u'recordings_recording', ['datetime', 'deployment_id'])

        # Removing unique constraint on 'Deployment', fields ['site', 'recorder', 'start']
        db.delete_unique(u'recordings_deployment', ['site_id', 'recorder_id', 'start'])

        # Removing unique constraint on 'Recorder', fields ['code', 'organisation']
        db.delete_unique(u'recordings_recorder', ['code', 'organisation_id'])

        # Removing unique constraint on 'Site', fields ['code', 'organisation']
        db.delete_unique(u'recordings_site', ['code', 'organisation_id'])

        # Deleting model 'Organisation'
        db.delete_table(u'recordings_organisation')

        # Deleting model 'Site'
        db.delete_table(u'recordings_site')

        # Deleting model 'Recorder'
        db.delete_table(u'recordings_recorder')

        # Deleting model 'Deployment'
        db.delete_table(u'recordings_deployment')

        # Deleting model 'Recording'
        db.delete_table(u'recordings_recording')

        # Deleting model 'Tag'
        db.delete_table(u'recordings_tag')

        # Deleting model 'Snippet'
        db.delete_table(u'recordings_snippet')

        # Deleting model 'Detector'
        db.delete_table(u'recordings_detector')

        # Deleting model 'Score'
        db.delete_table(u'recordings_score')

        # Deleting model 'Analysis'
        db.delete_table(u'recordings_analysis')

        # Removing M2M table for field tags on 'Analysis'
        db.delete_table('recordings_analysis_tags')

        # Deleting model 'AnalysisSet'
        db.delete_table(u'recordings_analysisset')

        # Deleting model 'Identification'
        db.delete_table(u'recordings_identification')

        # Removing M2M table for field scores on 'Identification'
        db.delete_table('recordings_identification_scores')

        # Removing M2M table for field true_tags on 'Identification'
        db.delete_table('recordings_identification_true_tags')

        # Removing M2M table for field false_tags on 'Identification'
        db.delete_table('recordings_identification_false_tags')


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
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analyses'", 'to': u"orm['recordings.Organisation']"}),
            'snippets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'analyses'", 'symmetrical': 'False', 'through': u"orm['recordings.AnalysisSet']", 'to': u"orm['recordings.Snippet']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['recordings.Tag']", 'symmetrical': 'False'}),
            'ubertag': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ubertags'", 'null': 'True', 'to': u"orm['recordings.Tag']"})
        },
        u'recordings.analysisset': {
            'Meta': {'object_name': 'AnalysisSet'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'set'", 'to': u"orm['recordings.Analysis']"}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['recordings']