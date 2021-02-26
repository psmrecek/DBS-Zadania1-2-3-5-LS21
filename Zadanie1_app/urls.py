from django.urls import path

from . import views

app_name = 'Zadanie1_app'
urlpatterns = [

    path('v1/cas', views.current_datetime, name="cas"),
    path('v1/health', views.health, name="health"),
    path('', views.welcome, name="welcome"),
    path('error', views.error, name="error"),
]
