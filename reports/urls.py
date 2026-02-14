from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("profit/", views.profit, name="profit"),
    path("clients/", views.clients, name="clients"),
    path("yearly/", views.profit_yearly, name="profit_yearly"),
    path("categories/", views.categories, name="categories"),
    path("brew/", views.brew, name="brew"),
    path("monthly/", views.monthly, name="monthly"),
    path("process/", views.energy_process, name="energy_process"),
]
