# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0007_assign_due_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamCode',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('code', models.CharField(max_length=10)),
                ('expiry_date', models.DateTimeField()),
                ('exam', models.ForeignKey(to='examination.Exam')),
            ],
        ),
    ]
