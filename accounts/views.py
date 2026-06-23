from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps

from .models import User, Role, Permission
from .forms import LoginForm, UserForm, RoleForm


def require_perm(resource, action):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.has_resource_perm(resource, action):
                return render(request, "components/forbidden.html", status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next", "/"))
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@require_perm("users", "view")
def user_list(request):
    users = User.objects.select_related("role").all()
    return render(request, "accounts/user_list.html", {"users": users})


@require_perm("users", "add")
def user_create(request):
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_password("changeme123")
        user.save()
        form.save_m2m()
        messages.success(request, "تم إنشاء المستخدم بنجاح")
        if request.htmx:
            return render(request, "components/success_redirect.html", {"url": "/accounts/users/"})
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "إضافة مستخدم"})


@require_perm("users", "edit")
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث المستخدم بنجاح")
        if request.htmx:
            return render(request, "components/success_redirect.html", {"url": "/accounts/users/"})
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "تعديل مستخدم", "editing": True})


@require_perm("users", "delete")
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user == request.user:
            messages.error(request, "لا يمكنك حذف حسابك")
        elif user.is_superuser:
            messages.error(request, "لا يمكن حذف مدير النظام")
        else:
            user.delete()
            messages.success(request, "تم حذف المستخدم")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_confirm_delete.html", {"user_obj": user})


@require_perm("roles", "view")
def role_list(request):
    roles = Role.objects.prefetch_related("permissions", "users").all()
    return render(request, "accounts/role_list.html", {"roles": roles})


@require_perm("roles", "add")
def role_create(request):
    form = RoleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء الدور بنجاح")
        return redirect("accounts:role_list")
    permissions_grouped = {}
    for p in Permission.objects.all():
        group = p.get_resource_display()
        permissions_grouped.setdefault(group, []).append(p)
    return render(request, "accounts/role_form.html", {
        "form": form, "title": "إضافة دور", "permissions_grouped": permissions_grouped
    })


@require_perm("roles", "edit")
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث الدور بنجاح")
        return redirect("accounts:role_list")
    permissions_grouped = {}
    for p in Permission.objects.all():
        group = p.get_resource_display()
        permissions_grouped.setdefault(group, []).append(p)
    return render(request, "accounts/role_form.html", {
        "form": form, "title": "تعديل دور", "permissions_grouped": permissions_grouped, "editing": True
    })


@require_perm("roles", "delete")
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == "POST":
        if role.is_system:
            messages.error(request, "لا يمكن حذف دور النظام")
        else:
            role.delete()
            messages.success(request, "تم حذف الدور")
        return redirect("accounts:role_list")
    return render(request, "accounts/role_confirm_delete.html", {"role": role})
