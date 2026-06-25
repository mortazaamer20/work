from django.db import models
from django.conf import settings


class DailyAssessment(models.Model):
    """مُجمِّع التقييم اليومي لمستفيد واحد في يوم واحد.

    يُنشأ تلقائياً عند أول إدخال لأي نشاط، ويُجمِّع سجلات الأنشطة والعيادات
    التي يدخلها مسؤولو الأنشطة كلٌّ على حدة. الحالة العامة (الحضور/المزاج/...)
    صارت تُسجَّل لكل نشاط داخل ActivityRecord.
    """
    beneficiary = models.ForeignKey(
        "beneficiaries.Beneficiary", on_delete=models.CASCADE,
        verbose_name="المستفيد", related_name="daily_assessments"
    )
    date = models.DateField("التاريخ")
    notes = models.TextField("ملاحظات عامة", blank=True)

    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name="أنشأه", related_name="daily_assessments"
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
        """متوسط درجات الحالة العامة عبر كل سجلات الأنشطة لهذا اليوم."""
        vals = [r.behavioral_score for r in self.activity_records.all() if r.behavioral_score is not None]
        return round(sum(vals) / len(vals), 2) if vals else 0.0


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
    general_data = models.JSONField("بيانات الحالة العامة", default=dict, blank=True)
    score = models.FloatField("الدرجة", default=0)
    max_score = models.FloatField("الدرجة القصوى", default=100)
    behavioral_score = models.FloatField("درجة الحالة العامة", default=0)
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
            # الحالة العامة لكل جلسة تساهم في المحور السلوكي
            if rec.behavioral_score:
                axis_scores["behavioral"].append(min(float(rec.behavioral_score), 100.0))

        for rec in clinic_records:
            axis = rec.clinic.center.axis
            if axis in axis_scores:
                axis_scores[axis].append(min(rec.percentage, 100.0))

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
