from io import TextIOWrapper

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from app.exam_tools import ExamUploader
from app.forms import UploadExamFileForm
from app.models import (UserX, RegistrationCode, Exam, Group, GroupExamLink,
                        ExamCode, Question, AnswerChoice)


class UserXInline(admin.StackedInline):
    model = UserX


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'code', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('is_staff', 'is_superuser', 'date_joined', 'last_login')
    inlines = (UserXInline,)

    def code(self, obj):
        return obj.userx.code


# replaces User's string representation
def user_str(self):
    if hasattr(self, 'userx'):
        code = self.userx.code
    else:
        code = None
    if self.last_name and self.first_name:
        return "{}:{}:{} {}".format(
            code, self.username, self.last_name, self.first_name
        )
    elif self.last_name:
        return "{}:{}:{}".format(
            code, self.username, self.last_name
        )
    else:
        return "{}:{}".format(code, self.username)
User.__str__ = user_str


class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'used')


admin.site.unregister(DjangoGroup)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(RegistrationCode, RegistrationCodeAdmin)


class GroupExamLinkInline(admin.TabularInline):
    model = GroupExamLink
    fieldsets = (
        (None, {
            'fields': ('exam', 'due_date', 'creation_date')
        }),
    )
    readonly_fields = ('creation_date',)
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    inlines = (GroupExamLinkInline,)


class ExamCodeInline(admin.TabularInline):
    model = ExamCode
    fieldsets = (
        (None, {
            'fields': ('code', 'expiry_date')
        }),
    )
    extra = 1


class ExamAdmin(admin.ModelAdmin):
    inlines = (ExamCodeInline,)
    change_list_template = 'admin/app/exam/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^upload/$',
                self.admin_site.admin_view(self.upload_view),
                name="exam_upload"),
        ]
        return my_urls + urls

    def upload_view(self, request):
        if request.method == 'POST':
            form = UploadExamFileForm(request.POST, request.FILES)
            if form.is_valid():
                text_file = TextIOWrapper(
                    request.FILES['file'],
                    encoding='utf8', newline=''
                )
                exam_uploader = ExamUploader(
                    form.cleaned_data['exam_name'],
                    form.cleaned_data['num_questions']
                )
                exam_uploader.load_csv(
                    text_file, form.cleaned_data['has_headers']
                )
                exam_uploader.save_to_db()
                messages.success(request, 'Test uploaded successfully')
                return redirect('admin:app_exam_changelist')
        else:
            form = UploadExamFileForm()
        context = dict(
            admin.site.each_context(request),
            has_change_permission=True,
            title='Select file to upload',
            form=form,
            errors=form.errors
        )
        return render(
            request, 'admin/app/exam/upload_form.html', context
        )


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'type', 'text', 'rating')
    list_filter = ('exam',)
    inlines = (AnswerChoiceInline,)


admin.site.register(Exam, ExamAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Question, QuestionAdmin)
