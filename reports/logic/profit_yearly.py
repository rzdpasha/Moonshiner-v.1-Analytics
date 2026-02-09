import json
from datetime import datetime
from calendar import month_name
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.db.models.functions import ExtractMonth

from homebrew.models import Income, Cost, Energy


@staff_member_required
def profit_yearly_report(request):

    year = request.GET.get("year")
    if year and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year


    income_raw = (
        Income.objects.filter(date__year=year)  # Было date0__year
        .annotate(month=ExtractMonth("date0"))
        .values("month")
        .annotate(total=Sum("total_price"))
    )

    cost_raw = (
        Cost.objects.filter(date__year=year)
        .annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(total=Sum("total_price"))
    )

    energy_raw = (
        Energy.objects.filter(time_start__year=year)
        .annotate(month=ExtractMonth("time_start"))
        .values("month")
        .annotate(total=Sum("total_price"))
    )

    def to_map(qs):

        d = {}
        for row in qs:
            m = row.get("month")
            t = row.get("total") or 0
            if m is None:
                continue
            d[int(m)] = Decimal(str(t))
        return d

    income_map = to_map(income_raw)
    cost_map = to_map(cost_raw)
    energy_map = to_map(energy_raw)

    labels = [month_name[m] for m in range(1, 13)]  # ['January','February',...]
    incomes = []
    costs = []
    energies = []
    profits = []

    for m in range(1, 13):
        inc = income_map.get(m, Decimal("0.00"))
        cst = cost_map.get(m, Decimal("0.00"))
        eng = energy_map.get(m, Decimal("0.00"))

        inc_f = float(inc)
        cst_f = float(cst)
        eng_f = float(eng)
        prof_f = float(inc - cst - eng)

        incomes.append(inc_f)
        costs.append(cst_f)
        energies.append(eng_f)
        profits.append(prof_f)


    context = {
        "year": year,
        "labels": json.dumps(labels),  # JSON string: ["January","February",...]
        "incomes": json.dumps(incomes),  # JSON array of floats
        "costs": json.dumps(costs),
        "energies": json.dumps(energies),
        "profits": json.dumps(profits),
        "total_income": sum(incomes),
        "total_cost": sum(costs),
        "total_energy": sum(energies),
        "total_profit": sum(profits),
        "prev_year": year - 1,
        "next_year": year + 1,
    }

    return context
