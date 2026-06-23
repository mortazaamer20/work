from django.db import models
from django.conf import settings


class DailyAssessment(models.Model):
    ATTENDANCE_CHOICES = [
        ("on_time", "حاضر في الوقت"),
        ("late", "حاضر متأخر"),
        ("absent_excused", "غائب بعذر"),
        ("absent", "غائب"),
    ]
    MOOD_CHOICES = [
        ("stable", "مستقر"),
        ("anxious", "قلق"),
        ("withdrawn", "منطوٍ"),
        ("sad", "حزين ومنطوٍ"),
        ("verbal_aggression", "عدواني لفظياً"),
        ("physical_aggression", "عدواني جسدياً"),
        ("agitated", "قلق ومتوتر"),
    ]
    APPEARANCE_CHOICES = [
        ("excellent", "ملتزم بالزي الموحد ونظيف بالكامل"),
        ("good", "ملتزم أو تبدو عليه علامات إهمال"),
        ("poor", "غير ملتزم بالنظافة الشخصية"),
    ]
    INTERACTION_CHOICES = [
        (1, "رافض المشاركة"),
        (2, "قليل الانسجام ويحرّك الفوضى"),
        (3, "مشارك ومتوسط الأداء"),
        (4, "مبادر ونشيط وساعد زملاءه"),
        (5, "قائد نشيط يساعد زملاءه"),
    ]

    beneficiary = models.ForeignKey(
        "beneficiaries.Beneficiary", on_delete=models.CASCADE,
        verbose_name="المستفيد", related_name="daily_assessments"
    )
    date = models.DateField("التاريخ")
    attendance = models.CharField("الحضور", max_length=20, choices=ATTENDANCE_CHOICES)
    interaction_level = models.PositiveSmallIntegerField("مستوى التفاعل والمشاركة", choices=INTERACTION_CHOICES)
    mood = models.CharField("الحالة المزاجية", max_length=30, choices=MOOD_CHOICES)
    appearance = models.CharField("المظهر والنظافة", max_length=20, choices=APPEARANCE_CHOICES)
    notes = models.TextField("ملاحظات عامة", blank=True)

    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name="المقيّم", related_name="daily_assessments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تقييم يومي"
        verbose_name_plural = "التقييمات اليومية"
        unique_together = ("beneficiary", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.beneficiary} - {self.date}"

    @property
    def behavioral_score(self):
        score = Decimal("0")
        if self.attendance in ("on_time",):
            score += Decimal("30")
        elif self.attendance == "late":
            score += Decimal("15")
        score += Decimal(str(self.interaction_level)) * Decimal("8")
        if self.mood == "stable":
            score += Decimal("20")
        elif self.mood in ("anxious", "sad", "withdrawn"):
            score += Decimal("10")
        if self.appearance == "excellent":
            score += Decimal("10")
        elif self.appearance == "good":
            score += Decimal("5")
        return min(score, Decimal("100"))


