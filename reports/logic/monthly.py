import json
from datetime import datetime
from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count, IntegerField
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from homebrew.models import Income, Cost, Energy


def _parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


def fmt_money_int(value: int) -> str:
    try:
        v = int(value)
    except Exception:
        v = 0
    return f"{v:,}".replace(",", " ") + " ₽"


@staff_member_required
def monthly_report(request):
    """
    Продажи по месяцам (по date по умолчанию)
    params:
      - from / to
      - date_field = date0|date
      - view = b|c (controls template - optional)
    """
    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))
    date_field = request.GET.get("date_field", "date")
    view = request.GET.get("view", "b")

    # base qss
    inc_qs = Income.objects.all()
    if date_from:
        inc_qs = inc_qs.filter(**{f"{date_field}__date__gte": date_from})
    if date_to:
        inc_qs = inc_qs.filter(**{f"{date_field}__date__lte": date_to})

    grouped = (
        inc_qs.annotate(month=TruncMonth(date_field))
        .values("month")
        .annotate(
            orders=Coalesce(Count("id"), 0),
            liters=Coalesce(
                Sum("count", output_field=IntegerField()),
                0,
                output_field=IntegerField(),
            ),
            revenue=Coalesce(
                Sum("total_price", output_field=IntegerField()),
                0,
                output_field=IntegerField(),
            ),
        )
        .order_by("month")
    )

    labels = []
    liters = []
    revenue = []
    for r in grouped:
        m = r["month"]
        label = m.strftime("%Y-%m") if m else ""
        labels.append(label)
        liters.append(int(r["liters"]))
        revenue.append(int(r["revenue"]))

    # summary KPIs
    total_revenue = fmt_money_int(sum(revenue))
    total_liters = sum(liters)
    total_orders = sum(r["orders"] for r in grouped)

    context = {
        "title": "Продажи по месяцам",
        "grouped": grouped,
        "labels_json": json.dumps(labels, ensure_ascii=False),
        "liters_json": json.dumps(liters),
        "revenue_json": json.dumps(revenue),
        "total_revenue": total_revenue,
        "total_liters": total_liters,
        "total_orders": total_orders,
        "date_from": date_from,
        "date_to": date_to,
        "date_field": date_field,
    }

    # template = "reports/monthly.html"
    # return render(request, template, context)
    return context
