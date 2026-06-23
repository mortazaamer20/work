import json
from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from accounts.views import require_perm
from beneficiaries.models import Beneficiary
from centers.models import Center, Activity, ActivityField, Clinic, ClinicField
from .models import DailyAssessment, ActivityRecord, ClinicRecord, RehabilitationIndex
from .forms import DailyAssessmentForm


@require_perm("assessments", "view")
def assessment_list(request):
    qs = DailyAssessment.objects.select_related("beneficiary", "assessed_by", "rehab_index").order_by("-date")
    q = request.GET.get("q", "").strip()
    d = request.GET.get("date", "")
    if q:
        qs = qs.filter(Q(beneficiary__full_name__icontains=q) | Q(beneficiary__ref_number__icontains=q))
    if d:
        qs = qs.filter(date=d)
    template = "assessments/assessment_list_partial.html" if request.htmx else "assessments/assessment_list.html"
    return render(request, template, {"assessments": qs[:100], "q": q, "date_filter": d})


@require_perm("assessments", "add")
def assessment_create(request):
    beneficiary_id = request.GET.get("beneficiary")
    initial = {"date": date.today()}
    if beneficiary_id:
        initial["beneficiary"] = beneficiary_id
    form = DailyAssessmentForm(request.POST or None, initial=initial)
    form.fields["beneficiary"].queryset = Beneficiary.objects.filter(status="active")

    accessible_centers = request.user.get_accessible_centers()
    activities = Activity.objects.filter(center__in=accessible_centers, is_active=True).select_related("center").prefetch_related("fields")
    clinics = Clinic.objects.filter(center__in=accessible_centers, is_active=True).select_related("center").prefetch_related("fields")

    if request.method == "POST" and form.is_valid():
        assessment = form.save(commit=False)
        assessment.assessed_by = request.user
        assessment.save()

        _save_activity_records(request, assessment, activities)
        _save_clinic_records(request, assessment, clinics)

        rehab_index, _ = RehabilitationIndex.objects.get_or_create(assessment=assessment)
        rehab_index.calculate()

        messages.success(request, f"تم حفظ التقييم اليومي - مؤشر التأهيل: {rehab_index.total_score}%")
        return redirect("assessments:detail", pk=assessment.pk)

    return render(request, "assessments/assessment_form.html", {
        "form": form, "activities": activities, "clinics": clinics, "title": "تقييم يومي جديد"
    })


@require_perm("assessments", "edit")
def assessment_edit(request, pk):
    assessment = get_object_or_404(DailyAssessment, pk=pk)
    form = DailyAssessmentForm(request.POST or None, instance=assessment)
    form.fields["beneficiary"].queryset = Beneficiary.objects.filter(
        Q(status="active") | Q(pk=assessment.beneficiary_id)
    )

    accessible_centers = request.user.get_accessible_centers()
    activities = Activity.objects.filter(center__in=accessible_centers, is_active=True).select_related("center").prefetch_related("fields")
    clinics = Clinic.objects.filter(center__in=accessible_centers, is_active=True).select_related("center").prefetch_related("fields")

    existing_activity_data = {}
    for rec in assessment.activity_records.all():
        existing_activity_data[rec.activity_id] = rec.data

    existing_clinic_data = {}
    for rec in assessment.clinic_records.all():
        existing_clinic_data[rec.clinic_id] = rec.data

    if request.method == "POST" and form.is_valid():
        form.save()

        assessment.activity_records.all().delete()
        assessment.clinic_records.all().delete()

        _save_activity_records(request, assessment, activities)
        _save_clinic_records(request, assessment, clinics)

        rehab_index, _ = RehabilitationIndex.objects.get_or_create(assessment=assessment)
        rehab_index.calculate()

        messages.success(request, "تم تحديث التقييم")
        return redirect("assessments:detail", pk=assessment.pk)

    return render(request, "assessments/assessment_form.html", {
        "form": form, "activities": activities, "clinics": clinics,
        "title": "تعديل التقييم", "editing": True,
        "existing_activity_data": json.dumps({str(k): v for k, v in existing_activity_data.items()}),
        "existing_clinic_data": json.dumps({str(k): v for k, v in existing_clinic_data.items()}),
    })


@require_perm("assessments", "view")
def assessment_detail(request, pk):
    assessment = get_object_or_404(
        DailyAssessment.objects.select_related("beneficiary", "assessed_by", "rehab_index"),
        pk=pk
    )
    activity_records = assessment.activity_records.select_related("activity__center").all()
    clinic_records = assessment.clinic_records.select_related("clinic__center").all()
    return render(request, "assessments/assessment_detail.html", {
        "assessment": assessment, "activity_records": activity_records, "clinic_records": clinic_records
    })


@require_perm("assessments", "delete")
def assessment_delete(request, pk):
    assessment = get_object_or_404(DailyAssessment, pk=pk)
    if request.method == "POST":
        assessment.delete()
        messages.success(request, "تم حذف التقييم")
        return redirect("assessments:list")
    return render(request, "assessments/assessment_confirm_delete.html", {"assessment": assessment})


def _save_activity_records(request, assessment, activities):
    for activity in activities:
        prefix = f"activity_{activity.pk}_"
        data = {}
        total_score = Decimal("0")
        total_max = Decimal("0")
        has_data = False

        for field in activity.fields.all():
            key = prefix + field.field_key
            value = request.POST.get(key, "").strip()
            if value:
                has_data = True
                data[field.field_key] = value
                if field.field_type in ("rating", "rating10", "number"):
                    try:
                        val = Decimal(value)
                        total_score += val
                        total_max += field.max_score
                    except Exception:
                        pass

        if has_data:
            score_pct = (total_score / total_max * 100) if total_max > 0 else Decimal("0")
            ActivityRecord.objects.create(
                assessment=assessment, activity=activity,
                data=data, score=score_pct, max_score=Decimal("100"),
                notes=request.POST.get(f"activity_{activity.pk}_notes", ""),
                recorded_by=request.user,
            )


def _save_clinic_records(request, assessment, clinics):
    for clinic in clinics:
        prefix = f"clinic_{clinic.pk}_"
        data = {}
        has_data = False
        total_score = Decimal("0")
        total_max = Decimal("0")

        for field in clinic.fields.all():
            key = prefix + field.field_key
            value = request.POST.get(key, "").strip()
            if value:
                has_data = True
                data[field.field_key] = value
                if field.field_type in ("rating", "rating10", "number"):
                    try:
                        val = Decimal(value)
                        if field.normal_min is not None and field.normal_max is not None:
                            if field.normal_min <= val <= field.normal_max:
                                total_score += Decimal("1")
                            total_max += Decimal("1")
                        else:
                            total_score += val
                            total_max += field.max_score if hasattr(field, "max_score") else Decimal("5")
                    except Exception:
                        pass

        if has_data:
            score_pct = (total_score / total_max * 100) if total_max > 0 else Decimal("50")
            ClinicRecord.objects.create(
                assessment=assessment, clinic=clinic,
                data=data, score=score_pct, max_score=Decimal("100"),
                notes=request.POST.get(f"clinic_{clinic.pk}_notes", ""),
                recorded_by=request.user,
            )
