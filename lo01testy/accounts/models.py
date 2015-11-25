from django.db import models
from django.contrib.auth.models import User

from examination.models import Exam


# may extend django.contrib.auth.models.User
class Student(models.Model):
    """Extension of a User model"""
    user = models.OneToOneField(User)
    rating = models.IntegerField(default=1500)


class RegisterCode(models.Model):
    """Codes required during registration of the user in the system.

    During registration user is asked to enter one of the codes which is
    uniquely generated for each student.
    Code is deleted after being used.
    """
    # in the future, code will be used to identify students
    code = models.CharField(max_length=16)
