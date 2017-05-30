from django.db import models
from django.contrib.auth.models import User


class UserX(models.Model):
    """Additional information extending a basic user model"""
    user = models.OneToOneField(User)
    code = models.CharField(max_length=16, unique=True)
    rating = models.IntegerField(default=1500)

    def __str__(self):
        return self.code


class RegistrationCode(models.Model):
    """
    Codes required during registration of the user.
    
    During registration user must provide a unique student code which is
    deleted after use.
    """
    code = models.CharField(max_length=16, unique=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class Exam(models.Model):
    """Table containing the list of all exams"""
    name = models.CharField(max_length=30)
    num_questions = models.IntegerField()

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    A group gathering multiple students.

    Exams are assigned to the group and all students which belong to that
    group have access to the exam.
    """
    name = models.CharField(max_length=40)
    exams = models.ManyToManyField(Exam, through='GroupExamLink')
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class GroupExamLink(models.Model):
    """An intermediary table containing details of group-exam relation."""
    exam = models.ForeignKey(Exam)
    group = models.ForeignKey(Group)
    # date due exam must be taken by the group
    # in case of conflict, always the latest due date is considered.
    due_date = models.DateField(editable=True)
    # date when exam was assigned to group
    creation_date = models.DateField(auto_now_add=True)


class ExamCode(models.Model):
    """
    Table of codes required to start the exam in graded mode.
    Student inputs the code provided by teacher during the assessed work.
    """
    exam = models.ForeignKey(Exam)
    code = models.CharField(max_length=16)
    # expiration time of the code
    expiry_date = models.DateTimeField()

    def __str__(self):
        return "Code for test {}".format(self.exam.name)


class Question(models.Model):
    """Table of questions assigned to a particular exam."""
    SINGLE_CHOICE = 'S'
    MULTIPLE_CHOICE = 'M'
    TYPE_CHOICES = (
        (SINGLE_CHOICE, 'Single choice'),
        (MULTIPLE_CHOICE, 'Multiple choice'),
    )
    DEFAULT_RATING = 1500
    exam = models.ForeignKey(Exam, related_name='questions')
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES
    )
    text = models.TextField()
    # the difficulty (rating) of the question
    rating = models.IntegerField(default=DEFAULT_RATING)

    def __str__(self):
        # noinspection PyTypeChecker
        if len(self.text) > 50:
            return "{}: {}...".format(self.exam.name, self.text[:50])
        else:
            return "{}: {}".format(self.exam.name, self.text)


class AnswerChoice(models.Model):
    """Table of answers assigned to a multiple choice question."""
    question = models.ForeignKey(Question, related_name='answers')
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField()

    def __str__(self):
        # noinspection PyTypeChecker
        if len(self.text) > 50:
            # noinspection PyUnresolvedReferences
            return "Q{}: {}...".format(self.question_id, self.text[:50])
        else:
            # noinspection PyUnresolvedReferences
            return "Q{}: {}".format(self.question_id, self.text)
