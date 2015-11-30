from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .enums import QuestionType


class Exam(models.Model):
    """Table of all exams."""
    name = models.CharField(max_length=30)
    # number of questions which student will be asked during the test.
    num_questions = models.IntegerField()

    def __str__(self):
        return self.name


class Group(models.Model):
    """A group of students.

    Exams are assigned to the group and all students which belong to that
    group have access to the exam.
    """
    name = models.CharField(max_length=40)
    exams = models.ManyToManyField(Exam, through='Assign')
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Assign(models.Model):
    """An intermediary table containing details of group-exam relation."""
    exam = models.ForeignKey(Exam)
    group = models.ForeignKey(Group)
    # date due exam must be taken by the group
    # in case of conflict, always the latest due date is considered.
    due_date = models.DateField(editable=True)
    # date when exam was added to group
    creation_date = models.DateField(auto_now_add=True)


class ExamCode(models.Model):
    """Table of codes required to take the exam in grade mode.

    During the assessed workshop, student inputs the code provided by teacher.
    Code required for grade mode only."""
    exam = models.ForeignKey(Exam)
    code = models.CharField(max_length=10)
    # expiration time of the code
    expiry_date = models.DateTimeField()

    def __str__(self):
        return "code for test {}".format(self.exam_id)


class Question(models.Model):
    """Table of questions assigned to a particular exam."""
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
    # the difficulty (rating) of the question
    rating = models.IntegerField(default=1500)

    def __str__(self):
        if len(self.text) > 50:
            return "{}: {}...".format(self.exam_id, self.text[:50])
        else:
            return "{}: {}".format(self.exam_id, self.text)


class Answer(models.Model):
    """Table of answers assigned to a question."""
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField()

    def __str__(self):
        if len(self.text) > 50:
            return "Q{}: {}...".format(self.question_id, self.text[:50])
        else:
            return "Q{}: {}".format(self.question_id, self.text)


class ExamLog(models.Model):
    """Collection of all exams already taken by students."""
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam)
    # date when exam was taken
    date = models.DateField(auto_now_add=True)
    # rating of the user when was taking the exam
    user_rating = models.IntegerField()

    def __str__(self):
        return "{} - {} - {}".format(
            self.date, self.exam.name, self.user.username
        )

    class Meta:
        verbose_name_plural = 'exams log'


# this model is storing students' answers
# it's user in open-ended questions rather than single/multiple choice
class AnswerLog(models.Model):
    """Collection of answers given by students during exams"""
    exam_log = models.ForeignKey(ExamLog)
    question = models.ForeignKey(Question)
    # answer contains a json object with student's answer
    answer = models.CharField(max_length=25)
    # whether questions was already graded
    graded = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'answers log'
