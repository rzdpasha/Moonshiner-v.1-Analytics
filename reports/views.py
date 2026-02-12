from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .logic.profit import profit_report
from .logic.profit_yearly import profit_yearly_report
from .logic.monthly import monthly_report
from .logic.categories import categories_report
from .logic.brews import brews_report
from .logic.clients import clients_report

@login_required
def index(request):
    return render(request, "reports/base_reports.html")

@login_required
def profit(request):
    context = profit_report(request)
    return render(request, "reports/profit.html", context)

@login_required
def profit_yearly(request):
    context = profit_yearly_report(request)
    print(type(context))
    return render(request, "reports/profit_yearly.html", context)

@login_required
def categories(request):
    context = categories_report(request)
    return render(request, "reports/categories.html", context)

@login_required
def brew(request):
    context = brews_report(request)
    return render(request, "reports/brews.html", context)

@login_required
def monthly(request):
    context = monthly_report(request)
    print(type(context))
    return render(request, "reports/monthly.html", context)

@login_required
def clients(request):
    context = clients_report(request)
    return render(request, "reports/clients.html", context)
