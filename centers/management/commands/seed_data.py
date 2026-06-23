from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Permission, Role, User
from centers.models import Center, Activity, ActivityField, Clinic, ClinicField


class Command(BaseCommand):
    help = "تحميل البيانات الأولية للمراكز والأنشطة والعيادات والصلاحيات"

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_permissions()
        self._create_centers()
        self._create_default_roles()
        self._create_admin()
        self.stdout.write(self.style.SUCCESS("تم تحميل البيانات بنجاح!"))

    def _create_permissions(self):
        for resource, _ in Permission.RESOURCE_CHOICES:
            for action, _ in Permission.ACTION_CHOICES:
                Permission.objects.get_or_create(
                    resource=resource, action=action,
                    defaults={"description": ""}
                )
        self.stdout.write(f"  الصلاحيات: {Permission.objects.count()}")

    def _create_centers(self):
        centers_data = [
            {
                "name": "المركز الحرفي", "slug": "craft", "icon": "bi-tools",
                "color": "#b45309", "axis": "skill_technical", "weight": 5, "order": 1,
                "activities": [
                    {"name": "النجارة", "slug": "carpentry", "fields": [
                        {"name": "استخدام المنشار اليدوي والكهربائي", "field_key": "saw_usage", "field_type": "rating", "max_score": 5},
                        {"name": "دقة قياسات الخشب وقصّه", "field_key": "measurement_accuracy", "field_type": "rating", "max_score": 5},
                        {"name": "القدرة على تجميع الأجزاء", "field_key": "assembly", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "النقش", "slug": "engraving", "fields": [
                        {"name": "مستوى التحكم بأدوات الحفر", "field_key": "tool_control", "field_type": "rating", "max_score": 5},
                        {"name": "الدقة على السطح الخشبية أو الجبسية", "field_key": "precision", "field_type": "rating", "max_score": 5},
                        {"name": "الصبر أثناء التفاصيل الصغيرة", "field_key": "patience", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الخياطة", "slug": "sewing", "fields": [
                        {"name": "لحم الإبرة واستخدام ماكينة الخياطة", "field_key": "needle_sewing", "field_type": "rating", "max_score": 5},
                        {"name": "قص القماش بناءً على المقاسات", "field_key": "fabric_cutting", "field_type": "rating", "max_score": 5},
                        {"name": "جودة الخيوط وتناسقها", "field_key": "thread_quality", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الأعمال اليدوية (التدوير)", "slug": "handicraft", "fields": [
                        {"name": "القدرة على إعادة تدوير الخامات", "field_key": "recycling", "field_type": "rating", "max_score": 5},
                        {"name": "استخدام الصمغ والأدوات البسيطة", "field_key": "basic_tools", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "البستنة", "slug": "gardening", "fields": [
                        {"name": "الالتزام بمواعيد ري النباتات", "field_key": "watering_schedule", "field_type": "rating", "max_score": 5},
                        {"name": "القدرة على تقليم الأشجار", "field_key": "pruning", "field_type": "rating", "max_score": 5},
                        {"name": "التعامل مع النباتات المتضررة", "field_key": "damaged_plants", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "النحت (تشكيل)", "slug": "sculpture", "fields": [
                        {"name": "مستوى تشكيل الطين والجبس", "field_key": "clay_molding", "field_type": "rating", "max_score": 5},
                        {"name": "تحديد الأبعاد الثلاثية", "field_key": "3d_dimensions", "field_type": "rating", "max_score": 5},
                        {"name": "التحكم بقوة الضغط باليدين", "field_key": "pressure_control", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "المركز الرياضي", "slug": "sports", "icon": "bi-trophy",
                "color": "#059669", "axis": "social_spiritual", "weight": 5, "order": 2,
                "activities": [
                    {"name": "الجيم (Gym)", "slug": "gym", "fields": [
                        {"name": "الأوزان المستطاع رفعها", "field_key": "weights", "field_type": "number", "max_score": 100},
                        {"name": "عدد المجموعات والتكرارات", "field_key": "sets_reps", "field_type": "text", "max_score": 5},
                        {"name": "الالتزام بالمزج بين التمارين", "field_key": "exercise_mix", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "السباحة", "slug": "swimming", "fields": [
                        {"name": "المسافة المقطوعة بالأمتار", "field_key": "distance", "field_type": "number", "max_score": 100},
                        {"name": "القدرة على السباحة تحت الماء", "field_key": "underwater", "field_type": "rating", "max_score": 5},
                        {"name": "إتقان حركات التنفس", "field_key": "breathing", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الركض", "slug": "running", "fields": [
                        {"name": "المسافة المقطوعة بالكيلومترات", "field_key": "distance_km", "field_type": "number", "max_score": 10},
                        {"name": "الوقت المستغرق لقطع المسافة", "field_key": "time", "field_type": "text", "max_score": 5},
                        {"name": "معدل ضربات القلب بعد الركض", "field_key": "heart_rate", "field_type": "number", "max_score": 200},
                    ]},
                    {"name": "المصارعة", "slug": "wrestling", "fields": [
                        {"name": "الالتزام بقواعد اللعبة", "field_key": "rules", "field_type": "rating", "max_score": 5},
                        {"name": "القدرة على تطبيق حركات الدفاع", "field_key": "defense", "field_type": "rating", "max_score": 5},
                        {"name": "تقبل الهزيمة أو الخسارة", "field_key": "sportsmanship", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "كرة القدم", "slug": "football", "fields": [
                        {"name": "مستوى اللياقة البدنية", "field_key": "fitness", "field_type": "rating", "max_score": 5},
                        {"name": "دقة التمرير والتسديد", "field_key": "passing_accuracy", "field_type": "rating", "max_score": 5},
                        {"name": "الالتزام باللعب الجماعي", "field_key": "teamwork", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "المركز الثقافي", "slug": "cultural", "icon": "bi-book",
                "color": "#7c3aed", "axis": "social_spiritual", "weight": 5, "order": 3,
                "activities": [
                    {"name": "المسرح", "slug": "theater", "fields": [
                        {"name": "حفظ النص المسرحي", "field_key": "memorization", "field_type": "rating", "max_score": 5},
                        {"name": "التعبير الجسدي والنفعل", "field_key": "expression", "field_type": "rating", "max_score": 5},
                        {"name": "الشجاعة في مواجهة الجمهور", "field_key": "courage", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "القرآن", "slug": "quran", "fields": [
                        {"name": "السور والآيات المحفوظة اليوم", "field_key": "memorized_today", "field_type": "text", "max_score": 5},
                        {"name": "عدد الأخطاء في التلاوة والتجويد", "field_key": "error_count", "field_type": "number", "max_score": 10},
                        {"name": "الالتزام بالحضور في حلقة الحفظ", "field_key": "attendance", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "محو الأمية", "slug": "literacy", "fields": [
                        {"name": "الحروف أو الكلمات الجديدة المتعلّمة", "field_key": "new_words", "field_type": "text", "max_score": 5},
                        {"name": "مستوى الأداء في الاختبارات المبسّطة", "field_key": "test_score", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "المكتبة", "slug": "library", "fields": [
                        {"name": "اسم الكتاب أو الرواية", "field_key": "book_name", "field_type": "text", "max_score": 5},
                        {"name": "عدد الصفحات المقروءة", "field_key": "pages_read", "field_type": "number", "max_score": 100},
                        {"name": "القدرة على تلخيص الأفكار", "field_key": "summarizing", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "العلاج الروحي (12 خطوة)", "slug": "spiritual-therapy", "fields": [
                        {"name": "الالتزام بأوقات الصلوات والعبادات", "field_key": "prayer_commitment", "field_type": "rating", "max_score": 5},
                        {"name": "مستوى الخشوع والاستغراق", "field_key": "devotion", "field_type": "rating", "max_score": 5},
                        {"name": "التخلص من الأفكار المدمّرة", "field_key": "harmful_thoughts", "field_type": "rating", "max_score": 5},
                        {"name": "معرفة الخطوات الـ 12", "field_key": "12_steps_knowledge", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "المركز الصحي", "slug": "health", "icon": "bi-heart-pulse",
                "color": "#dc2626", "axis": "medical_psychological", "weight": 40, "order": 4,
                "clinics": [
                    {"name": "عيادة نزع السموم (Detox)", "slug": "detox", "fields": [
                        {"name": "تاريخ فحص السموم الدموي", "field_key": "test_date", "field_type": "date"},
                        {"name": "نتيجة الفحص", "field_key": "test_result", "field_type": "choice",
                         "choices_text": "إيجابي\nسلبي"},
                        {"name": "تركيز المواد في الجسم", "field_key": "concentration", "field_type": "text"},
                    ]},
                    {"name": "عيادة الصحة الجسمية", "slug": "physical-health", "fields": [
                        {"name": "ضغط الدم", "field_key": "blood_pressure", "field_type": "text", "unit": "ملم زئبق"},
                        {"name": "درجة حرارة الجسم", "field_key": "temperature", "field_type": "number", "unit": "°م", "normal_min": 36, "normal_max": 37.5},
                        {"name": "معدل السكر", "field_key": "blood_sugar", "field_type": "number", "unit": "ملغ/دل", "normal_min": 70, "normal_max": 140},
                        {"name": "الوزن الكلي", "field_key": "weight", "field_type": "number", "unit": "كغم"},
                        {"name": "وجود آلام جسدية أو شكاوى", "field_key": "complaints", "field_type": "textarea"},
                    ]},
                    {"name": "عيادة صحة الأسنان", "slug": "dental", "fields": [
                        {"name": "حالة نظافة الفم", "field_key": "oral_hygiene", "field_type": "choice",
                         "choices_text": "ممتازة\nجيدة\nضعيفة"},
                        {"name": "اكتمال خطة علاج الأسنان", "field_key": "treatment_progress", "field_type": "rating", "max_score": 5},
                        {"name": "الالتزام بتعليمات غسل الأسنان", "field_key": "brushing_compliance", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الصحة النفسية", "slug": "mental-health", "fields": [
                        {"name": "الأعراض الانسحابية (القلق، الرعشة)", "field_key": "withdrawal_symptoms", "field_type": "choice",
                         "choices_text": "لا يوجد\nخفيفة\nمتوسطة\nشديدة"},
                        {"name": "مستوى تقييم الاكتئاب والقلق", "field_key": "depression_anxiety", "field_type": "rating", "max_score": 5},
                        {"name": "مستوى الرغبة بالمرض والتعاطي (Craving)", "field_key": "craving_level", "field_type": "rating", "max_score": 5},
                        {"name": "مدى مقاومة الرغبة الشخصية", "field_key": "craving_resistance", "field_type": "rating", "max_score": 5},
                        {"name": "مستوى التبصر بالمرض", "field_key": "insight", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "المركز الرقمي", "slug": "digital", "icon": "bi-cpu",
                "color": "#2563eb", "axis": "skill_technical", "weight": 5, "order": 5,
                "activities": [
                    {"name": "تمارين التركيز والانتباه", "slug": "focus", "fields": [
                        {"name": "مدة الاستمرارية في أداء المهمة (دقيقة)", "field_key": "focus_duration", "field_type": "number", "max_score": 60},
                        {"name": "مستوى الذاكرة المركّبة أثناء اللعبة", "field_key": "memory_level", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "تمارين التخطيط", "slug": "planning", "fields": [
                        {"name": "مرات الحل الصحيح للمشكلات الرقمية", "field_key": "correct_solutions", "field_type": "number", "max_score": 10},
                        {"name": "الوقت المستهلك للوصول للحل الصحيح", "field_key": "solution_time", "field_type": "text"},
                    ]},
                    {"name": "تمارين سرعة الاستجابة", "slug": "reaction-time", "fields": [
                        {"name": "زمن الفعل بالثانية", "field_key": "reaction_ms", "field_type": "number", "max_score": 1000},
                        {"name": "دقة الإجابة", "field_key": "accuracy", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "تمارين الإدراك المعرفي", "slug": "cognition", "fields": [
                        {"name": "نسبة النجاح في رصد العناصر", "field_key": "success_rate", "field_type": "number", "max_score": 100},
                        {"name": "التركيز في المنتصف", "field_key": "central_focus", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "الخدمة الاجتماعية", "slug": "social-service", "icon": "bi-people",
                "color": "#0891b2", "axis": "social_spiritual", "weight": 5, "order": 6,
                "activities": [
                    {"name": "صحة الطفل", "slug": "child-health", "fields": [
                        {"name": "مستوى وعي المستفيد باحتياجاتهم", "field_key": "awareness", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "صحة الأسرة", "slug": "family-health", "fields": [
                        {"name": "مدى تحسّن لغة الحوار مع الزوجة/الوالدين", "field_key": "dialogue", "field_type": "rating", "max_score": 5},
                        {"name": "تخفيف حدة الخلافات العائلية", "field_key": "conflict_reduction", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "التحصين السلوكي", "slug": "behavioral-immunization", "fields": [
                        {"name": "قدرة المستفيد على تحديد المحفّزات", "field_key": "trigger_identification", "field_type": "rating", "max_score": 5},
                        {"name": "وضوح خطط عملية لتجنّبها", "field_key": "avoidance_plans", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "التثقيف الاجتماعي", "slug": "social-education", "fields": [
                        {"name": "استيعاب المستفيد للقوانين", "field_key": "legal_awareness", "field_type": "rating", "max_score": 5},
                        {"name": "بناء علاقات صداقة صحية", "field_key": "healthy_friendships", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
            {
                "name": "مركز الإعلام", "slug": "media", "icon": "bi-camera-reels",
                "color": "#ec4899", "axis": "skill_technical", "weight": 5, "order": 7,
                "activities": [
                    {"name": "التصوير", "slug": "photography", "fields": [
                        {"name": "فهم قواعد تكوين الصورة", "field_key": "composition", "field_type": "rating", "max_score": 5},
                        {"name": "ضبط إعدادات الكاميرا", "field_key": "camera_settings", "field_type": "rating", "max_score": 5},
                        {"name": "القدرة على التقاط صور واضحة ذات مغزى", "field_key": "photo_quality", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الإذاعة والتلفزيون", "slug": "broadcasting", "fields": [
                        {"name": "مستوى محاورة الجروح", "field_key": "vocal_skills", "field_type": "rating", "max_score": 5},
                        {"name": "جودة الصورة والتقديم", "field_key": "presentation_quality", "field_type": "rating", "max_score": 5},
                        {"name": "القدرة على قراءة نشرة أو تقديم برنامج", "field_key": "news_reading", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الكرافيك والديزاين", "slug": "graphic-design", "fields": [
                        {"name": "مستوى التمكن من أدوات برامج التصميم", "field_key": "software_skills", "field_type": "rating", "max_score": 5},
                        {"name": "تناسق الألوان والكتل في التصميم", "field_key": "color_harmony", "field_type": "rating", "max_score": 5},
                    ]},
                    {"name": "الذكاء الاصطناعي", "slug": "ai", "fields": [
                        {"name": "القدرة على كتابة الأوامر النصّية", "field_key": "prompt_writing", "field_type": "rating", "max_score": 5},
                        {"name": "استخدام تطبيقات الذكاء الاصطناعي", "field_key": "ai_apps_usage", "field_type": "rating", "max_score": 5},
                    ]},
                ],
            },
        ]

        for cdata in centers_data:
            center, _ = Center.objects.get_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"], "icon": cdata["icon"], "color": cdata["color"],
                    "axis": cdata["axis"], "weight": cdata["weight"], "order": cdata["order"],
                }
            )
            for adata in cdata.get("activities", []):
                activity, _ = Activity.objects.get_or_create(
                    center=center, slug=adata["slug"],
                    defaults={"name": adata["name"], "order": 0}
                )
                for i, fdata in enumerate(adata.get("fields", [])):
                    ActivityField.objects.get_or_create(
                        activity=activity, field_key=fdata["field_key"],
                        defaults={
                            "name": fdata["name"],
                            "field_type": fdata["field_type"],
                            "max_score": fdata.get("max_score", 5),
                            "order": i,
                        }
                    )
            for cldata in cdata.get("clinics", []):
                clinic, _ = Clinic.objects.get_or_create(
                    center=center, slug=cldata["slug"],
                    defaults={"name": cldata["name"], "order": 0}
                )
                for i, fdata in enumerate(cldata.get("fields", [])):
                    ClinicField.objects.get_or_create(
                        clinic=clinic, field_key=fdata["field_key"],
                        defaults={
                            "name": fdata["name"],
                            "field_type": fdata["field_type"],
                            "choices_text": fdata.get("choices_text", ""),
                            "unit": fdata.get("unit", ""),
                            "normal_min": fdata.get("normal_min"),
                            "normal_max": fdata.get("normal_max"),
                            "order": i,
                        }
                    )

        self.stdout.write(f"  المراكز: {Center.objects.count()}")
        self.stdout.write(f"  الأنشطة: {Activity.objects.count()}")
        self.stdout.write(f"  حقول الأنشطة: {ActivityField.objects.count()}")
        self.stdout.write(f"  العيادات: {Clinic.objects.count()}")
        self.stdout.write(f"  حقول العيادات: {ClinicField.objects.count()}")

    def _create_default_roles(self):
        all_perms = Permission.objects.all()

        admin_role, _ = Role.objects.get_or_create(
            name="مدير عام",
            defaults={"description": "صلاحيات كاملة على النظام", "is_system": True}
        )
        admin_role.permissions.set(all_perms)

        supervisor_role, _ = Role.objects.get_or_create(
            name="مشرف مركز",
            defaults={"description": "إدارة الأنشطة والتقييمات في مراكز محددة"}
        )
        supervisor_perms = Permission.objects.filter(
            resource__in=["beneficiaries", "assessments", "activities", "clinics", "dashboard"],
            action__in=["view", "add", "edit"]
        )
        supervisor_role.permissions.set(supervisor_perms)

        doctor_role, _ = Role.objects.get_or_create(
            name="طبيب",
            defaults={"description": "الوصول للملفات الطبية والتقييمات"}
        )
        doctor_perms = Permission.objects.filter(
            resource__in=["beneficiaries", "assessments", "clinics", "dashboard"],
            action__in=["view", "add", "edit"]
        )
        doctor_role.permissions.set(doctor_perms)

        trainer_role, _ = Role.objects.get_or_create(
            name="مدرّب نشاط",
            defaults={"description": "تسجيل بيانات الأنشطة فقط"}
        )
        trainer_perms = Permission.objects.filter(
            resource__in=["beneficiaries", "assessments", "activities"],
            action__in=["view", "add", "edit"]
        )
        trainer_role.permissions.set(trainer_perms)

        social_role, _ = Role.objects.get_or_create(
            name="أخصائي اجتماعي",
            defaults={"description": "الخدمة الاجتماعية والتقارير"}
        )
        social_perms = Permission.objects.filter(
            resource__in=["beneficiaries", "assessments", "dashboard", "reports"],
            action__in=["view", "add", "edit"]
        )
        social_role.permissions.set(social_perms)

        data_entry_role, _ = Role.objects.get_or_create(
            name="إدخال بيانات",
            defaults={"description": "إدخال بيانات المستفيدين والتقييمات فقط"}
        )
        data_entry_perms = Permission.objects.filter(
            resource__in=["beneficiaries", "assessments"],
            action__in=["view", "add", "edit"]
        )
        data_entry_role.permissions.set(data_entry_perms)

        self.stdout.write(f"  الأدوار: {Role.objects.count()}")

    def _create_admin(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="admin123",
                full_name="مدير النظام",
            )
            self.stdout.write("  المستخدم الإداري: admin / admin123")
