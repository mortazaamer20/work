from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.views import require_perm
from .models import Beneficiary
from .forms import BeneficiaryForm


@require_perm("beneficiaries", "view")
def beneficiary_list(request):
    qs = Beneficiary.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(ref_number__icontains=q))
    if status:
        qs = qs.filter(status=status)
    template = "beneficiaries/beneficiary_list_partial.html" if request.htmx else "beneficiaries/beneficiary_list.html"
    return render(request, template, {"beneficiaries": qs, "q": q, "status": status})


@require_perm("beneficiaries", "view")
def beneficiary_detail(request, pk):
    b = get_object_or_404(Beneficiary, pk=pk)
    assessments = b.daily_assessments.select_related("rehab_index").order_by("-date")[:30]
    return render(request, "beneficiaries/beneficiary_detail.html", {"b": b, "assessments": assessments})


@require_perm("beneficiaries", "add")
def beneficiary_create(request):
    form = BeneficiaryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        b = form.save(commit=False)
        b.created_by = request.user
        b.save()
        messages.success(request, "تم إضافة المستفيد بنجاح")
        return redirect("beneficiaries:detail", pk=b.pk)
    return render(request, "beneficiaries/beneficiary_form.html", {"form": form, "title": "إضافة مستفيد"})


@require_perm("beneficiaries", "edit")
def beneficiary_edit(request, pk):
    b = get_object_or_404(Beneficiary, pk=pk)
    form = BeneficiaryForm(request.POST or None, request.FILES or None, instance=b)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث بيانات المستفيد")
        return redirect("beneficiaries:detail", pk=b.pk)
    return render(request, "beneficiaries/beneficiary_form.html", {"form": form, "title": "تعديل مستفيد", "b": b})


@require_perm("beneficiaries", "delete")
def beneficiary_delete(request, pk):
    b = get_object_or_404(Beneficiary, pk=pk)
    if request.method == "POST":
        b.delete()
        messages.success(request, "تم حذف المستفيد")
        return redirect("beneficiaries:list")
    return render(request, "beneficiaries/beneficiary_confirm_delete.html", {"b": b})
