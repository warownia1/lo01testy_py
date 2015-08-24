# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0005_auto_20150710_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('exam', models.ForeignKey(to='examination.Exam')),
            ],
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='group',
        ),
        migrations.AlterField(
            model_name='group',
            name='exams',
            field=models.ManyToManyField(to='examination.Exam', through='examination.Assign'),
        ),
        migrations.DeleteModel(
            name='Assignment',
        ),
        migrations.AddField(
            model_name='assign',
            name='group',
            field=models.ForeignKey(to='examination.Group'),
        ),
    ]
