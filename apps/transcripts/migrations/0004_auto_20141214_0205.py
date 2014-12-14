# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcripts', '0003_auto_20141213_1731'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ('mission', 'number')},
        ),
    ]
