from django.contrib import admin
from .models import BannerImage, RushFormLink, RushSlide
from adminsortable2.admin import SortableAdminMixin

admin.site.register(BannerImage)
admin.site.register(RushFormLink)

class RushSlideAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('caption', 'image')

admin.site.register(RushSlide, RushSlideAdmin)