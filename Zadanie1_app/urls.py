from django.urls import path

from . import views
from . import views2
from . import views3
from . import views5

app_name = 'Zadanie1_app'

urlpatterns = [

    path('v1/health', views.health, name="health"),
    path('', views.welcome, name="welcome"),

    path('v1/ov/submissions/', views2.url_dispatcher, name="get_print_pages"),
    path('v1/ov/submissions', views2.url_dispatcher, name="get_print_pages"),
    path('v1/ov/submissions/<int:table_id>', views2.delete_row, name="delete_row"),
    path('v1/companies/', views3.z3_get_print_pages, name="Zadanie_3_GET"),
    path('v1/companies', views3.z3_get_print_pages, name="Zadanie_3_GET"),

    path('v2/test/', views5.test, name="test"),
    path('v2/ov/submissions/', views5.submissions_url_dispatcher, name="submissions"),
    path('v2/ov/submissions', views5.submissions_url_dispatcher, name="submissions"),
    path('v2/ov/submissions/<int:table_id>', views5.submissions_url_dispatcher, name="submissions"),
    path('v2/ov/submissions/<int:table_id>/', views5.submissions_url_dispatcher, name="submissions"),

    path('v2/companies/', views5.companies_get_pages, name="companies"),
    path('v2/companies', views5.companies_get_pages, name="companies"),

]


