from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from accounts.models import Student, RegisterCode

    
class MyUserAdmin(UserAdmin):
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
    pass
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'first_name', 'last_name', 'rating',)
    readonly_fields = ('user',)
    
    def first_name(self, obj):
        return obj.user.first_name
    def last_name(self,obj):
        return obj.user.last_name
    pass
    

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(RegisterCode)