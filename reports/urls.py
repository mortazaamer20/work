from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_home, name="home"),
    path("individual/", views.individual_report, name="individual"),
    path("center/", views.center_report, name="center"),
    path("group/", views.group_report, name="group"),
    path("period/", views.period_report, name="period"),
    path("data-delete/<int:pk>/", views.beneficiary_data_delete, name="data_delete"),
]
