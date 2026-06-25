from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Permission(models.Model):
    RESOURCE_CHOICES = [
        ("beneficiaries", "المستفيدين"),
        ("assessments", "التقييمات اليومية"),
        ("centers", "المراكز"),
        ("activities", "الأنشطة"),
        ("clinics", "العيادات"),
        ("dashboard", "لوحة المؤشرات"),
        ("users", "المستخدمين"),
        ("roles", "الأدوار والصلاحيات"),
        ("reports", "التقارير"),
        ("settings", "الإعدادات"),
    ]
    ACTION_CHOICES = [
        ("view", "عرض"),
        ("add", "إضافة"),
        ("edit", "تعديل"),
        ("delete", "حذف"),
        ("export", "تصدير"),
    ]

    resource = models.CharField("المورد", max_length=50, choices=RESOURCE_CHOICES)
    action = models.CharField("الإجراء", max_length=20, choices=ACTION_CHOICES)
    description = models.CharField("الوصف", max_length=200, blank=True)

    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"
        unique_together = ("resource", "action")
        ordering = ["resource", "action"]

    def __str__(self):
        return f"{self.get_resource_display()} - {self.get_action_display()}"


class Role(models.Model):
    name = models.CharField("اسم الدور", max_length=100, unique=True)
    description = models.TextField("الوصف", blank=True)
    permissions = models.ManyToManyField(Permission, verbose_name="الصلاحيات", blank=True)
    centers = models.ManyToManyField(
        "centers.Center", verbose_name="المراكز المتاحة", blank=True,
    )
    is_system = models.BooleanField("دور نظام", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def has_perm(self, resource, action):
        return self.permissions.filter(resource=resource, action=action).exists()


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("اسم المستخدم مطلوب")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    full_name = models.CharField("الاسم الكامل", max_length=200)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="الدور", related_name="users"
    )
    assigned_centers = models.ManyToManyField(
        "centers.Center", verbose_name="المراكز المعيّنة", blank=True,
    )
    assigned_activities = models.ManyToManyField(
        "centers.Activity", verbose_name="الأنشطة المعيّنة", blank=True,
        help_text="عيّن أنشطة محددة لمسؤول النشاط؛ اتركها فارغة لمنح صلاحية المركز بالكامل"
    )
    is_active = models.BooleanField("نشط", default=True)

    objects = UserManager()

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.full_name or self.username

    def get_accessible_centers(self):
        if self.is_superuser:
            from centers.models import Center
            return Center.objects.all()
        user_centers = self.assigned_centers.all()
        if user_centers.exists():
            return user_centers
        if self.role:
            role_centers = self.role.centers.all()
            if role_centers.exists():
                return role_centers
        from centers.models import Center
        return Center.objects.none()

    def get_accessible_activities(self):
        """الأنشطة التي يحق للمستخدم إدخال/عرض بياناتها (هرمياً).

        - المدير العام (superuser): كل الأنشطة.
        - مسؤول نشاط (assigned_activities محددة): أنشطته فقط.
        - مسؤول مركز (assigned_centers / role.centers): كل أنشطة مراكزه.
        """
        from centers.models import Activity
        if self.is_superuser:
            return Activity.objects.filter(is_active=True)
        own = self.assigned_activities.filter(is_active=True)
        if own.exists():
            return own
        centers = self.get_accessible_centers()
        return Activity.objects.filter(center__in=centers, is_active=True)

    def get_accessible_clinics(self):
        """العيادات تتبع صلاحية المركز (لا تُسنَد فردياً)."""
        from centers.models import Clinic
        if self.is_superuser:
            return Clinic.objects.filter(is_active=True)
        # مسؤول النشاط المحدد بنشاط فقط لا يصل للعيادات
        if self.assigned_activities.exists():
            return Clinic.objects.none()
        centers = self.get_accessible_centers()
        return Clinic.objects.filter(center__in=centers, is_active=True)

    def has_resource_perm(self, resource, action):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.has_perm(resource, action)
