# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('examination', '0011_exam_num_questions'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerRegister',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('answer', models.CharField(max_length=25)),
                ('graded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExamRegister',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('user_rating', models.IntegerField()),
                ('exam', models.ForeignKey(to='examination.Exam')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='answerregister',
            name='exam_attempt',
            field=models.ForeignKey(to='examination.ExamRegister'),
        ),
    ]
