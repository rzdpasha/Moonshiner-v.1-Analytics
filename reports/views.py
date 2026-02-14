from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .logic.profit import profit_report as get_profit_data
from .logic.profit_yearly import profit_yearly_report as get_yearly_data
from .logic.monthly import monthly_report as get_monthly_data
from .logic.categories import categories_report as get_categories_data
from .logic.brews import brews_report as get_brews_data
from .logic.clients import clients_report as get_clients_data
from .logic.energy_process import energy_process_report as get_energy_data

@login_required
def index(request):
    return render(request, "reports/base_reports.html")

@login_required
def profit(request):
    context = get_profit_data(request)
    return render(request, "reports/profit.html", context)

@login_required
def profit_yearly(request):
    context = get_yearly_data(request)
    print(type(context))
    return render(request, "reports/profit_yearly.html", context)

@login_required
def categories(request):
    context = get_categories_data(request)
    return render(request, "reports/categories.html", context)

@login_required
def brew(request):
    context = get_brews_data(request)
    return render(request, "reports/brews.html", context)

@login_required
def monthly(request):
    context = get_monthly_data(request)
    print(type(context))
    return render(request, "reports/monthly.html", context)

@login_required
def clients(request):
    context = get_clients_data(request)
    return render(request, "reports/clients.html", context)

@login_required
def energy_process(request):
    context = get_energy_data(request)
    return render(request, "reports/energy_process_report.html", context)
