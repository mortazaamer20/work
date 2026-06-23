from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import inlineformset_factory

from accounts.views import require_perm
from .models import Center, Activity, ActivityField, Clinic, ClinicField
from .forms import CenterForm, ActivityForm, ActivityFieldForm, ClinicForm, ClinicFieldForm


@require_perm("centers", "view")
def center_list(request):
    centers = Center.objects.prefetch_related("activities", "clinics").all()
    return render(request, "centers/center_list.html", {"centers": centers})


@require_perm("centers", "add")
def center_create(request):
    form = CenterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء المركز بنجاح")
        return redirect("centers:list")
    return render(request, "centers/center_form.html", {"form": form, "title": "إضافة مركز"})


@require_perm("centers", "edit")
def center_edit(request, pk):
    center = get_object_or_404(Center, pk=pk)
    form = CenterForm(request.POST or None, instance=center)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث المركز")
        return redirect("centers:list")
    return render(request, "centers/center_form.html", {"form": form, "title": "تعديل مركز"})


@require_perm("centers", "delete")
def center_delete(request, pk):
    center = get_object_or_404(Center, pk=pk)
    if request.method == "POST":
        center.delete()
        messages.success(request, "تم حذف المركز")
        return redirect("centers:list")
    return render(request, "centers/center_confirm_delete.html", {"center": center})


@require_perm("activities", "view")
def activity_list(request, center_pk):
    center = get_object_or_404(Center, pk=center_pk)
    activities = center.activities.prefetch_related("fields").all()
    return render(request, "centers/activity_list.html", {"center": center, "activities": activities})


@require_perm("activities", "add")
def activity_create(request, center_pk):
    center = get_object_or_404(Center, pk=center_pk)
    FieldFormSet = inlineformset_factory(
        Activity, ActivityField, form=ActivityFieldForm, extra=3, can_delete=True
    )
    form = ActivityForm(request.POST or None, initial={"center": center})
    formset = FieldFormSet(request.POST or None, prefix="fields")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        activity = form.save()
        formset.instance = activity
        formset.save()
        messages.success(request, "تم إنشاء النشاط وحقوله")
        return redirect("centers:activity_list", center_pk=center.pk)
    form.fields["center"].initial = center
    return render(request, "centers/activity_edit.html", {
        "form": form, "formset": formset, "center": center, "activity": None, "title": "إضافة نشاط"
    })


@require_perm("activities", "edit")
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    FieldFormSet = inlineformset_factory(
        Activity, ActivityField, form=ActivityFieldForm, extra=1, can_delete=True
    )
    form = ActivityForm(request.POST or None, instance=activity)
    formset = FieldFormSet(request.POST or None, instance=activity, prefix="fields")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "تم تحديث النشاط وحقوله")
        return redirect("centers:activity_list", center_pk=activity.center.pk)
    return render(request, "centers/activity_edit.html", {
        "form": form, "formset": formset, "activity": activity, "center": activity.center, "title": "تعديل النشاط وحقوله"
    })


@require_perm("activities", "delete")
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    center_pk = activity.center.pk
    if request.method == "POST":
        activity.delete()
        messages.success(request, "تم حذف النشاط")
        return redirect("centers:activity_list", center_pk=center_pk)
    return render(request, "centers/activity_confirm_delete.html", {"activity": activity})


@require_perm("clinics", "view")
def clinic_list(request, center_pk):
    center = get_object_or_404(Center, pk=center_pk)
    clinics = center.clinics.prefetch_related("fields").all()
    return render(request, "centers/clinic_list.html", {"center": center, "clinics": clinics})


@require_perm("clinics", "add")
def clinic_create(request, center_pk):
    center = get_object_or_404(Center, pk=center_pk)
    FieldFormSet = inlineformset_factory(
        Clinic, ClinicField, form=ClinicFieldForm, extra=3, can_delete=True
    )
    form = ClinicForm(request.POST or None, initial={"center": center})
    formset = FieldFormSet(request.POST or None, prefix="fields")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        clinic = form.save()
        formset.instance = clinic
        formset.save()
        messages.success(request, "تم إنشاء العيادة وحقولها")
        return redirect("centers:clinic_list", center_pk=center.pk)
    form.fields["center"].initial = center
    return render(request, "centers/clinic_edit.html", {
        "form": form, "formset": formset, "center": center, "clinic": None, "title": "إضافة عيادة"
    })


@require_perm("clinics", "edit")
def clinic_edit(request, pk):
    clinic = get_object_or_404(Clinic, pk=pk)
    FieldFormSet = inlineformset_factory(
        Clinic, ClinicField, form=ClinicFieldForm, extra=1, can_delete=True
    )
    form = ClinicForm(request.POST or None, instance=clinic)
    formset = FieldFormSet(request.POST or None, instance=clinic, prefix="fields")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "تم تحديث العيادة وحقولها")
        return redirect("centers:clinic_list", center_pk=clinic.center.pk)
    return render(request, "centers/clinic_edit.html", {
        "form": form, "formset": formset, "clinic": clinic, "center": clinic.center, "title": "تعديل العيادة وحقولها"
    })


@require_perm("clinics", "delete")
def clinic_delete(request, pk):
    clinic = get_object_or_404(Clinic, pk=pk)
    center_pk = clinic.center.pk
    if request.method == "POST":
        clinic.delete()
        messages.success(request, "تم حذف العيادة")
        return redirect("centers:clinic_list", center_pk=center_pk)
    return render(request, "centers/clinic_confirm_delete.html", {"clinic": clinic})
