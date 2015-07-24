from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/$', views.exams_list, name="list"),
    url(r'^(?P<id>[0-9]+)/$', views.show_exam, name='show'),
    url(r'^start/(?P<id>[0-9]+)/$', views.start_exam, name='start'),
    url(r'^question/$', views.question, name='question'),
    url(r'^result/$', views.show_results, name='show_results'),
]
