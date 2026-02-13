from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from decimal import Decimal
import json

from homebrew.models import Income


def _parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


@staff_member_required
def categories_report(request):

    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))

    qs = Income.objects.all()

    if date_from:
        qs = qs.filter(date__date__gte=date_from)  # Было date0__date
    if date_to:
        qs = qs.filter(date__date__lte=date_to)  # Было date0__date

    # группировка по категориям
    grouped = (
        qs.values("category__title")
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
        .order_by("category__title")
    )

    # данные для JS-графиков
    labels = [g["category__title"] for g in grouped]
    qty_list = [int(g["liters"]) // 2 for g in grouped]
    revenue_list = [int(g["revenue"]) for g in grouped]

    context = {
        "title": "Отчёт по категориям",
        "grouped": grouped,
        "date_from": date_from,
        "date_to": date_to,
        # сериализованные данные
        "labels_json": json.dumps(labels, ensure_ascii=False),
        "qty_json": json.dumps(qty_list),
        "revenue_json": json.dumps(revenue_list),
    }

    return render(request, "reports/categories.html", context)
