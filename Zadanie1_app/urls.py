from django.urls import path, re_path

from . import views
from . import views2

app_name = 'Zadanie1_app'
urlpatterns = [

    path('v1/cas', views.current_datetime, name="cas"),
    path('v1/health', views.health, name="health"),
    path('', views.welcome, name="welcome"),
    path('error', views.error, name="error"),
    path('v1/ov/submissions/first5', views2.first5, name="first5"),
    path('v1/ov/submissions/', views2.url_dispatcher, name="get_print_pages"),
    path('v1/ov/submissions', views2.url_dispatcher, name="get_print_pages"),
    path('v1/ov/submissions/<int:id>', views2.delete_row, name="delete_row"),
    path('debug', views2.debug, name="debug"),

]
