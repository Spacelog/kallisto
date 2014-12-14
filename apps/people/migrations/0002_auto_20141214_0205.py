# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pages_approved',
            field=models.IntegerField(default=0, help_text='Number of pages approved as correct.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='pages_cleaned',
            field=models.IntegerField(default=0, help_text='Number of pages cleaned (with edits).'),
            preserve_default=True,
        ),
    ]
