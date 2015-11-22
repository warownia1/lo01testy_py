from django.contrib import admin
from django.contrib.auth.models import User
from .models import *


class AssignInline(admin.TabularInline):
    model = Assign
    fieldsets = (
        (None, {
            'fields': ('exam', 'due_date', 'creation_date')
        }),
    )
    readonly_fields = ('creation_date',)
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    inlines = (AssignInline,)


class ExamCodeInline(admin.TabularInline):
    model = ExamCode
    fieldsets = (
        (None, {
            'fields': ('code', 'expiry_date')
        }),
    )
    extra = 1


class ExamAdmin(admin.ModelAdmin):
    inlines = (ExamCodeInline, )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)


class AnswerRegisterInline(admin.TabularInline):
    model = AnswerRegister
    extra = 0
    readonly_fields = ('exam_attempt', 'question', 'answer', 'graded')


class ExamRegisterAdmin(admin.ModelAdmin):
    inlines = (AnswerRegisterInline, )
    readonly_fields = ('user', 'exam', 'date', 'user_rating')
    list_filter = ('exam', 'date')


admin.site.register(Exam, ExamAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ExamRegister, ExamRegisterAdmin)
