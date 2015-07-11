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
    

# class MembershipInline(admin.TabularInline):
    # model = Membership
    # extra = 5
    
    
class GroupAdmin(admin.ModelAdmin):
    inlines = (AssignInline,)


admin.site.register(Exam)
admin.site.register(Group, GroupAdmin)
