from django.contrib import admin
from .models import OmuraMuseum,UserPath,MuseumImage,MuseumEvaluation
# Register your models here.

admin.site.register(OmuraMuseum)
admin.site.register(MuseumImage)
admin.site.register(UserPath)
admin.site.register(MuseumEvaluation)