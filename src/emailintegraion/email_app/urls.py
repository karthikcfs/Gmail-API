from django.conf.urls import url
from django.conf.urls import include

from . import views

urlpatterns = [
    url(r'^report/', views.email_report, name='view_email_report'),
    url(r'^rules/(?P<action>.*)/$', views.rules_action, name='gmail_action_rules'),
]
