from django.conf.urls import url, include

import app.views.accounts
import app.views.exam
from app import views


accounts_urlpatterns = [
    url(r'^login/(?:(?P<username>[\w\-\.@]+)/)?$',
        views.accounts.login_view, name='login'),
    url(r'^register/$', views.accounts.register_view, name='registration'),
    url(r'^logout/$', views.accounts.logout_view, name='logout'),
    url(r'^profile/$', views.accounts.profile_view, name='profile'),
    url(r'^settings/$', views.accounts.settings_view, name='settings'),
]

exam_urlpatterns = [
    url(r'^list/$', views.exam.exams_list_view, name='list'),
    url(r'^info/([0-9]+)/$', views.exam.exam_info_view, name='info'),
    url(r'^start/([0-9]+)/$', views.exam.exam_start_view, name='start'),
    url(r'^question/$', views.exam.question_view, name='question'),
    url(r'^finished/$', views.exam.finished_view, name='finished'),
]

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^accounts/', include(accounts_urlpatterns, namespace='accounts')),
    url(r'^exam/', include(exam_urlpatterns, namespace='exam')),
]
