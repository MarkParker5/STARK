from django.urls import path

from . import views

urlpatterns = [
	path('text', views.text, name = 'text'),
	path('command', views.command, name = 'command'),
]
