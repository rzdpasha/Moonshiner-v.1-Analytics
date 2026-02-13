import json
from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum, Count, IntegerField, F, ExpressionWrapper
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from homebrew.models import Income, Buyer


# helper formatting
def fmt_money_int(value: int) -> str:
    # strict accounting style: "12 345 ₽"
    try:
        v = int(value)
    except Exception:
        v = 0
    return f"{v:,}".replace(",", " ") + " ₽"


def _parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


@staff_member_required
def clients_report(request):
    """
    Клиентский отчет.
    Query params:
      - from, to : yyyy-mm-dd
      - view = b|c  (B - expanded, C - dashboard)
      - top = int (how many top clients to show in KPI)
    """
    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))
    view = request.GET.get("view", "b").lower()
    top_n = int(request.GET.get("top", 10))
    print(top_n)

    qs = Income.objects.select_related("client").all()
    if date_from:
        qs = qs.filter(date__date__gte=date_from)  # Было date0__date
    if date_to:
        qs = qs.filter(date__date__lte=date_to)  # Было date0__date

    grouped = (
        qs.values(
            "client_id", "client__client"
        )  # client name field in your models is 'client'
        .annotate(
            purchases=Count("id"),
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
        .order_by("-revenue")
    )

    grouped2 = (
        qs.values("client_id", "client__client")
        .annotate(
            purchases=Count("id"),
            liters=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("count") * Decimal("0.5"),
                        output_field=DecimalField(max_digits=6, decimal_places=2),
                    )
                ),
                0,
                output_field=DecimalField(max_digits=6, decimal_places=2),
            ),
            revenue=Coalesce(
                Sum("total_price", output_field=IntegerField()),
                0,
                output_field=IntegerField(),
            ),
        )
        .order_by("-liters")
    )

    grouped3 = (
        qs.values("client_id", "client__client")
        .annotate(
            orders_count=Count(
                "order_group_id", distinct=True
            )  # Считаем уникальные заказы
        )
        .order_by("-orders_count")
    )

    # aggregate totals for KPI
    total_clients = grouped.count()
    total_purchases = sum(g["purchases"] for g in grouped)
    total_liters = sum(g["liters"] for g in grouped) // 2
    total_revenue_int = sum(int(g["revenue"]) for g in grouped)

    # top clients
    top_clients = list(grouped[:top_n])
    top_volume = list(grouped2[:top_n])
    top_loyalty = list(grouped3[:top_n])

    # prepare chart data
    labels = [g["client__client"] for g in grouped]
    chart_liters = [int(g["liters"]) // 2 for g in grouped]
    chart_revenue = [int(g["revenue"]) for g in grouped]

    # format KPIs
    kpis = {
        "total_clients": total_clients,
        "total_purchases": total_purchases,
        "total_liters": total_liters,
        "total_revenue": fmt_money_int(total_revenue_int),
    }

    context = {
        "title": "Отчёт по клиентам",
        "grouped": grouped,
        "top_clients": top_clients,
        "top_volume": top_volume,
        "top_loyalty": top_loyalty,  # Добавили!
        "kpis": kpis,
        "labels_json": json.dumps(labels, ensure_ascii=False),
        "liters_json": json.dumps(chart_liters),
        "revenue_json": json.dumps(chart_revenue),
        "date_from": date_from,
        "date_to": date_to,
        "view": view,
    }

    template = "reports/clients.html"

    return render(request, template, context)
