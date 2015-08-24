# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_examgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examgroup',
            name='exams',
        ),
        migrations.RemoveField(
            model_name='examgroup',
            name='members',
        ),
        migrations.DeleteModel(
            name='ExamGroup',
        ),
    ]
