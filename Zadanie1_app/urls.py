from django.urls import path

from . import views
from . import views2
from . import views3

app_name = 'Zadanie1_app'
urlpatterns = [

    path('v1/health', views.health, name="health"),
    path('', views.welcome, name="welcome"),
    path('v1/ov/submissions/', views2.url_dispatcher, name="z3_get_print_pages"),
    path('v1/ov/submissions', views2.url_dispatcher, name="z3_get_print_pages"),
    path('v1/ov/submissions/<int:table_id>', views2.delete_row, name="delete_row"),
    path('v1/companies/', views3.z3_get_print_pages, name="Zadanie_3_GET"),
    path('v1/companies', views3.z3_get_print_pages, name="Zadanie_3_GET"),

]
