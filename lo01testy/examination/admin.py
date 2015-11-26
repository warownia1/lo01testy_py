from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.conf.urls import url
from django.shortcuts import render, render_to_response

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

    change_list_template = "admin/examination/exam/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^upload/$', self.admin_site.admin_view(self.upload_view),
            name="examination_exam_upload"),
        ]
        return my_urls + urls

    def upload_view(self, request):
        return render(
            request, 'admin/examination/exam/upload_form.html',
            {
                'title': "Select file to upload",
                'has_permission': True,
                'has_add_permission': True,
                'has_change_permission': True,
                'site_url': reverse('index')
            }
        )


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
