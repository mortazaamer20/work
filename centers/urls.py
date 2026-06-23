from django.urls import path
from . import views

app_name = "centers"

urlpatterns = [
    path("", views.center_list, name="list"),
    path("create/", views.center_create, name="center_create"),
    path("<int:pk>/edit/", views.center_edit, name="center_edit"),
    path("<int:pk>/delete/", views.center_delete, name="center_delete"),
    path("<int:center_pk>/activities/", views.activity_list, name="activity_list"),
    path("<int:center_pk>/activities/create/", views.activity_create, name="activity_create"),
    path("activities/<int:pk>/edit/", views.activity_edit, name="activity_edit"),
    path("activities/<int:pk>/delete/", views.activity_delete, name="activity_delete"),
    path("<int:center_pk>/clinics/", views.clinic_list, name="clinic_list"),
    path("<int:center_pk>/clinics/create/", views.clinic_create, name="clinic_create"),
    path("clinics/<int:pk>/edit/", views.clinic_edit, name="clinic_edit"),
    path("clinics/<int:pk>/delete/", views.clinic_delete, name="clinic_delete"),
]
