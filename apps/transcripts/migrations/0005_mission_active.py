# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcripts', '0004_auto_20141214_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='active',
            field=models.BooleanField(default=True, help_text='Are we currently cleaning this mission?'),
            preserve_default=True,
        ),
    ]
