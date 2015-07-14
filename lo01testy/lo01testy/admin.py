from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

class MyAdminSite(AdminSite):
	pass

admin_site = MyAdminSite(name='myadmin')

