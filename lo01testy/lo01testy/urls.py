"""lo01testy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import tmp.views
import accounts.views
import examination.views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tmp/$', tmp.views.index),
    url(r'^login/(?:(?P<username>[\w+\-\.@]+)/)?$', accounts.views.login_user, name='login'),
    url(r'^register/$', accounts.views.register_user, name='registration'),
    url(r'^logout/$', accounts.views.logout_user, name='logout'),
    url(r'^user/id/(?P<id>[0-9]+)/$', accounts.views.show_user, name='show_user'),
    url(r'^user/(?:(?P<username>[\w+\-\.@]+)/)?$', accounts.views.show_user, name='show_user'),
    url(r'^exam/list/$', examination.views.exams_list, name="exams_list"),
    url(r'^exam/id/(?P<id>[0-9]+)/$', examination.views.show_exam, name='show_exam'),
]
