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
import accounts.views
import examination.views


exam_urlpatterns = [
    url(r'^list/$', examination.views.exams_list, name="list"),
    url(r'^overview/(?P<id>[0-9]+)/$',
        examination.views.exam_overview, name='overview'),
    url(r'^init/(?P<id>[0-9]+)/$', examination.views.init_exam, name='init'),
    url(r'^question/$', examination.views.question, name='question'),
    url(r'^result/$', examination.views.final_result, name='show_results'),
]

accounts_urlpatterns = [
    url(r'^login/(?:(?P<username>[\w+\-\.@]+)/)?$',
        accounts.views.login_user, name='login'),
    url(r'^register/$', accounts.views.register_user, name='registration'),
    url(r'^logout/$', accounts.views.logout_user, name='logout'),
    url(r'^user/id/(?P<id>[0-9]+)/$',
        accounts.views.user_profile, name='user_profile'),
    url(r'^user/(?:(?P<username>[\w+\-\.@]+)/)?$',
        accounts.views.user_profile, name='user_profile'),
    url(r'^settings/$', accounts.views.account_settings, name='settings'),
    url(r'^settings/email/$',
        accounts.views.change_email, name='change_email'),
    url(r'^settings/password/$',
        accounts.views.change_password, name='change_password'),
    url(r'^settings/personal/$',
        accounts.views.change_personal, name='change_personal'),
]

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', accounts.views.index, name="index"),

    url(r'^accounts/', include(accounts_urlpatterns, namespace='accounts')),
    url(r'^exam/', include(exam_urlpatterns, namespace='exam')),
]
