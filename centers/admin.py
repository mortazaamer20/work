from django.contrib import admin
from .models import Center, Activity, ActivityField, Clinic, ClinicField, GeneralField

admin.site.register(Center)
admin.site.register(Activity)
admin.site.register(ActivityField)
admin.site.register(Clinic)
admin.site.register(ClinicField)
admin.site.register(GeneralField)
