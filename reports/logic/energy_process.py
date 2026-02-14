from datetime import datetime
from calendar import month_name
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from homebrew.models import Energy
import json


def energy_process_report(request):
    year = request.GET.get("year")
    year = int(year) if year and year.isdigit() else datetime.now().year

    # Группируем: Месяц + Тип процесса
    qs = (
        Energy.objects.filter(time_start__year=year)
        .annotate(month=TruncMonth("time_start"))
        .values("month", "type")
        .annotate(total_kwh=Sum("total"))
        .order_by("month")
    )

    # Названия месяцев для оси X
    labels = [month_name[m] for m in range(1, 13)]

    # Список всех типов процессов из модели
    # types = [t[0] for t in Energy.TYPE_CHOICES]
    types = Energy.objects.filter(time_start__year=year).values_list('type', flat=True).distinct()

    # Готовим структуру: { 'RECT': [0, 0, 15.5, ...], 'DSTL': [...] }
    # 12 нулей для каждого месяца
    datasets_map = {t: [0.0] * 12 for t in types}

    for row in qs:
        m_idx = row["month"].month - 1  # Индекс 0-11
        proc_type = row["type"]
        if proc_type in datasets_map:
            datasets_map[proc_type][m_idx] = float(row["total_kwh"] or 0)

    # Формируем данные для Chart.js
    chart_datasets = []
    colors = {
        "RECT": "#5511ff", "DSTL": "#00d1b2",
        "VCDS": "#ffdd57", "MCRT": "#ff3860",
        "NDRF": "#ff851b", "OTHR": "#7a7a7a"
    }

    for proc_type, values in datasets_map.items():
        chart_datasets.append({
            "label": proc_type,
            "data": values,
            "backgroundColor": colors.get(proc_type, "#cccccc"),
        })

    context = {
        "year": year,
        "labels_json": json.dumps(labels),
        "datasets_json": json.dumps(chart_datasets),
        "prev_year": year - 1,
        "next_year": year + 1,
        "total_kwh_year": sum(sum(v) for v in datasets_map.values())
    }
    return context