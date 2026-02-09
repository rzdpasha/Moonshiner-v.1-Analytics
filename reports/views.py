from django.shortcuts import render
from .logic.profit import profit_report
from .logic.profit_yearly import profit_yearly_report
from .logic.monthly import monthly_report
from .logic.categories import categories_report
from .logic.brews import brews_report
from .logic.clients import clients_report

def index(request):
    return render(request, "reports/base_reports.html")


def profit(request):
    context = profit_report(request)
    return render(request, "reports/profit.html", context)


def profit_yearly(request):
    context = profit_yearly_report(request)
    print(type(context))
    return render(request, "reports/profit_yearly.html", context)


def categories(request):
    context = categories_report(request)
    return render(request, "reports/categories.html", context)


def brew(request):
    context = brews_report(request)
    return render(request, "reports/brews.html", context)


def monthly(request):
    context = monthly_report(request)
    print(type(context))
    return render(request, "reports/monthly.html", context)


def clients(request):
    context = clients_report(request)
    return render(request, "reports/clients.html", context)
