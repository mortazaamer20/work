from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("report/<int:pk>/", views.beneficiary_report, name="beneficiary_report"),
]
