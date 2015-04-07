# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_auto_20150209_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='score',
            field=models.FloatField(default=0, help_text='Current score; decays over time (see decay_scores command).'),
        ),
    ]
