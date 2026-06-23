from django.urls import path
from . import views

app_name = "beneficiaries"

urlpatterns = [
    path("", views.beneficiary_list, name="list"),
    path("<int:pk>/", views.beneficiary_detail, name="detail"),
    path("create/", views.beneficiary_create, name="create"),
    path("<int:pk>/edit/", views.beneficiary_edit, name="edit"),
    path("<int:pk>/delete/", views.beneficiary_delete, name="delete"),
]
