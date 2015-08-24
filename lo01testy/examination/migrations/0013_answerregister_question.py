# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0012_auto_20150724_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerregister',
            name='question',
            field=models.ForeignKey(to='examination.Question', default=1),
            preserve_default=False,
        ),
    ]
