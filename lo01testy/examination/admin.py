from django.contrib import admin
from django.contrib.auth.models import User
from .models import *
from lo01testy.admin import admin_site


class AssignInline(admin.TabularInline):
    model = Assign
    fieldsets = (
        (None, {
            'fields': ('exam', 'due_date', 'creation_date')
        }),
    )
    readonly_fields = ('creation_date',)
    extra = 1


class ExamCodeInline(admin.TabularInline):
    model = ExamCode
    fieldsets = (
        (None, {
            'fields': ('code', 'expiry_date')
        }),
    )
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    inlines = (AssignInline,)


class ExamAdmin(admin.ModelAdmin):
    inlines = (ExamCodeInline, )


admin.site.register(Exam, ExamAdmin)
admin.site.register(Group, GroupAdmin)

# admin_site.register(Exam)
# admin_site.register(Group, GroupAdmin)
