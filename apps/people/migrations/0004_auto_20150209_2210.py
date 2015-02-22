# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def initial_scores(apps, schema_editor):
    User = apps.get_model("people", "User")
    User.objects.all().update(
        score=models.F('pages_approved') + models.F('pages_cleaned'),
    )
        

class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_user_score'),
    ]

    operations = [
        migrations.RunPython(initial_scores),
    ]
