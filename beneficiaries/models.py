from django.db import models
from django.conf import settings


class Beneficiary(models.Model):
    GENDER_CHOICES = [
        ("male", "ذكر"),
        ("female", "أنثى"),
    ]
    STATUS_CHOICES = [
        ("active", "نشط"),
        ("discharged", "خرج"),
        ("suspended", "معلّق"),
        ("transferred", "محوّل"),
    ]

    ref_number = models.CharField("الرقم المرجعي", max_length=50, unique=True)
    full_name = models.CharField("الاسم الكامل", max_length=300)
    gender = models.CharField("الجنس", max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField("تاريخ الميلاد")
    national_id = models.CharField("رقم الهوية", max_length=50, blank=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    emergency_contact = models.CharField("جهة اتصال الطوارئ", max_length=200, blank=True)
    emergency_phone = models.CharField("هاتف الطوارئ", max_length=20, blank=True)
    address = models.TextField("العنوان", blank=True)

    admission_date = models.DateField("تاريخ الدخول")
    expected_discharge_date = models.DateField("تاريخ الخروج المتوقع", null=True, blank=True)
    actual_discharge_date = models.DateField("تاريخ الخروج الفعلي", null=True, blank=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default="active")
    admission_reason = models.TextField("سبب الدخول", blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    photo = models.ImageField("الصورة الشخصية", upload_to="beneficiaries/photos/", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name="أنشئ بواسطة", related_name="created_beneficiaries"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مستفيد"
        verbose_name_plural = "المستفيدون"
        ordering = ["-admission_date", "full_name"]

    def __str__(self):
        return f"{self.ref_number} - {self.full_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
