# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0006_auto_20150710_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='assign',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2015, 7, 10, 20, 5, 3, 475383, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
