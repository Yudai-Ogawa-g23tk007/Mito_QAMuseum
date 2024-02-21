from django.contrib import admin
from .models import Museum,UserPath,MuseumImage,MuseumEvaluation
# Register your models here.

admin.site.register(Museum)
admin.site.register(MuseumImage)
admin.site.register(UserPath)
admin.site.register(MuseumEvaluation)