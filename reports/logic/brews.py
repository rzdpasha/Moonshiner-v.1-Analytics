from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime

from homebrew.models import Income


def _parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


@staff_member_required
def brews_report(request):
    """
    Отчёт по напиткам:
      - liters = count
      - revenue = total_price
      - drink = Income.variant.brew
    """

    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))

    qs = Income.objects.select_related("variant", "variant__brew")

    if date_from:
        qs = qs.filter(date__date__gte=date_from)  # Было date0__date
    if date_to:
        qs = qs.filter(date__date__lte=date_to)  # Было date0__date

    # --- группировка ---
    grouped = (
        qs.values("variant__brew__title")
        .annotate(
            qty=Count("id"),
            liters=Coalesce(
                Sum("count", output_field=models.IntegerField()),
                0,
                output_field=models.IntegerField(),
            ),
            revenue=Coalesce(
                Sum("total_price", output_field=models.IntegerField()),
                0,
                output_field=models.IntegerField(),
            ),
        )
        .order_by("variant__brew__title")
    )

    # --- графики ---
    labels = [g["variant__brew__title"] for g in grouped]
    chart_liters = [int(g["liters"]) for g in grouped]
    chart_revenue = [int(g["revenue"]) for g in grouped]

    # --- totals ---
    total_liters = sum(chart_liters)
    total_revenue = sum(chart_revenue)

    # --- TOP-5 ---
    top5_liters = sorted(grouped, key=lambda g: int(g["liters"]), reverse=True)[:5]
    top5_revenue = sorted(grouped, key=lambda g: int(g["revenue"]), reverse=True)[:5]

    context = {
        "title": "Отчёт по напиткам",
        "grouped": grouped,
        "labels": labels,
        "chart_liters": chart_liters,
        "chart_revenue": chart_revenue,
        "total_liters": total_liters,
        "total_revenue": total_revenue,
        "top5_liters": top5_liters,
        "top5_revenue": top5_revenue,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "reports/brews.html", context)
