from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from accounts.models import Student, RegistrationCode


class StudentInline(admin.StackedInline):
    model = Student


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'student_code', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ("Personal info", {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ("Permissions", {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ("Important dates", {
            'fields': ('last_login', 'date_joined')
        }),
    )
    readonly_fields = ('is_staff', 'is_superuser', 'date_joined', 'last_login')
    inlines = (StudentInline, )

    def student_code(self, object):
        return object.student.code


# Very ugly solution, shame on you!
def user_str(self):
    if hasattr(self, 'student'):
        code = self.student.code
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


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(RegistrationCode, RegistrationCodeAdmin)
