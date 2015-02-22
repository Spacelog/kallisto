# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcripts', '0005_mission_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='wiki',
            field=models.URLField(help_text='URL of wiki page for useful notes.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
