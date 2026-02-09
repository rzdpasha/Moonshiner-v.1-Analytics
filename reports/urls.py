from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("profit/", views.profit_report, name="profit"),
    path("clients/", views.clients_report, name="clients"),
    path("yearly/", views.profit_yearly, name="profit_yearly"),
    path("categories/", views.categories_report, name="categories"),
    path("brew/", views.brews_report, name="brew"),
    path("monthly/", views.monthly, name="monthly"),

]
