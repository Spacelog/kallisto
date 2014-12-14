# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lib.media
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Full name (eg Mercury-Atlas 7).', max_length=500)),
                ('short_name', models.CharField(help_text='Short name (eg MA7).', max_length=10)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('patch', lib.media.MigratableImageField(height_field=b'patch_height', width_field=b'patch_width')),
                ('patch_width', models.IntegerField(default=0, null=True, editable=False, blank=True)),
                ('patch_height', models.IntegerField(default=0, null=True, editable=False, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveIntegerField()),
                ('original', lib.media.MigratableImageField(height_field=b'original_height', width_field=b'original_width')),
                ('original_width', models.IntegerField(default=0, null=True, editable=False, blank=True)),
                ('original_height', models.IntegerField(default=0, null=True, editable=False, blank=True)),
                ('original_text', models.TextField()),
                ('approved', models.BooleanField(default=False, help_text='Is the latest revision approved?')),
                ('locked_until', models.DateTimeField(null=True, blank=True)),
                ('locked_by', models.ForeignKey(related_name=b'pages_locked', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('mission', models.ForeignKey(related_name=b'pages', to='transcripts.Mission')),
            ],
            options={
                'ordering': ('number',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('by', models.ForeignKey(related_name=b'page_revisions', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(related_name=b'revisions', to='transcripts.Page')),
            ],
            options={
                'ordering': ('when',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='revision',
            unique_together=set([('page', 'by')]),
        ),
    ]
