from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User)
    rating = models.IntegerField(default=1500)

    
class RegisterCode(models.Model):
    code = models.CharField(max_length=16)
    