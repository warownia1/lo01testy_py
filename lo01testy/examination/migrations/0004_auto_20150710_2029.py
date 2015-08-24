# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0003_examgroup'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExamGroup',
            new_name='Group',
        ),
    ]
