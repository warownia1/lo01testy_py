# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0010_auto_20150715_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='num_questions',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]
