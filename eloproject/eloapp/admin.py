from django.contrib import admin
from .models import Race, RaceResult, Rider

# Register your models here.
admin.site.register(RaceResult)
admin.site.register(Race)
admin.site.register(Rider)