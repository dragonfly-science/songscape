# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration:
    def forwards(self, orm):
        db.rename_column('recordings_recording', 'sample_rate', 'framerate')
        db.add_column('recordings_recording', 'sampwidth', models.IntegerField(default=2), keep_default=False)

    def backwards(self, orm):
        db.rename_column('recordings_recording', 'framerate', 'samplerate')
        db.add_column('recordings_recording', 'sampwidth')