class ActivityRecord(models.Model):
    assessment = models.ForeignKey(
        DailyAssessment, on_delete=models.CASCADE,
        verbose_name="التقييم اليومي", related_name="activity_records"
    )
    activity = models.ForeignKey(
        "centers.Activity", on_delete=models.CASCADE,
        verbose_name="النشاط", related_name="records"
    )
    data = models.JSONField("البيانات", default=dict)
    score = models.FloatField("الدرجة", default=0)
    max_score = models.FloatField("الدرجة القصوى", default=100)
    notes = models.TextField("ملاحظات", blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name="المسجّل"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل نشاط"
        verbose_name_plural = "سجلات الأنشطة"
        unique_together = ("assessment", "activity")

    def __str__(self):
        return f"{self.assessment.beneficiary} - {self.activity.name} - {self.assessment.date}"

    @property
    def percentage(self):
        if not self.max_score:
            return 0.0
        try:
            return min((self.score / self.max_score) * 100, 100.0)
        except Exception:
            return 0.0


class ClinicRecord(models.Model):
    assessment = models.ForeignKey(
        DailyAssessment, on_delete=models.CASCADE,
        verbose_name="التقييم اليومي", related_name="clinic_records"
    )
    clinic = models.ForeignKey(
        "centers.Clinic", on_delete=models.CASCADE,
        verbose_name="العيادة", related_name="records"
    )
    data = models.JSONField("البيانات", default=dict)
    score = models.FloatField("الدرجة", default=0)
    max_score = models.FloatField("الدرجة القصوى", default=100)
    notes = models.TextField("ملاحظات", blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name="المسجّل"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل عيادة"
        verbose_name_plural = "سجلات العيادات"
        unique_together = ("assessment", "clinic")

    def __str__(self):
        return f"{self.assessment.beneficiary} - {self.clinic.name} - {self.assessment.date}"

    @property
    def percentage(self):
        if not self.max_score:
            return 0.0
        try:
            return min((self.score / self.max_score) * 100, 100.0)
        except Exception:
            return 0.0


class RehabilitationIndex(models.Model):
    STATUS_CHOICES = [
        ("progressing", "تقدّم مستقر"),
        ("stable", "ثابت"),
        ("regressing", "تراجع يحتاج تدخّل"),
    ]

    assessment = models.OneToOneField(
        DailyAssessment, on_delete=models.CASCADE,
        verbose_name="التقييم اليومي", related_name="rehab_index"
    )
    medical_psychological_score = models.FloatField("الطبي والنفسي", default=0)
    behavioral_score = models.FloatField("السلوكي والانضباطي", default=0)
    skill_technical_score = models.FloatField("المهاري والتقني", default=0)
    social_spiritual_score = models.FloatField("الاجتماعي والروحي", default=0)

    medical_weight = models.FloatField("وزن الطبي", default=40)
    behavioral_weight = models.FloatField("وزن السلوكي", default=20)
    skill_weight = models.FloatField("وزن المهاري", default=20)
    social_weight = models.FloatField("وزن الاجتماعي", default=20)

    total_score = models.FloatField("المؤشر الكلي", default=0)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default="stable")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مؤشر التأهيل"
        verbose_name_plural = "مؤشرات التأهيل"

    def __str__(self):
        return f"{self.assessment.beneficiary} - {self.assessment.date} - {self.total_score}%"

    def calculate(self):
        behavioral_base = self.assessment.behavioral_score

        activity_records = self.assessment.activity_records.all()
        clinic_records = self.assessment.clinic_records.all()

        axis_scores = {
            "medical_psychological": [],
            "behavioral": [],
            "skill_technical": [],
            "social_spiritual": [],
        }

        for rec in activity_records:
            axis = rec.activity.center.axis
            if axis in axis_scores:
                axis_scores[axis].append(min(rec.percentage, 100.0))

        for rec in clinic_records:
            axis = rec.clinic.center.axis
            if axis in axis_scores:
                axis_scores[axis].append(min(rec.percentage, 100.0))

        axis_scores["behavioral"].append(float(behavioral_base))

        def avg(lst):
            return sum(lst) / len(lst) if lst else 0.0

        self.medical_psychological_score = round(avg(axis_scores["medical_psychological"]), 2)
        self.skill_technical_score = round(avg(axis_scores["skill_technical"]), 2)
        self.social_spiritual_score = round(avg(axis_scores["social_spiritual"]), 2)
        self.behavioral_score = round(avg(axis_scores["behavioral"]), 2)

        total = (
            self.medical_psychological_score * self.medical_weight / 100 +
            self.behavioral_score * self.behavioral_weight / 100 +
            self.skill_technical_score * self.skill_weight / 100 +
            self.social_spiritual_score * self.social_weight / 100
        )
        self.total_score = round(total, 2)

        if self.total_score >= 60:
            self.status = "progressing"
        elif self.total_score >= 40:
            self.status = "stable"
        else:
            self.status = "regressing"

        self.save()
