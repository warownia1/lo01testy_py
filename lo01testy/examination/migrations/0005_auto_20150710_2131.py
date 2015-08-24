# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0004_auto_20150710_2029'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('exam', models.ForeignKey(to='examination.Exam')),
            ],
        ),
        migrations.RemoveField(
            model_name='group',
            name='exams'
        ),
        migrations.AddField(
            model_name='group',
            name='exams',
            field=models.ManyToManyField(through='examination.Assignment', to='examination.Exam'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='group',
            field=models.ForeignKey(to='examination.Group'),
        ),
    ]
