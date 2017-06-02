from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class UserX(models.Model):
    """Additional information extending a basic user model"""
    user = models.OneToOneField(User, verbose_name=_('user'))
    code = models.CharField(max_length=16, unique=True,
                            verbose_name=_('user code'))
    rating = models.IntegerField(default=1500, verbose_name=_('rating'))

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')


class RegistrationCode(models.Model):
    """
    Codes required during registration of the user.
    
    During registration user must provide a unique student code which is
    deleted after use.
    """
    code = models.CharField(max_length=16, unique=True,
                            verbose_name=_('user code'))
    used = models.BooleanField(default=False, verbose_name=_('used'))

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('Registration key')
        verbose_name_plural = _('Registration keys')


class Exam(models.Model):
    """Table containing the list of all exams"""
    name = models.CharField(max_length=30, verbose_name=_('name'))
    num_questions = models.IntegerField(verbose_name=_('number of questions'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')


class Group(models.Model):
    """
    A group gathering multiple students.

    Exams are assigned to the group and all students which belong to that
    group have access to the exam.
    """
    name = models.CharField(max_length=40, verbose_name=_('name'))
    exams = models.ManyToManyField(Exam, through='GroupExamLink',
                                   verbose_name=_('exams'))
    members = models.ManyToManyField(User, verbose_name=_('members'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')


class GroupExamLink(models.Model):
    """An intermediary table containing details of group-exam relation."""
    exam = models.ForeignKey(Exam, verbose_name=_('exam'))
    group = models.ForeignKey(Group, verbose_name=_('group'))
    # date due exam must be taken by the group
    # in case of conflict, always the latest due date is considered.
    due_date = models.DateField(editable=True, verbose_name=_('due date'))
    # date when exam was assigned to group
    creation_date = models.DateField(auto_now_add=True,
                                     verbose_name=_('creation date'))

    class Meta:
        verbose_name = _('Group exam link')
        verbose_name_plural = _('Group exam links')


class ExamCode(models.Model):
    """
    Table of codes required to start the exam in graded mode.
    Student inputs the code provided by teacher during the assessed work.
    """
    exam = models.ForeignKey(Exam, verbose_name=_('creation date'))
    code = models.CharField(max_length=16, verbose_name=_('code'))
    # expiration time of the code
    expiry_date = models.DateTimeField(verbose_name=_('expiry date'))

    def __str__(self):
        return "Code for test {}".format(self.exam.name)

    class Meta:
        verbose_name = _('Exam code')
        verbose_name_plural = _('Exam codes')


class Question(models.Model):
    """Table of questions assigned to a particular exam."""
    SINGLE_CHOICE = 'S'
    MULTIPLE_CHOICE = 'M'
    TYPE_CHOICES = (
        (SINGLE_CHOICE, _('Single choice')),
        (MULTIPLE_CHOICE, _('Multiple choice')),
    )
    DEFAULT_RATING = 1500
    exam = models.ForeignKey(Exam, related_name='questions',
                             verbose_name=_('exam'))
    type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                            verbose_name=_('type'))
    text = models.TextField(verbose_name=_('text'))
    # the difficulty (rating) of the question
    rating = models.IntegerField(default=DEFAULT_RATING,
                                 verbose_name=_('rating'))

    def __str__(self):
        # noinspection PyTypeChecker
        if len(self.text) > 50:
            return "{}: {}...".format(self.exam.name, self.text[:50])
        else:
            return "{}: {}".format(self.exam.name, self.text)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


class AnswerChoice(models.Model):
    """Table of answers assigned to a multiple choice question."""
    question = models.ForeignKey(Question, related_name='answers',
                                 verbose_name=_('question'))
    text = models.CharField(max_length=100, verbose_name=_('text'))
    is_correct = models.BooleanField(verbose_name=_('is correct?'))

    def __str__(self):
        # noinspection PyTypeChecker
        if len(self.text) > 50:
            # noinspection PyUnresolvedReferences
            return "Q{}: {}...".format(self.question_id, self.text[:50])
        else:
            # noinspection PyUnresolvedReferences
            return "Q{}: {}".format(self.question_id, self.text)

    class Meta:
        verbose_name = _('Answer choice')
        verbose_name_plural = _('Answer choices')
