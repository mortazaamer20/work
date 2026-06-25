import json
from datetime import date


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from accounts.views import require_perm
from beneficiaries.models import Beneficiary
from centers.models import Activity, Clinic, GeneralField
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


def _scoped_activities(user):
    return user.get_accessible_activities().select_related("center").prefetch_related("fields") \
        .order_by("center__order", "center__name", "order", "name")


def _scoped_clinics(user):
    return user.get_accessible_clinics().select_related("center").prefetch_related("fields") \
        .order_by("center__order", "center__name", "order", "name")


def _general_fields():
    return GeneralField.objects.filter(is_active=True).order_by("order", "name")


@require_perm("assessments", "add")
def assessment_create(request):
    beneficiary_id = request.GET.get("beneficiary")
    initial = {"date": date.today()}
    if beneficiary_id:
        initial["beneficiary"] = beneficiary_id
    form = DailyAssessmentForm(request.POST or None, initial=initial)
    form.fields["beneficiary"].queryset = Beneficiary.objects.filter(status="active")

    activities = _scoped_activities(request.user)
    clinics = _scoped_clinics(request.user)
    general_fields = list(_general_fields())

    if request.method == "POST" and form.is_valid():
        # مُجمِّع اليوم: يُنشأ مرة واحدة لكل مستفيد+تاريخ ويُشارَك بين المسؤولين
        assessment, created = DailyAssessment.objects.get_or_create(
            beneficiary=form.cleaned_data["beneficiary"],
            date=form.cleaned_data["date"],
            defaults={"assessed_by": request.user, "notes": form.cleaned_data.get("notes", "")},
        )
        if not created and form.cleaned_data.get("notes"):
            assessment.notes = form.cleaned_data["notes"]
            assessment.save()

        _save_activity_records(request, assessment, activities, general_fields, prune=False)
        _save_clinic_records(request, assessment, clinics, prune=False)

        rehab_index, _ = RehabilitationIndex.objects.get_or_create(assessment=assessment)
        rehab_index.calculate()

        messages.success(request, f"تم حفظ التقييم - مؤشر التأهيل: {rehab_index.total_score}%")
        return redirect("assessments:detail", pk=assessment.pk)

    return render(request, "assessments/assessment_form.html", {
        "form": form, "activities": activities, "clinics": clinics,
        "general_fields": general_fields, "title": "تقييم يومي جديد",
    })


@require_perm("assessments", "edit")
def assessment_edit(request, pk):
    assessment = get_object_or_404(DailyAssessment, pk=pk)
    form = DailyAssessmentForm(request.POST or None, instance=assessment)
    form.fields["beneficiary"].queryset = Beneficiary.objects.filter(
        Q(status="active") | Q(pk=assessment.beneficiary_id)
    )

    activities = _scoped_activities(request.user)
    clinics = _scoped_clinics(request.user)
    general_fields = list(_general_fields())

    # عبّئ بيانات السجلات الموجودة (ضمن نطاق المستخدم فقط)
    accessible_activity_ids = set(activities.values_list("pk", flat=True))
    accessible_clinic_ids = set(clinics.values_list("pk", flat=True))

    existing_activity_data = {}
    for rec in assessment.activity_records.all():
        if rec.activity_id not in accessible_activity_ids:
            continue
        data = dict(rec.data or {})
        for gk, gv in (rec.general_data or {}).items():
            data["__g_" + gk] = gv
        data["__notes__"] = rec.notes or ""
        existing_activity_data[rec.activity_id] = data

    existing_clinic_data = {}
    for rec in assessment.clinic_records.all():
        if rec.clinic_id not in accessible_clinic_ids:
            continue
        data = dict(rec.data or {})
        data["__notes__"] = rec.notes or ""
        existing_clinic_data[rec.clinic_id] = data

    if request.method == "POST" and form.is_valid():
        form.save()

        _save_activity_records(request, assessment, activities, general_fields)
        _save_clinic_records(request, assessment, clinics)

        rehab_index, _ = RehabilitationIndex.objects.get_or_create(assessment=assessment)
        rehab_index.calculate()

        messages.success(request, "تم تحديث التقييم")
        return redirect("assessments:detail", pk=assessment.pk)

    return render(request, "assessments/assessment_form.html", {
        "form": form, "activities": activities, "clinics": clinics,
        "general_fields": general_fields, "title": "تعديل التقييم", "editing": True,
        "existing_activity_data": json.dumps({str(k): v for k, v in existing_activity_data.items()}),
        "existing_clinic_data": json.dumps({str(k): v for k, v in existing_clinic_data.items()}),
    })


