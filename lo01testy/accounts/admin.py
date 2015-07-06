from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from accounts.models import Student, RegisterCode


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False

    
class UserAdmin(UserAdmin):
    inlines = (StudentInline, )
    

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(RegisterCode)