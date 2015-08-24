# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='name',
            field=models.CharField(default='Dummy exam', max_length=30),
            preserve_default=False,
        ),
    ]
