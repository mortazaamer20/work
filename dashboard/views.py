from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render
from django.db.models import Avg, Count, Q

from accounts.views import require_perm
from beneficiaries.models import Beneficiary
from assessments.models import DailyAssessment, RehabilitationIndex


@require_perm("dashboard", "view")
def dashboard_home(request):
    today = date.today()
    active_beneficiaries = Beneficiary.objects.filter(status="active").count()
    total_beneficiaries = Beneficiary.objects.count()

    today_assessments = DailyAssessment.objects.filter(date=today)
    today_count = today_assessments.count()
    pending_count = active_beneficiaries - today_count

    today_indices = RehabilitationIndex.objects.filter(assessment__date=today)
    avg_score = today_indices.aggregate(avg=Avg("total_score"))["avg"] or 0

    progressing = today_indices.filter(status="progressing").count()
    stable = today_indices.filter(status="stable").count()
    regressing = today_indices.filter(status="regressing").count()

    recent_assessments = DailyAssessment.objects.select_related(
        "beneficiary", "rehab_index"
    ).order_by("-date", "-created_at")[:20]

    week_ago = today - timedelta(days=7)
    weekly_avg = RehabilitationIndex.objects.filter(
        assessment__date__gte=week_ago
    ).values("assessment__date").annotate(
        avg_score=Avg("total_score")
    ).order_by("assessment__date")

    axis_averages = today_indices.aggregate(
        medical=Avg("medical_psychological_score"),
        behavioral=Avg("behavioral_score"),
        skill=Avg("skill_technical_score"),
        social=Avg("social_spiritual_score"),
    )

    return render(request, "dashboard/home.html", {
        "today": today,
        "active_beneficiaries": active_beneficiaries,
        "total_beneficiaries": total_beneficiaries,
        "today_count": today_count,
        "pending_count": pending_count,
        "avg_score": round(avg_score, 1),
        "progressing": progressing,
        "stable": stable,
        "regressing": regressing,
        "recent_assessments": recent_assessments,
        "weekly_avg": list(weekly_avg),
        "axis_averages": axis_averages,
    })


@require_perm("reports", "view")
def beneficiary_report(request, pk):
    from beneficiaries.models import Beneficiary as B
    from django.shortcuts import get_object_or_404
    b = get_object_or_404(B, pk=pk)
    assessments = DailyAssessment.objects.filter(beneficiary=b).select_related("rehab_index").order_by("-date")[:30]
    indices = RehabilitationIndex.objects.filter(assessment__beneficiary=b).order_by("-assessment__date")[:30]
    return render(request, "dashboard/beneficiary_report.html", {
        "b": b, "assessments": assessments, "indices": indices
    })
