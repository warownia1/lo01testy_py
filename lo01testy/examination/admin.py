from io import TextIOWrapper

from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf.urls import url
from django.shortcuts import render, redirect

from .models import Exam, Group, Assign, ExamCode, Question, Answer, \
                    ExamLog, AnswerLog
from .forms import UploadExamFileForm
from .utils import ExamUpload


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
        if request.method == 'POST':
            form = UploadExamFileForm(request.POST, request.FILES)
            if form.is_valid():
                exam_name = form.cleaned_data['exam_name']
                num_questions = form.cleaned_data['num_questions']
                file = request.FILES['file']
                text_file = TextIOWrapper(
                    file.file, encoding=request.encoding, newline=''
                )
                has_headers = form.cleaned_data['has_headers']
                exam_upload = ExamUpload(exam_name, num_questions)
                exam_upload.read_file(text_file, request.encoding, has_headers)
                exam_upload.save_to_db()
                messages.success(
                    request,
                    "The exam \"{}\" was uploaded successfully.".format(
                        exam_name
                    )
                )
                return redirect('admin:examination_exam_changelist')
        else:
            form = UploadExamFileForm()
        context = dict(
            admin.site.each_context(request),
            has_change_permission=True,
            title="Select file to upload",
            form=form,
            errors=form.errors
        )
        return render(
            request, 'admin/examination/exam/upload_form.html', context
        )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'type', 'text', 'rating')
    list_filter = ('exam', )
    inlines = (AnswerInline,)


class AnswerLogInline(admin.TabularInline):
    model = AnswerLog
    extra = 0
    readonly_fields = ('exam_log', 'question', 'answer', 'graded')


class ExamLogAdmin(admin.ModelAdmin):
    inlines = (AnswerLogInline, )
    readonly_fields = ('user', 'exam', 'date', 'user_rating')
    list_filter = ('exam', 'date')


admin.site.register(Exam, ExamAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ExamLog, ExamLogAdmin)