@require_perm("assessments", "view")
def assessment_detail(request, pk):
    assessment = get_object_or_404(
        DailyAssessment.objects.select_related("beneficiary", "assessed_by", "rehab_index"),
        pk=pk
    )
    activity_records = list(
        assessment.activity_records.select_related("activity__center", "recorded_by").prefetch_related("activity__fields").all()
    )
    clinic_records = list(
        assessment.clinic_records.select_related("clinic__center", "recorded_by").prefetch_related("clinic__fields").all()
    )

    general_labels = {f.field_key: f.name for f in GeneralField.objects.all()}

    for rec in activity_records:
        labels = {f.field_key: f.name for f in rec.activity.fields.all()}
        rec.detail_items = [
            {"label": labels.get(k, k), "value": v}
            for k, v in (rec.data or {}).items()
        ]
        rec.general_items = [
            {"label": general_labels.get(k, k), "value": v}
            for k, v in (rec.general_data or {}).items()
        ]
    for rec in clinic_records:
        field_map = {f.field_key: f for f in rec.clinic.fields.all()}
        items = []
        for k, v in (rec.data or {}).items():
            f = field_map.get(k)
            label = f.name if f else k
            unit = f.unit if f and f.unit else ""
            items.append({"label": label, "value": v, "unit": unit})
        rec.detail_items = items

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


def _general_score(request, prefix, general_fields):
    """يحسب درجة الحالة العامة (0-100) من الحقول العامة المُدخلة، ويعيد (data, score, has)."""
    data = {}
    total = 0.0
    total_max = 0.0
    has = False
    for field in general_fields:
        value = request.POST.get(prefix + "__g_" + field.field_key, "").strip()
        if value:
            has = True
            data[field.field_key] = value
            if field.counts_in_score and field.field_type in ("rating", "rating10", "number", "boolean"):
                try:
                    val = float(value)
                    total += val
                    total_max += float(field.max_score) if field.max_score else (
                        10.0 if field.field_type == "rating10" else (1.0 if field.field_type == "boolean" else 5.0)
                    )
                except (ValueError, TypeError):
                    pass
    score = round(min(total / total_max * 100, 100.0), 2) if total_max > 0 else 0.0
    return data, score, has


def _save_activity_records(request, assessment, activities, general_fields, prune=True):
    for activity in activities:
        prefix = f"activity_{activity.pk}_"
        data = {}
        total_score = 0.0
        total_max = 0.0
        has_data = False

        for field in activity.fields.all():
            value = request.POST.get(prefix + field.field_key, "").strip()
            if value:
                has_data = True
                data[field.field_key] = value
                if field.field_type in ("rating", "rating10", "number"):
                    try:
                        total_score += float(value)
                        total_max += float(field.max_score)
                    except (ValueError, TypeError):
                        pass

        general_data, behavioral, has_general = _general_score(request, prefix, general_fields)
        notes = request.POST.get(prefix + "notes", "").strip()
        if not (has_data or has_general or notes):
            # في وضع التعديل (النموذج مُعبّأ مسبقاً) احذف السجل إن أفرغه المستخدم
            if prune:
                assessment.activity_records.filter(activity=activity).delete()
            continue

        score_pct = round(total_score / total_max * 100, 2) if total_max > 0 else 0.0
        score_pct = min(score_pct, 100.0)
        ActivityRecord.objects.update_or_create(
            assessment=assessment, activity=activity,
            defaults={
                "data": data, "general_data": general_data,
                "score": score_pct, "max_score": 100, "behavioral_score": behavioral,
                "notes": notes, "recorded_by": request.user,
            },
        )


def _save_clinic_records(request, assessment, clinics, prune=True):
    for clinic in clinics:
        prefix = f"clinic_{clinic.pk}_"
        data = {}
        has_data = False
        total_score = 0.0
        total_max = 0.0

        for field in clinic.fields.all():
            value = request.POST.get(prefix + field.field_key, "").strip()
            if value:
                has_data = True
                data[field.field_key] = value
                if field.field_type in ("rating", "rating10", "number"):
                    try:
                        val = float(value)
                        if field.normal_min is not None and field.normal_max is not None:
                            if field.normal_min <= val <= field.normal_max:
                                total_score += 1.0
                            total_max += 1.0
                        else:
                            total_score += val
                            total_max += 5.0 if field.field_type == "rating" else (10.0 if field.field_type == "rating10" else 100.0)
                    except (ValueError, TypeError):
                        pass

        notes = request.POST.get(prefix + "notes", "").strip()
        if has_data or notes:
            score_pct = round(total_score / total_max * 100, 2) if total_max > 0 else 50.0
            score_pct = min(score_pct, 100.0)
            ClinicRecord.objects.update_or_create(
                assessment=assessment, clinic=clinic,
                defaults={
                    "data": data, "score": score_pct, "max_score": 100,
                    "notes": notes, "recorded_by": request.user,
                },
            )
        elif prune:
            assessment.clinic_records.filter(clinic=clinic).delete()
