# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0008_examcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('text', models.TextField()),
                ('is_correct', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('type', models.CharField(choices=[('S', 'Single choice'), ('M', 'Multiple choice'), ('O', 'Open-ended')], default='S', max_length=1)),
                ('text', models.TextField()),
                ('rating', models.IntegerField(default=1500)),
                ('exam', models.ForeignKey(to='examination.Exam')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='examination.Question'),
        ),
    ]
