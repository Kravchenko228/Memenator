from django.contrib import admin
from .models import MemeTemplate, Meme, Rating

# Register your models here
admin.site.register(MemeTemplate)
admin.site.register(Meme)
admin.site.register(Rating)
