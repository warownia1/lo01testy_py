from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .enums import QuestionType


class Exam(models.Model):
    name = models.CharField(max_length=30)
    num_questions = models.IntegerField()

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

    def __str__(self):
        return "code for test {}".format(self.exam_id)


class Question(models.Model):
    SINGLE_CHOICE = QuestionType.single_choice
    MULTIPLE_CHOICE = QuestionType.multiple_choice
    OPEN_ENDED = QuestionType.open_ended
    TYPE_CHOICES = (
        (SINGLE_CHOICE, 'Single choice'),
        (MULTIPLE_CHOICE, 'Multiple choice'),
        (OPEN_ENDED, 'Open-ended'),
    )
    exam = models.ForeignKey(Exam)
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=SINGLE_CHOICE
    )
    text = models.TextField()
    rating = models.IntegerField(default=1500)

    def __str__(self):
        if len(self.text) > 50:
            return "{}: {}...".format(self.exam_id, self.text[:50])
        else:
            return "{}: {}".format(self.exam_id, self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField()

    def __str__(self):
        if len(self.text) > 50:
            return "Q{}: {}...".format(self.question_id, self.text[:50])
        else:
            return "Q{}: {}".format(self.question_id, self.text)
            
            
class ExamRegister(models.Model):
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam)
    date = models.DateField(auto_now_add=True)
    user_rating = models.IntegerField()
    
    def __str__(self):
        return "{} - {} - {}".format(
            self.date, self.exam.name, self.user.username)
    
    
class AnswerRegister(models.Model):
    exam_attempt = models.ForeignKey(ExamRegister)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=25)
    graded = models.BooleanField(default=False)
