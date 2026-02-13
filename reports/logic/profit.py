from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce, TruncDay, TruncMonth
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from decimal import Decimal
from datetime import datetime
from homebrew.models import Income, Cost, Energy


def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return datetime.strptime(s, "%Y-%m-%d").date()


@staff_member_required
def profit_report(request):
    """
    Отчёт: Прибыль = Income - Cost - Energy
    """

    # ---- Параметры ----
    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))
    agg = request.GET.get("agg", "day")  # day / month

    date_from2 = _parse_date(request.GET.get("from2"))
    date_to2 = _parse_date(request.GET.get("to2"))

    # ---- Базовые QuerySet ----
    incomes_qs = Income.objects.all()
    costs_qs = Cost.objects.all()
    energy_qs = Energy.objects.all()

    if date_from:
        incomes_qs = incomes_qs.filter(date__date__gte=date_from)
        costs_qs = costs_qs.filter(date__date__gte=date_from)
        energy_qs = energy_qs.filter(time_start__date__gte=date_from)

    if date_to:
        incomes_qs = incomes_qs.filter(date__date__lte=date_to)
        costs_qs = costs_qs.filter(date__date__lte=date_to)
        energy_qs = energy_qs.filter(time_start__date__lte=date_to)

    # ---- ИТОГО ЗА ПЕРИОД ----
    total_income = Decimal(
        incomes_qs.aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            )
        )["s"]
    )

    total_cost = Decimal(
        costs_qs.aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            )
        )["s"]
    )

    total_energy = Decimal(
        energy_qs.aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            )
        )["s"]
    )

    profit = total_income - total_cost - total_energy

    # ---- АГРЕГАЦИЯ ПО ДНЯМ/МЕСЯЦАМ ----
    trunc = TruncMonth if agg == "month" else TruncDay
    label_format = "%Y-%m" if agg == "month" else "%Y-%m-%d"

    incomes_grouped = (
        incomes_qs.annotate(period=trunc("date0"))
        .values("period")
        .annotate(
            total=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by("period")
    )

    costs_grouped = (
        costs_qs.annotate(period=trunc("date"))
        .values("period")
        .annotate(
            total=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by("period")
    )

    energy_grouped = (
        energy_qs.annotate(period=trunc("time_start"))
        .values("period")
        .annotate(
            total=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .order_by("period")
    )
    # ---- Сводим периоды ----
    labels_set = set()

    for rows in (incomes_grouped, costs_grouped, energy_grouped):
        for row in rows:
            period = row["period"]
            if hasattr(period, "date"):
                period = period.date()
            labels_set.add(period)

    labels = sorted(labels_set)

    def fmt(d):
        return d.strftime(label_format)

    labels_str = [fmt(d) for d in labels]

    # ---- Быстрые lookup-таблицы ----
    inc_map = {
        (r["period"].date() if hasattr(r["period"], "date") else r["period"]): Decimal(
            r["total"] or 0
        )
        for r in incomes_grouped
    }

    cost_map = {
        (r["period"].date() if hasattr(r["period"], "date") else r["period"]): Decimal(
            r["total"] or 0
        )
        for r in costs_grouped
    }

    en_map = {
        (r["period"].date() if hasattr(r["period"], "date") else r["period"]): Decimal(
            r["total"] or 0
        )
        for r in energy_grouped
    }

    # ---- Данные для графиков ----
    chart_income = [float(inc_map.get(d, 0)) for d in labels]
    chart_cost = [float(cost_map.get(d, 0)) for d in labels]
    chart_energy = [float(en_map.get(d, 0)) for d in labels]
    chart_profit = [
        float(inc_map.get(d, 0) - cost_map.get(d, 0) - en_map.get(d, 0)) for d in labels
    ]

    # ---- Сравнение периодов ----
    compare = None

    if date_from2 and date_to2:
        inc2 = Income.objects.filter(
            date__date__gte=date_from2,
            date__date__lte=date_to2,  # Переделал на date вместо date0. Причина понятна
        ).aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )[
            "s"
        ]

        cost2 = Cost.objects.filter(
            date__date__gte=date_from2, date__date__lte=date_to2
        ).aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )[
            "s"
        ]

        en2 = Energy.objects.filter(
            time_start__date__gte=date_from2, time_start__date__lte=date_to2
        ).aggregate(
            s=Coalesce(
                Sum(
                    "total_price",
                    output_field=models.DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )[
            "s"
        ]

        profit2 = inc2 - cost2 - en2

        def pct(old, new):
            old = Decimal(old or 0)
            new = Decimal(new or 0)
            if old == 0:
                return None
            return float((new - old) / old * 100)

        compare = {
            "period1": {
                "income": float(total_income),
                "cost": float(total_cost),
                "energy": float(total_energy),
                "profit": float(profit),
            },
            "period2": {
                "income": float(inc2),
                "cost": float(cost2),
                "energy": float(en2),
                "profit": float(profit2),
            },
            "change_pct": {
                "income": pct(inc2, total_income),
                "cost": pct(cost2, total_cost),
                "energy": pct(en2, total_energy),
                "profit": pct(profit2, profit),
            },
            "period_labels": {
                "from1": date_from,
                "to1": date_to,
                "from2": date_from2,
                "to2": date_to2,
            },
        }

    # ---- Контекст ----
    context = {
        "title": "Отчёт по прибыли (Income − Cost − Energy)",
        "total_income": total_income,
        "total_cost": total_cost,
        "total_energy": total_energy,
        "profit": profit,
        "labels": labels_str,
        "chart_income": chart_income,
        "chart_cost": chart_cost,
        "chart_energy": chart_energy,
        "chart_profit": chart_profit,
        "agg": agg,
        "compare": compare,
        "date_from": date_from,
        "date_to": date_to,
        "date_from2": date_from2,
        "date_to2": date_to2,
    }

    return render(request, "reports/profit.html", context)
