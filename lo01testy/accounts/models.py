from django.db import models
from django.contrib.auth.models import User

from examination.models import Exam


class Student(models.Model):
    user = models.OneToOneField(User)
    rating = models.IntegerField(default=1500)
    
    def __str__(self):
        return self.user.__str__()

    
class RegisterCode(models.Model):
    code = models.CharField(max_length=16)
    
  