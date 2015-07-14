from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Exam(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=40)
    exams = models.ManyToManyField(Exam, through='Assign')
    members = models.ManyToManyField(User)
    
    def __str__(self):
        return self.name
    
    
class Assign(models.Model):
    exam = models.ForeignKey(Exam)
    group = models.ForeignKey(Group)
    due_date = models.DateField(editable=True)
    creation_date = models.DateField(auto_now_add=True)
    
class ExamCode(models.Model):
    exam = models.ForeignKey(Exam)
    code = models.CharField(max_length=10)
    expiry_date = models.DateTimeField()
  