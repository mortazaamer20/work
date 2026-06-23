from django.db import models


class Center(models.Model):
    name = models.CharField("اسم المركز", max_length=200, unique=True)
    slug = models.SlugField("المعرّف", max_length=200, unique=True, allow_unicode=True)
    description = models.TextField("الوصف", blank=True)
    icon = models.CharField("الأيقونة", max_length=50, default="bi-building")
    color = models.CharField("اللون", max_length=7, default="#0d6efd")
    weight = models.DecimalField(
        "الوزن في مؤشر التأهيل", max_digits=5, decimal_places=2, default=0,
        help_text="النسبة المئوية لوزن هذا المركز في حساب مؤشر التأهيل اليومي"
    )
    axis = models.CharField("المحور", max_length=50, choices=[
        ("medical_psychological", "المحور الطبي والنفسي"),
        ("behavioral", "المحور السلوكي والانضباطي"),
        ("skill_technical", "المحور المهاري والتقني"),
        ("social_spiritual", "المحور الاجتماعي والروحي"),
    ], default="skill_technical")
    is_active = models.BooleanField("نشط", default=True)
    order = models.PositiveIntegerField("الترتيب", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مركز"
        verbose_name_plural = "المراكز"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Activity(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="المركز", related_name="activities")
    name = models.CharField("اسم النشاط", max_length=200)
    slug = models.SlugField("المعرّف", max_length=200, allow_unicode=True)
    description = models.TextField("الوصف", blank=True)
    is_active = models.BooleanField("نشط", default=True)
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "نشاط"
        verbose_name_plural = "الأنشطة"
        unique_together = ("center", "slug")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.center.name} - {self.name}"


class ActivityField(models.Model):
    FIELD_TYPES = [
        ("text", "نص"),
        ("number", "رقم"),
        ("rating", "تقييم (1-5)"),
        ("rating10", "تقييم (1-10)"),
        ("boolean", "نعم/لا"),
        ("choice", "اختيار"),
        ("date", "تاريخ"),
        ("time", "وقت"),
        ("textarea", "نص طويل"),
    ]

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="النشاط", related_name="fields")
    name = models.CharField("اسم الحقل", max_length=200)
    field_key = models.SlugField("مفتاح الحقل", max_length=200, allow_unicode=True)
    field_type = models.CharField("نوع الحقل", max_length=20, choices=FIELD_TYPES)
    choices_text = models.TextField("الخيارات", blank=True, help_text="خيار واحد في كل سطر (لنوع الاختيار)")
    is_required = models.BooleanField("مطلوب", default=True)
    max_score = models.DecimalField("الدرجة القصوى", max_digits=5, decimal_places=2, default=5)
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "حقل النشاط"
        verbose_name_plural = "حقول الأنشطة"
        unique_together = ("activity", "field_key")
        ordering = ["order"]

    def __str__(self):
        return f"{self.activity.name} - {self.name}"

    def get_choices_list(self):
        if not self.choices_text:
            return []
        return [c.strip() for c in self.choices_text.split("\n") if c.strip()]


class Clinic(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="المركز", related_name="clinics")
    name = models.CharField("اسم العيادة", max_length=200)
    slug = models.SlugField("المعرّف", max_length=200, allow_unicode=True)
    description = models.TextField("الوصف", blank=True)
    is_active = models.BooleanField("نشط", default=True)
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "عيادة"
        verbose_name_plural = "العيادات"
        unique_together = ("center", "slug")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.center.name} - {self.name}"


class ClinicField(models.Model):
    FIELD_TYPES = ActivityField.FIELD_TYPES

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, verbose_name="العيادة", related_name="fields")
    name = models.CharField("اسم الحقل", max_length=200)
    field_key = models.SlugField("مفتاح الحقل", max_length=200, allow_unicode=True)
    field_type = models.CharField("نوع الحقل", max_length=20, choices=FIELD_TYPES)
    choices_text = models.TextField("الخيارات", blank=True, help_text="خيار واحد في كل سطر")
    is_required = models.BooleanField("مطلوب", default=True)
    unit = models.CharField("الوحدة", max_length=50, blank=True, help_text="مثل: ملم زئبق، كغم، °م")
    normal_min = models.DecimalField("الحد الأدنى الطبيعي", max_digits=10, decimal_places=2, null=True, blank=True)
    normal_max = models.DecimalField("الحد الأعلى الطبيعي", max_digits=10, decimal_places=2, null=True, blank=True)
    order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "حقل العيادة"
        verbose_name_plural = "حقول العيادات"
        unique_together = ("clinic", "field_key")
        ordering = ["order"]

    def __str__(self):
        return f"{self.clinic.name} - {self.name}"

    def get_choices_list(self):
        if not self.choices_text:
            return []
        return [c.strip() for c in self.choices_text.split("\n") if c.strip()]
